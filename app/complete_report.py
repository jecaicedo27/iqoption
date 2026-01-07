#!/usr/bin/env python3
from iqoptionapi.stable_api import IQ_Option
from app.config import EMAIL, PASSWORD
import requests
from datetime import datetime, timedelta

# Connect to IQ Option API
print("🔌 Conectando a IQ Option...")
api = IQ_Option(EMAIL, PASSWORD)
api.connect()
api.change_balance("REAL")

# Get API trade history
print("📥 Descargando historial de resultados...")
since = int((datetime.now() - timedelta(days=1)).timestamp())
res = api.get_position_history_v2("binary-option", 300, 0, 0, 0)

# Build API results map
api_results = {}
if isinstance(res, tuple) and res[0]:
    history = res[1].get('positions', [])
    for trade in history:
        close_time = int(trade['close_time'] / 1000)
        if close_time > since:
            pl = float(trade['close_profit']) - float(trade['invest'])
            api_results[close_time] = {
                'result': 'WIN' if pl > 0 else 'LOSS',
                'pl': pl,
                'invest': float(trade['invest'])
            }

print(f"✅ {len(api_results)} resultados descargados de la API\n")

# Function to find closest API result
def find_result(timestamp_str):
    dt = datetime.fromisoformat(timestamp_str.replace('Z', '+00:00'))
    ts = int(dt.timestamp())
    
    # Find closest within 120 seconds
    closest = None
    min_diff = 120
    
    for api_ts, data in api_results.items():
        diff = abs(api_ts - ts)
        if diff < min_diff:
            min_diff = diff
            closest = data
    
    return closest

# Get QuestDB data
quest_url = "http://localhost:9000/exec"

# ==== OTC REPORT ====
print("="*110)
print("❌ EURUSD-OTC (Over-The-Counter - DESCONTINUADO)")
print("="*110)

query_otc = """
SELECT timestamp, prediction, confidence, price 
FROM trades_memory 
WHERE asset = 'EURUSD-OTC'
AND timestamp > dateadd('h', -24, now())
ORDER BY timestamp ASC
"""
response_otc = requests.get(quest_url, params={"query": query_otc, "fmt": "json"})
data_otc = response_otc.json()

otc_wins = 0
otc_losses = 0
otc_total_pl = 0
otc_by_conf = {'75%': {'w': 0, 't': 0}, '80%': {'w': 0, 't': 0}, '85%': {'w': 0, 't': 0}, '90%+': {'w': 0, 't': 0}}

if 'dataset' in data_otc and data_otc['dataset']:
    print(f"{'#':<4} {'Hora':<10} {'Pred':<5} {'Conf':<6} {'Precio':<10} {'Resultado':<8} {'P&L':<12}")
    print("-"*110)
    
    for idx, row in enumerate(data_otc['dataset'], 1):
        timestamp = row[0]
        prediction = row[1]
        confidence = row[2]
        price = row[3]
        
        dt = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
        time_str = dt.strftime('%H:%M:%S')
        conf_pct = int(confidence * 100)
        
        # Find result
        result_data = find_result(timestamp)
        if result_data:
            result = result_data['result']
            pl = result_data['pl']
            
            if result == 'WIN':
                otc_wins += 1
                conf_key = '75%' if conf_pct == 75 else '80%' if conf_pct == 80 else '85%' if conf_pct == 85 else '90%+'
                otc_by_conf[conf_key]['w'] += 1
            else:
                otc_losses += 1
            
            otc_total_pl += pl
            
            conf_key = '75%' if conf_pct == 75 else '80%' if conf_pct == 80 else '85%' if conf_pct == 85 else '90%+'
            otc_by_conf[conf_key]['t'] += 1
            
            print(f"{idx:<4} {time_str:<10} {prediction:<5} {conf_pct:>3}% {price:<10.5f} {result:<8} ${pl:>+10,.0f}")
        else:
            print(f"{idx:<4} {time_str:<10} {prediction:<5} {conf_pct:>3}% {price:<10.5f} {'?':<8} {'N/A':<12}")
    
    print("-"*110)
    total_otc = otc_wins + otc_losses
    wr_otc = (otc_wins / total_otc * 100) if total_otc > 0 else 0
    print(f"Total: {total_otc} | Wins: {otc_wins} | Losses: {otc_losses} | Win Rate: {wr_otc:.1f}% | P&L: ${otc_total_pl:+,.0f}")
    
    print("\nPor Nivel de Confianza:")
    for conf, stats in otc_by_conf.items():
        if stats['t'] > 0:
            wr = (stats['w'] / stats['t'] * 100)
            print(f"  {conf}: {stats['t']} trades | {stats['w']} wins | Win Rate: {wr:.1f}%")

