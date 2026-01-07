from iqoptionapi.stable_api import IQ_Option
from app.config import EMAIL, PASSWORD, DEFAULT_ASSET
import time

def debug_digital():
    print("Connecting...")
    api = IQ_Option(EMAIL, PASSWORD)
    api.connect()
    print("Connected.")
    
    print(f"Testing Digital Buy on {DEFAULT_ASSET}...")
    try:
        # Check Strike IDs first?
        # api.get_strike_list(DEFAULT_ASSET, 1) # 1 min
        
        # Try Buy
        # Note: current price check
        print("Buying Call...")
        id_dig = api.buy_digital_spot(DEFAULT_ASSET, 1, "call", 1)
        print(f"Result ID: {id_dig}")
        
    except Exception as e:
        print(f"CRASH: {e}")

if __name__ == "__main__":
    debug_digital()
