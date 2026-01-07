#!/usr/bin/env python3
"""
Simulate with LOGGING to see Gemini responses
"""
import requests
import google.generativeai as genai
import os
import time
import pandas as pd

print("="*80)
print("🔍 SIMULACIÓN CON LOGGING DETALLADO")
print("="*80)

# Setup Gemini
GOOGLE_API_KEY = "AIzaSyD3x7u6GNSLNIVXN8OuE3euORi9wZDcy6c"
genai.configure(api_key=GOOGLE_API_KEY)
model = genai.GenerativeModel('gemini-2.0-flash-exp')

# Query candles from QuestDB
quest_url = "http://localhost:9000/exec"
query = "SELECT * FROM candles_history WHERE asset = 'EURUSD-op' ORDER BY timestamp"
response = requests.get(quest_url, params={"query": query, "fmt": "json"})
data = response.json()

columns = [col['name'] for col in data['columns']]
df = pd.DataFrame(data['dataset'], columns=columns)
df['timestamp'] = pd.to_datetime(df['timestamp'])

print(f"✅ Cargadas {len(df)} velas")
print(f"🎯 Analizando con logging completo...")
print("="*80)

def check_volatility_filter(df_slice):
    if len(df_slice) < 15:
        return False, 0
    
    last_15 = df_slice.tail(15)
    price_high = last_15['high'].max()
    price_low = last_15['low'].min()
    price_range = price_high - price_low
    current_price = last_15['close'].iloc[-1]
    range_pct = (price_range / current_price) * 100
    
    return range_pct >= 0.04, range_pct

def ask_gemini_simple(df_slice):
    """Simplified prompt - less restrictive"""
    latest = df_slice.tail(30)[['timestamp', 'open', 'high', 'low', 'close', 'volume']].to_string(index=False)
    
    # SIMPLIFIED PROMPT
    prompt = f"""
    Analyze these 60-second candles for EURUSD.
    
    {latest}
    
    Based on recent price action, what is the most probable direction for the NEXT candle?
    Focus on momentum, volume, and any clear patterns.
    
    Respond ONLY in this format:
    ACTION: CALL or PUT or WAIT
    CONFIDENCE: 0-100
    REASON: Brief explanation
    """
    
    try:
        response = model.generate_content(prompt)
        return response.text.strip()
    except Exception as e:
        return f"ERROR: {e}"

def parse_response(text):
    lines = text.split('\n')
    action = "WAIT"
    confidence = 0
    
    for line in lines:
        if 'ACTION:' in line.upper():
            if 'CALL' in line.upper():
                action = 'CALL'
            elif 'PUT' in line.upper():
                action = 'PUT'
        if 'CONFIDENCE:' in line.upper():
            try:
                conf_str = line.split(':')[1].strip()
                confidence = int(''.join(filter(str.isdigit, conf_str)))
            except:
                pass
    
    return action, confidence

# Analyze first 5 windows that pass filter
analyzed = 0
passed_filter = 0
signals = 0

for i in range(30, len(df), 15):
    df_slice = df.iloc[:i+1]
    
    passes_filter, range_pct = check_volatility_filter(df_slice)
    analyzed += 1
    
    if not passes_filter:
        continue
    
    passed_filter += 1
    entry_time = df.iloc[i]['timestamp']
    
    print(f"\n{'='*80}")
    print(f"VENTANA #{passed_filter} | Tiempo: {entry_time} | Range: {range_pct:.3f}%")
    print(f"{'='*80}")
    
    # Ask Gemini with simplified prompt
    response = ask_gemini_simple(df_slice)
    action, confidence = parse_response(response)
    
    print(f"\n📝 RESPUESTA DE GEMINI:")
    print(response)
    print(f"\n✅ PARSEADO: ACTION={action} | CONFIDENCE={confidence}%")
    
    if action in ['CALL', 'PUT'] and confidence >= 70:
        signals += 1
        print(f"🎯 SEÑAL VÁLIDA #{signals}")
    else:
        print(f"❌ No alcanza umbral (≥70%)")
    
    time.sleep(3)  # Rate limit
    
    # Only analyze first 5 to save time
    if passed_filter >= 5:
        print(f"\n{'='*80}")
        print("⏸️  Deteniendo análisis (primeras 5 ventanas mostradas)")
        print(f"{'='*80}")
        break

print(f"\n{'='*80}")
print("📊 RESUMEN")
print(f"{'='*80}")
print(f"Ventanas totales: {analyzed}")
print(f"Pasaron filtro: {passed_filter}")
print(f"Señales generadas: {signals}")
print(f"{'='*80}")
