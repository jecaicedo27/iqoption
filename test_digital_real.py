from iqoptionapi.stable_api import IQ_Option
from app.config import EMAIL, PASSWORD
import time

api = IQ_Option(EMAIL, PASSWORD)
api.connect()
api.update_ACTIVES_OPCODE()
api.change_balance("PRACTICE")

ASSET = "EURUSD-op"
AMOUNT = 1

print(f"👉 Attempting DIGITAL Buy on {ASSET} (1 min)...")

# Digital Spot
check, id = api.buy_digital_spot(ASSET, AMOUNT, "call", 1)

if check:
    print(f"✅ SUCCESS! Digital Trade Placed. ID: {id}")
else:
    print(f"❌ Failed 1m: {id}")
    
    print("\n👉 Attempting 5 min Digital...")
    check, id = api.buy_digital_spot(ASSET, AMOUNT, "call", 5)
    if check:
        print(f"✅ SUCCESS 5m! ID: {id}")
    else:
        print(f"❌ Failed 5m: {id}")
