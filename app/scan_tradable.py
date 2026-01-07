from app.connection import IQConnector
import time

def scan_assets():
    print("🚀 Connecting to IQ Option for Asset Scan...")
    connector = IQConnector()
    if not connector.connect(): 
        print("❌ Connection Failed")
        return

    # Major Real Market Pairs (No OTC)
    targets = [
        "EURUSD", "GBPUSD", "USDJPY", "AUDUSD", "USDCAD", 
        "USDCHF", "NZDUSD", "EURJPY", "GBPJPY", "EURGBP",
        "AUDJPY", "CADJPY", "AUDCAD", "GBPCHF", "EURCAD"
    ]
    
    print(f"📋 Scanning {len(targets)} Real Market Assets with $1 Test Trades...")
    print("="*50)
    
    found_any = False
    
    for asset in targets:
        print(f"\n🔎 Testing: {asset} ...")
        
        # 1. Check if "Open" logically (Candles exist)
        candles = connector.api.get_candles(asset, 60, 1, time.time())
        if not candles:
            print(f"   ⚠️ No Data (Market Closed?)")
            continue
            
        # 2. Attempt $1 Trade (Turbo 1m)
        print(f"   💸 Attempting $1 Call (Turbo)...")
        check, order_id = connector.api.buy(1, asset, "call", 1)
        
        if check:
            print(f"   ✅ SUCCESS! Trade Accepted. ID: {order_id}")
            print(f"   🎉 FOUND TRADABLE ASSET: {asset}")
            found_any = True
            break 
        else:
            print(f"   ❌ Rejected (Turbo).")
            # Digital fallback removed to prevent hangs
            
        time.sleep(0.5) # Fast scan
        
    print("="*50)
    if not found_any:
        print("🛑 SCAN COMPLETE: No Tradable Real Market Assets found.")
        print("💡 Recommendation: Use OTC.")
    else:
        print("✅ SCAN COMPLETE: We have a winner.")

if __name__ == "__main__":
    scan_assets()
