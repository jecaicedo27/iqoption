#!/usr/bin/env python3
from iqoptionapi.stable_api import IQ_Option
import iqoptionapi.constants as OP_code
from app.config import EMAIL, PASSWORD
import time

api = IQ_Option(EMAIL, PASSWORD)
api.connect()
api.change_balance("REAL")

# Inject EURUSD-op
OP_code.ACTIVES["EURUSD-op"] = 1861

print(f"🕐 Current time: {time.strftime('%Y-%m-%d %H:%M:%S')}")

# Try to get live data
candles = api.get_candles("EURUSD-op", 60, 3, time.time())
if candles:
    print(f"✅ Candle data available: Last close = {candles[-1]['close']}")
else:
    print("❌ No candle data")

# Try a small test buy
print("\n🧪 Testing Binary buy ($4000)...")
check, trade_id = api.buy(4000, "EURUSD-op", "call", 1)
print(f"Result: check={check}, trade_id={trade_id}")

if not check:
    print("\n🔍 Trying EURUSD-OTC instead...")
    OP_code.ACTIVES["EURUSD-OTC"] = 1
    candles_otc = api.get_candles("EURUSD-OTC", 60, 3, time.time())
    if candles_otc:
        print(f"✅ OTC available: Last close = {candles_otc[-1]['close']}")
        check_otc, id_otc = api.buy(4000, "EURUSD-OTC", "call", 1)
        print(f"OTC Result: check={check_otc}, trade_id={id_otc}")
