from app.connection import IQConnector
import time

def scan_common_pairs():
    connector = IQConnector()
    if not connector.connect(): return
    
    connector.api.change_balance("REAL")
    
    # Common pairs, Crypto, and others
    pairs = [
        "BTCUSD", "ETHUSD", "XRPUSD",
        "AAPL", "AMZN", "MSFT", "TSLA",
        "Gold", "CrudeOil",
        "US100", "US500"
    ]
    
    amount = 2000 # 2000 COP is roughly $0.5 USD, usually min is $1 or 4000 COP but let's try 4000 to be safe
    amount = 4000 
    
    print(f"\n🚀 SCANNING COMMON PAIRS (Amount: {amount} COP)...")
    
    for pair in pairs:
        print(f"\n[ {pair} ]")
        
        # Test Binary
        print("  Testing Binary 1m...")
        check, id = connector.api.buy(amount, pair, "call", 1)
        if check:
            print(f"  ✅ BINARY WORKED! ID: {id}")
            return pair, "BINARY"
        else:
            print("  ❌ Binary Rejected.")
            
    print("\n--- SCAN COMPLETE: NO ASSET FOUND ---")
    return None, None

if __name__ == "__main__":
    asset, mode = scan_common_pairs()
    if asset:
        print(f"\n💡 RECOMMENDATION: Use {asset} in {mode} mode.")
    else:
        print("\n💡 CONCLUSION: No common real market pair is currently open for API trading.")
