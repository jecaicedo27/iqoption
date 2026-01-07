from app.connection import IQConnector
import iqoptionapi.constants as OP_code
import time
import json

def test_custom_id_real():
    connector = IQConnector()
    if not connector.connect(): return
    
    # Inject custom mapping
    OP_code.ACTIVES['EURUSD-op'] = 1861
    
    connector.api.change_balance("REAL")
    
    asset = "EURUSD-op"
    amount = 5000 # COD 5000
    
    print(f"\n💸 Attempting ADVANCED Buy using Custom ID ({asset} -> 1861)...")
    
    # Clear logs
    connector.api.api.buy_multi_option = {}
    
    check, id = connector.api.buy(amount, asset, "call", 1)
    
    print(f"Check: {check} | ID: {id}")
    
    if not check:
        buy_response = connector.api.api.buy_multi_option.get('buy', {})
        print("\n--- RAW WEBSOCKET RESPONSE ---")
        print(json.dumps(buy_response, indent=2))

if __name__ == "__main__":
    test_custom_id_real()
