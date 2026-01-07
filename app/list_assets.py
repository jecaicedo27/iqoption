from app.connection import IQConnector

def main():
    connector = IQConnector()
    if not connector.connect():
        return

    print("Fetching all open assets...")
    # Get all actives
    alls = connector.api.get_all_ACTIVES_OPCODE()
    
    # Filter for OTC or known pairs
    print("\n--- POSIBLES ACTIVOS ---")
    for name, id in alls.items():
        if "PEN" in name or "USD" in name:
            print(f"Name: {name} | ID: {id}")

if __name__ == "__main__":
    main()
