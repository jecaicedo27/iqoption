#!/usr/bin/env python3
"""
Get real trade history from IQ Option - Last 24 hours
"""
from iqoptionapi.stable_api import IQ_Option
import iqoptionapi.constants as OP_code
from app.config import EMAIL, PASSWORD
import time
from datetime import datetime, timedelta
import pandas as pd

# Connect
api = IQ_Option(EMAIL, PASSWORD)
api.connect()
api.change_balance("REAL")

print("="*80)
print("📊 HISTORIAL REAL DE TRADES - ÚLTIMAS 24 HORAS")
print("="*80)

# Get position history
print("\n🔍 Consultando historial de IQ Option...")

# Try different methods to get history
trades = []

# Method 1: Digital Options
try:
    result = api.get_position_history_v2("binary-option", 100, 0, 0, 0)
    if isinstance(result, tuple) and result[0]:
        positions = result[1].get('positions', [])
        print(f"✅ Encontradas {len(positions)} binary options")
        
        # Filter last 24h
        cutoff_time = time.time() - (24 * 60 * 60)
        
        for pos in positions:
            open_time = pos.get('open_time', 0) / 1000
            close_time = pos.get('close_time', 0) / 1000
            
            if open_time >= cutoff_time:
                invest = float(pos.get('invest', 0))
                profit = float(pos.get('close_profit', 0))
                pl = profit - invest
                result = 'WIN' if pl > 0 else 'LOSS'
                
                trades.append({
                    'open_time': datetime.fromtimestamp(open_time),
                    'close_time': datetime.fromtimestamp(close_time),
                    'asset': pos.get('instrument_active_id', 'Unknown'),
                    'direction': pos.get('instrument_dir', 'Unknown'),
                    'invest': invest,
                    'profit': profit,
                    'pl': pl,
                    'result': result,
                    'type': 'Binary'
                })
except Exception as e:
    print(f"⚠️ Error en binary options: {e}")

# Method 2: Digital Options History
try:
    result = api.get_digital_position_history("digital-option", 100)
    if result:
        print(f"✅ Encontradas {len(result)} digital options")
        
        cutoff_time = time.time() - (24 * 60 * 60)
        
        for pos in result:
            open_time = pos.get('open_time', 0) / 1000
            close_time = pos.get('close_time', 0) / 1000
            
            if open_time >= cutoff_time:
                invest = float(pos.get('amount', 0))
                profit = float(pos.get('profit', 0))
                pl = profit
                result_val = 'WIN' if pl > 0 else 'LOSS'
                
                trades.append({
                    'open_time': datetime.fromtimestamp(open_time),
                    'close_time': datetime.fromtimestamp(close_time),
                    'asset': pos.get('instrument_id', 'Unknown'),
                    'direction': pos.get('direction', 'Unknown'),
                    'invest': invest,
                    'profit': profit,
                    'pl': pl,
                    'result': result_val,
                    'type': 'Digital'
                })
except Exception as e:
    print(f"⚠️ Error en digital options: {e}")

# Display results
print("\n" + "="*80)
print("📈 TRADES REALIZADOS (últimas 24h)")
print("="*80)

if trades:
    df = pd.DataFrame(trades)
    df = df.sort_values('open_time')
    
    print(f"\nTotal Trades: {len(df)}\n")
    
    for idx, trade in df.iterrows():
        emoji = '✅' if trade['result'] == 'WIN' else '❌'
        print(f"{emoji} {trade['open_time'].strftime('%Y-%m-%d %H:%M')} | "
              f"{trade['asset']:<15} | {trade['direction']:<4} | "
              f"Invest: ${trade['invest']:>6.0f} | "
              f"P&L: ${trade['pl']:>+7.0f}")
    
    # Statistics
    print(f"\n{'='*80}")
    print("📊 ESTADÍSTICAS")
    print(f"{'='*80}")
    
    wins = (df['result'] == 'WIN').sum()
    losses = (df['result'] == 'LOSS').sum()
    win_rate = (wins / len(df) * 100) if len(df) > 0 else 0
    total_pl = df['pl'].sum()
    total_invested = df['invest'].sum()
    
    print(f"Total Operaciones: {len(df)}")
    print(f"✅ Wins: {wins} ({wins/len(df)*100:.1f}%)")
    print(f"❌ Losses: {losses} ({losses/len(df)*100:.1f}%)")
    print(f"📈 Win Rate: {win_rate:.1f}%")
    print(f"💰 P&L Total: ${total_pl:+,.0f} COP")
    print(f"💵 Total Invertido: ${total_invested:,.0f} COP")
    
    if total_invested > 0:
        roi = (total_pl / total_invested * 100)
        print(f"📈 ROI: {roi:+.1f}%")
    
    # By asset
    print(f"\n📊 Por Asset:")
    for asset in df['asset'].unique():
        asset_trades = df[df['asset'] == asset]
        asset_wins = (asset_trades['result'] == 'WIN').sum()
        asset_wr = (asset_wins / len(asset_trades) * 100)
        asset_pl = asset_trades['pl'].sum()
        print(f"  {asset}: {len(asset_trades)} trades | {asset_wins} wins | "
              f"WR: {asset_wr:.1f}% | P&L: ${asset_pl:+,.0f}")
    
    # Save
    df.to_csv('/var/www/iqoption/real_trades_24h.csv', index=False)
    print(f"\n💾 Guardado en: /var/www/iqoption/real_trades_24h.csv")
    
else:
    print("\n⚠️ No se encontraron trades en las últimas 24 horas")
    print("Esto puede significar:")
    print("  - El bot no ha operado")
    print("  - Las operaciones son muy antiguas")
    print("  - Problemas con la API de IQ Option")

print("="*80)
