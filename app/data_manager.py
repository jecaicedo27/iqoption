import time
from app.config import DEFAULT_ASSET, DEFAULT_TIMEFRAME

class DataManager:
    def __init__(self, api):
        self.api = api

    def get_candles(self, asset=DEFAULT_ASSET, timeframe=DEFAULT_TIMEFRAME, amount=10):
        """
        Fetch historical candles.
        """
        print(f"Fetching {amount} candles for {asset}...")
        candles = self.api.get_candles(asset, timeframe * 60, amount, time.time())
        return candles

    def start_stream(self, asset=DEFAULT_ASSET):
        """
        Start real-time data stream for an asset.
        """
        self.api.start_candles_stream(asset, 60, 1)
        print(f"Started stream for {asset}")
