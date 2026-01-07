#!/usr/bin/env python3
import pandas as pd
import google.generativeai as genai
import os
import time
from datetime import datetime

# Load candles
df = pd.read_csv('/var/www/iqoption/candles_24h.csv')
df['datetime'] = pd.to_datetime(df['datetime'])

print("="*80)
print("🧪 SIMULACIÓN DE ESTRATEGIA ACTUAL")
print("="*80)
print(f"Velas cargadas: {len(df)}")
print(f"Período: {df['datetime'].min()} → {df['datetime'].max()}")
print(f"Filtro anti-lateral: Range ≥ 0.04% en 15 min")
print("="*80)

# Setup Gemini
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))
model = genai.GenerativeModel('gemini-2.0-flash-exp')

def check_volatility_filter(df_slice):
    """Check if 15-min window has enough volatility"""
    if len(df_slice) < 15:
        return False, 0
    
    last_15 = df_slice.tail(15)
    price_high = last_15['max'].max()
    price_low = last_15['min'].min()
    price_range = price_high - price_low
    current_price = last_15['close'].iloc[-1]
    range_pct = (price_range / current_price) * 100
    
    return range_pct >= 0.04, range_pct  # Changed from 0.05 to 0.04

def ask_gemini(df_slice):
    """Ask Gemini for prediction"""
    latest = df_slice.tail(30).to_string(index=False)
    
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
        text = response.text.strip()
        return text
    except Exception as e:
        return f"ACTION: WAIT | CONFIDENCE: 0 | Error: {e}"

# Parse Gemini response
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

# Simulate
results = []
total_analyzed = 0
total_filtered = 0
total_signals = 0

print("\n🔄 Simulando... (esto puede tardar unos minutos)\n")

# Start from candle 30 (need history for context)
for i in range(30, len(df), 15):  # Check every 15 minutes
    df_slice = df.iloc[:i+1]  # All data up to this point
    
    # Apply volatility filter
    passes_filter, range_pct = check_volatility_filter(df_slice)
    total_analyzed += 1
    
    if not passes_filter:
        total_filtered += 1
        continue
    
    # Ask Gemini
    response = ask_gemini(df_slice)
    action, confidence = parse_response(response)
    
    if action in ['CALL', 'PUT'] and confidence >= 75:
        total_signals += 1
        entry_price = df.iloc[i]['close']
        entry_time = df.iloc[i]['datetime']
        
        # Get result (next candle)
        if i + 1 < len(df):
            exit_price = df.iloc[i+1]['close']
            
            if action == 'CALL':
                win = exit_price > entry_price
            else:  # PUT
                win = exit_price < entry_price
            
            pl = 3400 if win else -4000  # Typical binary options payout
            
            results.append({
                'time': entry_time,
                'action': action,
                'confidence': confidence,
                'entry': entry_price,
                'exit': exit_price,
                'result': 'WIN' if win else 'LOSS',
                'pl': pl,
                'range_pct': range_pct
            })
            
            print(f"#{total_signals:>3} | {entry_time} | {action:<4} {confidence}% | "
                  f"Range: {range_pct:.3f}% | {'✅ WIN' if win else '❌ LOSS':<8} | P&L: ${pl:>+6}")
    
    # Rate limiting
    if total_signals > 0 and total_signals % 5 == 0:
        time.sleep(2)  # Avoid API rate limits

# Results Analysis
print("\n" + "="*80)
print("📊 RESULTADOS DE LA SIMULACIÓN")
print("="*80)

if results:
    results_df = pd.DataFrame(results)
    
    total_trades = len(results_df)
    wins = (results_df['result'] == 'WIN').sum()
    losses = (results_df['result'] == 'LOSS').sum()
    win_rate = (wins / total_trades * 100) if total_trades > 0 else 0
    total_pl = results_df['pl'].sum()
    
    print(f"Total Ventanas Analizadas: {total_analyzed}")
    print(f"Bloqueadas por Filtro: {total_filtered} ({total_filtered/total_analyzed*100:.1f}%)")
    print(f"Señales Generadas: {total_signals}")
    print(f"\nTrades Ejecutados: {total_trades}")
    print(f"✅ Wins: {wins}")
    print(f"❌ Losses: {losses}")
    print(f"📈 Win Rate: {win_rate:.1f}%")
    print(f"💰 P&L Total: ${total_pl:+,} COP")
    
    # By confidence level
    print(f"\n📊 Por Nivel de Confianza:")
    for conf_level in [75, 80, 85, 90]:
        conf_trades = results_df[results_df['confidence'] >= conf_level]
        if len(conf_trades) > 0:
            conf_wins = (conf_trades['result'] == 'WIN').sum()
            conf_wr = (conf_wins / len(conf_trades) * 100)
            print(f"  {conf_level}%+: {len(conf_trades)} trades | {conf_wins} wins | WR: {conf_wr:.1f}%")
    
    # Save results
    results_df.to_csv('/var/www/iqoption/simulation_results.csv', index=False)
    print(f"\n💾 Resultados guardados en: /var/www/iqoption/simulation_results.csv")
else:
    print("⚠️ No se generaron señales en la simulación")
    print(f"Ventanas analizadas: {total_analyzed}")
    print(f"Bloqueadas por filtro: {total_filtered}")

print("="*80)
