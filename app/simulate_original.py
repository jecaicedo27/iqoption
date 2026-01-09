#!/usr/bin/env python3
"""
Simulation with ORIGINAL prompt (before strict trend requirements)
"""
import requests
import google.generativeai as genai
import time
import pandas as pd

print("="*80)
print("🧪 SIMULACIÓN - PROMPT ORIGINAL (Pre-Trend Filter)")
print("="*80)

# Setup Gemini
GOOGLE_API_KEY = "AIzaSyD3x7u6GNSLNIVXN8OuE3euORi9wZDcy6c"
genai.configure(api_key=GOOGLE_API_KEY)
model = genai.GenerativeModel('gemini-2.0-flash-exp')

# Load candles from QuestDB
quest_url = "http://localhost:9000/exec"
query = "SELECT * FROM candles_history WHERE asset = 'EURUSD-op' ORDER BY timestamp"
response = requests.get(quest_url, params={"query": query, "fmt": "json"})
data = response.json()

columns = [col['name'] for col in data['columns']]
df = pd.DataFrame(data['dataset'], columns=columns)
df['timestamp'] = pd.to_datetime(df['timestamp'])

print(f"✅ Cargadas {len(df)} velas")
print(f"📊 Período: {df['timestamp'].min()} → {df['timestamp'].max()}")
print(f"🎯 Filtro: Range ≥ 0.04% | Confianza ≥ 75%")
print(f"📝 Prompt: ORIGINAL (flexible, sin restricciones estrictas)")
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

def ask_gemini_original(df_slice):
    """ORIGINAL PROMPT - Pre-strict-trend-filter"""
    latest = df_slice.tail(60)[['timestamp', 'open', 'high', 'low', 'close', 'volume']].to_string(index=False)
    
    # ORIGINAL PROMPT
    prompt = f"""
    Act as a Quantitative Systematic Trader. Analyze these 60s candles for EURUSD-op.
    
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

# Simulate
results = []
total_analyzed = 0
total_filtered = 0
total_signals = 0

print("\n🔄 Simulando...\n")

for i in range(60, len(df), 15):  # Start at 60 for full hour context
    df_slice = df.iloc[:i+1]
    
    passes_filter, range_pct = check_volatility_filter(df_slice)
    total_analyzed += 1
    
    if not passes_filter:
        total_filtered += 1
        continue
    
    # Ask Gemini with original prompt
    response = ask_gemini_original(df_slice)
    action, confidence = parse_response(response)
    
    if action in ['CALL', 'PUT'] and confidence >= 75:
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
                'range_pct': range_pct
            })
            
            result_emoji = '✅' if win else '❌'
            print(f"#{total_signals:>2} | {entry_time} | {action:<4} {confidence}% | "
                  f"Range: {range_pct:.3f}% | {result_emoji} | ${pl:>+6}")
    
    # Rate limiting
    if total_signals > 0 and total_signals % 10 == 0:
        print(f"  ... {total_signals} señales procesadas...")
        time.sleep(3)

# Results
print("\n" + "="*80)
print("📊 RESULTADOS FINALES - PROMPT ORIGINAL")
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
    print(f"\n📈 RESULTADOS DE TRADES:")
    print(f"  Total Ejecutados: {total_trades}")
    print(f"  ✅ Wins: {wins} ({wins/total_trades*100:.1f}%)")
    print(f"  ❌ Losses: {losses} ({losses/total_trades*100:.1f}%)")
    print(f"  📊 Win Rate: {win_rate:.1f}%")
    print(f"  💰 P&L Total: ${total_pl:+,} COP")
    
    # ROI
    total_invested = total_trades * 4000
    roi = (total_pl / total_invested * 100) if total_invested > 0 else 0
    print(f"  📈 ROI: {roi:+.1f}%")
    
    # By confidence
    print(f"\n📊 Por Nivel de Confianza:")
    for conf_level in [75, 80, 85, 90]:
        conf_trades = results_df[results_df['confidence'] >= conf_level]
        if len(conf_trades) > 0:
            conf_wins = (conf_trades['result'] == 'WIN').sum()
            conf_wr = (conf_wins / len(conf_trades) * 100)
            conf_pl = conf_trades['pl'].sum()
            print(f"  {conf_level}%+: {len(conf_trades):>2} trades | {conf_wins:>2} wins | "
                  f"WR: {conf_wr:>5.1f}% | P&L: ${conf_pl:>+7,}")
    
    # Save
    results_df.to_csv('/var/www/iqoption/simulation_original.csv', index=False)
    print(f"\n💾 Guardado: /var/www/iqoption/simulation_original.csv")
    
    # Final recommendation
    print(f"\n{'='*80}")
    print("💡 COMPARACIÓN DE ESTRATEGIAS:")
    print(f"{'='*80}")
    print(f"1. Prompt Actual (Strict Trend):  0 trades | N/A WR | Muy conservador")
    print(f"2. Prompt Simplificado:            6 trades | 33.3% WR | NO rentable")
    print(f"3. Prompt Original (este):        {total_trades} trades | {win_rate:.1f}% WR | ", end="")
    if win_rate >= 55:
        print(f"✅ RENTABLE - RECOMENDADO")
    elif win_rate >= 50:
        print(f"⚠️  Marginal")
    else:
        print(f"❌ NO rentable")
else:
    print("⚠️ No se generaron señales")
    print(f"Ventanas analizadas: {total_analyzed}")
    print(f"Bloqueadas: {total_filtered}")

print("="*80)
