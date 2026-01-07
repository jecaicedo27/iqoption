from app.connection import IQConnector
import time
from datetime import datetime, timedelta

def safe_digital_buy():
    connector = IQConnector()
    if not connector.connect(): return
    
    connector.api.change_balance("REAL")
    
    active = "EURUSD"
    amount = 5000
    action = "C" # Call
    duration = 1
    
    # Manually calculate instrument_id to avoid the hang
    timestamp = int(connector.api.api.timesync.server_timestamp)
    # Simplified exp calculation for 1m
    exp = (timestamp // 60) * 60 + 60
    
    dateFormated = str(datetime.utcfromtimestamp(exp).strftime("%Y%m%d%H%M"))
    instrument_id = "do" + active + dateFormated + "PT" + str(duration) + "M" + action + "SPT"
    
    print(f"💸 Attempting SAFE DIGITAL Buy: {instrument_id}")
    
    connector.api.api.digital_option_placed_id = None
    connector.api.api.place_digital_option(instrument_id, amount)
    
    start = time.time()
    while connector.api.api.digital_option_placed_id is None:
        if time.time() - start > 5:
            print("❌ TIMEOUT: No response for Digital Buy in 5s.")
            break
        time.sleep(0.1)
        
    result = connector.api.api.digital_option_placed_id
    print(f"Result: {result}")
    
    if result and not isinstance(result, int):
        print(f"Reason: {result}")

if __name__ == "__main__":
    safe_digital_buy()
