from app.analysis import MarketAnalyzer
from app.ai_brain import NeuralTraderMultivariable
import pandas as pd
import numpy as np

DATA_FILE = "market_data.csv" # 10k candles of 5s data

def sim_5s():
    print(f"Loading data from {DATA_FILE}...")
    try:
        df = pd.read_csv(DATA_FILE)
    except FileNotFoundError:
        print("Error: No data file found.")
        return

    # Rename timestamp if needed (csv has 'timestamp', prepare expects 'from' or handles it)
    if 'timestamp' in df.columns:
        df.rename(columns={'timestamp': 'from'}, inplace=True)
        
    df.sort_values('from', inplace=True)
    
    print(f"Data Loaded: {len(df)} candles.")
    
    # 2. Analyze
    analyzer = MarketAnalyzer()
    # Analyzer expects list of dicts or DF. It prepares DF.
    # prepare_data converts 'from' to datetime.
    df = analyzer.prepare_data(df.to_dict('records'))
    df = analyzer.add_technical_indicators(df)
    df.dropna(inplace=True)
    
    print(f"Data Cleaned: {len(df)} candles.")

    # 3. Load Brain (The one just trained on this data)
    brain = NeuralTraderMultivariable()
    if not brain.load(): return
    
    print("Simulating Hyper-Guaracha 5s Trading...")
    wins = 0
    losses = 0
    balance = 0
    trades = 0
    
    # --- OPTIMIZED BATCH PREDICTION ---
    print("Preparing data for Vectorized Prediction...")
    
    # 1. Select Features (Must match training exactly)
    features_list = ['close', 'rsi', 'bollinger_upper', 'bollinger_lower', 'macd', 'macd_signal', 'volume']
    
    # Ensure all exist
    missing = [f for f in features_list if f not in df.columns]
    if missing:
        print(f"Error: Missing columns {missing}")
        return

    dataset = df[features_list].values
    
    # 2. Scale Data (Using the loaded scaler from training)
    print("Scaling data...")
    try:
        scaled_dataset = brain.scaler.transform(dataset)
    except Exception as e:
        print(f"Scaling Error: {e}")
        return
        
    # 3. Create Sliding Windows (X)
    # Sequence length = 60
    seq_len = 60
    X = []
    # Map batch index back to df index
    valid_indices = [] 
    
    # Start from seq_len. 
    # End at len(df) - 6 (to allow checking result of +6 candles)
    
    start_idx = seq_len
    end_idx = len(df) - 6
    
    for i in range(start_idx, end_idx):
        # Window from i-60 to i
        window = scaled_dataset[i-seq_len:i]
        X.append(window)
        valid_indices.append(i)
        
    X = np.array(X)
    print(f"Predicting batch of {len(X)} samples...")
    
    # 4. Batch Predict
    probs = brain.model.predict(X, batch_size=2048, verbose=1)
    
    # 5. Evaluate P/L
    print("Evaluating P/L...")
    
    # 5. Evaluate P/L for multiple thresholds
    print("Evaluating P/L for thresholds [0.51, 0.53, 0.55, 0.60, 0.70]...")
    
    thresholds = [0.511, 0.53, 0.55, 0.60, 0.70]
    
    for threshold in thresholds:
        wins = 0
        losses = 0
        balance = 0
        trades_count = 0
        
        for j, i in enumerate(valid_indices):
            prob_up = probs[j][0]
            
            # Logic: AI > Threshold AND Trend (MACD)
            # MACD values from original DF (unscaled)
            macd_val = df.iloc[i-1]['macd']
            macd_sig = df.iloc[i-1]['macd_signal']
            trend = "BULL" if macd_val > macd_sig else "BEAR"
            
            action = None
            
            # Hybrid Logic
            if prob_up > threshold and trend == "BULL": 
                action = "CALL"
            elif prob_up < threshold and trend == "BEAR" and prob_up < (1.0 - threshold):
                # Symmetric threshold for PUT (e.g. < 0.49 if thresh is 0.51)
                # But our model output is 0.50 centered? 
                # Model trained with sigmoid (0-1).
                # If threshold is 0.60 (High confidence UP), then < 0.40 is High confidence DOWN.
                action = "PUT"
                
            # Original Logic used 'prob_up < threshold' for PUT which is wrong for high thresholds
            # Fixed here: PUT triggers if prob < (1 - threshold) roughly.
            # actually better: prob_up < (1 - (threshold - 0.5)) if centered?
            # Let's stick to symmetric:
            # CALL if prob > X
            # PUT if prob < (1-X) 
            
            # Re-evaluating logic for "Standard":
            # If threshold is 0.511 -> PUT < 0.489
            # If threshold is 0.60 -> PUT < 0.40
            
            lower_threshold = 1.0 - threshold
            
            if prob_up > threshold and trend == "BULL":
                action = "CALL"
            elif prob_up < lower_threshold and trend == "BEAR":
                action = "PUT"

            if action:
                trades_count += 1
                current_close = df.iloc[i]['close']
                future_close = df.iloc[i+6]['close'] # 30s expiry (6 candles)
                
                won = False
                if action == "CALL" and future_close > current_close: won = True
                if action == "PUT" and future_close < current_close: won = True
                
                if won:
                    wins += 1
                    balance += 87 # Profit $87
                else:
                    losses += 1
                    balance -= 100 # Loss $100
        
        total = wins + losses
        wr = (wins/total*100) if total > 0 else 0
        print(f"THRESH {threshold}: Trades={total} | WR={wr:.2f}% | Balance=${balance}")
    
    print("\n" + "="*40)
    print(f"RESULTADO SIMULACIÓN HYPER-GUARACHA (5s / 30s Expiry)")
    print(f"Data Range: ~{len(df)*5/60/60:.1f} Hours")
    print("="*40)
    print(f"Total Trades: {total} (Est. {total*2:.0f} daily)")
    print(f"Ganadas: {wins} | Perdidas: {losses}")
    print(f"Win Rate: {wr:.2f}%")
    print(f"PROFIT ESTIMADO (24h proy): ${balance * (24 / (len(df)*5/3600)):.2f}")
    print(f"BALANCE REAL (Last ~14h): ${balance:.2f}")
    print("="*40)

if __name__ == "__main__":
    sim_5s()
