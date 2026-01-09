#!/usr/bin/env python3
"""
Resultados reales extraídos de las imágenes del historial de IQ Option
Hora: Colombia (UTC-5)
"""

# Datos extraídos de las imágenes (10 imágenes total)
trades_from_images = [
    # === PRIMER BATCH ===
    # Imagen 1 
    {"time": "23:45", "result": "WIN", "pl": 3400},
    {"time": "22:44", "result": "LOSS", "pl": -4000},
    {"time": "22:41", "result": "WIN", "pl": 3400},
    {"time": "22:30", "result": "LOSS", "pl": -4000},
    {"time": "22:27", "result": "LOSS", "pl": -4000},
    {"time": "22:17", "result": "LOSS", "pl": -4000},
    {"time": "22:15", "result": "LOSS", "pl": -4000},
    {"time": "22:14", "result": "LOSS", "pl": -4000},
    {"time": "22:10", "result": "LOSS", "pl": -4000},
    
    # Imagen 2
    {"time": "22:09", "result": "LOSS", "pl": -4000},
    {"time": "22:07", "result": "WIN", "pl": 3400},
    {"time": "22:06", "result": "WIN", "pl": 3400},
    {"time": "22:05", "result": "LOSS", "pl": -4000},
    {"time": "22:04", "result": "PUSH", "pl": 0},
    {"time": "22:03", "result": "LOSS", "pl": -4000},
    {"time": "22:02", "result": "WIN", "pl": 3400},
    {"time": "22:01", "result": "LOSS", "pl": -4000},
    {"time": "22:00", "result": "LOSS", "pl": -4000},
    
    # Imagen 3
    {"time": "22:00", "result": "LOSS", "pl": -4000},
    {"time": "21:58", "result": "LOSS", "pl": -4000},
    {"time": "21:57", "result": "WIN", "pl": 3400},
    {"time": "21:55", "result": "LOSS", "pl": -600},
    {"time": "21:54", "result": "WIN", "pl": 3400},
    {"time": "21:53", "result": "LOSS", "pl": -4000},
    {"time": "21:48", "result": "LOSS", "pl": -4000},
    {"time": "21:44", "result": "LOSS", "pl": -4000},
    {"time": "21:42", "result": "LOSS", "pl": -4000},
    {"time": "21:41", "result": "WIN", "pl": 3400},
    
    # Imagen 4
    {"time": "21:37", "result": "WIN", "pl": 3400},
    {"time": "21:36", "result": "WIN", "pl": 3400},
    {"time": "21:33", "result": "LOSS", "pl": -4000},
    {"time": "21:30", "result": "LOSS", "pl": -4000},
    {"time": "21:28", "result": "WIN", "pl": 3400},
    {"time": "21:27", "result": "WIN", "pl": 3400},
    {"time": "21:25", "result": "LOSS", "pl": -4000},
    {"time": "21:24", "result": "WIN", "pl": 3400},
    {"time": "21:23", "result": "WIN", "pl": 3400},
    
    # Imagen 5
    {"time": "21:22", "result": "WIN", "pl": 3400},
    {"time": "21:21", "result": "LOSS", "pl": -4000},
    {"time": "21:20", "result": "WIN", "pl": 3400},
    {"time": "21:19", "result": "WIN", "pl": 3400},
    {"time": "21:17", "result": "WIN", "pl": 3400},
    {"time": "21:13", "result": "LOSS", "pl": -4000},
    {"time": "21:11", "result": "LOSS", "pl": -4000},
    {"time": "21:10", "result": "WIN", "pl": 3400},
    {"time": "21:08", "result": "WIN", "pl": 3400},
    
    # === SEGUNDO BATCH - 19:14 a 21:05 ===
    # Imagen 6
    {"time": "21:05", "result": "LOSS", "pl": -4000},
    {"time": "21:04", "result": "WIN", "pl": 3400},
    {"time": "21:03", "result": "LOSS", "pl": -4000},
    {"time": "21:02", "result": "WIN", "pl": 3400},
    {"time": "20:58", "result": "LOSS", "pl": -4000},
    {"time": "20:57", "result": "WIN", "pl": 6800},
    {"time": "20:55", "result": "WIN", "pl": 3400},
    {"time": "20:53", "result": "LOSS", "pl": -4000},
    {"time": "20:50", "result": "LOSS", "pl": -8000},
    {"time": "20:48", "result": "LOSS", "pl": -4000},
    
    # Imagen 7
    {"time": "20:46", "result": "WIN", "pl": 3400},
    {"time": "20:45", "result": "LOSS", "pl": -4000},
    {"time": "20:44", "result": "LOSS", "pl": -4000},
    {"time": "20:43", "result": "LOSS", "pl": -4000},
    {"time": "20:40", "result": "WIN", "pl": 3400},
    {"time": "20:38", "result": "LOSS", "pl": -4000},
    {"time": "20:37", "result": "LOSS", "pl": -4000},
    {"time": "20:33", "result": "LOSS", "pl": -4000},
    {"time": "20:26", "result": "WIN", "pl": 3400},
    
    # Imagen 8
    {"time": "20:21", "result": "LOSS", "pl": -4000},
    {"time": "20:18", "result": "WIN", "pl": 3400},
    {"time": "20:17", "result": "LOSS", "pl": -4000},
    {"time": "20:15", "result": "LOSS", "pl": -4000},
    {"time": "20:11", "result": "LOSS", "pl": -4000},
    {"time": "20:10", "result": "LOSS", "pl": -4000},
    {"time": "20:09", "result": "LOSS", "pl": -4000},
    {"time": "20:08", "result": "LOSS", "pl": -4000},
    {"time": "20:07", "result": "WIN", "pl": 3400},
    {"time": "20:05", "result": "LOSS", "pl": -4000},
    {"time": "20:04", "result": "WIN", "pl": 3400},
    {"time": "20:03", "result": "WIN", "pl": 3400},
    {"time": "20:02", "result": "WIN", "pl": 3400},
    
    # Imagen 9
    {"time": "19:58", "result": "LOSS", "pl": -4000},
    {"time": "19:57", "result": "LOSS", "pl": -4000},
    {"time": "19:55", "result": "LOSS", "pl": -4000},
    {"time": "19:54", "result": "LOSS", "pl": -4000},
    {"time": "19:51", "result": "WIN", "pl": 3400},
    {"time": "19:50", "result": "WIN", "pl": 3400},
    {"time": "19:49", "result": "LOSS", "pl": -4000},
    {"time": "19:45", "result": "LOSS", "pl": -4000},
    {"time": "19:42", "result": "LOSS", "pl": -4000},
    {"time": "19:41", "result": "LOSS", "pl": -4000},
    {"time": "19:40", "result": "LOSS", "pl": -4000},
    {"time": "19:38", "result": "LOSS", "pl": -4000},
   
    # Imagen 10
    {"time": "19:37", "result": "WIN", "pl": 3400},
    {"time": "19:35", "result": "LOSS", "pl": -4000},
    {"time": "19:33", "result": "LOSS", "pl": -4000},
    {"time": "19:32", "result": "LOSS", "pl": -4000},
    {"time": "19:29", "result": "WIN", "pl": 6800},
    {"time": "19:26", "result": "WIN", "pl": 6800},
    {"time": "19:24", "result": "WIN", "pl": 3400},
    {"time": "19:21", "result": "LOSS", "pl": -4000},
    {"time": "19:20", "result": "LOSS", "pl": -4000},
    {"time": "19:18", "result": "LOSS", "pl": -4000},
    {"time": "19:15", "result": "WIN", "pl": 3400},
    {"time": "19:14", "result": "WIN", "pl": 3400},
]

