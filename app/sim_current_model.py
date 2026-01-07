import pandas as pd
import numpy as np
import tensorflow as pd_tf # Just to avoid confusing imports, assume keras handling
from tensorflow.keras.models import load_model
import joblib
import questdb.ingress as qdb
from app.config import DEFAULT_ASSET

# Configuration matching Bot
THRESHOLD = 0.51 # Baseline activity check
SEQUENCE_LENGTH = 10

def load_data():
    print("⏳ Loading data from QuestDB...")
    # Fetch all data
    # In a real scenario, we might want to split, but user asked for "what we have"
    # We will simulate on the last 20% to represent "unseen" or just all of it to see "fit".
    # Usually simulation is best on validation set. 
    # Let's fetch everything.
    import requests
    import io
    
    query = "SELECT * FROM market_training"
    r = requests.get("http://localhost:9000/exec", params={"query": query})
    if r.status_code == 200:
        data = r.json()
        df = pd.DataFrame(data['dataset'], columns=[c['name'] for c in data['columns']])
        # Sort by timestamp just in case
        df['timestamp'] = pd.to_datetime(df['timestamp'])
        df.sort_values('timestamp', inplace=True)
        return df
    else:
        print("❌ DB Error")
        return pd.DataFrame()

def simulate():
    # 1. Load Resources
    print("🧠 Loading Model & Scaler...")
    try:
        model = load_model("model_quest_24h.keras")
        scaler = joblib.load("scaler_quest.pkl")
    except:
        print("❌ Model/Scaler not found!")
        return

    # 2. Load Data
    df = load_data()
    if df.empty: return
    
    print(f"📊 Data Loaded: {len(df)} candles")
    
    # 3. Preprocess (Scaling)
    # Match ai_transformer logic
    # features = ['close', 'volume', 'rsi', 'ema_200', + time features?]
    # Need to check exactly what features expected. 
    # Usually [close, volume, rsi, hour_sin, hour_cos, minute_sin, minute_cos] (7 features)
    
    # Recalculate time features if missing or use existing columns
    # DB columns: asset, open, close, min, max, volume, rsi, ema_200, timestamp
    # We need to reconstruct the EXACT feature set used in training.
    # App usually does this in `ai_transformer.py`.
    # I will replicate simple feature eng here.
    
    df['hour'] = df['timestamp'].dt.hour
    df['minute'] = df['timestamp'].dt.minute
    df['hour_sin'] = np.sin(2 * np.pi * df['hour'] / 24)
    df['hour_cos'] = np.cos(2 * np.pi * df['hour'] / 24)
    df['min_sin'] = np.sin(2 * np.pi * df['minute'] / 60)
    df['min_cos'] = np.cos(2 * np.pi * df['minute'] / 60)
    
    # STATIONARY FEATURES
    df['price_pct'] = df['close'].pct_change()
    df['vol_pct'] = df['volume'].pct_change()
    df.fillna(0, inplace=True)
    
    feature_cols = ['price_pct', 'vol_pct', 'rsi', 'hour_sin', 'hour_cos', 'min_sin', 'min_cos']
    
    # Scaling
    data = df[feature_cols].values
    data_scaled = scaler.transform(data) 
    
    # 4. Simulation Loop
    total_trades = 0
    wins = 0
    losses = 0
    
    # Need sequences
    # We can iterate or batch predict. Batch is faster.
    
    X = []
    # Index mapping to original DF to check outcome
    indices = [] 
    
    for i in range(SEQUENCE_LENGTH, len(data_scaled)):
        seq = data_scaled[i-SEQUENCE_LENGTH:i]
        X.append(seq)
        indices.append(i)
        
    X = np.array(X)
    print(f"🔮 Predicting on {len(X)} sequences...")
    
    probs = model.predict(X, verbose=0)
    
    print("⚡ Analyzing outcomes...")
    
    for i, prob_up in enumerate(probs):
        idx = indices[i]
        current_close = df.iloc[idx]['close']
        
        # Determine Outcome (Close 1 min later = 4 candles later)
        # 15s candles -> 1 min = 4 candles forward
        future_idx = idx + 4 
        if future_idx >= len(df): continue
        
        future_close = df.iloc[future_idx]['close']
        
        action = None
        if prob_up > THRESHOLD:
            action = "CALL"
        elif prob_up < (1.0 - THRESHOLD):
            action = "PUT"
            
        if action:
            total_trades += 1
            is_win = False
            
            if action == "CALL":
                if future_close > current_close: is_win = True
            elif action == "PUT":
                if future_close < current_close: is_win = True
                
            if is_win:
                wins += 1
            else:
                losses += 1
                
    # 5. Report
    print("\n" + "="*30)
    print("📈 SIMULATION RESULTS (EURUSD-OTC)")
    print("="*30)
    print(f"Threshold: {THRESHOLD} (Conf > {int(THRESHOLD*100)}%)")
    print(f"Total Trades: {total_trades}")
    print(f"Wins: {wins}")
    print(f"Losses: {losses}")
    
    if total_trades > 0:
        win_rate = (wins / total_trades) * 100
        print(f"🏆 Win Rate: {win_rate:.2f}%")
        
        # Simple PnL (Payout 88%)
        profit = (wins * 0.88 * 100) - (losses * 100) # $100 bet
        print(f"💰 Est. PnL ($100/trade): ${profit:.2f}")
    else:
        print("⚠️ No trades triggered (Threshold too high?).")
    print("="*30)

if __name__ == "__main__":
    simulate()
