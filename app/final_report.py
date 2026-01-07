#!/usr/bin/env python3
import requests
from datetime import datetime

quest_url = "http://localhost:9000/exec"

# ==== OTC REPORT ====
print("="*120)
print("❌ EURUSD-OTC (Over-The-Counter - DESCONTINUADO)")
print("="*120)

query_otc = """
SELECT timestamp, prediction, confidence, price, result, profit
FROM trades_memory 
WHERE asset = 'EURUSD-OTC'
AND timestamp > dateadd('h', -24, now())
ORDER BY timestamp ASC
"""
response_otc = requests.get(quest_url, params={"query": query_otc, "fmt": "json"})
data_otc = response_otc.json()

otc_wins = 0
otc_losses = 0
otc_pending = 0
otc_total_pl = 0
otc_by_conf = {'75%': {'w': 0, 'l': 0, 't': 0}, '80%': {'w': 0, 'l': 0, 't': 0}, 
               '85%': {'w': 0, 'l': 0, 't': 0}, '90%+': {'w': 0, 'l': 0, 't': 0}}

if 'dataset' in data_otc and data_otc['dataset']:
    print(f"{'#':<4} {'Hora':<10} {'Pred':<5} {'Conf':<6} {'Precio':<10} {'Resultado':<10} {'P&L':<12}")
    print("-"*120)
    
    for idx, row in enumerate(data_otc['dataset'], 1):
        timestamp = row[0]
        prediction = row[1]
        confidence = row[2]
        price = row[3]
        result = row[4] if len(row) > 4 else 'PENDING'
        profit = row[5] if len(row) > 5 else 0
        
        dt = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
        time_str = dt.strftime('%H:%M:%S')
        conf_pct = int(confidence * 100)
        
        conf_key = '75%' if conf_pct == 75 else '80%' if conf_pct == 80 else '85%' if conf_pct == 85 else '90%+'
        otc_by_conf[conf_key]['t'] += 1
        
        if result == 'WIN':
            otc_wins += 1
            otc_by_conf[conf_key]['w'] += 1
            otc_total_pl += profit
            print(f"{idx:<4} {time_str:<10} {prediction:<5} {conf_pct:>3}% {price:<10.5f} {'✅ WIN':<10} ${profit:>+10,.0f}")
        elif result == 'LOSS':
            otc_losses += 1
            otc_by_conf[conf_key]['l'] += 1
            otc_total_pl += profit
            print(f"{idx:<4} {time_str:<10} {prediction:<5} {conf_pct:>3}% {price:<10.5f} {'❌ LOSS':<10} ${profit:>+10,.0f}")
        else:
            otc_pending += 1
            print(f"{idx:<4} {time_str:<10} {prediction:<5} {conf_pct:>3}% {price:<10.5f} {'⏳ PENDING':<10} {'N/A':<12}")
    
    print("-"*120)
    total_otc = otc_wins + otc_losses
    wr_otc = (otc_wins / total_otc * 100) if total_otc > 0 else 0
    print(f"📊 Total: {len(data_otc['dataset'])} | Cerrados: {total_otc} | Wins: {otc_wins} | Losses: {otc_losses} | "
          f"Pending: {otc_pending} | Win Rate: {wr_otc:.1f}% | P&L: ${otc_total_pl:+,.0f}")
    
    print("\n📈 Por Nivel de Confianza:")
    for conf, stats in sorted(otc_by_conf.items()):
        if stats['t'] > 0:
            closed = stats['w'] + stats['l']
            wr = (stats['w'] / closed * 100) if closed > 0 else 0
            print(f"  {conf}: {stats['t']:>3} trades | {stats['w']:>2} wins | {stats['l']:>2} losses | "
                  f"Win Rate: {wr:>5.1f}%")

# ==== REAL MARKET REPORT ====
print("\n" + "="*120)
print("✅ EURUSD-op (Mercado Real Forex - ACTIVO)")
print("="*120)

query_real = """
SELECT timestamp, prediction, confidence, price, result, profit
FROM trades_memory 
WHERE asset = 'EURUSD-op'
AND timestamp > dateadd('h', -24, now())
ORDER BY timestamp ASC
"""
response_real = requests.get(quest_url, params={"query": query_real, "fmt": "json"})
data_real = response_real.json()

