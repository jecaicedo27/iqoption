import pandas as pd
import numpy as np
import tensorflow as tf
from tensorflow import keras
from tensorflow.keras import layers
from app.db_quest import QuestDBManager
from sklearn.preprocessing import MinMaxScaler
import pickle
import sys

# Silence
import os
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'

def load_data_from_quest():
    print("🐘 Fetching training data from QuestDB...")
    db = QuestDBManager()
    # Query all data from market_training
    # We need timestamp to extract features
    # Casting volume to double for scaler compatibility
    query = "select timestamp, close, volume, rsi from market_training order by timestamp asc"
    
    # Use pandas via REST API (CSV format)
    # db_quest.get_training_data uses REST returns List[Dict] usually or DF?
    # Let's use direct curl logic inside QuestDBManager or just reimplement minimal fetch here
    # to ensure DataFrame with correct types.
    
    import requests
    import io
    
    resp = requests.get(f"http://localhost:9000/exp?query={query}")
    if resp.status_code == 200:
        df = pd.read_csv(io.StringIO(resp.text))
        # QuestDB CSV export header: "timestamp","close","volume","rsi"
        return df
    else:
        print(f"❌ Error fetching data: {resp.text}")
        sys.exit(1)

def add_time_features(df):
    # QuestDB timestamp format in CSV: usually ISO 8601
    df['timestamp'] = pd.to_datetime(df['timestamp'])
    
    # Extract Hour and Minute
    # Normalize to 0-1 range roughly, or use cyclic encoding (Sine/Cosine).
    # For simplicity and robustness with trees/NN, normalized float is okay, 
    # but cyclic is better 23:59 -> 00:00 close.
    # Let's use simple normalization first: Hour/23, Minute/59.
    
    df['hour'] = df['timestamp'].dt.hour
    df['minute'] = df['timestamp'].dt.minute
    
    # Cyclic encoding
    df['hour_sin'] = np.sin(2 * np.pi * df['hour'] / 24)
    df['hour_cos'] = np.cos(2 * np.pi * df['hour'] / 24)
    df['min_sin'] = np.sin(2 * np.pi * df['minute'] / 60)
    df['min_cos'] = np.cos(2 * np.pi * df['minute'] / 60)
    
    return df

def create_transformer_model(input_shape):
    inputs = keras.Input(shape=input_shape)
    
    # Transformer Block
    x = layers.MultiHeadAttention(num_heads=4, key_dim=4)(inputs, inputs)
    x = layers.Dropout(0.1)(x)
    x = layers.LayerNormalization(epsilon=1e-6)(x + inputs) # Residual
    
    # Global Avg Pooling (to flatten time dimension)
    x = layers.GlobalAveragePooling1D()(x)
    
    # Dense Layers
    x = layers.Dense(64, activation="relu")(x)
    x = layers.Dropout(0.1)(x)
    x = layers.Dense(32, activation="relu")(x)
    
    # Output: 1 neuron (Probability of Price UP)
    # Using Sigmoid for binary 0-1
    outputs = layers.Dense(1, activation="sigmoid")(x)
    
    model = keras.Model(inputs=inputs, outputs=outputs)
    model.compile(optimizer="adam", loss="binary_crossentropy", metrics=["accuracy"])
    return model

def train():
    df = load_data_from_quest()
    print(f"✅ Loaded {len(df)} candles.")
    
    # 1. Feature Engineering
    df = add_time_features(df)
    
    # NEW: Calculate Percentage Changes (Stationary Features)
    # This prevents the model from being biased by absolute price levels
    df['price_pct'] = df['close'].pct_change()
    df['vol_pct'] = df['volume'].pct_change()
    # Filling NaNs from pct_change
    df.fillna(0, inplace=True)
    
    SEQ_LEN = 10
    
    # Stationary feature columns
    feature_cols = ['price_pct', 'vol_pct', 'rsi', 'hour_sin', 'hour_cos', 'min_sin', 'min_cos']
    
    data = df[feature_cols].values
    
    # 2. Targets (Ground Truth): 1 if price goes UP in next candle
    targets = (df['close'].shift(-1) > df['close']).astype(int).values
    
    # Drop first and last rows to handle shifts/pct_change NaNs
    data = data[1:-1]
    targets = targets[1:-1]
    
    # Scale Data
    scaler = MinMaxScaler()
    data_scaled = scaler.fit_transform(data)
    
    # Create Sequences
    X = []
    y = []
    
    for i in range(len(data_scaled) - SEQ_LEN):
        X.append(data_scaled[i : i + SEQ_LEN])
        y.append(targets[i + SEQ_LEN])
        
    X = np.array(X)
    y = np.array(y)
    
    print(f"Training Shape: X={X.shape}, y={y.shape}")
    
    # Split
    split = int(len(X) * 0.8)
    X_train, X_test = X[:split], X[split:]
    y_train, y_test = y[:split], y[split:]
    
    # Model
    model = create_transformer_model((SEQ_LEN, len(feature_cols)))
    
    print("🧠 Training Transformer (Volume + Time Aware)...")
    history = model.fit(
        X_train, y_train,
        validation_data=(X_test, y_test),
        epochs=20,
        batch_size=256,
        verbose=1
    )
    
    # Save
    model.save("model_quest_24h.keras")
    with open("scaler_quest.pkl", "wb") as f:
        pickle.dump(scaler, f)
        
    print("✅ Model Saved: model_quest_24h.keras")
    print("✅ Scaler Saved: scaler_quest.pkl")

if __name__ == "__main__":
    train()
