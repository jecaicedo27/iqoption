#!/usr/bin/env python3
from iqoptionapi.stable_api import IQ_Option
from app.config import EMAIL, PASSWORD
import time

api = IQ_Option(EMAIL, PASSWORD)
api.connect()
api.change_balance("REAL")

print(f"🕐 Current time: {time.strftime('%Y-%m-%d %H:%M:%S')}")

assets_to_test = ["BTCUSD", "ETHUSD", "EURUSD-OTC", "GBPUSD-OTC"]

for asset in assets_to_test:
    print(f"\n🧪 Testing {asset}...")
    
    # Get candles
    candles = api.get_candles(asset, 60, 3, time.time())
    if candles:
        print(f"  ✅ Data: Last close = {candles[-1]['close']}")
    else:
        print(f"  ❌ No data")
        continue
    
    # Try buy
    check, trade_id = api.buy(4000, asset, "call", 1)
    if check:
        print(f"  ✅ Buy SUCCESS! Trade ID: {trade_id}")
    else:
        print(f"  ❌ Buy FAILED: {trade_id}")
