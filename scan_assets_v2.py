from iqoptionapi.stable_api import IQ_Option
from app.config import EMAIL, PASSWORD
import time

api = IQ_Option(EMAIL, PASSWORD)
api.connect()

print("Updating opcodes...")
api.update_ACTIVES_OPCODE()
instruments = api.get_all_ACTIVES_OPCODE()

print("\n--- AVAILABLE ASSETS (Turbo/Binary) ---")

for asset_name, id in instruments.items():
    # Attempt to simply check if it's open by checking payout
    try:
        if "-op" in asset_name: # Only check OTC
            profit = api.get_all_profit()[asset_name]['turbo']
            if profit > 0:
                 print(f"✅ {asset_name} | Payout: {profit * 100}%")
    except:
        pass
