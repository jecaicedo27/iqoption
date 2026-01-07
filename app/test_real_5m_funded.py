from app.connection import IQConnector
import time

def test_real_binary_5m():
    print("🚀 Connecting to Real Account for 5m Test...")
    connector = IQConnector()
    if not connector.connect(): return
    
    # Switch to REAL balance if not already there
    connector.api.change_balance("REAL")
    
    asset = "EURUSD"
    print(f"🎯 Target: {asset} (Real Market)")
    amount = 5000 # 5000 COP
    
    print(f"\n💸 Attempting REAL Binary Buy ({amount} COP, Call, 5m)...")
    check, id = connector.api.buy(amount, asset, "call", 5)
    
    if check:
        print(f"✅ SUCCESS! 5-min Real Trade Accepted. ID: {id}")
    else:
        print(f"❌ REJECTED. Result: {check}")
        # Try to find reason in websocket client
        # This is a bit hacky but often helps
        # last_response = connector.api.api.websocket_client.api_dict.get('buy_complete', 'N/A')
        # print(f"Last API Response: {last_response}")

if __name__ == "__main__":
    test_real_binary_5m()
