from app.connection import IQConnector
import time

def final_test_real():
    print("🚀 Attempting FINAL REAL MARKET TEST...")
    connector = IQConnector()
    if not connector.connect(): return

    asset = "EURUSD"
    print(f"🎯 Target: {asset} (Real Market)")
    
    # 1. Try Standard Buy
    print("\n💸 Attempting Standard Buy ($1, Call, 1m)...")
    check, id = connector.api.buy(1, asset, "call", 1)
    if check:
        print(f"✅ SUCCESS! Standard Real Trade Accepted. ID: {id}")
        return True
    else:
        print(f"❌ Standard Rejected.")
        
    # 2. Try Digital Fallback
    print("\n💸 Attempting Digital Fallback ($1, Call, 1m)...")
    try:
        check_d, id_d = connector.api.buy_digital_spot(asset, 1, "call", 1)
        if check_d:
            print(f"✅ SUCCESS! Digital Real Trade Accepted. ID: {id_d}")
            return True
        else:
            print(f"❌ Digital Rejected.")
    except Exception as e:
        print(f"Error Digital: {e}")
        
    return False

if __name__ == "__main__":
    if final_test_real():
        print("\n🏆 VERDICT: REAL MARKET IS OPEN FOR BUSINESS!")
    else:
        print("\n🛑 VERDICT: Still Blocked/Closed on Real Market.")
