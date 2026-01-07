from app.connection import IQConnector

def check_balance():
    connector = IQConnector()
    if not connector.connect(): return
    
    # Get Balance
    bal = connector.api.get_balance()
    print(f"Current Balance: ${bal}")
    
    # Get recent trades? (Hard to track P/L without local DB, but balance diff helps)
    # We can check profit of specific id if needed, but balance is easiest snapshot.

if __name__ == "__main__":
    check_balance()