# Análisis
total_trades = len(trades_from_images)
wins = sum(1 for t in trades_from_images if t['result'] == 'WIN')
losses = sum(1 for t in trades_from_images if t['result'] == 'LOSS')
pushes = sum(1 for t in trades_from_images if t['result'] == 'PUSH')
total_pl = sum(t['pl'] for t in trades_from_images)

win_rate = (wins / (wins + losses) * 100) if (wins + losses) > 0 else 0

print("="*80)
print("📊 RESULTADOS REALES - EXTRAÍDOS DE IMÁGENES")
print("="*80)
print(f"\n🕐 Rango de tiempo: 21:08 - 23:45 (Hora Colombia)")
print(f"\nTotal de trades: {total_trades}")
print(f"✅ Wins: {wins} ({wins/total_trades*100:.1f}%)")
print(f"❌ Losses: {losses} ({losses/total_trades*100:.1f}%)")
print(f"⚪ Empates: {pushes}")
print(f"\n📈 Win Rate (sin empates): {win_rate:.1f}%")
print(f"💰 P&L Total: ${total_pl:+,} COP")

# ROI
total_invested = (wins + losses) * 4000 + 600  # El trade de $8000 perdió $600
roi = (total_pl / total_invested * 100)
print(f"📈 ROI: {roi:+.1f}%")

