#!/usr/bin/env python3
import requests
from datetime import datetime

# Get QuestDB data
quest_url = "http://localhost:9000/exec"

print("="*100)
print("📊 REPORTE COMPARATIVO: OTC vs REAL MARKET")
print("="*100)

# Query for OTC
query_otc = """
SELECT timestamp, prediction, confidence, price 
FROM trades_memory 
WHERE asset = 'EURUSD-OTC'
AND timestamp > dateadd('h', -24, now())
ORDER BY timestamp ASC
"""
response_otc = requests.get(quest_url, params={"query": query_otc, "fmt": "json"})
data_otc = response_otc.json()

# Query for Real Market
query_real = """
SELECT timestamp, prediction, confidence, price 
FROM trades_memory 
WHERE asset = 'EURUSD-op'
AND timestamp > dateadd('h', -24, now())
ORDER BY timestamp ASC
"""
response_real = requests.get(quest_url, params={"query": query_real, "fmt": "json"})
data_real = response_real.json()

# Process OTC
print("\n" + "="*100)
print("❌ EURUSD-OTC (Over-The-Counter - DESCONTINUADO)")
print("="*100)
if 'dataset' in data_otc and data_otc['dataset']:
    conf_otc = {'75%': 0, '80%': 0, '85%': 0, '90%+': 0}
    
    print(f"{'#':<4} {'Hora':<10} {'Pred':<5} {'Conf':<6} {'Precio':<10}")
    print("-"*100)
    
    for idx, row in enumerate(data_otc['dataset'], 1):
        timestamp = row[0]
        prediction = row[1]
        confidence = row[2]
        price = row[3]
        
        dt = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
        time_str = dt.strftime('%H:%M:%S')
        conf_pct = int(confidence * 100)
        
        # Count confidence levels
        if conf_pct == 75:
            conf_otc['75%'] += 1
        elif conf_pct == 80:
            conf_otc['80%'] += 1
        elif conf_pct == 85:
            conf_otc['85%'] += 1
        else:
            conf_otc['90%+'] += 1
        
        if idx <= 10 or idx > len(data_otc['dataset']) - 5:  # First 10 and last 5
            print(f"{idx:<4} {time_str:<10} {prediction:<5} {conf_pct:>3}% {price:<10.5f}")
        elif idx == 11:
            print(f"... ({len(data_otc['dataset']) - 15} trades omitidos) ...")
    
    print("-"*100)
    print(f"Total Trades OTC: {len(data_otc['dataset'])}")
    print(f"Por Confianza:")
    for level, count in conf_otc.items():
        if count > 0:
            print(f"  {level}: {count} trades ({count/len(data_otc['dataset'])*100:.1f}%)")

# Process Real Market
print("\n" + "="*100)
print("✅ EURUSD-op (Mercado Real Forex - ACTIVO)")
print("="*100)
if 'dataset' in data_real and data_real['dataset']:
    conf_real = {'75%': 0, '80%': 0, '85%': 0, '90%+': 0}
    
    print(f"{'#':<4} {'Hora':<10} {'Pred':<5} {'Conf':<6} {'Precio':<10}")
    print("-"*100)
    
    for idx, row in enumerate(data_real['dataset'], 1):
        timestamp = row[0]
        prediction = row[1]
        confidence = row[2]
        price = row[3]
        
        dt = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
        time_str = dt.strftime('%H:%M:%S')
        conf_pct = int(confidence * 100)
        
        # Count confidence levels
        if conf_pct == 75:
            conf_real['75%'] += 1
        elif conf_pct == 80:
            conf_real['80%'] += 1
        elif conf_pct == 85:
            conf_real['85%'] += 1
        else:
            conf_real['90%+'] += 1
        
        # Show all since there are fewer
        print(f"{idx:<4} {time_str:<10} {prediction:<5} {conf_pct:>3}% {price:<10.5f}")
    
    print("-"*100)
    print(f"Total Trades REAL: {len(data_real['dataset'])}")
    print(f"Por Confianza:")
    for level, count in conf_real.items():
        if count > 0:
            print(f"  {level}: {count} trades ({count/len(data_real['dataset'])*100:.1f}%)")
else:
    print("No hay trades en EURUSD-op registrados.")

# Summary
print("\n" + "="*100)
print("📈 RESUMEN COMPARATIVO")
print("="*100)
otc_count = len(data_otc['dataset']) if 'dataset' in data_otc else 0
real_count = len(data_real['dataset']) if 'dataset' in data_real else 0
print(f"Total OTC:  {otc_count} trades (❌ Mercado ruidoso - DESCONTINUADO)")
print(f"Total REAL: {real_count} trades (✅ Mercado limpio - ACTIVO)")
print(f"TOTAL:      {otc_count + real_count} trades")
print("="*100)
