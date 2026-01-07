#!/usr/bin/env python3
from iqoptionapi.stable_api import IQ_Option
from app.config import EMAIL, PASSWORD
import time
from datetime import datetime, timedelta
import requests

# Connect to IQ Option
api = IQ_Option(EMAIL, PASSWORD)
api.connect()
api.change_balance("REAL")

# Get QuestDB data with confidence
print("📊 Consultando QuestDB...")
quest_url = "http://localhost:9000/exec"
query = """
SELECT timestamp, asset, prediction, confidence, price, model_id 
FROM trades_memory 
WHERE asset IN ('EURUSD-op', 'EURUSD-OTC')
AND timestamp > dateadd('d', -1, now())
ORDER BY timestamp DESC
"""
response = requests.get(quest_url, params={"query": query, "fmt": "json"})
quest_data = response.json()

# Get API trade history
print("🔍 Consultando IQ Option API...")
since = int((datetime.now() - timedelta(days=1)).timestamp())
res = api.get_position_history_v2("binary-option", 200, 0, 0, 0)

api_trades = {}
if isinstance(res, tuple) and res[0]:
    history = res[1].get('positions', [])
    for trade in history:
        close_time = trade['close_time'] / 1000
        if close_time > since:
            trade_id = trade.get('external_id', trade.get('id'))
            pl = float(trade['close_profit']) - float(trade['invest'])
            api_trades[close_time] = {
                'result': 'WIN' if pl > 0 else 'LOSS',
                'pl': pl,
                'invest': float(trade['invest']),
                'close_time': close_time
            }

# Merge data
print("\n" + "="*80)
print("📋 REPORTE COMPLETO DE OPERACIONES")
print("="*80)
print(f"{'Hora':<10} {'Asset':<12} {'Pred':<5} {'Conf':<6} {'Precio':<10} {'Resultado':<8} {'P&L':<12}")
print("-"*80)

total_trades = 0
total_wins = 0
total_losses = 0
total_pnl = 0

conf_levels = {'75%': {'wins': 0, 'total': 0}, '80%': {'wins': 0, 'total': 0}, '85%': {'wins': 0, 'total': 0}, '90%+': {'wins': 0, 'total': 0}}

if 'dataset' in quest_data:
    for row in reversed(quest_data['dataset']):  # Oldest first
        timestamp = row[0]
        asset = row[1]
        prediction = row[2]
        confidence = row[3]
        price = row[4]
        
        dt = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
        ts = dt.timestamp()
        
        # Find closest API trade (within 2 minutes)
        closest_trade = None
        min_diff = float('inf')
        for api_time, api_data in api_trades.items():
            diff = abs(api_time - ts)
            if diff < min_diff and diff < 120:  # Within 2 minutes
                min_diff = diff
                closest_trade = api_data
        
        if closest_trade:
            result = closest_trade['result']
            pl = closest_trade['pl']
            total_trades += 1
            total_pnl += pl
            
            if result == 'WIN':
                total_wins += 1
            else:
                total_losses += 1
            
            # Track by confidence
            conf_pct = int(confidence * 100)
            if conf_pct == 75:
                conf_levels['75%']['total'] += 1
                if result == 'WIN': conf_levels['75%']['wins'] += 1
            elif conf_pct == 80:
                conf_levels['80%']['total'] += 1
                if result == 'WIN': conf_levels['80%']['wins'] += 1
            elif conf_pct == 85:
                conf_levels['85%']['total'] += 1
                if result == 'WIN': conf_levels['85%']['wins'] += 1
            else:
                conf_levels['90%+']['total'] += 1
                if result == 'WIN': conf_levels['90%+']['wins'] += 1
            
            time_str = dt.strftime('%H:%M:%S')
            print(f"{time_str:<10} {asset:<12} {prediction:<5} {conf_pct:>3}% {price:<10.5f} {result:<8} ${pl:>+10,.0f}")

print("-"*80)
print(f"\n{'RESUMEN GENERAL':^80}")
print("="*80)
print(f"Total Operaciones: {total_trades}")
print(f"✅ Wins:           {total_wins} ({total_wins/total_trades*100:.1f}%)" if total_trades > 0 else "✅ Wins: 0")
print(f"❌ Losses:         {total_losses} ({total_losses/total_trades*100:.1f}%)" if total_trades > 0 else "❌ Losses: 0")
print(f"💰 P&L Neto:       ${total_pnl:+,.0f} COP")
print("="*80)

print(f"\n{'ANÁLISIS POR NIVEL DE CONFIANZA':^80}")
print("="*80)
for level, stats in conf_levels.items():
    if stats['total'] > 0:
        win_rate = stats['wins'] / stats['total'] * 100
        print(f"{level:>5} | Trades: {stats['total']:>3} | Wins: {stats['wins']:>3} | Win Rate: {win_rate:>5.1f}%")
print("="*80)
