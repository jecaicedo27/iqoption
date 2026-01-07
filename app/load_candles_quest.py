#!/usr/bin/env python3
"""
Step 1: Download candles and save to QuestDB
"""
from iqoptionapi.stable_api import IQ_Option
import iqoptionapi.constants as OP_code
from app.config import EMAIL, PASSWORD
from questdb.ingress import Sender, TimestampNanos
import time

# Connect to IQ Option
api = IQ_Option(EMAIL, PASSWORD)
api.connect()
api.change_balance("REAL")

# Inject EURUSD-op
OP_code.ACTIVES["EURUSD-op"] = 1861

print("="*80)
print("📥 DESCARGANDO VELAS → QuestDB")
print("="*80)

# Get candles (24 hours)
end_time = int(time.time())
candles = api.get_candles("EURUSD-op", 60, 1440, end_time)

if not candles:
    print("❌ Error descargando velas")
    exit(1)

print(f"✅ Descargadas {len(candles)} velas")
print(f"📊 Guardando en QuestDB...")

# Save to QuestDB using ILP
conf = 'tcp::addr=localhost:9009;'
saved = 0

with Sender.from_conf(conf) as sender:
    for candle in candles:
        try:
            ts = TimestampNanos(int(candle['from'] * 1e9))
            
            sender.row(
                'candles_history',
                symbols={
                    'asset': 'EURUSD-op',
                },
                columns={
                    'open': float(candle['open']),
                    'high': float(candle['max']),
                    'low': float(candle['min']),
                    'close': float(candle['close']),
                    'volume': int(candle['volume']),
                    'range': float(candle['max'] - candle['min']),
                    'range_pct': float((candle['max'] - candle['min']) / candle['close'] * 100)
                },
                at=ts
            )
            saved += 1
            
            if saved % 100 == 0:
                sender.flush()
                print(f"  Guardadas {saved}/{len(candles)} velas...")
                
        except Exception as e:
            print(f"⚠️ Error en vela: {e}")
            continue
    
    sender.flush()

print(f"✅ {saved} velas guardadas en QuestDB (tabla: candles_history)")
print("="*80)
