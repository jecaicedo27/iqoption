from iqoptionapi.stable_api import IQ_Option
from app.config import EMAIL, PASSWORD
import time

api = IQ_Option(EMAIL, PASSWORD)
api.connect()
api.change_balance("PRACTICE")
api.update_ACTIVES_OPCODE()

print("🧹 RUNNING BINARY SWEEP (Buying $1 Call everywhere)...")

# List of potential OTC assets
assets = [
    "EURUSD-OTC", "EURUSD-op", 
    "GBPUSD-OTC", "GBPUSD-op",
    "USDJPY-OTC", "USDJPY-op",
    "AUDCAD-OTC", "AUDCAD-op",
    "NZDUSD-OTC", "NZDUSD-op",
    "EURGBP-OTC", "EURGBP-op"
]

for asset in assets:
    print(f"\n👉 Testing {asset} (BINARY 15m)...") # 15 min expiration is safer
    
    # Try Binary Buy (Not Digital)
    check, id = api.buy(1, asset, "call", 15)
    
    if check:
        print(f"✅ API Says SUCCESS for {asset}! ID: {id}")
        print("👀 CHECK YOUR APP NOW!")
    else:
        print(f"❌ Failed: {asset}")

print("\nSweep Complete.")