# ==== REAL MARKET REPORT ====
print("\n" + "="*110)
print("✅ EURUSD-op (Mercado Real Forex - ACTIVO)")
print("="*110)

query_real = """
SELECT timestamp, prediction, confidence, price 
FROM trades_memory 
WHERE asset = 'EURUSD-op'
AND timestamp > dateadd('h', -24, now())
ORDER BY timestamp ASC
"""
response_real = requests.get(quest_url, params={"query": query_real, "fmt": "json"})
data_real = response_real.json()

real_wins = 0
real_losses = 0
real_total_pl = 0
real_by_conf = {'75%': {'w': 0, 't': 0}, '80%': {'w': 0, 't': 0}, '85%': {'w': 0, 't': 0}, '90%+': {'w': 0, 't': 0}}

if 'dataset' in data_real and data_real['dataset']:
    print(f"{'#':<4} {'Hora':<10} {'Pred':<5} {'Conf':<6} {'Precio':<10} {'Resultado':<8} {'P&L':<12}")
    print("-"*110)
    
    for idx, row in enumerate(data_real['dataset'], 1):
        timestamp = row[0]
        prediction = row[1]
        confidence = row[2]
        price = row[3]
        
        dt = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
        time_str = dt.strftime('%H:%M:%S')
        conf_pct = int(confidence * 100)
        
        # Find result
        result_data = find_result(timestamp)
        if result_data:
            result = result_data['result']
            pl = result_data['pl']
            
            if result == 'WIN':
                real_wins += 1
                conf_key = '75%' if conf_pct == 75 else '80%' if conf_pct == 80 else '85%' if conf_pct == 85 else '90%+'
                real_by_conf[conf_key]['w'] += 1
            else:
                real_losses += 1
            
            real_total_pl += pl
            
            conf_key = '75%' if conf_pct == 75 else '80%' if conf_pct == 80 else '85%' if conf_pct == 85 else '90%+'
            real_by_conf[conf_key]['t'] += 1
            
            print(f"{idx:<4} {time_str:<10} {prediction:<5} {conf_pct:>3}% {price:<10.5f} {result:<8} ${pl:>+10,.0f}")
        else:
            print(f"{idx:<4} {time_str:<10} {prediction:<5} {conf_pct:>3}% {price:<10.5f} {'PENDING':<8} {'N/A':<12}")
    
    print("-"*110)
    total_real = real_wins + real_losses
    wr_real = (real_wins / total_real * 100) if total_real > 0 else 0
    print(f"Total: {total_real} | Wins: {real_wins} | Losses: {real_losses} | Win Rate: {wr_real:.1f}% | P&L: ${real_total_pl:+,.0f}")
    
    print("\nPor Nivel de Confianza:")
    for conf, stats in real_by_conf.items():
        if stats['t'] > 0:
            wr = (stats['w'] / stats['t'] * 100)
            print(f"  {conf}: {stats['t']} trades | {stats['w']} wins | Win Rate: {wr:.1f}%")

# SUMMARY
print("\n" + "="*110)
print("📊 RESUMEN COMPARATIVO")
print("="*110)
print(f"OTC:  Win Rate: {wr_otc:.1f}% | P&L: ${otc_total_pl:+,.0f} COP")
print(f"REAL: Win Rate: {wr_real:.1f}% | P&L: ${real_total_pl:+,.0f} COP")
print(f"TOTAL P&L: ${otc_total_pl + real_total_pl:+,.0f} COP")
print("="*110)
