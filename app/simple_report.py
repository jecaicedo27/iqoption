#!/usr/bin/env python3
from iqoptionapi.stable_api import IQ_Option
from app.config import EMAIL, PASSWORD
import time
from datetime import datetime
import requests

# Get QuestDB data
print("📊 Consultando QuestDB para últimas 24h...")
quest_url = "http://localhost:9000/exec"
query = """
SELECT timestamp, asset, prediction, confidence, price, model_id 
FROM trades_memory 
WHERE timestamp > dateadd('h', -24, now())
ORDER BY timestamp ASC
"""
response = requests.get(quest_url, params={"query": query, "fmt": "json"})
quest_data = response.json()

print("\n" + "="*100)
print("📋 REPORTE DE TRADES (Últimas 24 horas)")
print("="*100)
print(f"{'#':<4} {'Hora':<10} {'Asset':<14} {'Pred':<5} {'Conf':<6} {'Precio':<10} {'Modelo':<25}")
print("-"*100)

total = 0
by_conf = {}
by_asset = {}

if 'dataset' in quest_data and quest_data['dataset']:
    for idx, row in enumerate(quest_data['dataset'], 1):
        timestamp = row[0]
        asset = row[1]
        prediction = row[2]
        confidence = row[3]
        price = row[4]
        model = row[5] if len(row) > 5 else 'N/A'
        
        dt = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
        time_str = dt.strftime('%H:%M:%S')
        conf_pct = int(confidence * 100)
        
        print(f"{idx:<4} {time_str:<10} {asset:<14} {prediction:<5} {conf_pct:>3}% {price:<10.5f} {model:<25}")
        
        total += 1
        
        # Stats by confidence
        conf_key = f"{conf_pct}%"
        by_conf[conf_key] = by_conf.get(conf_key, 0) + 1
        
        # Stats by asset
        by_asset[asset] = by_asset.get(asset, 0) + 1

print("-"*100)
print(f"\n{'ESTADÍSTICAS':^100}")
print("="*100)
print(f"Total Trades Registrados: {total}")
print(f"\nPor Asset:")
for asset, count in by_asset.items():
    print(f"  {asset}: {count} trades")

print(f"\nPor Nivel de Confianza:")
for conf, count in sorted(by_conf.items()):
    print(f"  {conf}: {count} trades")
print("="*100)

print("\n⚠️  NOTA: Los resultados (Win/Loss) se consultan desde la plataforma IQ Option.")
print("El sistema registra las ENTRADAS pero los resultados finales deben verificarse manualmente")
print("o esperando 1-2 minutos después del cierre de cada trade.\n")

# Show balance
api = IQ_Option(EMAIL, PASSWORD)
if api.connect():
    api.change_balance("REAL")
    balance = api.get_balance()
    print(f"💰 Balance Actual: ${balance:,.2f} COP")
