from app.connection import IQConnector
import csv
import time

DATA_FILE = "market_data_real.csv"
ASSET = "EURUSD" # Real

def collect_real():
    connector = IQConnector()
    if not connector.connect(): return
    
    end_time = time.time()
    all_candles = []
    needed = 10000
    
    print(f"Collecting {needed} REAL MARKET candles for {ASSET}...")
    
    while len(all_candles) < needed:
        print(f"Fetched {len(all_candles)}/{needed}...")
        candles = connector.api.get_candles(ASSET, 60, 1000, end_time)
        if not candles: break
        
        all_candles.extend(candles)
        end_time = candles[0]['from'] - 1
        time.sleep(1)
        
    all_candles.sort(key=lambda x: x['from'])
    
    headers = ['timestamp', 'open', 'close', 'min', 'max', 'volume']
    with open(DATA_FILE, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(headers)
        for c in all_candles:
            writer.writerow([c['from'], c['open'], c['close'], c['min'], c['max'], c['volume']])
            
    print(f"Saved {len(all_candles)} real candles to {DATA_FILE}")

if __name__ == "__main__":
    collect_real()
