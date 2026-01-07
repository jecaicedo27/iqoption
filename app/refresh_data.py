from app.connection import IQConnector
import csv
import time
import os

DATA_FILE = "market_data_real.csv"
ASSET = "EURUSD" # Always learn on Real market for now

def refresh_data():
    connector = IQConnector()
    if not connector.connect(): return
    
    # Fetch latest 10000 candles to capture recent regime
    # Note: verify timeframe. Real market training was on 1m? Yes (default).
    
    end_time = time.time()
    all_candles = []
    needed = 10000
    
    print(f"🔄 Power Nap: Downloading latest {needed} candles from {ASSET}...")
    
    while len(all_candles) < needed:
        # print(f"Fetched {len(all_candles)}...")
        candles = connector.api.get_candles(ASSET, 60, 1000, end_time)
        if not candles: break
        
        all_candles.extend(candles)
        end_time = candles[0]['from'] - 1
        time.sleep(0.5)
        
    all_candles.sort(key=lambda x: x['from'])
    
    # Overwrite CSV
    headers = ['timestamp', 'open', 'close', 'min', 'max', 'volume']
    with open(DATA_FILE, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(headers)
        for c in all_candles:
            writer.writerow([c['from'], c['open'], c['close'], c['min'], c['max'], c['volume']])
            
    print(f"✅ Data Refreshed! {len(all_candles)} candles ready for training.")

if __name__ == "__main__":
    refresh_data()