real_wins = 0
real_losses = 0
real_pending = 0
real_total_pl = 0
real_by_conf = {'75%': {'w': 0, 'l': 0, 't': 0}, '80%': {'w': 0, 'l': 0, 't': 0}, 
                '85%': {'w': 0, 'l': 0, 't': 0}, '90%+': {'w': 0, 'l': 0, 't': 0}}

if 'dataset' in data_real and data_real['dataset']:
    print(f"{'#':<4} {'Hora':<10} {'Pred':<5} {'Conf':<6} {'Precio':<10} {'Resultado':<10} {'P&L':<12}")
    print("-"*120)
    
    for idx, row in enumerate(data_real['dataset'], 1):
        timestamp = row[0]
        prediction = row[1]
        confidence = row[2]
        price = row[3]
        result = row[4] if len(row) > 4 else 'PENDING'
        profit = row[5] if len(row) > 5 else 0
        
        dt = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
        time_str = dt.strftime('%H:%M:%S')
        conf_pct = int(confidence * 100)
        
        conf_key = '75%' if conf_pct == 75 else '80%' if conf_pct == 80 else '85%' if conf_pct == 85 else '90%+'
        real_by_conf[conf_key]['t'] += 1
        
        if result == 'WIN':
            real_wins += 1
            real_by_conf[conf_key]['w'] += 1
            real_total_pl += profit
            print(f"{idx:<4} {time_str:<10} {prediction:<5} {conf_pct:>3}% {price:<10.5f} {'✅ WIN':<10} ${profit:>+10,.0f}")
        elif result == 'LOSS':
            real_losses += 1
            real_by_conf[conf_key]['l'] += 1
            real_total_pl += profit
            print(f"{idx:<4} {time_str:<10} {prediction:<5} {conf_pct:>3}% {price:<10.5f} {'❌ LOSS':<10} ${profit:>+10,.0f}")
        else:
            real_pending += 1
            print(f"{idx:<4} {time_str:<10} {prediction:<5} {conf_pct:>3}% {price:<10.5f} {'⏳ PENDING':<10} {'N/A':<12}")
    
    print("-"*120)
    total_real = real_wins + real_losses
    wr_real = (real_wins / total_real * 100) if total_real > 0 else 0
    print(f"📊 Total: {len(data_real['dataset'])} | Cerrados: {total_real} | Wins: {real_wins} | Losses: {real_losses} | "
          f"Pending: {real_pending} | Win Rate: {wr_real:.1f}% | P&L: ${real_total_pl:+,.0f}")
    
    print("\n📈 Por Nivel de Confianza:")
    for conf, stats in sorted(real_by_conf.items()):
        if stats['t'] > 0:
            closed = stats['w'] + stats['l']
            wr = (stats['w'] / closed * 100) if closed > 0 else 0
            print(f"  {conf}: {stats['t']:>3} trades | {stats['w']:>2} wins | {stats['l']:>2} losses | "
                  f"Win Rate: {wr:>5.1f}%")

# ==== SUMMARY ====
print("\n" + "="*120)
print("📊 RESUMEN COMPARATIVO FINAL")
print("="*120)
print(f"{'Asset':<15} {'Total':<8} {'Cerrados':<10} {'Wins':<6} {'Losses':<8} {'Win Rate':<10} {'P&L':<15}")
print("-"*120)
print(f"{'OTC':<15} {len(data_otc['dataset']) if 'dataset' in data_otc else 0:<8} "
      f"{otc_wins + otc_losses:<10} {otc_wins:<6} {otc_losses:<8} {wr_otc:<10.1f} ${otc_total_pl:>+12,.0f}")
print(f"{'REAL':<15} {len(data_real['dataset']) if 'dataset' in data_real else 0:<8} "
      f"{real_wins + real_losses:<10} {real_wins:<6} {real_losses:<8} {wr_real:<10.1f} ${real_total_pl:>+12,.0f}")
print("-"*120)
print(f"{'TOTAL':<15} {(len(data_otc['dataset']) if 'dataset' in data_otc else 0) + (len(data_real['dataset']) if 'dataset' in data_real else 0):<8} "
      f"{otc_wins + otc_losses + real_wins + real_losses:<10} {otc_wins + real_wins:<6} {otc_losses + real_losses:<8} "
      f"{((otc_wins + real_wins) / (otc_wins + otc_losses + real_wins + real_losses) * 100) if (otc_wins + otc_losses + real_wins + real_losses) > 0 else 0:<10.1f} "
      f"${otc_total_pl + real_total_pl:>+12,.0f}")
print("="*120)
