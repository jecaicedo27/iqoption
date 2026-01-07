import pandas as pd
import numpy as np
from tensorflow.keras.models import load_model
import joblib
import requests
import os
import sys

# Configuration
SEQUENCE_LENGTH = 10
THRESHOLDS = [0.51, 0.52, 0.53, 0.54, 0.55, 0.56, 0.57, 0.58, 0.59, 0.60]

def load_data():
    import requests
    query = "SELECT * FROM market_training ORDER BY timestamp ASC"
    r = requests.get("http://localhost:9000/exec", params={"query": query})
    if r.status_code == 200:
        data = r.json()
        df = pd.DataFrame(data['dataset'], columns=[c['name'] for c in data['columns']])
        df['timestamp'] = pd.to_datetime(df['timestamp'])
        return df
    return pd.DataFrame()

def run_multi_simulation():
    print("🧠 Loading Model & Data...")
    try:
        model = load_model("model_quest_24h.keras")
        scaler = joblib.load("scaler_quest.pkl")
    except Exception as e:
        print(f"❌ Load Error: {e}")
        return

    df = load_data()
    if df.empty: return
    
    # Feature Engineering
    df['hour'] = df['timestamp'].dt.hour
    df['minute'] = df['timestamp'].dt.minute
    df['hour_sin'] = np.sin(2 * np.pi * df['hour'] / 24)
    df['hour_cos'] = np.cos(2 * np.pi * df['hour'] / 24)
    df['min_sin'] = np.sin(2 * np.pi * df['minute'] / 60)
    df['min_cos'] = np.cos(2 * np.pi * df['minute'] / 60)
    
    df['price_pct'] = df['close'].pct_change()
    df['vol_pct'] = df['volume'].pct_change()
    df.fillna(0, inplace=True)
    
    feature_cols = ['price_pct', 'vol_pct', 'rsi', 'hour_sin', 'hour_cos', 'min_sin', 'min_cos']
    data = df[feature_cols].values
    data_scaled = scaler.transform(data)
    
    X = []
    indices = []
    for i in range(SEQUENCE_LENGTH, len(data_scaled)):
        X.append(data_scaled[i-SEQUENCE_LENGTH:i])
        indices.append(i)
    X = np.array(X)
    
    print(f"🔮 Predicting on {len(X)} sequences...")
    probs = model.predict(X, batch_size=1024, verbose=0)
    
    results = []
    
    for t in THRESHOLDS:
        total = 0
        wins = 0
        losses = 0
        
        for i, prob_up in enumerate(probs):
            idx = indices[i]
            future_idx = idx + 4
            if future_idx >= len(df): continue
            
            current_close = df.iloc[idx]['close']
            future_close = df.iloc[future_idx]['close']
            
            action = None
            if prob_up > t: action = "CALL"
            elif prob_up < (1.0 - t): action = "PUT"
            
            if action:
                total += 1
                is_win = (action == "CALL" and future_close > current_close) or \
                         (action == "PUT" and future_close < current_close)
                if is_win: wins += 1
                else: losses += 1
        
        win_rate = (wins / total * 100) if total > 0 else 0
        pnl = (wins * 86) - (losses * 100) # Assuming $100 bet and 86% payout
        results.append({
            "Threshold": f"{int(t*100)}%",
            "Trades": total,
            "Wins": wins,
            "Losses": losses,
            "WinRate": f"{win_rate:.2f}%",
            "PnL": f"${pnl:,}"
        })
        print(f"✅ Calculated for {int(t*100)}%")

    # Print Final Table
    report_df = pd.DataFrame(results)
    print("\n" + "="*50)
    print("📊 MULTI-THRESHOLD SIMULATION REPORT")
    print("="*50)
    print(report_df.to_string(index=False))
    print("="*50)

if __name__ == "__main__":
    run_multi_simulation()
