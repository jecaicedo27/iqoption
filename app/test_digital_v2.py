from iqoptionapi.stable_api import IQ_Option
from app.config import EMAIL, PASSWORD
import threading
import time

def buy_digital_wrapper(api):
    print("Attempting Digital Buy (1m)...")
    try:
        # Asset, Amount, Action, Duration
        id_dig = api.buy_digital_spot("BTCUSD", 10, "call", 1)
        print(f"✅ Digital Buy Result: {id_dig}")
    except Exception as e:
        print(f"❌ Digital Buy Error: {e}")

def test():
    print("Connecting...")
    api = IQ_Option(EMAIL, PASSWORD)
    api.connect()
    api.change_balance("PRACTICE")
    
    print("Updating Digital availability...")
    # This subscribes to digital data
    api.subscribe_strike_list("EURUSD", 1)
    time.sleep(2)
    
    # Run buy in thread to avoid blocking main if it hangs
    t = threading.Thread(target=buy_digital_wrapper, args=(api,))
    t.start()
    
    # Wait max 10 seconds
    t.join(timeout=10)
    
    if t.is_alive():
        print("⚠️ Digital Buy Timed Out (HUNG). System unhealthy.")
    else:
        print("Test Finished.")

if __name__ == "__main__":
    test()
