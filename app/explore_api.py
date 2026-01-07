from iqoptionapi.stable_api import IQ_Option
from app.config import EMAIL, PASSWORD, DEFAULT_ASSET
import time

def explore():
    print("Connecting...")
    api = IQ_Option(EMAIL, PASSWORD)
    api.connect()
    
    # 1. Check Traders Mood (Sentiment)
    print(f"\n--- Traders Mood for {DEFAULT_ASSET} ---")
    api.start_mood_stream(DEFAULT_ASSET)
    time.sleep(2)
    mood = api.get_traders_mood(DEFAULT_ASSET)
    print(f"Sentiment: {mood}") # expect dict like {client dict} or float code
    api.stop_mood_stream(DEFAULT_ASSET)
    
    # 2. Check Available Instruments/Profile
    # print("\n--- Profile Data ---")
    # print(api.get_profile_ansyc())
    
    # 3. Check Candle Keys (Raw)
    print("\n--- Raw Candle Keys ---")
    candles = api.get_candles(DEFAULT_ASSET, 60, 1, time.time())
    if candles:
        print(candles[0].keys())

if __name__ == "__main__":
    explore()
