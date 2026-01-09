from iqoptionapi.stable_api import IQ_Option
from app.config import EMAIL, PASSWORD
import time

api = IQ_Option(EMAIL, PASSWORD)
api.connect()
api.update_ACTIVES_OPCODE() # FIX for KeyError
api.change_balance("PRACTICE")

ASSET = "EURUSD-op"
AMOUNT = 1

print(f"👉 Attempting BINARY (Not Digital) Buy on {ASSET}...")

# Try 5 minute expiration (usually always open on OTC)
# "call" direction
check, id = api.buy(AMOUNT, ASSET, "call", 5)

if check:
    print(f"✅ SUCCESS! Binary Trade Placed. ID: {id}")
else:
    print(f"❌ Failed: {id}")

