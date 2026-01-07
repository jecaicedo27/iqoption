from iqoptionapi.stable_api import IQ_Option
from app.config import EMAIL, PASSWORD

def test_otc():
    print("Connecting...")
    api = IQ_Option(EMAIL, PASSWORD)
    api.connect()
    api.change_balance("PRACTICE")
    
    bal = api.get_balance()
    print(f"💰 Current Balance: {bal}")
    
    asset = "EURUSD-OTC"
    amount = 10
    
    print(f"\nTesting Buy CALL on {asset} (1m)...")
    check, id = api.buy(amount, asset, "call", 1)
    if check:
        print(f"✅ SUCCESS: {asset} Buy ID: {id}")
    else:
        print(f"❌ FAILED: {asset}. Result: {id}")

if __name__ == "__main__":
    test_otc()
