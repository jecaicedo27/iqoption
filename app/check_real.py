from app.connection import IQConnector
import time

def check_real_data():
    connector = IQConnector()
    if not connector.connect(): return
    
    print("\n🔍 Checking Market Correctness...")
    
def check_real_data():
    connector = IQConnector()
    if not connector.connect(): return
    
    print("\n🔍 Checking Market Correctness (Candle Freshness Test)...")
    
    current_time = time.time()
    
    def check_asset(asset_name):
        # Fetch last 3 candles
        try:
            candles = connector.api.get_candles(asset_name, 60, 3, current_time)
            if not candles: return False, "No Data"
            
            last_candle_time = candles[-1]['from']
            diff = current_time - last_candle_time
            
            # If last candle is older than 5 minutes, market is likely closed
            if diff < 300: # 5 minutes
                return True, f"Active (Lag: {int(diff)}s)"
            else:
                return False, f"Stale (Last: {time.ctime(last_candle_time)})"
        except Exception as e:
            return False, f"Error: {e}"

    # Check EURUSD
    real_ok, real_msg = check_asset("EURUSD")
    print(f"💶 EURUSD (Real): {'✅ OPEN' if real_ok else '❌ CLOSED'} -> {real_msg}")
    
    # Check EURUSD-OTC
    otc_ok, otc_msg = check_asset("EURUSD-OTC")
    print(f"🎰 EURUSD-OTC:    {'✅ OPEN' if otc_ok else '❌ CLOSED'}  -> {otc_msg}")
    
    print("-" * 30)
    if real_ok:
        print("💡 RECOMMENDATION: Switch to Real Market (EURUSD).")
    else:
        print("💡 RECOMMENDATION: Stay on OTC (EURUSD-OTC).")

if __name__ == "__main__":
    check_real_data()
