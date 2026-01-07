import pandas as pd
import numpy as np
import tensorflow as tf
from tensorflow import keras
from tensorflow.keras import layers
from sklearn.preprocessing import MinMaxScaler
import pickle
import requests
import os
import sys

# Silence
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'

def load_data_json(query):
    print(f"📡 Querying JSON: {query[:50]}...")
    try:
        r = requests.get("http://localhost:9000/exec", params={"query": query})
        if r.status_code == 200:
            data = r.json()
            if 'dataset' in data:
                return pd.DataFrame(data['dataset'], columns=[c['name'] for c in data['columns']])
            else:
                print(f"⚠️ No data for query: {query}")
                return pd.DataFrame()
        else:
            print(f"❌ DB Error: {r.text}")
            return pd.DataFrame()
    except Exception as e:
        print(f"❌ Connection Error: {e}")
        return pd.DataFrame()

def process_and_train():
    # 1. Load Data (JSON Only)
    df_market = load_data_json("SELECT timestamp, close, volume, rsi FROM market_training ORDER BY timestamp ASC")
    df_losses = load_data_json("SELECT timestamp, prediction, result FROM trades_memory WHERE result = 'LOSS'")
    
    if df_market.empty:
        print("❌ No market data to train on.")
        return

    print(f"📊 Market: {len(df_market)} rows | Losses: {len(df_losses)} rows")
    
    df_market['timestamp'] = pd.to_datetime(df_market['timestamp'])
    if not df_losses.empty:
        df_losses['timestamp'] = pd.to_datetime(df_losses['timestamp'])
    
    # 2. Time Features
    df_market['hour'] = df_market['timestamp'].dt.hour
    df_market['minute'] = df_market['timestamp'].dt.minute
    df_market['hour_sin'] = np.sin(2 * np.pi * df_market['hour'] / 24)
    df_market['hour_cos'] = np.cos(2 * np.pi * df_market['hour'] / 24)
    df_market['min_sin'] = np.sin(2 * np.pi * df_market['minute'] / 60)
    df_market['min_cos'] = np.cos(2 * np.pi * df_market['minute'] / 60)
    
    # 3. Labeling and Correction
    # Next Close Direction
    df_market['target'] = (df_market['close'].shift(-1) > df_market['close']).astype(int)
    df_market['weight'] = 1.0
    
    # Apply user correction: If we lost a PUT, the reality was UP/Neutral. 
    # Let's force it to 1 and weight it heavily.
    if not df_losses.empty:
        for _, row in df_losses.iterrows():
            # Find exact or closest candle
            mask = (df_market['timestamp'] >= row['timestamp'] - pd.Timedelta(seconds=15)) & \
                   (df_market['timestamp'] <= row['timestamp'] + pd.Timedelta(seconds=15))
            
            if row['prediction'] == 'PUT' and row['result'] == 'LOSS':
                df_market.loc[mask, 'target'] = 1 # Correction
                df_market.loc[mask, 'weight'] = 20.0 # Force Learning
    
    # 4. Prepare Sequences (Transformer input)
    SEQ_LEN = 10
    feature_cols = ['close', 'volume', 'rsi', 'hour_sin', 'hour_cos', 'min_sin', 'min_cos']
    
    data = df_market[feature_cols].values
    scaler = MinMaxScaler() # New Scaler
    data_scaled = scaler.fit_transform(data) 
    
    X, y, weights = [], [], []
    for i in range(len(data_scaled) - SEQ_LEN - 1):
        X.append(data_scaled[i : i + SEQ_LEN])
        y.append(df_market.iloc[i + SEQ_LEN]['target'])
        weights.append(df_market.iloc[i + SEQ_LEN]['weight'])
    
    X, y, weights = np.array(X), np.array(y), np.array(weights)
    
    # 5. Training (Fine-Tuning)
    print("🧠 Re-training Transformer (Sniper Correction)...")
    
    # Reuse current model architecture
    model = keras.models.load_model("model_quest_24h.keras")
    
    model.fit(
        X, y,
        sample_weight=weights,
        epochs=5, # Short burst to fix errors
        batch_size=256,
        verbose=1
    )
    
    model.save("model_quest_24h.keras")
    print("✅ Model Updated with Error Corrections.")

if __name__ == "__main__":
    process_and_train()