print(f"\n{'='*80}")
print("💡 ANÁLISIS:")
print(f"{'='*80}")

if win_rate >= 55:
    print(f"✅ EXCELENTE - Win Rate de {win_rate:.1f}% es RENTABLE")
    print(f"💰 En ~3 horas generó ${total_pl:+,} COP")
elif win_rate >= 50:
    print(f"⚠️  MARGINAL - Win Rate de {win_rate:.1f}%")
else:
    print(f"❌ BAJO - Win Rate de {win_rate:.1f}%")

print(f"\nNota: Estos son solo {total_trades} trades de los ~270 registrados en 24h")
print(f"Representan aproximadamente el {total_trades/270*100:.1f}% del total")
print("="*80)

# Save for later analysis
import json
with open('/var/www/iqoption/real_results_sample.json', 'w') as f:
    json.dump({
        'trades': trades_from_images,
        'summary': {
            'total': total_trades,
            'wins': wins,
            'losses': losses,
            'pushes': pushes,
            'win_rate': win_rate,
            'total_pl': total_pl,
            'roi': roi
        }
    }, f, indent=2)

print(f"\n💾 Datos guardados en: real_results_sample.json")

# === TERCER BATCH - 14:08 a 19:08 ===
batch3_trades = [
    # Imagen 11
    {"time": "19:08", "result": "LOSS", "pl": -4000},
    {"time": "19:03", "result": "WIN", "pl": 3400},
    {"time": "18:21", "result": "WIN", "pl": 3400},
    {"time": "18:20", "result": "LOSS", "pl": -4000},
    {"time": "18:17", "result": "WIN", "pl": 3400},
    {"time": "18:15", "result": "LOSS", "pl": -4000},
    {"time": "18:14", "result": "LOSS", "pl": -4000},
    {"time": "18:13", "result": "WIN", "pl": 3400},
    {"time": "17:29", "result": "WIN", "pl": 11640},  # Digital
    {"time": "17:17", "result": "LOSS", "pl": -4000},
    {"time": "17:16", "result": "WIN", "pl": 3400},
    {"time": "17:14", "result": "LOSS", "pl": -4000},
    
    # Imagen 12
    {"time": "17:13", "result": "LOSS", "pl": -4000},
    {"time": "17:12", "result": "LOSS", "pl": -4000},
    {"time": "17:12", "result": "WIN", "pl": 3400},  # GBP/USD
    {"time": "16:00", "result": "LOSS", "pl": -4000},
    {"time": "15:59", "result": "WIN", "pl": 3400},
    {"time": "15:57", "result": "WIN", "pl": 3400},
    {"time": "15:56", "result": "WIN", "pl": 3400},
    {"time": "15:54", "result": "WIN", "pl": 3400},
    {"time": "15:53", "result": "WIN", "pl": 3400},
    {"time": "15:52", "result": "LOSS", "pl": -4000},
    {"time": "15:51", "result": "LOSS", "pl": -4000},
    {"time": "15:49", "result": "WIN", "pl": 3400},
    
    # Imagen 13
    {"time": "15:47", "result": "LOSS", "pl": -8000},
    {"time": "15:43", "result": "LOSS", "pl": -4000},
    {"time": "15:42", "result": "LOSS", "pl": -4000},
    {"time": "15:40", "result": "WIN", "pl": 3400},
    {"time": "15:39", "result": "WIN", "pl": 3400},
    {"time": "15:38", "result": "WIN", "pl": 3400},
    {"time": "15:36", "result": "LOSS", "pl": -4000},
    {"time": "15:35", "result": "WIN", "pl": 3400},
    {"time": "15:34", "result": "LOSS", "pl": -4000},
    {"time": "15:30", "result": "LOSS", "pl": -4000},
    {"time": "15:27", "result": "WIN", "pl": 3400},
    {"time": "15:22", "result": "LOSS", "pl": -600},
    
    # Imagen 14
    {"time": "15:21", "result": "WIN", "pl": 3400},
    {"time": "15:20", "result": "WIN", "pl": 3400},
    {"time": "15:19", "result": "WIN", "pl": 3400},
    {"time": "15:18", "result": "LOSS", "pl": -8000},
    {"time": "15:16", "result": "LOSS", "pl": -4000},
    {"time": "15:15", "result": "LOSS", "pl": -4000},
    {"time": "15:14", "result": "LOSS", "pl": -4000},
    {"time": "14:40", "result": "LOSS", "pl": -4000},
    {"time": "14:38", "result": "PUSH", "pl": 0},
    {"time": "14:37", "result": "WIN", "pl": 3400},
    {"time": "14:33", "result": "WIN", "pl": 3400},
    {"time": "14:31", "result": "WIN", "pl": 3400},
    {"time": "14:29", "result": "WIN", "pl": 3400},
    
    # Imagen 15
    {"time": "14:28", "result": "WIN", "pl": 3400},
    {"time": "14:27", "result": "LOSS", "pl": -4000},
    {"time": "14:26", "result": "WIN", "pl": 3400},
    {"time": "14:25", "result": "WIN", "pl": 3400},
    {"time": "14:24", "result": "WIN", "pl": 3400},
    {"time": "14:23", "result": "LOSS", "pl": -4000},
    {"time": "14:21", "result": "LOSS", "pl": -4000},
    {"time": "14:20", "result": "LOSS", "pl": -4000},
    {"time": "14:18", "result": "LOSS", "pl": -4000},
    {"time": "14:17", "result": "WIN", "pl": 3400},
    {"time": "14:12", "result": "WIN", "pl": 3400},
    {"time": "14:11", "result": "WIN", "pl": 3400},
    {"time": "14:08", "result": "PUSH", "pl": 0},
]

