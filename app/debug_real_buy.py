from app.connection import IQConnector
import time
import json

def debug_real_buy():
    connector = IQConnector()
    if not connector.connect(): return
    
    # Switch to REAL
    connector.api.change_balance("REAL")
    
    asset = "BTCUSD"
    amount = 5000 # 5000 COP
    
    print(f"\n💸 Attempting DEBUG REAL Buy ({asset}, {amount} COP, Call, 1m)...")
    
    # We'll use the internal send_websocket method if possible to see everything
    # or just monitor the api_dict
    
    # 1. Clear previous buy info
    connector.api.api.buy_multi_option = {}
    
    check, id_or_msg = connector.api.buy(amount, asset, "call", 1)
    
    print(f"Check: {check} | ID/Msg: {id_or_msg}")
    
    # Inspect the full response if check failed
    if not check:
        buy_response = connector.api.api.buy_multi_option.get('buy', {})
        print("\n--- RAW WEBSOCKET RESPONSE ---")
        print(json.dumps(buy_response, indent=2))

if __name__ == "__main__":
    debug_real_buy()
