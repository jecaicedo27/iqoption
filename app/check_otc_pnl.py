#!/usr/bin/env python3
from iqoptionapi.stable_api import IQ_Option
from app.config import EMAIL, PASSWORD
import time
from datetime import datetime, timedelta

api = IQ_Option(EMAIL, PASSWORD)
api.connect()
api.change_balance("REAL")

print("🔍 Consultando historial de trades en EURUSD-OTC...")
print(f"Hora actual: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")

# Get trades from the last 6 hours
since = int((datetime.now() - timedelta(hours=6)).timestamp())

# Try position history
res = api.get_position_history_v2("binary-option", 100, 0, 0, 0)

trades_today = []
wins = 0
losses = 0
total_profit = 0

if isinstance(res, tuple) and res[0]:
    history = res[1].get('positions', [])
    
    for trade in history:
        close_time = trade['close_time'] / 1000
        
        # Filter last 6 hours
        if close_time > since:
            asset = trade.get('instrument_underlying', 'Unknown')
            
            # Filter EURUSD-OTC only
            if 'EURUSD' not in asset.upper():
                continue
                
            pl = float(trade['close_profit']) - float(trade['invest'])
            invest = float(trade['invest'])
            
            result = "WIN" if pl > 0 else "LOSS"
            if pl > 0:
                wins += 1
            else:
                losses += 1
            
            total_profit += pl
            
            time_str = datetime.fromtimestamp(close_time).strftime('%H:%M:%S')
            print(f"{time_str} | ${invest:,.0f} | {result:4} | P&L: ${pl:+,.2f}")

print(f"\n{'='*50}")
print(f"📊 RESUMEN (Últimas 6 horas)")
print(f"{'='*50}")
print(f"Total Trades: {wins + losses}")
print(f"✅ Wins:      {wins}")
print(f"❌ Losses:    {losses}")
print(f"Win Rate:    {(wins/(wins+losses)*100) if (wins+losses)>0 else 0:.1f}%")
print(f"💰 P&L Neto: ${total_profit:+,.2f} COP")
print(f"{'='*50}")
