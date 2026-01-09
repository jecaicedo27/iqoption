from iqoptionapi.stable_api import IQ_Option
from app.config import EMAIL, PASSWORD, DEFAULT_ASSET
import time

print("LOGIN...")
api = IQ_Option(EMAIL, PASSWORD)
check, reason = api.connect()
if not check:
    print(f"❌ Connect failed: {reason}")
    exit(1)

print("CONNECTED")
api.change_balance("REAL")
print(f"Balance: {api.get_balance()}")

# print("CHECKING OPEN ASSETS...")
# opentime = api.get_all_open_time()
# if opentime and 'binary' in opentime and 'EURUSD' in opentime['binary']:
#    print(f"EURUSD Binary Status: {opentime['binary']['EURUSD']['open']}")

print(f"GET CANDLES...")
for asset in ["EURUSD-op", "EURUSD", "EURUSD-OTC"]:
    print(f"Trying {asset}...")
    try:
        candles = api.get_candles(asset, 60, 10, time.time())
        if candles:
            print(f"✅ Got {len(candles)} candles for {asset}.")
        else:
            print(f"❌ Empty candles for {asset}")
    except Exception as e:
        print(f"⚠️ Error {asset}: {e}")
    time.sleep(1)
