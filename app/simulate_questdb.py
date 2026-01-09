import pandas as pd
import google.generativeai as genai
import time
from datetime import datetime
from app.db_quest import QuestDBManager
from app.config import GOOGLE_API_KEY
import re # Keep re for parse_response function

# Configuration
genai.configure(api_key=GOOGLE_API_KEY)
# model = genai.GenerativeModel('gemini-pro')
model = genai.GenerativeModel('gemini-pro-latest')

def log(msg):
    print(msg, flush=True)
    with open("debug_log.txt", "a") as f:
        f.write(msg + "\n")

def get_data_from_questdb():
    log("📡 Descargando datos desde QuestDB (candles_history)...")
    query = "SELECT * FROM candles_history ORDER BY timestamp ASC"
    try:
        r = requests.get("http://localhost:9000/exec", params={'query': query, 'fmt': 'json'})
        if r.status_code == 200:
            data = r.json()
            if 'dataset' in data:
                cols = [c['name'] for c in data['columns']]
                df = pd.DataFrame(data['dataset'], columns=cols)
                df['timestamp'] = pd.to_datetime(df['timestamp'])
                log(f"✅ Cargados {len(df)} registros desde DB")
                return df
            else:
                log("⚠️ Estructura JSON inesperada")
                return None
        else:
            log(f"❌ Error HTTP: {r.text}")
            return None
    except Exception as e:
        log(f"❌ Error conexión DB: {e}")
        return None

def ask_gemini(df_window):
    cols_to_show = ['timestamp', 'open', 'high', 'low', 'close', 'volume']
    data_str = df_window[cols_to_show].copy()
    data_str['timestamp'] = data_str['timestamp'].dt.strftime('%H:%M')
    latest = data_str.tail(60).to_string(index=False)
    
    prompt = f"""
    Act as a Quantitative Systematic Trader. Analyze these 60 candles for EURUSD-op (1 min timeframe).
    
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
        return response.text.strip()
    except Exception as e:
        raise e

def parse_response(text):
    raw_upper = text.upper()
    action = "WAIT"
    confidence = 0.0
    
    if "ACTION: CALL" in raw_upper or '"ACTION": "CALL"' in raw_upper: action = "CALL"
    elif "ACTION: PUT" in raw_upper or '"ACTION": "PUT"' in raw_upper: action = "PUT"
    
    match = re.search(r'CONFIDENCE[:\s]+(\d+)', text, re.IGNORECASE)
    if match: confidence = float(match.group(1))
    
    return action, confidence

import concurrent.futures

def process_candle(i, window, target_candle):
    try:
        response = ask_gemini(window)
        action, confidence = parse_response(response)
        
        if action in ["CALL", "PUT"] and confidence >= 70:
            open_price = target_candle['open']
            close_price = target_candle['close']
            
            result = "PENDING"
            pl = 0
            
            if action == "CALL":
                if close_price > open_price:
                    result = "WIN"
                    pl = 3320
                elif close_price < open_price:
                    result = "LOSS"
                    pl = -4000
                else: 
                    result = "PUSH"
                    pl = 0
            elif action == "PUT":
                if close_price < open_price:
                    result = "WIN"
                    pl = 3320
                elif close_price > open_price:
                    result = "LOSS"
                    pl = -4000
                else:
                    result = "PUSH"
                    pl = 0
            
            # Formato de fila para log instantáneo
            symbol = "✅" if result == "WIN" else "❌" if result == "LOSS" else "➖"
            time_str = target_candle['timestamp'].strftime('%H:%M')
            row_str = f"{time_str:<6} | {action:<4} | {confidence:<4}% | {symbol} {result:<4} | {pl:+}"
            log(row_str)
            
            return {
                "time": target_candle['timestamp'],
                "action": action,
                "confidence": confidence,
                "result": result,
                "pl": pl
            }
    except Exception as e:
        # log(f"Err {i}: {e}")
        pass
    return None

def run_simulation():
    open("debug_log.txt", "w").close() 
    log("🚀 Iniciando script PARALELO (20 hilos)...")
    
    df = get_data_from_questdb()
    if df is None or len(df) < 65:
        log("❌ Datos insuficientes")
        return

    log(f"📅 Rango Temporal: {df['timestamp'].iloc[0]} -> {df['timestamp'].iloc[-1]}")
    
    trades = []
    step = 4
    indices = range(60, len(df)-1, step)
    
    log(f"{'HORA':<6} | {'ACCIÓN':<4} | {'CONF':<4} | {'RESULTADO':<8} | {'P&L':<8}")
    log("-" * 50)

    # PARALLEL EXECUTION
    with concurrent.futures.ThreadPoolExecutor(max_workers=20) as executor:
        future_to_idx = {
            executor.submit(process_candle, i, df.iloc[i-60:i], df.iloc[i]): i 
            for i in indices
        }
        
        count = 0
        total = len(indices)
        for future in concurrent.futures.as_completed(future_to_idx):
            res = future.result()
            count += 1
            if count % 20 == 0:
                print(f"Progreso: {count}/{total}...", end="\r", flush=True)
            if res:
                trades.append(res)

    # Sort results
    trades.sort(key=lambda x: x['time'])
    
    wins = sum(1 for t in trades if t['result'] == "WIN")
    losses = sum(1 for t in trades if t['result'] == "LOSS")
    pushes = sum(1 for t in trades if t['result'] == "PUSH")
    trade_total = len(trades)
    balance = sum(t['pl'] for t in trades)
    wr = (wins/trade_total*100) if trade_total > 0 else 0

    df_results = pd.DataFrame([
        {k: (v.strftime('%H:%M') if k=='time' else v) for k,v in t.items()}
        for t in trades
    ])
    
    if not df_results.empty:
        log("\n" + "="*80)
        log("📋 TABLA DETALLADA DE SIMULACIÓN (Últimas 24h)")
        log("="*80)
        log(df_results.to_string(index=False))
        log("="*80)
        df_results.to_csv('simulacion_resultados.csv', index=False)
        log("💾 Tabla guardada en: simulacion_resultados.csv")
    
    log("\n" + "="*60)
    log("📊 RESUMEN FINAL")
    log("="*60)
    log(f"Total Trades: {trade_total}")
    log(f"✅ Wins: {wins}")
    log(f"❌ Losses: {losses}")
    log(f"📈 Win Rate: {wr:.2f}%")
    log(f"💰 P&L Proyectado: ${balance:+,} COP")
    log("="*60)

if __name__ == "__main__":
    run_simulation()
