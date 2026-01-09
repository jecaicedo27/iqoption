from iqoptionapi.stable_api import IQ_Option
from app.config import EMAIL, PASSWORD

api = IQ_Option(EMAIL, PASSWORD)
api.connect()
api.update_ACTIVES_OPCODE()

print("🔍 Searching for EURUSD OTC variants...")

all_assets = api.get_all_ACTIVES_OPCODE()

for name, id in all_assets.items():
    if "EUR" in name and "USD" in name:
        print(f"👉 Found: {name} (ID: {id})")

print("\n🔍 Checking Opened Pairs:")
actives = api.get_all_open_time()
try:
    for type_name, assets in actives.items():
        print(f"\nType: {type_name}")
        for asset, data in assets.items():
            if "EUR" in asset and "USD" in asset and data['open']:
                print(f"✅ OPEN: {asset}")
except:
    pass
