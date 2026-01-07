from iqoptionapi.stable_api import IQ_Option
from app.config import EMAIL, PASSWORD
DEFAULT_ASSET = "BTCUSD"

def check():
    print("Connecting...")
    api = IQ_Option(EMAIL, PASSWORD)
    api.connect()
    
    print(f"Checking {DEFAULT_ASSET} Availability...")
    
    # 1. Check Binary
    # get_all_open_time returns dict of open assets
    all_open = api.get_all_open_time()
    
    # 'binary' or 'turbo' (turbo is < 5min)
    # structure: all_open['turbo']['EURUSD']['open'] -> list of bool or times?
    
    is_turbo_open = False
    is_binary_open = False
    
    try:
        if all_open['turbo'][DEFAULT_ASSET]['open']:
            print("✅ TURBO (1-5m) is OPEN.")
            is_turbo_open = True
        else:
            print("❌ TURBO is CLOSED.")
    except:
        print("❌ TURBO data missing.")
        
    try:
        if all_open['binary'][DEFAULT_ASSET]['open']:
            print("✅ BINARY (15m+) is OPEN.")
            is_binary_open = True
        else:
            print("❌ BINARY is CLOSED.")
    except:
        print("❌ BINARY data missing.")
        
    # Check Digital
    try:
        digi = api.get_digital_spot_profit_after_sale_data(DEFAULT_ASSET, DEFAULT_ASSET, 1) # dummy call?
        # Actually checking open info is harder for digital.
        # But if Turbo/Binary is closed on Sunday might be standard.
        pass
    except:
        pass

    # Real Payout
    payout = api.get_all_profit()
    print(f"Payout Info for {DEFAULT_ASSET}: {payout.get(DEFAULT_ASSET, 'Unknown')}")

if __name__ == "__main__":
    check()
