from iqoptionapi.stable_api import IQ_Option
from app.config import EMAIL, PASSWORD
import time

print("Testing connection...")
api = IQ_Option(EMAIL, PASSWORD)
check = api.connect()
print(f"Connect success: {check}")

if check:
    print("Updating ACTIVES...")
    api.update_ACTIVES_OPCODE()
    
    print("Getting candles EURUSD-op...")
    try:
        can = api.get_candles("EURUSD-op", 60, 10, time.time())
        print(f"Got {len(can)} candles.")
    except Exception as e:
        print(f"Error op: {e}")
        
    print("Getting candles EURUSD...")
    try:
        can = api.get_candles("EURUSD", 60, 10, time.time())
        print(f"Got {len(can)} candles.")
    except Exception as e:
        print(f"Error forex: {e}")
else:
    print("Connect failed")
