from app.connection import IQConnector
import time

def test_otc_real_funded():
    print("🚀 Connecting to Real Account for OTC Test...")
    connector = IQConnector()
    if not connector.connect(): return
    
    connector.api.change_balance("REAL")
    
    asset = "EURUSD-OTC"
    print(f"🎯 Target: {asset} (OTC Market, Real Balance)")
    amount = 2000 # Smallest test
    
    print(f"\n💸 Attempting REAL OTC Buy ({amount} COP, Call, 1m)...")
    check, id = connector.api.buy(amount, asset, "call", 1)
    
    if check:
        print(f"✅ SUCCESS! OTC Real Trade Accepted. ID: {id}")
    else:
        print(f"❌ REJECTED. Result: {check}")

if __name__ == "__main__":
    test_otc_real_funded()
