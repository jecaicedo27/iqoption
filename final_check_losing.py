from iqoptionapi.stable_api import IQ_Option
from app.config import EMAIL, PASSWORD
import time
import pandas as pd

def check():
    api = IQ_Option(EMAIL, PASSWORD)
    api.connect()
    # 08:31:00 EST is 1767789060? No.
    # From Step 6915: index 58 from=1767792600 (08:30), index 59 from=1767792660 (08:31)
    # The candle 08:31 is 1767792660. 
    # Let's get candles around that time.
    for _ in range(5):
        candles = api.get_candles('EURUSD-op', 60, 5, 1767792660 + 300)
        if candles:
            df = pd.DataFrame(candles)
            df['time'] = pd.to_datetime(df['from'], unit='s').dt.tz_localize('UTC').dt.tz_convert('America/New_York')
            print(df[['time', 'open', 'close', 'high', 'low']])
            return
        time.sleep(2)
    print("Failed to get data after 5 attempts")

if __name__ == "__main__":
    check()
