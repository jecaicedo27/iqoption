from app.connection import IQConnector
import json

def list_all_real_assets():
    connector = IQConnector()
    if not connector.connect(): return
    
    # Update actives info
    print("Updating active list...")
    connector.api.update_ACTIVES_OPCODE()
    
    # Get all actives
    # 1: Binary (Turbo), 2: Binary (Binary), 3: Digital
    # But usually just get_all_open_time is more readable
    open_time = connector.api.get_all_open_time()
    
    print("\n--- NON-OTC BINARY ASSETS ---")
    binary = open_time.get('turbo', {}) # turbo is 1-5m
    real_binary = [a for a in binary if "-OTC" not in a]
    for a in real_binary:
        print(f"  {a}: {binary[a].get('open')}")
        
    print("\n--- NON-OTC DIGITAL ASSETS ---")
    digital = open_time.get('digital', {})
    real_digital = [a for a in digital if "-OTC" not in a]
    for a in real_digital:
        print(f"  {a}: {digital[a].get('open')}")

if __name__ == "__main__":
    list_all_real_assets()
