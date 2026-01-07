#!/usr/bin/env python3
from iqoptionapi.stable_api import IQ_Option
from app.config import EMAIL, PASSWORD
import time
import iqoptionapi.constants as OP_code

api = IQ_Option(EMAIL, PASSWORD)
api.connect()
api.change_balance("REAL")

print(f"🕐 Current time: {time.strftime('%Y-%m-%d %H:%M:%S')}")
print("🔍 Scanning available NON-OTC assets...\n")

# Test various non-OTC assets
assets_to_test = [
    ("EURUSD-op", 1861),  # Real market with injection
    "EURUSD",
    "GBPUSD", 
    "USDJPY",
    "AUDUSD",
    "USDCAD",
    "NZDUSD",
    "EURGBP",
    "EURJPY",
    "GBPJPY",
    "BTCUSD",
    "ETHUSD",
    "XAUUSD",  # Gold
]

available = []

for asset in assets_to_test:
    # Handle EURUSD-op special case
    if isinstance(asset, tuple):
        asset_name, asset_id = asset
        OP_code.ACTIVES[asset_name] = asset_id
    else:
        asset_name = asset
    
    print(f"Testing {asset_name}...", end=" ")
    
    # Get candles
    candles = api.get_candles(asset_name, 60, 3, time.time())
    if not candles:
        print("❌ No data")
        continue
    
    # Try buy
    check, trade_id = api.buy(4000, asset_name, "call", 1)
    if check:
        print(f"✅ AVAILABLE! (Trade: {trade_id})")
        available.append(asset_name)
    else:
        error_msg = str(trade_id)[:50]
        print(f"❌ {error_msg}")

print("\n" + "="*50)
print("✅ AVAILABLE NON-OTC ASSETS:")
if available:
    for asset in available:
        print(f"  • {asset}")
else:
    print("  None found. All markets appear closed.")
print("="*50)
