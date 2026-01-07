import time
import pandas as pd
from iqoptionapi.stable_api import IQ_Option
from app.config import EMAIL, PASSWORD, DEFAULT_ASSET

def inspect_data():
    print("Connecting to IQ Option...")
    api = IQ_Option(EMAIL, PASSWORD)
    check, reason = api.connect()
    if not check:
        print(f"Error connecting: {reason}")
        return

    print(f"Fetching 15s candles for {DEFAULT_ASSET}...")
    # 15s timeframe = size 15? No, IQ Option API usually uses seconds for size.
    # Standard: 60 (1 min).
    # For 15s, size=15.
    
    # Let's fetch 20 candles
    candles = api.get_candles(DEFAULT_ASSET, 15, 20, time.time())
    
    if not candles:
        print("No candles received.")
        return

    df = pd.DataFrame(candles)
    # Convert 'from' (timestamp) to readable date
    df['date'] = pd.to_datetime(df['from'], unit='s')
    
    # Reorder columns for readability
    cols = ['date', 'open', 'close', 'min', 'max', 'volume', 'id']
    print(df[cols].to_markdown(index=False))
    
    # Verify Volume
    zero_vol = (df['volume'] == 0).sum()
    print(f"\nTotal Candles: {len(df)}")
    print(f"Candles with Zero Volume: {zero_vol}")
    
    if zero_vol == len(df):
        print("⚠️ WARNING: ALL candles have 0 volume. OTC Market limitation?")

if __name__ == "__main__":
    inspect_data()
