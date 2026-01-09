import pandas as pd
import time
import re
import sys
import requests
import json
from datetime import datetime
from iqoptionapi.stable_api import IQ_Option
import iqoptionapi.constants as OP_code
from app.config import EMAIL, PASSWORD, DEFAULT_ASSET, DEFAULT_TIMEFRAME, DEFAULT_AMOUNT, ACCOUNT_TYPE
from app.db_quest import QuestDBManager

# Configuration for local Ollama
OLLAMA_URL = "http://localhost:11434/api/generate"
MODEL_NAME = "llama3.1:8b"

def wait_for_next_candle():
    """Wait until the 57th second of the current minute to trigger analysis"""
    print("⏳ Synchronizing with next candle (Sniper Mode)...")
    while True:
        now = datetime.now()
        if now.second == 57:
            time.sleep(0.1)
            break
        time.sleep(0.5)

def get_market_data(api, asset, count=60):
    # Fetch 60 candles of 60 seconds (1 minute each) = 1 hour of context
    candidates = api.get_candles(asset, 60, count, time.time())
    if not candidates: return None
    df = pd.DataFrame(candidates)
    df.rename(columns={'max': 'high', 'min': 'low'}, inplace=True)
    return df

def ask_local_llm(df):
    """Use local LLaMA 3.1 via Ollama"""
    # Solo últimas 20 velas (20 min) en lugar de 60 para mayor velocidad
    latest = df.tail(20).to_string(index=False)
    
    # PROMPT ORIGINAL (FLEXIBLE) - Optimizado para velocidad
    prompt = f"""
    Act as a Quantitative Systematic Trader. Analyze these 60s candles for {DEFAULT_ASSET}.
    
    DATA (Last 20 minutes):
    {latest}
    
    TASK: Identify High Probability setups for the next 1 minute.
    
    CRITERIA: Look for strong trend continuations or clear reversals at key levels.
    Analyze Volume, Close Price, and recent Volatility.
    
    RESPONSE FORMAT:
    ACTION: [CALL, PUT, or WAIT]
    CONFIDENCE: [0-100]
    REASON: [Short logical explanation]
    """
    
    try:
        response = requests.post(OLLAMA_URL, 
            json={
                "model": MODEL_NAME,
                "prompt": prompt,
                "stream": False
            },
            timeout=180  # 3 minute timeout (más tiempo para CPU)
        )
        
        if response.status_code == 200:
            result = response.json()
            return result.get('response', 'ERROR: No response')
        else:
            return f"ACTION: WAIT | CONFIDENCE: 0 | Error: API returned {response.status_code}"
            
    except Exception as e:
        return f"ACTION: WAIT | CONFIDENCE: 0 | Error: {e}"

def parse_response(text):
    text_upper = text.upper()
    action = "WAIT"
    confidence = 0.0
    
    # Regex for Action
    action_match = re.search(r'ACTION[:\s\"\'\*]+(CALL|PUT|WAIT)', text_upper)
    if action_match:
        action = action_match.group(1)
    
    # Extract confidence
    conf_match = re.search(r'CONFIDENCE[:\s\"\'\*]+(\d+)', text_upper)
    if conf_match:
        confidence = float(conf_match.group(1))
    
    return action, confidence, text

def run_llm_bot():
    print("🚀 LOCAL LLM BOT ACTIVATED (LLaMA 3.1 8B)")
    print(f"✅ Asset: {DEFAULT_ASSET} | Prompt: ORIGINAL (FLEXIBLE)")
    print(f"✅ Config: Confianza > 75% | Model: {MODEL_NAME}")
    print(f"💰 COSTO API: $0/mes (100% Local)")
    
    # Init DB
    db = QuestDBManager()
    
    api = IQ_Option(EMAIL, PASSWORD)
    if not api.connect():
        print("❌ Connection Failed")
        return
        
    print("🔄 Updating OpCodes...")
    api.update_ACTIVES_OPCODE()
    
    print(f"✅ Connected to IQ Option. Mode: {ACCOUNT_TYPE}")
    api.change_balance(ACCOUNT_TYPE)
    print(f"🎯 Default Asset: {DEFAULT_ASSET} | Amount: ${DEFAULT_AMOUNT}")
    
    iteration = 0
    last_trade_candle = 0
    
    while True:
        try:
            if not api.check_connect():
                print("⚠️  Lost connection. Reconnecting...")
                api.connect()
                
            iteration += 1
            
            df = get_market_data(api, DEFAULT_ASSET)
            
            if df is None or len(df) < 10:
                print("⚠️  Insufficient Data. Retrying...")
                time.sleep(2) 
                continue
            
            # Check if we already traded this candle
            current_candle_time = df.iloc[-1]['from']
            if current_candle_time == last_trade_candle:
                time.sleep(2)
                continue

            print(f"\n🎯 Analyzing Candle {time.strftime('%H:%M:%S', time.localtime(current_candle_time))}...")
            
            llm_raw = ask_local_llm(df)
            action, confidence, raw_text = parse_response(llm_raw)
            print(f"🧠 AI: {action} ({confidence}%)")
            
            if confidence == 0:
                print(f"⚠️ RAW ERROR: {llm_raw[:200]}")
            
            # Only trade if confidence >= 75%
            if action in ["CALL", "PUT"] and confidence >= 75:
                print(f"🔥 HIGH CONFIDENCE ({confidence}%) => EXECUTING {action}")
                
                direction = "call" if action == "CALL" else "put"
                check, trade_id = api.buy(DEFAULT_AMOUNT, DEFAULT_ASSET, direction, DEFAULT_TIMEFRAME)
                
                if check:
                    last_trade_candle = current_candle_time
                    
                    trade_timestamp = int(time.time())
                    print(f"✅ Trade Executed | ID: {trade_id}")
                    
                    db.save_trade(
                        asset=DEFAULT_ASSET,
                        timestamp=trade_timestamp,
                        trade_id=trade_id,
                        direction=action.lower(),
                        amount=DEFAULT_AMOUNT,
                        confidence=confidence,
                        ai_reason=raw_text,
                        market_data=df.to_json()
                    )
                    
                    print("⏳ Waiting for result...")
                    result_value = api.check_win_v3(trade_id)
                    
                    result = "UNKNOWN"
                    profit = 0
                    
                    if result_value is not None:
                        if result_value > 0:
                            result = "WIN"
                            profit = result_value
                        elif result_value < 0:
                            result = "LOSS"
                            profit = result_value
                        else:
                            result = "PUSH"
                            profit = 0
                    
                    print(f"📊 Result: {result} | Profit: ${profit}")
                    
                    db.update_trade_result(
                        trade_id=trade_id,
                        result=result,
                        profit=profit
                    )
                else:
                    print(f"❌ Trade Failed")
            
            # Ultra-conservative checking (every 60 seconds)
            time.sleep(60)
            
        except KeyboardInterrupt:
            print("\n\n🛑 Bot stopped by user")
            break
        except Exception as e:
            print(f"❌ ERROR: {e}")
            time.sleep(5)
            continue

if __name__ == "__main__":
    run_llm_bot()
