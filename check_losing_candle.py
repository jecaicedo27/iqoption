from iqoptionapi.stable_api import IQ_Option
from app.config import EMAIL, PASSWORD
import time
import pandas as pd

def check_candle():
    api = IQ_Option(EMAIL, PASSWORD)
    api.connect()
    # 08:31 EST (13:31 UTC) is 1767792660
    # Let's get candles from 08:30 to 08:33
    ts = 1767792660 + 120 # Current minute is around 08:32
    candles = api.get_candles('EURUSD-op', 60, 5, ts)
    if candles:
        df = pd.DataFrame(candles)
        df['time_est'] = pd.to_datetime(df['from'], unit='s').dt.tz_localize('UTC').dt.tz_convert('America/New_York')
        print(df[['time_est', 'open', 'close', 'high', 'low', 'volume']])
    else:
        print("No data")

if __name__ == "__main__":
    check_candle()
