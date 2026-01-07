from app.connection import IQConnector
import time
from datetime import datetime

def test_binary():
    print("🚀 Connecting to IQ Option (Binary Test)...")
    connector = IQConnector()
    if not connector.connect(): return

    # User screenshot showed AUD/CHF, but let's try EURUSD first if open, or AUDCHF
    # Note: Binary options usually expire at :00, :15, :30, :45
    asset = "EURUSD" 
    
    print(f"🎯 Target Asset: {asset}")
    
    print("🔍 Fetching Real-time Binary Expirations...")
    # connector.api.update_ACTIVES_OPCODE() # CAUSES ERROR 'underlying'
    
    # We need to find the "Binary" option expiration timestamp
    # It's usually a UNIX timestamp (int)
    
    # Let's try to calculate it manually first (Next 15 min slot)
    # E.g. if now is 9:22, next is 9:30.
    now = datetime.now()
    minutes = now.minute
    # Round up to next 15
    next_15 = (minutes // 15 + 1) * 15
    if next_15 >= 60:
        next_15 = 0
        hour_add = 1
    else:
        hour_add = 0
        
    # Construct target time
    # This is rough. Better to get from API.
    
    # try: 
    #     available = connector.api.get_all_open_time()
    # except: pass
        
    try:
        # EXPERIMENTAL: buyv3_by_raw_expired requires 'option' type and 'expired' timestamp
        # Let's try 15 min from standard buy with specific option string
        
        print("💸 Attempting Raw Binary Buy (15m)...")
        # option="binary" ?? or "turbo"?
        # EURUSD is Real used "binary" in the screenshot
        
        # Calculate strict timestamp for next quarter hour (00, 15, 30, 45)
        import time as t_mod
        now_ts = int(t_mod.time())
        remainder = 900 - (now_ts % 900) # 900s = 15m
        target_ts = now_ts + remainder
        
        print(f"   Target Timestamp: {target_ts} ({t_mod.ctime(target_ts)})")
        
        # params: price, active, direction, option, expired
        check, id = connector.api.buy_by_raw_expirations(1, asset, "call", "binary", target_ts)
        
        if check:
             print(f"✅ SUCCESS! Raw Binary Trade Placed. ID: {id}")
        else:
             print(f"❌ Failed Raw Binary. Trying 'turbo' type with long duration...")
             # Some binaries are technically 'turbo' if < 5m? No.
             check2, id2 = connector.api.buy_by_raw_expirations(1, asset, "call", "turbo", target_ts)
             if check2:
                 print(f"✅ SUCCESS! Turbo (Long) Trade Placed. ID: {id2}")
             else:
                 print("❌ Failed both methods.")

    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_binary()
