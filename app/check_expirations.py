from app.connection import IQConnector
import time
from datetime import datetime

def check_structure():
    print("Connecting...")
    connector = IQConnector()
    if not connector.connect(): return

    asset = "EURUSD"
    print(f"\n🔍 INSPECTING {asset} (Real Market)...")
    
    # Check Turbo (1-5 min) Profit/Availability
    print("\n--- TURBO (1-5 min) ---")
    try:
        turbo_p = connector.api.get_all_profit()
        if asset in turbo_p:
            print(f"Profit Info: {turbo_p[asset]}")
        else:
            print("No Turbo Profit info found.")
            
        # Try to get initialization data which usually contains active expirations
        # Or simpler: try to 'get_binary_option_detail' equivalent if available
    except Exception as e:
        print(f"Error checking Turbo: {e}")
        
    print("\n--- BINARY (>15 min usually, but checking all) ---")
    try:
        bin_p = connector.api.get_all_profit()
        # Sometimes key is just EURUSD, logic is internal.
        # Let's check specifics directly via a 'buy' dry-run or get_option_open_by_asset
    except:
        pass

    # CRITICAL: Check Real-time available expirations
    print("\n--- REAL-TIME EXPIRATIONS ---")
    try:
        # This function updates internal expiration list
        connector.api.update_ACTIVES_OPCODE()
        
        # There isn't a simple public "get_expirations" in stable_api usually, 
        # but we can try to deduce from initialization or open times.
        
        # Let's try to see if 'turbo' holds the data
        all_open = connector.api.get_all_open_time()
        if 'turbo' in all_open and asset in all_open['turbo']:
            print(f"Turbo Schedule: {all_open['turbo'][asset]['open']}")
        else:
            print("Turbo Schedule: Not found/Closed")
            
        if 'binary' in all_open and asset in all_open['binary']:
            print(f"Binary Schedule: {all_open['binary'][asset]['open']}")
        else:
            print("Binary Schedule: Not found/Closed")
            
    except Exception as e:
        print(f"Error checking expirations: {e}")

if __name__ == "__main__":
    check_structure()