# Add to main list
trades_from_images.extend(batch3_trades)

print("\n" + "="*80)
print("BATCH 3 AGREGADO - Nuevas operaciones")
print("="*80)
print(f"Trades en batch 3: {len(batch3_trades)}")

# === CUARTO BATCH - 08:39 a 14:05 ===
batch4_trades = [
    # Imagen 16
    {"time": "14:05", "result": "WIN", "pl": 3400},
    {"time": "14:04", "result": "LOSS", "pl": -600},
    {"time": "14:03", "result": "LOSS", "pl": -4000},
    {"time": "14:02", "result": "LOSS", "pl": -4000},
    {"time": "14:01", "result": "WIN", "pl": 3400},
    {"time": "14:00", "result": "WIN", "pl": 3400},
    {"time": "13:57", "result": "LOSS", "pl": -4000},
    {"time": "13:56", "result": "WIN", "pl": 3400},
    {"time": "13:55", "result": "WIN", "pl": 3400},
    {"time": "13:54", "result": "WIN", "pl": 3400},
    {"time": "13:53", "result": "WIN", "pl": 3400},
    {"time": "13:51", "result": "LOSS", "pl": -600},
    
    # Imagen 17
    {"time": "13:49", "result": "WIN", "pl": 3400},
    {"time": "13:47", "result": "LOSS", "pl": -4000},
    {"time": "13:46", "result": "WIN", "pl": 3400},
    {"time": "13:45", "result": "LOSS", "pl": -4000},
    {"time": "13:42", "result": "WIN", "pl": 3400},
    {"time": "13:39", "result": "WIN", "pl": 6800},
    {"time": "13:37", "result": "WIN", "pl": 3400},
    {"time": "13:35", "result": "LOSS", "pl": -4000},
    {"time": "13:34", "result": "LOSS", "pl": -4000},
    {"time": "13:33", "result": "WIN", "pl": 3400},
    {"time": "13:32", "result": "LOSS", "pl": -4000},
    {"time": "13:31", "result": "WIN", "pl": 3400},
    {"time": "13:28", "result": "LOSS", "pl": -4000},
    
    # Imagen 18
    {"time": "13:28", "result": "WIN", "pl": 3400},  # Segundo trade mismo tiempo
    {"time": "13:25", "result": "LOSS", "pl": -8000},
    {"time": "13:24", "result": "LOSS", "pl": -4000},
    {"time": "13:23", "result": "LOSS", "pl": -4000},
    {"time": "13:22", "result": "LOSS", "pl": -4000},
    {"time": "13:21", "result": "WIN", "pl": 3400},
    {"time": "13:20", "result": "WIN", "pl": 3400},
    {"time": "13:18", "result": "LOSS", "pl": -8000},
    {"time": "13:17", "result": "WIN", "pl": 3400},
    {"time": "13:16", "result": "LOSS", "pl": -4000},
    {"time": "13:13", "result": "LOSS", "pl": -4000},
    {"time": "13:12", "result": "LOSS", "pl": -4000},
    
    # Imagen 19
    {"time": "13:11", "result": "WIN", "pl": 3400},
    {"time": "09:20", "result": "LOSS", "pl": -4000},
    {"time": "09:19", "result": "WIN", "pl": 3400},
    {"time": "09:17", "result": "WIN", "pl": 6800},
    {"time": "09:15", "result": "LOSS", "pl": -4000},
    {"time": "09:11", "result": "WIN", "pl": 3400},
    {"time": "09:10", "result": "LOSS", "pl": -4000},
    {"time": "09:08", "result": "WIN", "pl": 3400},
    {"time": "09:07", "result": "LOSS", "pl": -4000},
    {"time": "09:04", "result": "LOSS", "pl": -4000},
    {"time": "09:02", "result": "WIN", "pl": 3400},
    {"time": "09:01", "result": "PUSH", "pl": 0},
    
    # Imagen 20
    {"time": "08:59", "result": "LOSS", "pl": -600},
    {"time": "08:56", "result": "LOSS", "pl": -4000},
    {"time": "08:55", "result": "WIN", "pl": 3400},
    {"time": "08:54", "result": "WIN", "pl": 3400},
    {"time": "08:53", "result": "LOSS", "pl": -4000},
    {"time": "08:52", "result": "LOSS", "pl": -4000},
    {"time": "08:50", "result": "WIN", "pl": 3400},
    {"time": "08:49", "result": "WIN", "pl": 3400},
    {"time": "08:47", "result": "WIN", "pl": 3400},
    {"time": "08:46", "result": "WIN", "pl": 3400},
    {"time": "08:45", "result": "LOSS", "pl": -4000},
    {"time": "08:41", "result": "WIN", "pl": 3400},
    {"time": "08:39", "result": "LOSS", "pl": -4000},
]

