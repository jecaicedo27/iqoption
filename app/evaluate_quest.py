import pandas as pd
import numpy as np
from tensorflow.keras.models import load_model
import joblib
from app.train_quest import load_data_from_quest, add_time_features

def evaluate():
    # 1. Load Data
    df = load_data_from_quest()
    df = add_time_features(df)
    
    # 2. Features (Must match training)
    features = ['close', 'volume', 'rsi', 'hour_sin', 'hour_cos', 'min_sin', 'min_cos']
    
    # Scale
    scaler = joblib.load("scaler_quest.pkl")
    dataset = df[features].values
    scaled_data = scaler.transform(dataset)
    
    # Targets
    targets = (df['close'].shift(-1) > df['close']).astype(int).values
    
    # 3. Prepare Test Set (Last 20%)
    SEQ_LEN = 10
    split = int(len(scaled_data) * 0.8)
    
    X_test = []
    y_test = []
    prices_test = [] # To calculate real PnL? No, purely directional for now.
    
    # Valid indices for test set
    # We need to start 'SEQ_LEN' after split to have context? 
    # Or split is on X.
    # Let's simple slice.
    
    print(f"Total Data: {len(scaled_data)}. Test Start Index: {split}")
    
    # Create sequences for Test only
    # Range: from split to end - 1 (for target)
    test_data_slice = scaled_data[split - SEQ_LEN:] # Add context
    test_targets_slice = targets[split:]
    
    X = []
    for i in range(SEQ_LEN, len(test_data_slice) - 1):
        X.append(test_data_slice[i-SEQ_LEN:i])
        
    y_true = test_targets_slice[:len(X)] # Sync length
    X = np.array(X)
    
    print(f"Test Set Size: {len(X)} samples")
    
    # 4. Predict
    model = load_model("model_quest_24h.keras")
    print("🔮 Predicting...")
    y_pred_prob = model.predict(X, verbose=0)
    
    # 5. Calculate Metrics
    threshold = 0.55 # Only trade if confident? Or just > 0.5?
    # Let's simulate the Bot's logic (Threshold 0.53 or similar)
    
    wins = 0
    losses = 0
    skipped = 0
    
    capital = 1000
    bet = 100
    payout = 0.87
    
    for i in range(len(y_pred_prob)):
        prob = y_pred_prob[i][0]
        actual = y_true[i]
        
        # Win Condition:
        # If Prob > 0.5 and Actual = 1 (UP) -> WIN
        # If Prob < 0.5 and Actual = 0 (DOWN) -> WIN
        
        # But we use Thresholds usually
        trade = None
        if prob > 0.53:
            trade = 1 # CALL
        elif prob < 0.47:
            trade = 0 # PUT
            
        if trade is not None:
            if trade == actual:
                wins += 1
                capital += bet * payout
            else:
                losses += 1
                capital -= bet
        else:
            skipped += 1
            
    total_trades = wins + losses
    win_rate = (wins / total_trades * 100) if total_trades > 0 else 0
    
    print("\n" + "="*30)
    print("📊 RESULTADOS EN DATA DE PRUEBA (Ultimas ~5 horas)")
    print("="*30)
    print(f"Model Accuracy (Raw >0.5): {model.evaluate(X, y_true, verbose=0)[1]*100:.2f}%")
    print(f"\n--- SIMULACIÓN (Umbral Confianza 0.53) ---")
    print(f"Total Operaciones: {total_trades}")
    print(f"WIN: {wins} | LOSS: {losses}")
    print(f"WIN RATE: {win_rate:.2f}%")
    print(f"Profit Estimado: ${capital - 1000:.2f} (Base $1000)")
    print("="*30)

if __name__ == "__main__":
    evaluate()
