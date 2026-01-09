#!/usr/bin/env python3
"""
ANÁLISIS FINAL COMPLETO - Todos los trades reales extraídos
"""

# Cargar datos desde el archivo que ya tiene todos los batches
exec(open('/var/www/iqoption/app/analyze_real_results.py').read().split('# Análisis')[0])

# Recalcular estadísticas completas
total_trades = len(trades_from_images)
wins = sum(1 for t in trades_from_images if t['result'] == 'WIN')
losses = sum(1 for t in trades_from_images if t['result'] == 'LOSS')
pushes = sum(1 for t in trades_from_images if t['result'] == 'PUSH')
total_pl = sum(t['pl'] for t in trades_from_images)

win_rate = (wins / (wins + losses) * 100) if (wins + losses) > 0 else 0

print("="*80)
print("📊 ANÁLISIS FINAL COMPLETO - TODOS LOS TRADES")
print("="*80)
print(f"\n🕐 Período: 23:45 (5 ene) hasta 23:45 (6 ene) - 24 horas completas")
print(f"\nTotal de trades analizados: {total_trades}")
print(f"✅ Wins: {wins} ({wins/total_trades*100:.1f}%)")
print(f"❌ Losses: {losses} ({losses/total_trades*100:.1f}%)")
print(f"⚪ Empates: {pushes} ({pushes/total_trades*100:.1f}%)")

print(f"\n{'='*80}")
print("📈 MÉTRICAS CLAVE")
print(f"{'='*80}")
print(f"Win Rate (sin empates): {win_rate:.2f}%")
print(f"P&L Total: ${total_pl:+,} COP")

# ROI
total_invested = sum(abs(t['pl']) if t['result'] == 'LOSS' else (abs(t['pl']) / 0.85) for t in trades_from_images if t['result'] in ['WIN', 'LOSS'])
roi = (total_pl / total_invested * 100) if total_invested > 0 else 0
print(f"Total Invertido: ${total_invested:,.0f} COP")
print(f"ROI: {roi:+.2f}%")

# Por hora
from collections import defaultdict
by_hour = defaultdict(lambda: {'wins': 0, 'losses': 0, 'pl': 0})
for t in trades_from_images:
    if t['result'] in ['WIN', 'LOSS']:
        hour = int(t['time'].split(':')[0])
        by_hour[hour]['wins' if t['result'] == 'WIN' else 'losses'] += 1
        by_hour[hour]['pl'] += t['pl']

print(f"\n{'='*80}")
print("📊 RENDIMIENTO POR HORA")
print(f"{'='*80}")
print(f"Hora | Trades | Wins | Losses | WR%  | P&L")
print("-"*80)

for hour in sorted(by_hour.keys()):
    h = by_hour[hour]
    total = h['wins'] + h['losses']
    wr = (h['wins'] / total * 100) if total > 0 else 0
    print(f"{hour:02d}h  | {total:>6} | {h['wins']:>4} | {h['losses']:>6} | {wr:>4.1f} | ${h['pl']:>+8,}")

print(f"\n{'='*80}")
print("💡 VEREDICTO FINAL")
print(f"{'='*80}")

if win_rate >= 55:
    print(f"✅ ESTRATEGIA RENTABLE")
    print(f"   Win Rate de {win_rate:.1f}% supera el mínimo necesario (54%)")
    print(f"   Generó ${total_pl:+,} COP en 24 horas")
    print(f"   ✅ RECOMENDACIÓN: Activar bot en vivo")
elif win_rate >= 50:
    print(f"⚠️  ESTRATEGIA MARGINAL")  
    print(f"   Win Rate de {win_rate:.1f}% está cerca del breakeven")
    print(f"   P&L: ${total_pl:+,} COP")
    print(f"   ⚠️  RECOMENDACIÓN: Optimizar antes de activar")
else:
    print(f"❌ ESTRATEGIA NO RENTABLE")
    print(f"   Win Rate de {win_rate:.1f}% está por debajo del mínimo (54%)")
    print(f"   Pérdida de ${total_pl:+,} COP en 24 horas")
    print(f"   ❌ RECOMENDACIÓN: NO ACTIVAR - Rediseñar estrategia")

print(f"\n{'='*80}")
print("📌 FACTORES CLAVE")
print(f"{'='*80}")
print(f"• Payout promedio: 85% → Necesitas >54% WR para ser rentable")
print(f"• WR actual: {win_rate:.1f}% → Brecha: {54-win_rate:+.1f} puntos")
print(f"• Total trades: {total_trades} (alta frecuencia)")
print(f"• Promedio por hora: {total_trades/24:.1f} trades/h")

if win_rate < 54:
    print(f"\n💡 MEJORAS SUGERIDAS:")
    print(f"   1. Aumentar umbral de confianza de 70% a 85%+")
    print(f"   2. Agregar filtros técnicos (RSI, MACD, Bandas de Bollinger)")
    print(f"   3. Evitar horas con peor WR (revisar tabla por hora)")
    print(f"   4. Considerar timeframe más alto (5min en lugar de 1min)")
    print(f"   5. Implementar Martingale controlado solo en alta confianza (90%+)")

print("="*80)

# Guardar reporte
with open('/var/www/iqoption/final_report.txt', 'w') as f:
    f.write(f"REPORTE FINAL - Bot Trading Gemini\n")
    f.write(f"="*80 + "\n")
    f.write(f"Período: 24 horas (5-6 enero 2026)\n")
    f.write(f"Total Trades: {total_trades}\n")
    f.write(f"Wins: {wins} ({win_rate:.2f}%)\n")
    f.write(f"Losses: {losses}\n")
    f.write(f"P&L: ${total_pl:+,} COP\n")
    f.write(f"ROI: {roi:+.2f}%\n")
    f.write(f"Veredicto: {'RENTABLE' if win_rate >= 55 else 'NO RENTABLE' if win_rate < 50 else 'MARGINAL'}\n")

print(f"\n💾 Reporte guardado: /var/www/iqoption/final_report.txt")
