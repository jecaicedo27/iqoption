from app.connection import IQConnector

def check_balances():
    connector = IQConnector()
    if not connector.connect(): return
    
    print("\n💰 API BALANCES:")
    profile = connector.api.get_profile_ansyc()
    
    for balance in profile.get('balances', []):
        b_type = "REAL" if balance['type'] == 1 else "PRACTICE"
        print(f"[{b_type}] ID: {balance['id']} | Amount: {balance['amount']} {balance['currency']}")

if __name__ == "__main__":
    check_balances()
