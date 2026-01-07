import time
from iqoptionapi.stable_api import IQ_Option
from app.config import EMAIL, PASSWORD, ACCOUNT_TYPE

class IQConnector:
    def __init__(self):
        self.email = EMAIL
        self.password = PASSWORD
        self.account_type = ACCOUNT_TYPE
        self.api = None

    def connect(self):
        print(f"Connecting to {self.email}...")
        self.api = IQ_Option(self.email, self.password)
        check, reason = self.api.connect()
        
        if check:
            print("Successfully connected!")
            self.api.change_balance(self.account_type)  # "PRACTICE" / "REAL"
            return True
        else:
            print(f"Connection failed: {reason}")
            return False

    def get_balance(self):
        if self.api:
            return self.api.get_balance()
        return None

    def check_connection(self):
        if self.api and self.api.check_connect():
            return True
        return False
