from app.connection import IQConnector
import json

def find_any_real_enabled():
    connector = IQConnector()
    if not connector.connect(): return
    
    print("Fetching Binary details...")
    try:
        data = connector.api.get_binary_option_detail()
        
        # Structure: {'EURUSD': {'turbo': True, 'binary': True}, ...}
        if not data:
             print("No global binary details returned.")
             return
             
        found = []
        for name, types in data.items():
            if "-OTC" not in name:
                # types is a dict like {'turbo': {...}, 'binary': {...}}
                asset_id = "N/A"
                for t in types:
                    if isinstance(types[t], dict) and 'id' in types[t]:
                        asset_id = types[t]['id']
                        break
                
                print(f"Asset: {name} | ID: {asset_id}")
                if types.get('turbo') or types.get('binary'):
                    found.append((name, asset_id))
        
        print(f"\nFound {len(found)} non-OTC enabled assets.")
        return found
        
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    find_any_real_enabled()
