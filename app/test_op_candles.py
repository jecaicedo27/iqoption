from app.connection import IQConnector
import iqoptionapi.constants as OP_code
import time

def test_candles_op():
    connector = IQConnector()
    if not connector.connect(): return
    
    # Inject
    OP_code.ACTIVES['EURUSD-op'] = 1861
    
    print(f"🔍 Fetching Candles for EURUSD-op (ID: 1861)...")
    
    # Try 15s candles
    candles = connector.api.get_candles("EURUSD-op", 15, 10, time.time())
    
    if candles:
        print(f"✅ SUCCESS! Fetched {len(candles)} candles.")
        print(f"Latest Candle: {candles[-1]}")
    else:
        print("❌ Failed to fetch candles.")

if __name__ == "__main__":
    test_candles_op()
