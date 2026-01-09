import pandas as pd
import google.generativeai as genai
import time
import requests
from datetime import datetime
import re
import concurrent.futures
from app.config import GOOGLE_API_KEY, DEFAULT_ASSET

# Configuration
genai.configure(api_key=GOOGLE_API_KEY)
# model = genai.GenerativeModel('gemini-2.0-flash-exp')
model = genai.GenerativeModel('gemini-1.5-flash')

QUESTDB_URL = "http://localhost:9000/exec"

def log(msg):
    print(msg, flush=True)

def get_data():
    # Fetch from 01:00 to provide 60min context for the first trade at 02:00
    query = "SELECT * FROM candles_history WHERE asset = 'EURUSD-op' AND timestamp >= '2026-01-07T01:00:00Z' AND timestamp <= '2026-01-07T03:30:00Z' ORDER BY timestamp ASC"
    r = requests.get(QUESTDB_URL, params={'query': query, 'fmt': 'json'})
    data = r.json()
    cols = [c['name'] for c in data['columns']]
    df = pd.DataFrame(data['dataset'], columns=cols)
    df['timestamp'] = pd.to_datetime(df['timestamp'])
    return df

def ask_gemini(df_window):
    latest = df_window.tail(60)[['timestamp', 'open', 'high', 'low', 'close', 'volume']].copy()
    latest['timestamp'] = latest['timestamp'].dt.strftime('%H:%M')
    
    prompt = f"""
    Act as a Quantitative Systematic Trader. Analyze these 60s candles for EURUSD-op.
    
    DATA (Last 1 hour):
    {latest.to_string(index=False)}
    
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
        return response.text.strip()
    except Exception as e:
        return f"ACTION: WAIT | CONFIDENCE: 0 | Error: {e}"

def parse_response(text):
    text_upper = text.upper()
    action = "WAIT"
    confidence = 0.0
    action_match = re.search(r'ACTION[:\s\"\'\*]+(CALL|PUT|WAIT)', text_upper)
    if action_match: action = action_match.group(1)
    conf_match = re.search(r'CONFIDENCE[:\s\"\'\*]+(\d+)', text_upper)
    if conf_match: confidence = float(conf_match.group(1))
    return action, confidence

def process_step(i, window, target):
    resp = ask_gemini(window)
    action, confidence = parse_response(resp)
    
    if action in ["CALL", "PUT"] and confidence >= 10:
        o, c = target['open'], target['close']
        win = (action == "CALL" and c > o) or (action == "PUT" and c < o)
        pl = 3400 if win else -4000
        res_str = "WIN" if win else "LOSS"
        log(f"{target['timestamp'].strftime('%H:%M')} | {action} | {confidence}% | {res_str} | {pl:+}")
        return {"time": target['timestamp'], "action": action, "conf": confidence, "res": res_str, "pl": pl}
    else:
        # Log even waits to see what's happening
        log(f"{target['timestamp'].strftime('%H:%M')} | {action} | {confidence}% | WAIT")

def run():
    df = get_data()
    log(f"✅ Cargadas {len(df)} velas. Iniciando simulación...")
    log(f"Sample data:\n{df.head().to_string()}")
    
    # We start from index where timestamp >= 02:00:00
    start_idx = df[df['timestamp'] >= '2026-01-07T02:00:00Z'].index[0]
    log(f"🚀 Simulando desde {df.iloc[start_idx]['timestamp']} hasta el final.")
    
    # Check first window
    window = df.iloc[start_idx-60:start_idx]
    log(f"First window size: {len(window)}")
    log(f"First window tail:\n{window.tail(3).to_string()}")
    
    trades = []
    # Analyze every candle in the interval
    indices = range(start_idx, len(df)-1)
    
    # SERIAL EXECUTION with delay to avoid 429
    for i in indices:
        res = process_step(i, df.iloc[i-60:i], df.iloc[i])
        if res: trades.append(res)
        time.sleep(5) # Safe RPM for 1.5 Flash

    trades.sort(key=lambda x: x['time'])
    results_df = pd.DataFrame(trades)
    
    if not results_df.empty:
        total = len(results_df)
        wins = len(results_df[results_df['res'] == 'WIN'])
        wr = (wins / total * 100)
        pnl = results_df['pl'].sum()
        log("\n" + "="*40)
        log(f"📊 RESUMEN 02:00 - 03:30 (HOY)")
        log(f"Total Trades: {total}")
        log(f"Wins: {wins} | Losses: {total-wins}")
        log(f"Win Rate: {wr:.2f}%")
        log(f"P&L: ${pnl:+,} COP")
        log("="*40)
    else:
        log("No se generaron trades con confianza >= 70%")

if __name__ == "__main__":
    run()
