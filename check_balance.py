from iqoptionapi.stable_api import IQ_Option
from app.config import EMAIL, PASSWORD, ACCOUNT_TYPE

print(f"Connecting with {EMAIL} in {ACCOUNT_TYPE} mode...")
api = IQ_Option(EMAIL, PASSWORD)
check, reason = api.connect()

if check:
    api.change_balance(ACCOUNT_TYPE)
    bal = api.get_balance()
    currency = api.get_currency()
    print(f"✅ Connected. Balance ({ACCOUNT_TYPE}): {bal} {currency}")
else:
    print(f"❌ Connection Failed: {reason}")
