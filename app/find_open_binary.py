from iqoptionapi.stable_api import IQ_Option
from app.config import EMAIL, PASSWORD

def find_open():
    print("Connecting...")
    api = IQ_Option(EMAIL, PASSWORD)
    api.connect()
    
    print("Fetching Payouts (Profit %)...")
    # This returns a dict { 'Asset': payout_float, ... }
    # e.g. 'EURUSD': 87
    profits = api.get_all_profit()
    
    open_assets = []
    
    for asset, data in profits.items():
        # data is defaultdict with 'binary'/'turbo'
        try:
            payout = data.get('binary', 0)
            turbo_payout = data.get('turbo', 0)
            
            # Prefer 5min+ (Binary)
            if payout > 0:
                print(f"✅ {asset}: Binary {int(payout*100)}% | Turbo {int(turbo_payout*100)}%")
                open_assets.append((asset, payout))
            elif turbo_payout > 0:
                 print(f"⚡ {asset}: Turbo {int(turbo_payout*100)}% (Binary Closed)")
        except:
            pass
            
    if not open_assets:
        print("❌ No assets returned positive payout.")
    else:
        # Suggest best one
        best = max(open_assets, key=lambda x: x[1])
        print(f"\n🏆 Best Asset: {best[0]} ({best[1]}%)")

if __name__ == "__main__":
    find_open()
