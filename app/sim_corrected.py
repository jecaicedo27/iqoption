import pandas as pd
import numpy as np
from tensorflow.keras.models import load_model
import pickle
import requests
import os
import sys

# Configuration
THRESHOLD = 0.51 # Consistent with previous successful run
SEQ_LEN = 10

def load_data_json(query):
    print(f"📡 Querying JSON: {query[:50]}...")
    try:
        r = requests.get("http://localhost:9000/exec", params={"query": query})
        if r.status_code == 200:
            data = r.json()
            if 'dataset' in data:
                return pd.DataFrame(data['dataset'], columns=[c['name'] for c in data['columns']])
            else:
                return pd.DataFrame()
        else:
            print(f"❌ DB Error: {r.text}")
            return pd.DataFrame()
    except Exception as e:
        print(f"❌ Connection Error: {e}")
        return pd.DataFrame()

def simulate():
    # 1. Load Model & Data
    print("🧠 Loading Corrected Model & Data...")
    try:
        model = load_model("model_quest_24h.keras")
    except Exception as e:
        print(f"❌ Model Load Error: {e}")
        return

    df = load_data_json("SELECT timestamp, close, volume, rsi FROM market_training ORDER BY timestamp DESC LIMIT 6000")
    if df.empty: return
    
    df['timestamp'] = pd.to_datetime(df['timestamp'])
    df = df.sort_values('timestamp').reset_index(drop=True)
    
    # Time Features
    df['hour'] = df['timestamp'].dt.hour
    df['minute'] = df['timestamp'].dt.minute
    df['hour_sin'] = np.sin(2 * np.pi * df['hour'] / 24)
    df['hour_cos'] = np.cos(2 * np.pi * df['hour'] / 24)
    df['min_sin'] = np.sin(2 * np.pi * df['minute'] / 60)
    df['min_cos'] = np.cos(2 * np.pi * df['minute'] / 60)
    
    feature_cols = ['close', 'volume', 'rsi', 'hour_sin', 'hour_cos', 'min_sin', 'min_cos']
    
    # Scaler re-fit (bypass corrupted pkl)
    from sklearn.preprocessing import MinMaxScaler
    data = df[feature_cols].values
    scaler = MinMaxScaler()
    data_scaled = scaler.fit_transform(data)
    
    # 3. Predict
    X = []
    for i in range(len(data_scaled) - SEQ_LEN):
        X.append(data_scaled[i : i + SEQ_LEN])
    X = np.array(X)
    
    print(f"🔮 Backtesting on {len(X)} sequences...")
    probs = model.predict(X, verbose=0)
    
    total_trades = 0
    wins = 0
    losses = 0
    calls = 0
    puts = 0
    
    for i, prob_up in enumerate(probs):
        idx = i + SEQ_LEN
        if idx + 4 >= len(df): continue # Need 1 min outcome
        
        current_close = df.iloc[idx]['close']
        future_close = df.iloc[idx + 4]['close']
        
        action = None
        if prob_up > THRESHOLD:
            action = "CALL"
            calls += 1
        elif prob_up < (1.0 - THRESHOLD):
            action = "PUT"
            puts += 1
            
        if action:
            total_trades += 1
            win = False
            if action == "CALL" and future_close > current_close: win = True
            if action == "PUT" and future_close < current_close: win = True
            
            if win: wins += 1
            else: losses += 1
            
    # 4. Results
    print("\n" + "="*30)
    print("📈 CORRECTED MODEL PERFORMANCE")
    print("="*30)
    print(f"Total Trades: {total_trades}")
    print(f"CALLs: {calls} | PUTs: {puts}")
    print(f"Wins: {wins} | Losses: {losses}")
    if total_trades > 0:
        win_rate = (wins / total_trades) * 100
        print(f"🏆 Win Rate: {win_rate:.2f}%")
    print("="*30)

if __name__ == "__main__":
    simulate()
