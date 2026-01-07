from iqoptionapi.stable_api import IQ_Option
from app.config import EMAIL, PASSWORD
import time

api = IQ_Option(EMAIL, PASSWORD)
api.connect()
api.change_balance("REAL")

# Check if market is open
import iqoptionapi.constants as OP_code
OP_code.ACTIVES["EURUSD-op"] = 1861

print("Checking EURUSD-op status...")
print(f"Current time: {time.strftime('%Y-%m-%d %H:%M:%S')}")

# Try to get candles
candles = api.get_candles("EURUSD-op", 60, 5, time.time())
if candles:
    print(f"✅ Market data available: {len(candles)} candles")
    print(f"Last candle close: {candles[-1]['close']}")
else:
    print("❌ No candles - Market might be closed")

# Check binary option availability
check = api.check_win_v3(1)
print(f"API Check result: {check}")
