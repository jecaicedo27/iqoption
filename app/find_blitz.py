from iqoptionapi.stable_api import IQ_Option
from app.config import EMAIL, PASSWORD

def find_blitz():
    print("Connecting...")
    api = IQ_Option(EMAIL, PASSWORD)
    api.connect()
    
    print("Searching for 'Blitz' or 'EUR/USD' assets...")
    all_assets = api.get_all_init()
    
    # Iterate through all interesting categories
    # usually inside 'result' -> 'turbo' or 'binary'
    found = []
    
    # Inspecting all instruments
    # Use get_all_open_time logic to see what is open too
    print("Fetching ALL Actives via OPCODE list...")
    # This usually works even if open_time fails
    actives = api.get_all_ACTIVES_OPCODE()
    
    # actives is dict: {id: 'ticker', ...} or similar? 
    # Actually it is {opcode: 'ticker'} ??
    # Let's verify structure by printing a few
    
    print(f"Total Actives in list: {len(actives)}")
    
    # Print first 20 items to see structure
    i = 0
    for k, v in actives.items():
        print(f"Sample: {k} -> {v}")
        i += 1
        if i > 20: break
            
    print(f"Total Matches: {found_count}")

if __name__ == "__main__":
    find_blitz()
