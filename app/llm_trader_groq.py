import pandas as pd
import time
import re
import sys
from datetime import datetime
from groq import Groq
from iqoptionapi.stable_api import IQ_Option
import iqoptionapi.constants as OP_code
from app.config import EMAIL, PASSWORD, DEFAULT_ASSET, DEFAULT_TIMEFRAME, DEFAULT_AMOUNT, ACCOUNT_TYPE, GROQ_API_KEY
from app.db_sqlite import SQLiteManager # Switched to SQLite

# Configuration for Groq
client = Groq(api_key=GROQ_API_KEY)
MODEL_NAME = "llama-3.1-8b-instant"  # Back to standard model

def get_market_data(api, asset, count=60):
    # Fetch 60 candles of 60 seconds (1 minute each) = 1 hour of context
    candidates = api.get_candles(asset, 60, count, time.time())
    if not candidates: return None
    df = pd.DataFrame(candidates)
    df.rename(columns={'max': 'high', 'min': 'low'}, inplace=True)
    return df

def ask_groq_llm(df):
    """Use Groq API with LLaMA 3.1 70B"""
    latest = df.tail(60).to_string(index=False)
    
    # PROMPT ORIGINAL (FLEXIBLE)
    prompt = f"""
    Act as a Quantitative Systematic Trader. Analyze these 60s candles for {DEFAULT_ASSET}.
    
    DATA (Last 1 hour):
    {latest}
    
    TASK: Analyze the market data to predict the direction for the NEXT candle (1 minute).
    
    STRATEGY GUIDELINES ("TREND KILLER"):
    1. **FOLLOW THE TREND**: This is an OTC market. Trends persist. DO NOT bet on reversals unless there is a massive rejection wick.
    2. **MOMENTUM**: If the last 3 candles are same color, assume continuation.
    3. **AVOID CALLS IN DOWNTRENDS**: If price is making lower lows, ONLY trade PUT or WAIT.
    4. **AVOID PUTS IN UPTRENDS**: If price is making higher highs, ONLY trade CALL or WAIT.
    5. **REVERSAL CONFIRMATION**: If betting on a reversal (e.g., CALL after downtrend), you MUST wait for a GREEN candle to close first. Never catch a falling knife.
    
    OUTPUT FORMAT (Strict JSON):
    
    RESPONSE FORMAT:
    Return ONLY a JSON object. Do not add any text before or after.
    {{
        "ACTION": "CALL" | "PUT" | "WAIT",
        "CONFIDENCE": 80-100,
        "REASON": "Short logical explanation citing Trend and Momentum."
    }}
    """
    
    try:
        chat_completion = client.chat.completions.create(
            messages=[
                {
                    "role": "user",
                    "content": prompt,
                }
            ],
            model=MODEL_NAME,
            temperature=0.3,
            max_tokens=200,
        )
        
        return chat_completion.choices[0].message.content
            
    except Exception as e:
        return f"ACTION: WAIT | CONFIDENCE: 0 | Error: {e}"

def parse_response(text):
    text = text.strip()
    action = "WAIT"
    confidence = 0.0
    
    try:
        # Try JSON parsing first
        import json
        if "{" in text:
            # Extract JSON if there's extra text
            start = text.find("{")
            end = text.rfind("}") + 1
            json_str = text[start:end]
            data = json.loads(json_str)
            action = data.get("ACTION", "WAIT").upper()
            confidence = float(data.get("CONFIDENCE", 0))
            return action, confidence, text
    except:
        pass

    # Fallback to Regex
    text_upper = text.upper()
    action_match = re.search(r'ACTION[:\s\"\'\*]+(CALL|PUT|WAIT)', text_upper)
    if action_match:
        action = action_match.group(1)
    
    conf_match = re.search(r'CONFIDENCE[:\s\"\'\*]+(\d+)', text_upper)
    if conf_match:
        confidence = float(conf_match.group(1))
    
    return action, confidence, text

