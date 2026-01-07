from iqoptionapi.stable_api import IQ_Option
from app.config import EMAIL, PASSWORD
import time
import pandas as pd
import numpy as np

def calculate_rsi(series, period=14):
    delta = series.diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
    rs = gain / loss
    return 100 - (100 / (1 + rs))

def scan_real():
    print("Connecting...")
    api = IQ_Option(EMAIL, PASSWORD)
    check, reason = api.connect() # Check result
    if not check:
        print(f"❌ Connection Failed: {reason}")
        return

    # 1. Get Payouts
    profits = api.get_all_profit()
    candidates = []
    
    print("\n🔍 Scanning REAL Markets (Payout > 70%)...")
    for asset, data in profits.items():
        # Exclude OTC
        if "-OTC" in asset:
            continue
            
        try:
            payout = data.get('binary', 0)
            turbo = data.get('turbo', 0)
            best_payout = max(payout, turbo)
             
            if best_payout > 0.70:
                candidates.append((asset, best_payout))
        except:
            pass
            
    # Sort by Payout descending
    candidates.sort(key=lambda x: x[1], reverse=True)
    
    # Limit to Top 10 to avoid blasting API
    candidates = candidates[:10]

    print(f"Found {len(candidates)} candidates (Top 10). Checking liveness...")
    
    valid_opportunities = []
    
    for asset, payout in candidates:
        time.sleep(1) # Sleep to avoid rate limit
        try:
            print(f"Checking {asset}...")
            # Fetch 10 candles (15s)
            candles = api.get_candles(asset, 15, 60, time.time())
            
            if not candles:
                continue
                
            last_candle = candles[-1]
            last_ts = last_candle['from']
            
            # Check if fresh (within last 2 mins)
            if time.time() - last_ts > 120:
                print(f"Assigning {asset}: Stale data (Closed?). Last: {time.ctime(last_ts)}")
                continue
                
            # Convert to DF for Indicators
            df = pd.DataFrame(candles)
            df['close'] = df['close'].astype(float)
            
            # Simple RSI
            df['rsi'] = calculate_rsi(df['close'], period=14)
            last_rsi = df['rsi'].iloc[-1]
            
            # Volatility check
            volatility = df['close'].std()
            
            print(f"✅ {asset} ({int(payout*100)}%): Alive. RSI={last_rsi:.1f} Vol={volatility:.5f}")
            
            # Heuristic Opportunity
            signal = "NEUTRAL"
            if last_rsi < 30: signal = "OVERSOLD (CALL?)"
            elif last_rsi > 70: signal = "OVERBOUGHT (PUT?)"
            
            if not np.isnan(last_rsi):
                valid_opportunities.append({
                    "Asset": asset,
                    "Payout": int(payout*100),
                    "RSI": round(last_rsi, 2),
                    "Signal": signal
                })
                
        except Exception as e:
            print(f"Error checking {asset}: {e}")
            
    # Sort by Opportunity (Extreme RSI)
    valid_opportunities.sort(key=lambda x: abs(x['RSI'] - 50), reverse=True)
    
    print("\n\n🏆 --- TOP REAL OPPORTUNITIES ---")
    if not valid_opportunities:
        print("No active real markets found (all stale/closed).")
    else:
        for opp in valid_opportunities:
            print(f"🔥 {opp['Asset']} [{opp['Payout']}%] | RSI: {opp['RSI']} -> {opp['Signal']}")

if __name__ == "__main__":
    scan_real()