trades_from_images.extend(batch4_trades)

print("\n" + "="*80)
print("BATCH 4 AGREGADO")
print("="*80)
print(f"Trades en batch 4: {len(batch4_trades)}")
print(f"Total acumulado: {len(trades_from_images)}")

# === QUINTO BATCH - 23:45 (día anterior) hasta 08:38 ===
batch5_trades = [
    # Imagen 21 (08:18-08:38)
    {"time": "08:38", "result": "WIN", "pl": 3400},
    {"time": "08:37", "result": "WIN", "pl": 6800},
    {"time": "08:32", "result": "LOSS", "pl": -4000},
    {"time": "08:30", "result": "LOSS", "pl": -4000},
    {"time": "08:29", "result": "LOSS", "pl": -4000},
    {"time": "08:26", "result": "LOSS", "pl": -4000},
    {"time": "08:24", "result": "WIN", "pl": 3400},
    {"time": "08:23", "result": "WIN", "pl": 3400},
    {"time": "08:22", "result": "LOSS", "pl": -4000},
    {"time": "08:20", "result": "LOSS", "pl": -4000},
    {"time": "08:19", "result": "LOSS", "pl": -4000},
    {"time": "08:18", "result": "WIN", "pl": 3400},
    
    # Imagen 22 (08:02-08:17)
    {"time": "08:17", "result": "LOSS", "pl": -4000},
    {"time": "08:16", "result": "LOSS", "pl": -4000},
    {"time": "08:15", "result": "LOSS", "pl": -8000},
    {"time": "08:14", "result": "LOSS", "pl": -4000},
    {"time": "08:11", "result": "WIN", "pl": 3400},
    {"time": "08:10", "result": "WIN", "pl": 3400},
    {"time": "08:08", "result": "WIN", "pl": 3400},
    {"time": "08:06", "result": "LOSS", "pl": -4000},
    {"time": "08:04", "result": "WIN", "pl": 6800},
    {"time": "08:02", "result": "LOSS", "pl": -4000},
    
    # Imagen 23 (07:38-07:59)
    {"time": "07:59", "result": "WIN", "pl": 3400},
    {"time": "07:57", "result": "WIN", "pl": 6800},
    {"time": "07:55", "result": "WIN", "pl": 3400},
    {"time": "07:54", "result": "LOSS", "pl": -4000},
    {"time": "07:51", "result": "WIN", "pl": 3400},
    {"time": "07:50", "result": "LOSS", "pl": -4000},
    {"time": "07:49", "result": "WIN", "pl": 3400},
    {"time": "07:48", "result": "WIN", "pl": 3400},
    {"time": "07:46", "result": "WIN", "pl": 3400},
    {"time": "07:45", "result": "LOSS", "pl": -4000},
    {"time": "07:42", "result": "WIN", "pl": 3400},
    {"time": "07:41", "result": "LOSS", "pl": -4000},
    {"time": "07:39", "result": "LOSS", "pl": -4000},
    {"time": "07:38", "result": "LOSS", "pl": -8000},
    
    # Imagen 24 (07:11-07:37)
    {"time": "07:37", "result": "LOSS", "pl": -4000},
    {"time": "07:36", "result": "LOSS", "pl": -4000},
    {"time": "07:35", "result": "LOSS", "pl": -4000},
    {"time": "07:32", "result": "LOSS", "pl": -4000},
    {"time": "07:29", "result": "LOSS", "pl": -4000},
    {"time": "07:28", "result": "LOSS", "pl": -4000},
    {"time": "07:21", "result": "WIN", "pl": 3400},
    {"time": "07:20", "result": "WIN", "pl": 3400},
    {"time": "07:17", "result": "LOSS", "pl": -600},
    {"time": "07:16", "result": "WIN", "pl": 3400},
    {"time": "07:13", "result": "LOSS", "pl": -600},
    {"time": "07:12", "result": "LOSS", "pl": -4000},
    {"time": "07:11", "result": "WIN", "pl": 3400},
    
    # Imagen 25 (23:45 día anterior hasta 07:08)
    {"time": "07:08", "result": "WIN", "pl": 3400},
    {"time": "07:06", "result": "LOSS", "pl": -4000},
    {"time": "07:04", "result": "WIN", "pl": 3400},
    {"time": "07:03", "result": "WIN", "pl": 3400},
    {"time": "07:02", "result": "WIN", "pl": 3400},
    {"time": "07:00", "result": "WIN", "pl": 3400},
    {"time": "00:02", "result": "LOSS", "pl": -4000},
    {"time": "23:57", "result": "LOSS", "pl": -4000},
    {"time": "23:56", "result": "WIN", "pl": 3400},
    {"time": "23:52", "result": "LOSS", "pl": -690},
    {"time": "23:50", "result": "WIN", "pl": 3320},
    {"time": "23:45", "result": "WIN", "pl": 3320},
]

