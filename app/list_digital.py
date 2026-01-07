from app.connection import IQConnector

def main():
    connector = IQConnector()
    if not connector.connect():
        return

    print("Fetching digital instruments...")
    # This might fail if the method name is different in this lib version
    try:
        instruments = connector.api.get_digital_instruments("USD")
        print("\n--- INSTRUMENTOS DIGITALES ---")
        for instrument in instruments:
            print(f"Name: {instrument}")
    except Exception as e:
        print(f"Error fetching digital: {e}")

if __name__ == "__main__":
    main()
