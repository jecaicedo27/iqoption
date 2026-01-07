from iqoptionapi.stable_api import IQ_Option
from app.config import EMAIL, PASSWORD
import json

def search_blitz():
    print("Connecting...")
    api = IQ_Option(EMAIL, PASSWORD)
    api.connect()
    
    print("Getting Init Config...")
    config = api.get_all_init()
    
    # Dump to string and search
    config_str = json.dumps(config)
    
    if "Blitz" in config_str or "blitz" in config_str or "BLITZ" in config_str:
        print("✅ FOUND 'Blitz' in config!")
        # Try to find context (snippet)
        idx = config_str.lower().find("blitz")
        start = max(0, idx - 100)
        end = min(len(config_str), idx + 100)
        print(f"Context: ...{config_str[start:end]}...")
    else:
        print("❌ 'Blitz' NOT found in config.")

if __name__ == "__main__":
    search_blitz()
