from app.connection import IQConnector
import time

def find_currently_open_real():
    connector = IQConnector()
    if not connector.connect(): return
    
    current_ts = int(time.time())
    print(f"Current TS: {current_ts} ({time.ctime(current_ts)})")
    
    print("Fetching Binary details...")
    try:
        data = connector.api.get_binary_option_detail()
        
        found = []
        for name, types in data.items():
            if "-OTC" in name: continue
            
            for t_name, info in types.items():
                if not info or not isinstance(info, dict): continue
                
                # Check status
                is_enabled = info.get('enabled', False)
                is_suspended = info.get('is_suspended', False)
                
                if is_enabled and not is_suspended:
                    # Check schedule
                    schedule = info.get('schedule', [])
                    is_in_schedule = False
                    for start, end in schedule:
                        if start <= current_ts <= end:
                            is_in_schedule = True
                            break
                    
                    if is_in_schedule:
                        print(f"✅ FOUND OPEN: {name} [{t_name}]")
                        found.append((name, t_name))
        
        if not found:
            print("\n❌ No non-OTC assets are currently within their trading schedule.")
        else:
            print(f"\nTotal open: {len(found)}")
            
        return found
        
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    find_currently_open_real()
