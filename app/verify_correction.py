import pandas as pd
import numpy as np
from tensorflow.keras.models import load_model
import joblib
import requests
import io
import os
import sys

# Configuration
THRESHOLD = 0.51
SEQ_LEN = 10

def load_data_json(query):
    r = requests.get("http://localhost:9000/exec", params={"query": query})
    if r.status_code == 200:
        data = r.json()
        return pd.DataFrame(data['dataset'], columns=[c['name'] for c in data['columns']])
    return pd.DataFrame()

def verify():
    print("🧠 Loading Model & Scaler...")
    try:
        model = load_model("model_quest_24h.keras")
        scaler = joblib.load("scaler_quest.pkl")
    except Exception as e:
        print(f"❌ Load Error: {e}")
        return

    # 1. Get failed trade timestamps
    df_losses = load_data_json("SELECT timestamp, prediction FROM trades_memory WHERE result = 'LOSS'")
    df_losses['timestamp'] = pd.to_datetime(df_losses['timestamp'])
    
    # 2. Get market data
    df_market = load_data_json("SELECT timestamp, close, volume, rsi FROM market_training ORDER BY timestamp ASC")
    df_market['timestamp'] = pd.to_datetime(df_market['timestamp'])
    
    # Stationary Features
    df_market['hour'] = df_market['timestamp'].dt.hour
    df_market['minute'] = df_market['timestamp'].dt.minute
    df_market['hour_sin'] = np.sin(2 * np.pi * df_market['hour'] / 24)
    df_market['hour_cos'] = np.cos(2 * np.pi * df_market['hour'] / 24)
    df_market['min_sin'] = np.sin(2 * np.pi * df_market['minute'] / 60)
    df_market['min_cos'] = np.cos(2 * np.pi * df_market['minute'] / 60)
    df_market['price_pct'] = df_market['close'].pct_change()
    df_market['vol_pct'] = df_market['volume'].pct_change()
    df_market.fillna(0, inplace=True)
    
    feature_cols = ['price_pct', 'vol_pct', 'rsi', 'hour_sin', 'hour_cos', 'min_sin', 'min_cos']
    data_scaled = scaler.transform(df_market[feature_cols].values)
    
    results = []
    
    print(f"🔍 Checking {len(df_losses)} specific moments...")
    
    for idx_loss, row_loss in df_losses.iterrows():
        # Find index in market data
        # Allow 15s tolerance
        matches = df_market[
            (df_market['timestamp'] >= row_loss['timestamp'] - pd.Timedelta(seconds=15)) & 
            (df_market['timestamp'] <= row_loss['timestamp'] + pd.Timedelta(seconds=15))
        ]
        
        if matches.empty: continue
        
        idx_market = matches.index[-1]
        
        if idx_market < SEQ_LEN: continue
        
        # Prepare sequence
        seq = data_scaled[idx_market - SEQ_LEN + 1 : idx_market + 1]
        if len(seq) < SEQ_LEN: continue
        
        input_seq = np.reshape(seq, (1, SEQ_LEN, len(feature_cols)))
        prob_up = model.predict(input_seq, verbose=0)[0][0]
        
        # Outcome: Did it go up 1 min later?
        current_close = df_market.iloc[idx_market]['close']
        future_idx = idx_market + 4
        if future_idx >= len(df_market): continue
        future_close = df_market.iloc[future_idx]['close']
        
        reality = "UP" if future_close > current_close else "DOWN/STAY"
        new_decision = "WAIT"
        if prob_up > THRESHOLD: new_decision = "CALL"
        elif prob_up < (1.0 - THRESHOLD): new_decision = "PUT"
        
        won_now = False
        if new_decision == "CALL" and reality == "UP": won_now = True
        if new_decision == "PUT" and reality == "DOWN/STAY": won_now = True
        
        results.append({
            "Time": row_loss['timestamp'],
            "Reality": reality,
            "New Prob": f"{prob_up:.4f}",
            "New Action": new_decision,
            "Fixed?": "✅ YES (Won)" if won_now else ("❌ NO (Lost again)" if new_decision != "WAIT" else "🛡️ SKIPPED (Wait)"),
            "Old Action": row_loss['prediction']
        })
        
    res_df = pd.DataFrame(results)
    print("\n" + "="*80)
    print("🎯 RE-PREDICTION RESULTS ON PREVIOUS FAILURES")
    print("="*80)
    print(res_df.to_string(index=False))
    
    fixed_count = sum(1 for r in results if "YES" in r['Fixed?'])
    skipped_count = sum(1 for r in results if "SKIPPED" in r['Fixed?'])
    failed_again = sum(1 for r in results if "NO" in r['Fixed?'])
    
    print(f"\nSummary: Fixed: {fixed_count} | Lost Again: {failed_again} | Filtered Out: {skipped_count}")

if __name__ == "__main__":
    verify()