trades_from_images.extend(batch5_trades)

print("\n" + "="*80)
print("BATCH 5 AGREGADO - ÚLTIMO BATCH")
print("="*80)
print(f"Trades en batch 5: {len(batch5_trades)}")
print(f"TOTAL COMPLETO: {len(trades_from_images)} trades")
print(f"\nCOBERTURA: {len(trades_from_images)/270*100:.1f}% de las 270 operaciones registradas")

# === SEXTO BATCH FINAL - 21:46 hasta 23:44 (5 ene) ===
batch6_trades = [
    # Imagen 26 (23:22-23:44)
    {"time": "23:44", "result": "LOSS", "pl": -4000},
    {"time": "23:42", "result": "LOSS", "pl": -4000},
    {"time": "23:38", "result": "WIN", "pl": 3320},
    {"time": "23:37", "result": "WIN", "pl": 3320},
    {"time": "23:35", "result": "PUSH", "pl": 0},
    {"time": "23:32", "result": "WIN", "pl": 3320},
    {"time": "23:30", "result": "LOSS", "pl": -4000},
    {"time": "23:28", "result": "WIN", "pl": 3320},
    {"time": "23:26", "result": "WIN", "pl": 3320},
    {"time": "23:25", "result": "PUSH", "pl": 0},
    {"time": "23:24", "result": "LOSS", "pl": -4000},
    {"time": "23:22", "result": "WIN", "pl": 3320},
    
    # Imagen 27 (22:52-23:20)
    {"time": "23:20", "result": "LOSS", "pl": -4000},
    {"time": "23:18", "result": "WIN", "pl": 3320},
    {"time": "23:14", "result": "LOSS", "pl": -4000},
    {"time": "23:10", "result": "WIN", "pl": 3320},
    {"time": "23:08", "result": "LOSS", "pl": -4000},
    {"time": "23:05", "result": "LOSS", "pl": -4000},
    {"time": "23:04", "result": "WIN", "pl": 3320},
    {"time": "22:59", "result": "WIN", "pl": 3320},
    {"time": "22:56", "result": "WIN", "pl": 3320},
    {"time": "22:54", "result": "WIN", "pl": 3320},
    {"time": "22:53", "result": "WIN", "pl": 3320},
    {"time": "22:52", "result": "WIN", "pl": 3320},
    
    # Imagen 28 (22:28-22:50)
    {"time": "22:50", "result": "WIN", "pl": 3320},
    {"time": "22:45", "result": "LOSS", "pl": -4000},
    {"time": "22:44", "result": "LOSS", "pl": -4000},
    {"time": "22:42", "result": "LOSS", "pl": -4000},
    {"time": "22:41", "result": "WIN", "pl": 3320},
    {"time": "22:40", "result": "WIN", "pl": 3320},
    {"time": "22:38", "result": "WIN", "pl": 3320},
    {"time": "22:33", "result": "LOSS", "pl": -4000},
    {"time": "22:32", "result": "WIN", "pl": 3320},
    {"time": "22:31", "result": "WIN", "pl": 3320},
    {"time": "22:29", "result": "LOSS", "pl": -4000},
    {"time": "22:28", "result": "WIN", "pl": 3320},
    
    # Imagen 29 (22:05-22:27)
    {"time": "22:27", "result": "WIN", "pl": 6640},
    {"time": "22:26", "result": "LOSS", "pl": -4000},
    {"time": "22:23", "result": "LOSS", "pl": -4000},
    {"time": "22:21", "result": "WIN", "pl": 3320},
    {"time": "22:19", "result": "LOSS", "pl": -4000},
    {"time": "22:18", "result": "LOSS", "pl": -660},
    {"time": "22:12", "result": "LOSS", "pl": -660},
    {"time": "22:11", "result": "LOSS", "pl": -4000},
    {"time": "22:10", "result": "WIN", "pl": 3320},
    {"time": "22:09", "result": "WIN", "pl": 3320},
    {"time": "22:08", "result": "LOSS", "pl": -8000},
    {"time": "22:07", "result": "WIN", "pl": 3320},
    {"time": "22:06", "result": "LOSS", "pl": -4000},
    {"time": "22:05", "result": "LOSS", "pl": -8000},
    
    # Imagen 30 (21:46-22:04)
    {"time": "22:04", "result": "LOSS", "pl": -4000},
    {"time": "22:03", "result": "WIN", "pl": 3320},
    {"time": "22:02", "result": "LOSS", "pl": -4000},
    {"time": "22:01", "result": "WIN", "pl": 3320},
    {"time": "22:00", "result": "WIN", "pl": 6640},
    {"time": "21:46", "result": "WIN", "pl": 2000},
]

trades_from_images.extend(batch6_trades)

print("\n" + "="*80)
print("BATCH 6 AGREGADO - ÚLTIMO BATCH FINAL")
print("="*80)
print(f"Trades en batch 6: {len(batch6_trades)}")
print(f"TOTAL DEFINITIVO: {len(trades_from_images)} trades")
