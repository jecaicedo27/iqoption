#!/usr/bin/env python3
"""
Step 2: Simulate strategy using QuestDB (FAST)
"""
import requests
import google.generativeai as genai
import os
import time
from datetime import datetime
import pandas as pd

print("="*80)
print("🧪 SIMULACIÓN RÁPIDA CON QuestDB")
print("="*80)

# Setup Gemini
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))
model = genai.GenerativeModel('gemini-2.0-flash-exp')

# Query candles from QuestDB
quest_url = "http://localhost:9000/exec"
query = "SELECT * FROM candles_history WHERE asset = 'EURUSD-op' ORDER BY timestamp"
response = requests.get(quest_url, params={"query": query, "fmt": "json"})
data = response.json()

if 'dataset' not in data:
    print("❌ No hay datos en QuestDB")
    exit(1)

# Convert to DataFrame
columns = [col['name'] for col in data['columns']]
df = pd.DataFrame(data['dataset'], columns=columns)
df['timestamp'] = pd.to_datetime(df['timestamp'])

print(f"✅ Cargadas {len(df)} velas desde QuestDB")
print(f"📊 Período: {df['timestamp'].min()} → {df['timestamp'].max()}")
print(f"🎯 Filtro: Range ≥ 0.04% en 15 min | Confianza ≥ 70%")
print("="*80)

def check_volatility_filter(df_slice):
    """Check 15-min volatility"""
    if len(df_slice) < 15:
        return False, 0
    
    last_15 = df_slice.tail(15)
    price_high = last_15['high'].max()
    price_low = last_15['low'].min()
    price_range = price_high - price_low
    current_price = last_15['close'].iloc[-1]
    range_pct = (price_range / current_price) * 100
    
    return range_pct >= 0.04, range_pct

def ask_gemini(df_slice):
    """Ask Gemini"""
    latest = df_slice.tail(30)[['timestamp', 'open', 'high', 'low', 'close', 'volume']].to_string(index=False)
    
    prompt = f"""
    Act as a Quantitative Systematic Trader. Analyze these 60s candles for EURUSD-op.
    
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
        return response.text.strip()
    except Exception as e:
        return f"ACTION: WAIT | CONFIDENCE: 0 | Error: {e}"

def parse_response(text):
    """Parse Gemini response"""
    lines = text.split('\n')
    action = "WAIT"
    confidence = 0
    reason = ""
    
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
        if 'REASON:' in line.upper():
            reason = line.split(':', 1)[1].strip() if ':' in line else ""
    
    return action, confidence, reason

# Simulate
results = []
total_analyzed = 0
total_filtered = 0
total_signals = 0

print("\n🔄 Simulando...\n")

for i in range(30, len(df), 15):  # Every 15 minutes
    df_slice = df.iloc[:i+1]
    
    # Filter
    passes_filter, range_pct = check_volatility_filter(df_slice)
    total_analyzed += 1
    
    if not passes_filter:
        total_filtered += 1
        continue
    
    # Ask Gemini
    response = ask_gemini(df_slice)
    action, confidence, reason = parse_response(response)
    
    # Lower threshold to 70%
    if action in ['CALL', 'PUT'] and confidence >= 70:
        total_signals += 1
        entry_price = df.iloc[i]['close']
        entry_time = df.iloc[i]['timestamp']
        
        # Get result
        if i + 1 < len(df):
            exit_price = df.iloc[i+1]['close']
            
            if action == 'CALL':
                win = exit_price > entry_price
            else:
                win = exit_price < entry_price
            
            pl = 3400 if win else -4000
            
            results.append({
                'time': entry_time,
                'action': action,
                'confidence': confidence,
                'entry': entry_price,
                'exit': exit_price,
                'result': 'WIN' if win else 'LOSS',
                'pl': pl,
                'range_pct': range_pct,
                'reason': reason[:100]  # First 100 chars
            })
            
            result_emoji = '✅ WIN' if win else '❌ LOSS'
            print(f"#{total_signals:>2} | {entry_time} | {action:<4} {confidence}% | "
                  f"Range: {range_pct:.3f}% | {result_emoji:<8} | ${pl:>+6}")
    
    # Rate limit
    if total_signals > 0 and total_signals % 5 == 0:
        time.sleep(2)

# Results
print("\n" + "="*80)
print("📊 RESULTADOS FINALES")
print("="*80)

if results:
    results_df = pd.DataFrame(results)
    
    total_trades = len(results_df)
    wins = (results_df['result'] == 'WIN').sum()
    losses = (results_df['result'] == 'LOSS').sum()
    win_rate = (wins / total_trades * 100) if total_trades > 0 else 0
    total_pl = results_df['pl'].sum()
    
    print(f"Ventanas Analizadas: {total_analyzed}")
    print(f"Bloqueadas por Filtro: {total_filtered} ({total_filtered/total_analyzed*100:.1f}%)")
    print(f"Señales Generadas: {total_signals}")
    print(f"\nTrades Ejecutados: {total_trades}")
    print(f"✅ Wins: {wins}")
    print(f"❌ Losses: {losses}")
    print(f"📈 Win Rate: {win_rate:.1f}%")
    print(f"💰 P&L Total: ${total_pl:+,} COP")
    
    # By confidence
    print(f"\n📊 Por Nivel de Confianza:")
    for conf_level in [70, 75, 80, 85]:
        conf_trades = results_df[results_df['confidence'] >= conf_level]
        if len(conf_trades) > 0:
            conf_wins = (conf_trades['result'] == 'WIN').sum()
            conf_wr = (conf_wins / len(conf_trades) * 100)
            conf_pl = conf_trades['pl'].sum()
            print(f"  {conf_level}%+: {len(conf_trades)} trades | {conf_wins} wins | "
                  f"WR: {conf_wr:.1f}% | P&L: ${conf_pl:+,}")
    
    # Save
    results_df.to_csv('/var/www/iqoption/simulation_results.csv', index=False)
    print(f"\n💾 Resultados en: /var/www/iqoption/simulation_results.csv")
else:
    print("⚠️ No se generaron señales")
    print(f"Ventanas analizadas: {total_analyzed}")
    print(f"Bloqueadas: {total_filtered}")

print("="*80)
