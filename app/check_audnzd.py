from iqoptionapi.stable_api import IQ_Option
from app.config import EMAIL, PASSWORD
import time

def check_audnzd():
    print("Connecting...")
    api = IQ_Option(EMAIL, PASSWORD)
    api.connect()
    
    asset = "AUDNZD"
    print(f"Checking {asset} candles...")
    
    try:
        candles = api.get_candles(asset, 60, 10, time.time())
        if candles:
            print(f"✅ {asset} Data Retrieved! Last: {candles[-1]}")
            # Try Dummy Buy
            api.change_balance("PRACTICE")
            print("Attempting Buy...")
            check, id = api.buy(10, asset, "call", 1)
            if check:
                print(f"✅ BUY SUCCESS: ID {id}")
            else:
                print(f"❌ BUY FAILED: {id}")
        else:
            print("❌ No candles returned.")
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    check_audnzd()
