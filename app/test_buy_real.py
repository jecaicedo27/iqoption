from iqoptionapi.stable_api import IQ_Option
from app.config import EMAIL, PASSWORD

def test_buy():
    print("Connecting...")
    api = IQ_Option(EMAIL, PASSWORD)
    api.connect()
    api.change_balance("PRACTICE")
    
    asset = "EURJPY"
    amount = 10
    
    print(f"\nTesting Buy CALL on {asset} (1m)...")
    check, id = api.buy(amount, asset, "call", 1)
    if check:
        print(f"✅ SUCCESS: {asset} Buy ID: {id}")
    else:
        print(f"❌ FAILED: {asset}. Result: {id}")
        
    print(f"\nTesting Buy CALL on {asset} (5m)...")
    check2, id2 = api.buy(amount, asset, "call", 5)
    if check2:
            print(f"✅ SUCCESS 5m: {asset} Buy ID: {id2}")
    else:
            print(f"❌ FAILED 5m: {asset}")

if __name__ == "__main__":
    test_buy()
