import google.generativeai as genai
import pandas as pd
import numpy as np
import time
import re
import os
import sys
from iqoptionapi.stable_api import IQ_Option
import iqoptionapi.constants as OP_code
from app.config import EMAIL, PASSWORD, DEFAULT_ASSET, DEFAULT_TIMEFRAME, DEFAULT_AMOUNT, ACCOUNT_TYPE
from app.db_quest import QuestDBManager

# Configuration
GOOGLE_API_KEY = "AIzaSyD3x7u6GNSLNIVXN8OuE3euORi9wZDcy6c"
genai.configure(api_key=GOOGLE_API_KEY)
model = genai.GenerativeModel('gemini-pro-latest') 

def get_market_data(api, asset, count=60):
    candidates = api.get_candles(asset, 15, count, time.time())
    if not candidates: return None
    df = pd.DataFrame(candidates)
    df.rename(columns={'max': 'high', 'min': 'low'}, inplace=True)
    return df

def ask_gemini(df):
    latest = df.tail(30).to_string(index=False)
    
    prompt = f"""
    Act as a Quantitative Systematic Trader. Analyze these {DEFAULT_TIMEFRAME}s candles for {DEFAULT_ASSET}.
    
    DATA (Last 30 minutes):
    {latest}
    
    CRITICAL RULE: ONLY trade during CLEAR TRENDS. AVOID sideways/ranging markets.
    
    TASK: 
    1. First, identify if we are in a CLEAR UPTREND or DOWNTREND:
       - UPTREND: Series of higher highs and higher lows
       - DOWNTREND: Series of lower highs and lower lows
    
    2. If NO clear trend (sideways/choppy), respond with WAIT.
    
    3. If CLEAR trend exists, identify High Probability trend continuation setups.
    
    CRITERIA: 
    - Strong directional bias over last 15-30 minutes
    - Volume confirmation
    - Avoid consolidations, tight ranges, and indecision
    
    RESPONSE FORMAT:
    ACTION: [CALL, PUT, or WAIT]
    CONFIDENCE: [0-100]
    REASON: [State if trending or sideways, then explain setup]
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
    
    try:
        match = re.search(r"CONFIDENCE[:\s\"']+(\d+)", raw_upper)
        if match:
            confidence = float(match.group(1)) / 100.0
    except:
        confidence = 0.0
        
    return action, confidence, text

def run_llm_bot():
    print("🚀 GENESIS: Gemini Pro Trader ACTIVATED (Reverted 75%)")
    
    # Init DB
    db = QuestDBManager()
    
    api = IQ_Option(EMAIL, PASSWORD)
    if not api.connect():
        print("❌ Connection Failed")
        return
        
    print(f"✅ Connected to IQ Option. Mode: {ACCOUNT_TYPE}")
    api.change_balance(ACCOUNT_TYPE) # Force Practice or Real from config
    print(f"🎯 Default Asset: {DEFAULT_ASSET} | Amount: ${DEFAULT_AMOUNT}")
    
    # --- ADVANCED REAL MARKET INJECTION ---
    if DEFAULT_ASSET == "EURUSD-op":
        print("🧬 Injecting EURUSD-op (ID: 1861) for Real Market Access...")
        OP_code.ACTIVES["EURUSD-op"] = 1861
    # -------------------------------------
    
    last_trade_candle = 0
    
    while True:
        try:
            df = get_market_data(api, DEFAULT_ASSET)
            if df is not None:
                # === PRE-FILTER: Detect Sideways Market ===
                # Calculate price range over last 15 candles (15 minutes)
                last_15 = df.tail(15)
                price_high = last_15['close'].max()
                price_low = last_15['close'].min()
                price_range = price_high - price_low
                current_price = df.iloc[-1]['close']
                
                # Calculate range as % of price
                range_pct = (price_range / current_price) * 100
                
                # If range is less than 0.05% (5 pips on EURUSD), it's sideways
                if range_pct < 0.05:
                    print(f"⚠️ SIDEWAYS MARKET DETECTED | Range: {range_pct:.3f}% | Skipping AI...")
                    time.sleep(15)
                    continue
                
                print(f"✅ Market Volatile Enough | Range: {range_pct:.3f}%")
                
                # Candle Identity
                current_candle_id = df.iloc[-1]['from'] # Timestamp of current candle
                
                # Ask AI
                raw_response = ask_gemini(df)
                action, conf, reason = parse_response(raw_response)
                
                print(f"\n--- AI PASS ---")
                print(f"RAW: {raw_response}")
                print(f"🤖 Gemini: {action} (Conf: {conf:.2f})")
                
                if action in ["CALL", "PUT"] and conf >= 0.75: # REVERTED: Min Confidence 75%
                    
                    # SAFETY CHECK: One trade per candle
                    if current_candle_id == last_trade_candle:
                         print(f"🛡️ SAFETY: Skipping duplicate trade on candle {current_candle_id}")
                         time.sleep(5)
                         continue
                         
                    print(f"🔥 Executing {action}...")
                    
                    # 1. Try Standard Turbo/Binary (Most liquid usually)
                    check, trade_id = api.buy(
                        DEFAULT_AMOUNT, 
                        DEFAULT_ASSET, 
                        action.lower(), 
                        1 # 1 Minute Turbo
                    )
                    
                    if check:
                        print(f"✅ BINARY Trade {trade_id} Placed.")
                        result_type = "BINARY"
                    else:
                        print("⚠️ Binary Rejected. Trying Digital...")
                        # 2. Fallback to Digital Options (Spot)
                        # CRITICAL FIX: Add timeout to prevent freezing
                        import signal
                        
                        def timeout_handler(signum, frame):
                            raise TimeoutError("Digital API timeout")
                        
                        try:
                            # Set 10 second timeout
                            signal.signal(signal.SIGALRM, timeout_handler)
                            signal.alarm(10)
                            
                            check, trade_id = api.buy_digital_spot(
                                DEFAULT_ASSET, 
                                DEFAULT_AMOUNT, 
                                action.lower(), 
                                1 # 1 minute duration
                            )
                            
                            signal.alarm(0)  # Cancel alarm
                        except TimeoutError:
                            print("❌ Digital TIMEOUT (10s). Skipping.")
                            check = False
                        except Exception as e:
                            print(f"❌ Digital Error: {e}")
                            check = False
                        
                        if check:
                            print(f"✅ DIGITAL Trade {trade_id} Placed.")
                            result_type = "DIGITAL"
                        else:
                            print("❌ ALL Rejected (Market Closed?)")
                            result_type = "FAILED"
                    
                    if check:
                        # Log to DB (Initially as PENDING)
                        # UPDATE SAFETY VAR
                        last_trade_candle = current_candle_id
                        
                        current_price = df.iloc[-1]['close']
                        trade_timestamp = time.time()
                        
                        db.save_trade(
                            asset=DEFAULT_ASSET,
                            price=current_price,
                            prediction=action,
                            confidence=conf,
                            features=[[current_price, 0, 0]], 
                            result="PENDING",
                            timestamp=trade_timestamp,
                            model_name=f"Gemini-Hybrid-75-{result_type}"
                        )
                        
                        # Wait for trade to complete (1 min trade + buffer)
                        print("⏳ Esperando 90s para verificar resultado...")
                        time.sleep(90)
                        
                        # Check result
                        try:
                            # Get recent position history
                            res = api.get_position_history_v2("binary-option", 10, 0, 0, 0)
                            
                            if isinstance(res, tuple) and res[0]:
                                history = res[1].get('positions', [])
                                
                                # Find our trade (closest by time)
                                for trade in history:
                                    close_time = trade['close_time'] / 1000
                                    if abs(close_time - trade_timestamp) < 120:  # Within 2 minutes
                                        pl = float(trade['close_profit']) - float(trade['invest'])
                                        result = 'WIN' if pl > 0 else 'LOSS'
                                        
                                        # Update in DB
                                        db.update_trade_result(
                                            asset=DEFAULT_ASSET,
                                            timestamp=trade_timestamp,
                                            result=result,
                                            profit=pl
                                        )
                                        break
                        except Exception as e:
                            print(f"⚠️ Error verificando resultado: {e}")
                        
                else:
                    print("🔭 Loitering...")
                    
            time.sleep(15)
            
        except KeyboardInterrupt:
            print("👋 Bye")
            break
        except Exception as e:
            print(f"⚠️ Error: {e}")
            time.sleep(5)

if __name__ == "__main__":
    run_llm_bot()
