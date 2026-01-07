from app.connection import IQConnector
from app.data_manager import DataManager

def main():
    # 1. Test Connection
    connector = IQConnector()
    if not connector.connect():
        print("Exiting...")
        return

    # 2. Get Balance
    balance = connector.get_balance()
    print(f"Current Balance: {balance}")

    # 3. Test Data Fetching
    dm = DataManager(connector.api)
    candles = dm.get_candles(amount=5)
    
    if candles:
        print("\nLast 5 Candles:")
        for candle in candles:
            print(f"Time: {candle['from']}, Close: {candle['close']}")
    else:
        print("Failed to fetch candles.")

if __name__ == "__main__":
    main()
