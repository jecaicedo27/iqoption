import google.generativeai as genai
import pandas as pd
import numpy as np
import time
import re
import os
import sys
from datetime import datetime
from iqoptionapi.stable_api import IQ_Option
import iqoptionapi.constants as OP_code
from app.config import EMAIL, PASSWORD, DEFAULT_ASSET, DEFAULT_TIMEFRAME, DEFAULT_AMOUNT, ACCOUNT_TYPE
from app.db_quest import QuestDBManager

# Configuration
GOOGLE_API_KEY = "AIzaSyD3x7u6GNSLNIVXN8OuE3euORi9wZDcy6c"
genai.configure(api_key=GOOGLE_API_KEY)
model = genai.GenerativeModel('gemini-pro-latest') 

# ✅ FILTRO DE HORARIOS - Basado en análisis de 343 trades reales
ALLOWED_HOURS = [14, 21, 23]  # Solo operar en estas horas (WR >55%)
BLOCKED_HOURS = [19, 20, 22]  # NUNCA operar en estas horas (WR <40%)

def is_trading_allowed():
    """Verifica si el horario actual está permitido para trading"""
    current_hour = datetime.now().hour
    
    if current_hour in BLOCKED_HOURS:
        print(f"🚫 HORA BLOQUEADA: {current_hour}h - Win Rate históricamente <40%")
        return False
    
    if current_hour not in ALLOWED_HOURS:
        print(f"⏸️  HORA PAUSADA: {current_hour}h - Solo operamos en 14h, 21h, 23h")
        return False
    
    print(f"✅ HORA PERMITIDA: {current_hour}h - Win Rate históricamente >55%")
    return True

def get_market_data(api, asset, count=60):
    candidates = api.get_candles(asset, 15, count, time.time())
    if not candidates: return None
    df = pd.DataFrame(candidates)
    df.rename(columns={'max': 'high', 'min': 'low'}, inplace=True)
    return df

def ask_gemini(df):
    latest = df.tail(60).to_string(index=False)
    
    prompt = f"""
    Act as a Quantitative Systematic Trader. Analyze these {DEFAULT_TIMEFRAME}s candles for {DEFAULT_ASSET}.
    
    DATA (Last 1 hour):
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
        response = model.generate_content(prompt)
        text = response.text.strip()
        return text
    except Exception as e:
        return f"ACTION: WAIT | CONFIDENCE: 0 | Error: {e}"

def parse_response(text):
    raw_upper = text.upper()
    action = "WAIT"
    confidence = 0.0
    
    # Improved robust parsing
    if "ACTION: CALL" in raw_upper or '"ACTION": "CALL"' in raw_upper or "'ACTION': 'CALL'" in raw_upper: 
        action = "CALL"
    elif "ACTION: PUT" in raw_upper or '"ACTION": "PUT"' in raw_upper or "'ACTION': 'PUT'" in raw_upper: 
        action = "PUT"
    
    # Extract confidence
    conf_match = re.search(r'CONFIDENCE[:\s]+(\d+)', text, re.IGNORECASE)
    if conf_match:
        confidence = float(conf_match.group(1))
    
    return action, confidence, text

def run_llm_bot():
    print("🚀 GENESIS: Gemini Pro Trader ACTIVATED (CON FILTRO DE HORARIOS)")
    print(f"✅ Horas permitidas: {ALLOWED_HOURS}")
    print(f"🚫 Horas bloqueadas: {BLOCKED_HOURS}")
    
    # Init DB
    db = QuestDBManager()
    
    api = IQ_Option(EMAIL, PASSWORD)
    if not api.connect():
        print("❌ Connection Failed")
        return
        
    print(f"✅ Connected to IQ Option. Mode: {ACCOUNT_TYPE}")
    api.change_balance(ACCOUNT_TYPE)
    print(f"🎯 Default Asset: {DEFAULT_ASSET} | Amount: ${DEFAULT_AMOUNT}")
    
    iteration = 0
    
    while True:
        try:
            iteration += 1
            print(f"\n{'='*60}")
            print(f"🔄 Cycle #{iteration} | {time.strftime('%Y-%m-%d %H:%M:%S')}")
            
            # ✅ VERIFICAR HORARIO ANTES DE ANALIZAR
            if not is_trading_allowed():
                print("⏸️  Esperando próxima hora permitida...")
                time.sleep(300)  # Esperar 5 minutos
                continue
            
            df = get_market_data(api, DEFAULT_ASSET)
            if df is None or len(df) < 10:
                print("⚠️  Insufficient Data")
                time.sleep(15)
                continue
            
            print(f"📊 Got {len(df)} candles. Analyzing...")
            gemini_raw = ask_gemini(df)
            print(f"🧠 Gemini: {gemini_raw[:150]}...")
            
            action, confidence, raw_text = parse_response(gemini_raw)
            print(f"📌 Parsed => ACTION: {action} | CONFIDENCE: {confidence}%")
            
            # Only trade if confidence >= 70%
            if action in ["CALL", "PUT"] and confidence >= 70:
                print(f"🎯 HIGH CONFIDENCE ({confidence}%) => EXECUTING {action}")
                
                direction = "call" if action == "CALL" else "put"
                check, trade_id = api.buy(DEFAULT_AMOUNT, DEFAULT_ASSET, direction, DEFAULT_TIMEFRAME)
                
                if check:
                    trade_timestamp = int(time.time())
                    print(f"✅ Trade Executed | ID: {trade_id} | Amount: ${DEFAULT_AMOUNT}")
                    
                    # Save to QuestDB with PENDING status
                    db.save_trade(
                        asset=DEFAULT_ASSET,
                        direction=direction,
                        amount=DEFAULT_AMOUNT,
                        confidence=confidence,
                        result="PENDING",
                        profit=0,
                        timestamp=trade_timestamp,
                        ai_reason=raw_text[:200]
                    )
                    
                    # Wait 90 seconds for trade to close
                    print("⏳ Waiting 90s for trade result...")
                    time.sleep(90)
                    
                    # Get result from IQ Option
                    try:
                        # Get recent trades from API
                        trades = api.get_optionsv2()
                        
                        # Find our trade
                        our_trade = None
                        for t in trades:
                            if t.get('id') == trade_id:
                                our_trade = t
                                break
                        
                        if our_trade:
                            win_amount = our_trade.get('win', 0)
                            if win_amount > 0:
                                result = "WIN"
                                profit = win_amount - DEFAULT_AMOUNT
                            else:
                                result = "LOSS"
                                profit = -DEFAULT_AMOUNT
                            
                            print(f"📊 Trade Result: {result} | Profit: ${profit:+.2f}")
                            
                            # Update in QuestDB
                            db.update_trade_result(
                                asset=DEFAULT_ASSET,
                                timestamp=trade_timestamp,
                                result=result,
                                profit=profit
                            )
                        else:
                            print("⚠️  Could not find trade result")
                    
                    except Exception as e:
                        print(f"⚠️  Error fetching trade result: {e}")
                    
                else:
                    print(f"❌ Trade Failed | Reason: {trade_id}")
            else:
                print(f"⏸️  NO TRADE: Confidence {confidence}% < 70% or action is WAIT")
            
            time.sleep(15)
            
        except KeyboardInterrupt:
            print("\n\n🛑 Bot stopped by user")
            break
        except Exception as e:
            print(f"❌ ERROR: {e}")
            time.sleep(15)
            continue

if __name__ == "__main__":
    run_llm_bot()
