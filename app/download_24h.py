#!/usr/bin/env python3
from iqoptionapi.stable_api import IQ_Option
import iqoptionapi.constants as OP_code
from app.config import EMAIL, PASSWORD
import time
import pandas as pd
from datetime import datetime, timedelta

# Connect
api = IQ_Option(EMAIL, PASSWORD)
api.connect()
api.change_balance("REAL")

# Inject EURUSD-op
OP_code.ACTIVES["EURUSD-op"] = 1861

print("📥 Descargando velas de las últimas 24 horas...")
print(f"Asset: EURUSD-op")
print(f"Timeframe: 60 segundos (1 minuto)")

# Calculate timestamps
end_time = int(time.time())
start_time = end_time - (24 * 60 * 60)  # 24 hours ago

# Get candles (max ~1440 candles for 24h at 1min)
candles = api.get_candles("EURUSD-op", 60, 1440, end_time)

if candles:
    print(f"✅ Descargadas {len(candles)} velas\n")
    
    # Convert to DataFrame
    df = pd.DataFrame(candles)
    
    # Add human-readable timestamp
    df['datetime'] = pd.to_datetime(df['from'], unit='s')
    
    # Calculate metrics
    df['range'] = df['max'] - df['min']
    df['range_pct'] = (df['range'] / df['close']) * 100
    
    # Reorder columns (use actual column names)
    df = df[['datetime', 'from', 'open', 'max', 'min', 'close', 'volume', 'range', 'range_pct']]
    
    # Save to CSV
    output_file = '/var/www/iqoption/candles_24h.csv'
    df.to_csv(output_file, index=False)
    print(f"💾 Guardado en: {output_file}")
    
    # Statistics
    print(f"\n{'='*80}")
    print(f"📊 ESTADÍSTICAS (Últimas 24 horas)")
    print(f"{'='*80}")
    print(f"Total Velas: {len(df)}")
    print(f"Período: {df['datetime'].min()} → {df['datetime'].max()}")
    print(f"\nPrecios:")
    print(f"  High: {df['max'].max():.5f}")
    print(f"  Low:  {df['min'].min():.5f}")
    print(f"  Rango Total: {(df['max'].max() - df['min'].min()):.5f}")
    print(f"\nVolatilidad por Vela:")
    print(f"  Range Promedio: {df['range'].mean():.5f}")
    print(f"  Range % Promedio: {df['range_pct'].mean():.4f}%")
    print(f"  Range % Máximo: {df['range_pct'].max():.4f}%")
    print(f"  Range % Mínimo: {df['range_pct'].min():.4f}%")
    
    # Analyze 15-min windows
    print(f"\n{'='*80}")
    print(f"📈 ANÁLISIS DE VENTANAS DE 15 MINUTOS")
    print(f"{'='*80}")
    
    windows = []
    for i in range(0, len(df) - 15, 15):
        window = df.iloc[i:i+15]
        window_range = window['max'].max() - window['min'].min()
        window_range_pct = (window_range / window['close'].mean()) * 100
        windows.append({
            'start': window['datetime'].iloc[0],
            'range_pct': window_range_pct
        })
    
    windows_df = pd.DataFrame(windows)
    
    print(f"Total Ventanas de 15min: {len(windows_df)}")
    print(f"Range % Promedio: {windows_df['range_pct'].mean():.4f}%")
    print(f"Range % Mediana: {windows_df['range_pct'].median():.4f}%")
    
    # Count sideways periods
    sideways_count = (windows_df['range_pct'] < 0.05).sum()
    trending_count = (windows_df['range_pct'] >= 0.05).sum()
    
    print(f"\nClasificación (umbral 0.05%):")
    print(f"  Lateral (< 0.05%): {sideways_count} ventanas ({sideways_count/len(windows_df)*100:.1f}%)")
    print(f"  Trending (≥ 0.05%): {trending_count} ventanas ({trending_count/len(windows_df)*100:.1f}%)")
    
    # Recommend threshold
    percentile_50 = windows_df['range_pct'].quantile(0.50)
    percentile_75 = windows_df['range_pct'].quantile(0.75)
    
    print(f"\n💡 RECOMENDACIÓN DE UMBRAL:")
    print(f"  50% de las ventanas tienen ≥ {percentile_50:.4f}%")
    print(f"  25% de las ventanas tienen ≥ {percentile_75:.4f}%")
    print(f"\n  Umbral actual: 0.05%")
    print(f"  Umbral sugerido: {percentile_50:.4f}% (bloquea 50% de períodos más tranquilos)")
    print(f"{'='*80}")
    
else:
    print("❌ Error descargando velas")
