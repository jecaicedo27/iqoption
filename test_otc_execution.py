from iqoptionapi.stable_api import IQ_Option
from app.config import EMAIL, PASSWORD
import time

api = IQ_Option(EMAIL, PASSWORD)
api.connect()
api.change_balance("PRACTICE")
api.update_ACTIVES_OPCODE() # Vital to update list

# OTC pairs to test
candidates = [
    "EURUSD-op", "GBPUSD-op", "USDJPY-op", 
    "AUDCAD-op", "NZDUSD-op", "EURGBP-op",
    "EURJPY-op", "GBPJPY-op"
]

print("🔎 Testing Active OTC Assets (Buying $1 Call)...")

for asset in candidates:
    print(f"\n👉 Testing {asset}...")
    
    # Try Digital Spot 1 min
    check, id = api.buy_digital_spot(asset, 1, "call", 1)
    
    if check:
        print(f"✅ SUCCESS! {asset} is WORKING completely.")
        print(f"Trade ID: {id}")
        break  # Found one!
    else:
        print(f"❌ Failed: {asset} -> {id}")
        time.sleep(1)

print("\nScan Complete.")
