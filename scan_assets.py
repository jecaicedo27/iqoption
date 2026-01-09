from iqoptionapi.stable_api import IQ_Option
from app.config import EMAIL, PASSWORD
import time

api = IQ_Option(EMAIL, PASSWORD)
api.connect()

print("Scanning for open Binary options (>80% Profit)...")

actives = api.get_all_open_time()

print("\n--- OPEN ASSETS ---")

found = False
for asset_name, data in actives['turbo'].items():
    if data['open']:
        # Check payout
        profit = api.get_commission_change_percentage(asset_name)(1, 'turbo')
        
        # Filter for logic assets
        if "-op" in asset_name and profit >= 80:
            print(f"✅ {asset_name} | Payout: {profit}%")
            found = True

if not found:
    print("❌ No high-payout OTC assets found.")
    # Check regular binary
    print("\nChecking Non-Turbo Binary:")
    for asset_name, data in actives['binary'].items():
        if data['open']:
             if "-op" in asset_name:
                print(f"✅ {asset_name} (Binary)")

