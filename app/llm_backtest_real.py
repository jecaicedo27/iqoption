import google.generativeai as genai
import pandas as pd
import numpy as np
import time
import os
import re
import iqoptionapi.constants as OP_code
from iqoptionapi.stable_api import IQ_Option
from app.config import EMAIL, PASSWORD, DEFAULT_ASSET, DEFAULT_AMOUNT, ACCOUNT_TYPE
from app.db_quest import QuestDBManager
from concurrent.futures import ThreadPoolExecutor, as_completed

# Configuration
GOOGLE_API_KEY = "AIzaSyD3x7u6GNSLNIVXN8OuE3euORi9wZDcy6c"
genai.configure(api_key=GOOGLE_API_KEY)
model_instance = genai.GenerativeModel('gemini-pro-latest')

# Inject EURUSD-op
OP_code.ACTIVES["EURUSD-op"] = 1861

def get_historical_candles(api, asset, count=360):
    print(f"📥 Fetching last {count} minutes of data for {asset}...")
    candles = api.get_candles(asset, 60, count, time.time())
    if not candles:
        return None
    df = pd.DataFrame(candles)
    df.rename(columns={'max': 'high', 'min': 'low'}, inplace=True)
    return df

def ask_gemini_sim(i, window, prev_close, actual_next_close):
    """
    Worker function for parallel AI calls. Pure Price Action.
    """
    latest_str = window.to_string(index=False)
    
    prompt = f"""
    Act as a Precision Systematic Trader. Analyze these 60s candles for EURUSD-op.
    
    DATA (Last 60m):
    {latest_str}
    
    TASK: Identify ULTRA-HIGH probability entries for the next 1 minute.
    
    CRITICAL: You are an extremely conservative trader. Only suggest CALL or PUT if you see a 100% clear, 
    undeniable high-conviction pattern (e.g. strong reversal at support/resistance, or perfect continuation).
    If the signal is anything less than certain, respond with 'WAIT'.
    
    RESPONSE FORMAT:
    ACTION: [CALL, PUT, or WAIT]
    CONFIDENCE: [0-100]
    REASON: [Short logical explanation]
    """
    
    try:
        response = model_instance.generate_content(prompt)
        text = response.text.upper()
        
        # Parse Action
        action = "WAIT"
        if "ACTION: CALL" in text: action = "CALL"
        elif "ACTION: PUT" in text: action = "PUT"
        
        # Parse Confidence
        conf = 0
        match = re.search(r"CONFIDENCE:\s*(\d+)", text)
        if match:
            conf = int(match.group(1)) / 100.0
            
        return {
            'index': i,
            'action': action,
            'conf': conf,
            'prev_close': prev_close,
            'actual_next_close': actual_next_close,
            'timestamp': window.iloc[-1]['from'] + 60
        }
    except Exception as e:
        return {'index': i, 'action': 'ERROR', 'error': str(e)}

def run_simulation():
    print("🚀 GENESIS: Ultra-Precision (85%) Price Action Sim")
    db = QuestDBManager()
    
    api = IQ_Option(EMAIL, PASSWORD)
    if not api.connect():
        print("❌ Connection Failed")
        return

    lookback_minutes = 360
    df = get_historical_candles(api, "EURUSD-op", lookback_minutes)
    if df is None or len(df) < 61:
        print("❌ Not enough data for simulation.")
        return

    print(f"\n⚡ Parallel Processing {len(df)-61} candles (Sliding Window)...")
    
    tasks = []
    with ThreadPoolExecutor(max_workers=5) as executor:
        for i in range(60, len(df) - 1):
            window = df.iloc[i-60:i]
            actual_next_close = df.iloc[i]['close']
            prev_close = df.iloc[i-1]['close']
            tasks.append(executor.submit(ask_gemini_sim, i, window, prev_close, actual_next_close))

        completed_count = 0
        trade_count = 0
        win_count = 0
        
        for future in as_completed(tasks):
            res = future.result()
            completed_count += 1
            
            if completed_count % 20 == 0:
                print(f"📈 Progress: {completed_count}/{len(tasks)} Analyzed")
            
            # 85% Confidence Threshold
            if res['action'] in ["CALL", "PUT"] and res['conf'] >= 0.85:
                trade_count += 1
                is_win = False
                if res['action'] == "CALL" and res['actual_next_close'] > res['prev_close']: is_win = True
                if res['action'] == "PUT" and res['actual_next_close'] < res['prev_close']: is_win = True
                
                outcome = "WIN" if is_win else "LOSS"
                if is_win: win_count += 1
                
                profit = 1.0 if is_win else -1.0
                features = [[res['actual_next_close'], 0, 0]]
                
                db.save_trade(
                    asset="EURUSD-op",
                    price=res['prev_close'],
                    prediction=res['action'],
                    confidence=res['conf'],
                    features=features,
                    result=outcome,
                    profit=profit,
                    timestamp=res['timestamp'],
                    model_name="Sim-Gemini-Ultra-85"
                )
                print(f"💎 PRECISION TRADE [{res['index']}]: {res['action']} ({res['conf']:.2f}) -> {outcome}")

    if trade_count > 0:
        win_rate = (win_count / trade_count) * 100
        print(f"\n--- 📊 FINAL ULTRA-85 REPORT ---")
        print(f"Total Analyzed: {completed_count}")
        print(f"Trades Executed: {trade_count}")
        print(f"Win Rate: {win_rate:.2f}%")
        print(f"Average Win Rate vs Baseline (52.8%): {win_rate - 52.8:.2f}% improvement")
    else:
        print("\n🏁 SIMULATION COMPLETE: No trades were confident enough at 85%.")

if __name__ == "__main__":
    run_simulation()
