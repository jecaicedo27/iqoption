from app.connection import IQConnector
import time

def main():
    connector = IQConnector()
    if not connector.connect(): return
    
    print("Testing 5-second candle fetch...")
    # timeframe=5 means 5 seconds
    candles = connector.api.get_candles("EURUSD-OTC", 5, 20, time.time())
    
    if candles:
        print(f"Success! Got {len(candles)} candles.")
        print(f"Sample: {candles[-1]}")
    else:
        print("Failed to fetch 5s candles.")

if __name__ == "__main__":
    main()
