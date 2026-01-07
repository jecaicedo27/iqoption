import pandas as pd
import numpy as np
from app.ai_transformer import TransformerTrader
from app.analysis import MarketAnalyzer

def sim_clusters():
    print("Cargando datos (10k velas, 15s)...")
    try:
        df = pd.read_csv("market_data_real.csv")
    except:
        print("No se encontró market_data_real.csv. Ejecuta refresh_data primero.")
        return
        
    analyzer = MarketAnalyzer()
    print("Calculando TODOS los indicadores...")
    df = analyzer.prepare_data(df.to_dict('records')) if 'open' not in df.columns else df
    df = analyzer.add_technical_indicators(df)
    df.dropna(inplace=True)
    
    # Definir Clusters
    clusters = [
        {"name": "Price Only", "features": ['close']},
        {"name": "Reversal (RSI+Boll+Stoch)", "features": ['close', 'rsi', 'bollinger_upper', 'bollinger_lower', 'stoch_k']},
        {"name": "Momentum (MACD+EMA)", "features": ['close', 'macd', 'macd_signal', 'ema_200']},
        {"name": "Volume Focused", "features": ['close', 'volume', 'rsi']},
        {"name": "Kitchen Sink (ALL)", "features": ['close', 'rsi', 'bollinger_upper', 'bollinger_lower', 'macd', 'macd_signal', 'volume', 'stoch_k']}
    ]
    
    results = []
    
    print("\n=== CLUSTER BATTLE (Optimization) ===")
    
    for cluster in clusters:
        print(f"\n🧪 Testing Cluster: {cluster['name']}")
        feats = cluster['features']
        
        # 1. Prepare Data specific to cluster
        dataset = df[feats].values
        
        # 2. Train Micro-Brain
        brain = TransformerTrader()
        # Create model with correct input shape
        brain.create_model(input_shape=(60, len(feats)))
        
        scaled_data = brain.scaler.fit_transform(dataset)
        
        X, y = [], []
        # Entrenar en primeras 9000, testear en ultimas 1000
        train_size = len(scaled_data) - 500
        
        for i in range(60, train_size):
            X.append(scaled_data[i-60:i])
            is_up = 1 if scaled_data[i+1][0] > scaled_data[i][0] else 0 # Target is always Close (index 0)
            y.append(is_up)
            
        X, y = np.array(X), np.array(y)
        
        print(f"   Training on {len(X)} samples (3 Epochs)...")
        brain.model.fit(X, y, epochs=3, batch_size=64, verbose=0)
        
        # 3. Simulate
        print("   Simulating on last 500 candles...")
        balance = 0
        wins = 0
        losses = 0
        
        start_test = train_size
        
        for i in range(start_test, len(scaled_data)-1):
            window = scaled_data[i-60:i]
            window = np.expand_dims(window, axis=0)
            
            prob_up = brain.model.predict(window, verbose=0)[0][0]
            
            threshold = 0.52
            prediction = None
            
            if prob_up > threshold:
                prediction = "CALL"
            elif prob_up < (1.0 - start_test):
                 prediction = "PUT"
            
            # Simple simulation without Filters (Pure AI Power Test)
            if prob_up > threshold:
                prediction = "CALL"
            elif prob_up < (1.0 - threshold):
                prediction = "PUT"
                
            if prediction:
                # 15s timeframe, 1m expiration -> Look 4 steps ahead
                current_close = df.iloc[i]['close']
                steps_ahead = 4
                if i + steps_ahead < len(df):
                    future_close = df.iloc[i+steps_ahead]['close']
                    
                    won = False
                    if prediction == "CALL":
                        won = future_close > current_close
                    else:
                        won = future_close < current_close
                        
                    if won:
                        wins += 1
                        balance += 87
                    else:
                        losses += 1
                        balance -= 100
                        
        total = wins + losses
        wr = (wins/total*100) if total > 0 else 0
        print(f"   Result: Trades={total} | WinRate={wr:.1f}% | P/L=${balance}")
        
        results.append({
            "Cluster": cluster['name'],
            "Win Rate": wr,
            "P/L": balance
        })
        
    # Find Winner
    best = max(results, key=lambda x: x['P/L'])
    
    print("\n=== FINAL RESULTS ===")
    print(pd.DataFrame(results))
    print(f"\n🏆 GANADOR: {best['Cluster']} (P/L: ${best['P/L']})")

if __name__ == "__main__":
    sim_clusters()
