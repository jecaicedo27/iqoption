from app.connection import IQConnector
import time

def scan_real_tradable():
    connector = IQConnector()
    if not connector.connect(): return
    
    # We'll try to check the "buyable" status without actually buying
    # Or just try a $1000 COP trade (min unit usually)
    
    pairs = ["EURUSD", "GBPUSD", "USDJPY", "AUDUSD", "EURJPY"]
    print("\n🔍 Scanning REAL MARKET Tradability (COP Account)...")
    
    for pair in pairs:
        print(f"\n--- {pair} ---")
        # 1. Binary Turbo 1m
        print(f"Trying Binary 1m...")
        check, _ = connector.api.buy(2000, pair, "call", 1) # 2000 COP test
        if check:
            print(f"✅ {pair} BINARY 1m OPEN")
        else:
            print(f"❌ {pair} BINARY 1m CLOSED/REJECTED")
            
        # 2. Digital 1m
        print(f"Trying Digital 1m...")
        try:
            # We use a timeout-like check or just wait briefly
            check_d, _ = connector.api.buy_digital_spot(pair, 2000, "call", 1)
            if check_d:
                print(f"✅ {pair} DIGITAL 1m OPEN")
            else:
                print(f"❌ {pair} DIGITAL 1m CLOSED/REJECTED")
        except Exception as e:
            print(f"⚠️ Digital Error: {e}")

if __name__ == "__main__":
    scan_real_tradable()
