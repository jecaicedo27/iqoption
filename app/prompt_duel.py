#!/usr/bin/env python3
import time
import pandas as pd
import re
import google.generativeai as genai
import concurrent.futures
from iqoptionapi.stable_api import IQ_Option
from app.config import EMAIL, PASSWORD, DEFAULT_ASSET, GOOGLE_API_KEY

# Setup Gemini
# Setup Gemini
try:
    genai.configure(api_key=GOOGLE_API_KEY)
    model = genai.GenerativeModel('gemini-2.0-flash-exp')
    # model = genai.GenerativeModel('gemini-pro')
except Exception as e:
    print(f"Error configuring Gemini: {e}")

THRESHOLD = 70

PROMPT_ORIGINAL = """
Act as a Quantitative Systematic Trader. Analyze these 60s candles for {asset}.

DATA (Last 1 hour):
{data}

TASK: Identify High Probability setups for the next 1 minute.

CRITERIA: Look for strong trend continuations or clear reversals at key levels.
Analyze Volume, Close Price, and recent Volatility.

RESPONSE FORMAT:
ACTION: [CALL, PUT, or WAIT]
CONFIDENCE: [0-100]
REASON: [Short logical explanation]
"""

PROMPT_STRICT = """
Act as a Quantitative Systematic Trader. Analyze these 60s candles for {asset}.

DATA (Last 30 minutes):
{data}

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

def parse_res(text):
    text_upper = text.upper()
    action = "WAIT"
    conf = 0.0
    
    act_match = re.search(r'ACTION[:\s\*]+(CALL|PUT|WAIT)', text_upper)
    if act_match: action = act_match.group(1)
    
    conf_match = re.search(r'CONFIDENCE[:\s\*]+(\d+)', text_upper)
    if conf_match: conf = float(conf_match.group(1))
    
    return action, conf

def simulate_step(i, df, prompt_template):
    # Context window (60 candles)
    if i < 60: return None
    
    window = df.iloc[i-60:i]
    # For STRICT prompt we might only show 30, but let's stick to standard input size for fairness or adjust if needed
    # The PROMPT_STRICT says "DATA (Last 30 minutes)", but let's give it 60 rows and let it decide or truncate.
    # Actually, to be fair to "PROMPT_STRICT" description, maybe we should slice? 
    # But usually more context is better. Let's send 60.
    
    latest_data = window.tail(60)[['timestamp', 'open', 'high', 'low', 'close', 'volume']].to_string(index=False)
    
    prompt = prompt_template.format(asset=DEFAULT_ASSET, data=latest_data)
    
    try:
        response = model.generate_content(prompt)
        content = response.text.strip()
        
        # DEBUG: Print first response
        if i == 200:
             print(f"\n[DEBUG {prompt_template[:10].strip()}] Response for {df.iloc[i]['timestamp']}:\n{content}\n")
             
        action, conf = parse_res(content)
        
        if action in ["CALL", "PUT"] and conf >= THRESHOLD:
            entry_price = df.iloc[i]['open']
            exit_price = df.iloc[i]['close']
            
            # Simple simulation: Entry at Open, Result at Close of SAME candle (1 min)
            # OR Next candle? Usually bot trades "next 1 minute".
            # If "next 1 minute", it means we analyze candle [i-1], trade starts at [i].
            # So if we are at index i, window is i-60:i. We predict for candle i (the one that follows the window).
            # So entry is open of candle i. Result is close of candle i.
            
            win = (exit_price > entry_price) if action == "CALL" else (exit_price < entry_price)
            pl = 3400 if win else -4000
            
            return {
                'timestamp': df.iloc[i]['timestamp'],
                'action': action,
                'conf': conf,
                'result': 'WIN' if win else 'LOSS',
                'pl': pl
            }
    except:
        pass
    return None

import iqoptionapi.constants as OP_code

def run_duel():
    print("⚔️  INICIANDO DUELO DE PROMPTS ⚔️")
    print(f"Confianza Objetivo: {THRESHOLD}% | Asset: {DEFAULT_ASSET}")
    
    # Inject ID for EURUSD-op
    if DEFAULT_ASSET == "EURUSD-op":
        print("🧬 Injecting EURUSD-op (ID: 1861) for Real Market Access...")
        OP_code.ACTIVES["EURUSD-op"] = 1861

    # 1. FETCH LIVE DATA
    print("📡 Conectando a IQ Option para obtener datos frescos...")
    api = IQ_Option(EMAIL, PASSWORD)
    
    # Retry connection
    for i in range(5):
        if api.connect():
            print("✅ Conectado.")
            break
        print(f"⚠️ Intento de conexión {i+1} fallido. Reintentando...")
        time.sleep(3)
    
    if not api.check_connect():
        print("❌ Error crítico: No se pudo conectar a IQ Option.")
        return

    # Get last 300 candles (5 hours)
    end_time = time.time()
    candidates = []
    
    # Retry getting candles
    for i in range(5):
        try:
           candidates = api.get_candles(DEFAULT_ASSET, 60, 300, end_time)
           if candidates:
               break
        except Exception as e:
           print(f"⚠️ Error obteniendo velas: {e}")
        time.sleep(2)
        api.connect() # Reconnect if candle fetch fails

    if not candidates:
        print("❌ No se pudieron obtener velas")
        return
    
    df = pd.DataFrame(candidates)
    df.rename(columns={'max': 'high', 'min': 'low'}, inplace=True)
    df['timestamp'] = pd.to_datetime(df['from'], unit='s')
    
    print(f"📊 Velas obtenidas: {len(df)} | Desde: {df['timestamp'].min()} HASTA: {df['timestamp'].max()}")
    print("Muestra de datos (Head):")
    print(df[['timestamp', 'open', 'close', 'volume']].head())
    print("Muestra de datos (Tail):")
    print(df[['timestamp', 'open', 'close', 'volume']].tail())
    
    # Indices to simulate
    indices = range(60, len(df))
    
    results = {"ORIGINAL": [], "STRICT": []}
    
    # We run in batches to avoid overwhelming API if too fast, but threadpool handles it.
    
    for name, p_temp in [("ORIGINAL", PROMPT_ORIGINAL), ("STRICT", PROMPT_STRICT)]:
        print(f"\n🔄 Simulando: Prompt {name}...")
        with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
            # Only processing last 20 samples to save time and tokens for this rapid test if user wants quick answer
            # User asked "competition", let's do last 60-90 minutes (market uptrend time)
            # The user image showed 11:00-11:08. Now is 11:30.
            # Let's focus on the last ~100 candles.
            
            target_indices = list(indices)[-120:] # Last 2 hours
            
            futures = {executor.submit(simulate_step, i, df, p_temp): i for i in target_indices}
            
            completed = 0
            for f in concurrent.futures.as_completed(futures):
                res = f.result()
                if res: results[name].append(res)
                completed += 1
                print(f"Progress: {completed}/{len(target_indices)}", end="\r")
        
        # Summary for this prompt
        p_res = pd.DataFrame(results[name])
        trades = len(p_res)
        if trades > 0:
            p_res = p_res.sort_values(by='timestamp')
            wins = (p_res['result'] == 'WIN').sum()
            wr = (wins / trades) * 100
            pl = p_res['pl'].sum()
            print(f"\n✅ {name}: {trades} trades | WR: {wr:.1f}% | P&L: ${pl:+,} COP")
            
            # Show last 5 trades
            print(p_res.tail(5)[['timestamp', 'action', 'conf', 'result']].to_string(index=False))
        else:
            print(f"\n⚠️ {name}: 0 trades generados en las últimas 2 horas.")

    print("\n" + "="*50)
    print("🏆 RESULTADO FINAL (Últimas 2 Horas)")
    print("="*50)
    for name in ["ORIGINAL", "STRICT"]:
        p_res = pd.DataFrame(results[name])
        t = len(p_res)
        wr = (p_res['result'] == 'WIN').sum() / t * 100 if t > 0 else 0
        pl = p_res['pl'].sum() if t > 0 else 0
        print(f"{name:<10} | Trades: {t:>2} | WinRate: {wr:>5.1f}% | P&L: ${pl:>+7,} COP")
    print("="*50)

if __name__ == "__main__":
    run_duel()
