from app.connection import IQConnector
import sys

def main():
    connector = IQConnector()
    if not connector.connect():
        sys.exit(1)
        
    print("Testing Buy on EURUSD-OTC...")
    check, id = connector.api.buy(10, "EURUSD-OTC", "call", 1)
    if check:
        print(f"SUCCESS! Market Open. ID: {id}")
    else:
        print("FAILED to buy EURUSD-OTC")
        
    print("Testing Buy on BTCUSD...")
    check, id = connector.api.buy(10, "BTCUSD", "call", 1)
    if check:
        print(f"SUCCESS! BTC Binary. ID: {id}")
    else:
        print("FAILED to buy BTCUSD (Binary)")
        
    try:
        print("Testing Digital Start...")
        id = connector.api.buy_digital_spot("BTCUSD", 10, "call", 1)
        if id:
             print(f"SUCCESS! BTC Digital. ID: {id}")
        else:
             print("FAILED to buy BTCUSD (Digital)")
    except Exception as e:
        print(f"Digital Error: {e}")

if __name__ == "__main__":
    main()