def run_llm_bot():
    print("🚀 GROQ API BOT ACTIVATED (LLaMA 3.1 70B)")
    print(f"✅ Asset: {DEFAULT_ASSET} | Prompt: ORIGINAL (FLEXIBLE)")
    print(f"✅ Config: Confianza > 75% | Model: {MODEL_NAME}")
    print(f"⚡ VELOCIDAD: ~0.5-1 segundo | COSTO: $0/mes (Tier Gratuito)")
    
    # Initialize DB (SQLite)
    db = SQLiteManager()
    
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
    consecutive_losses = 0
    
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
            
            start_time = time.time()
            groq_raw = ask_groq_llm(df)
            elapsed = time.time() - start_time
            
            action, confidence, raw_text = parse_response(groq_raw)
            print(f"🧠 AI: {action} ({confidence}%) | ⚡ Response time: {elapsed:.2f}s")
            
            if confidence == 0:
                print(f"⚠️ RAW ERROR: {groq_raw[:200]}")
                if "429" in groq_raw or "Rate limit" in groq_raw:
                    print("⛔ Rate Limit Hit: Sleeping for 120s...")
                    time.sleep(120)
                    continue
            
            # Only trade if confidence >= 75%
            if action in ["CALL", "PUT"] and confidence >= 75:
                print(f"🔥 HIGH CONFIDENCE ({confidence}%) => EXECUTING {action}")
                
                direction = "call" if action == "CALL" else "put"
                
                # --- ACTION MODE: Prority to Speed ---
                
                # Try 1: Turbo Binary (1 min)
                trade_id = None
                check, trade_id = api.buy(DEFAULT_AMOUNT, DEFAULT_ASSET, direction, 1)
                
                if not check:
                    print(f"⚠️ Turbo Failed. Reason: {trade_id}") # trade_id contains error reason if check=False
                    # Try 2: Digital Spot (1 min)
                    print("⚠️ Trying Digital 1m...")
                    check, trade_id = api.buy_digital_spot(DEFAULT_ASSET, DEFAULT_AMOUNT, direction, 1)
                
                if not check:
                    # Try 3: Binary (5 min) - Still acceptable action
                    print("⚠️ Digital 1m closed, trying Binary 5m...")
                     # Note: buy() uses minutes for interval
                    check, trade_id = api.buy(DEFAULT_AMOUNT, DEFAULT_ASSET, direction, 5)

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
                    
                    
                    # Initialize result
                    result = "UNKNOWN"
                    profit = 0
                    
                    start_wait = time.time()
                    while time.time() - start_wait < 360: # Max wait 6 mins
                        # Check Standard Binary Result
                        res_bin = api.check_win_v3(trade_id)
                        if res_bin is not None:
                            profit = res_bin
                            result = "WIN" if profit > 0 else "LOSS"
                            break

                        # Check Digital Result
                        check_dig, profit_dig = api.check_win_digital_v2(trade_id)
                        if check_dig:
                             profit = profit_dig
                             result = "WIN" if profit > 0 else "LOSS"
                             break
                        
                        time.sleep(1) # Prevent CPU burn
                    
                    print(f"📊 Result: {result} | Profit: ${profit}")
                    
                    db.update_trade_result(
                        trade_id=trade_id,
                        result=result,
                        profit=profit
                    )

                    if result == "WIN":
                         consecutive_losses = 0
                    elif result == "LOSS":
                         consecutive_losses += 1
                         if consecutive_losses >= 3:
                             print("⛔ 3 Consecutive Losses. Cooling down for 10 minutes...")
                             time.sleep(600)
                             consecutive_losses = 0
                else:
                    print(f"❌ Trade Failed: {trade_id}")
            
            # Adjusted to 45s to stay safer from Rate Limits
            time.sleep(45)
            
        except KeyboardInterrupt:
            print("\n\n🛑 Bot stopped by user")
            break
        except Exception as e:
            print(f"❌ ERROR: {e}")
            time.sleep(5)
            continue

if __name__ == "__main__":
    run_llm_bot()
