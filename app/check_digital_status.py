from app.connection import IQConnector

def check_digital_open():
    connector = IQConnector()
    if not connector.connect(): return
    
    asset = "EURUSD"
    print(f"\n🔍 Checking Digital Options for {asset} (REAL)...")
    
    # get_all_open_time() has digital info
    open_time = connector.api.get_all_open_time()
    
    digital_data = open_time.get('digital', {})
    if asset in digital_data:
        asset_info = digital_data[asset]
        print(f"Status: {'OPEN' if asset_info.get('open') else 'CLOSED'}")
    else:
        print(f"{asset} not found in Digital list.")

if __name__ == "__main__":
    check_digital_open()
