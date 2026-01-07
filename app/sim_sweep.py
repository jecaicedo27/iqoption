import time
import sys
import pandas as pd
import numpy as np
from app.connection import IQConnector
from app.data_manager import DataManager
from app.analysis import MarketAnalyzer
from app.ai_transformer import TransformerTrader
import tensorflow as tf

def sim_sweep():
    # Conexión
    connector = IQConnector()
    if not connector.connect():
        print("Error de conexión.")
        return

    data_manager = DataManager(connector.api)
    analyzer = MarketAnalyzer()
    
    # Timeframes a testear: 15s, 30s, 60s
    configs = [
        {"name": "15 Segundos", "tf": 15, "duration": 1}, # Duración 1 min expiration
        {"name": "30 Segundos", "tf": 30, "duration": 1},
        {"name": "1 Minuto",    "tf": 60, "duration": 1}
    ]
    
    results = []
    
    print("\n=== INICIANDO TIEMPO-SWEEP SIMULATION ===")
    
    for config in configs:
        print(f"\n🧪 Testeando: {config['name']}...")
        
        # 1. Bajar Data (2000 velas)
        print(f"   Descargando 3000 velas de {config['tf']}s...")
        try:
            candles = data_manager.get_candles(amount=3000, timeframe=config['tf'])
        except Exception as e:
            print(f"   Error bajando data: {e}")
            continue
            
        if not candles:
            print("   No data.")
            continue
            
        # 2. Procesar
        df = analyzer.prepare_data(candles)
        df = analyzer.add_technical_indicators(df)
        df.dropna(inplace=True)
        
        # 3. Entrenar Micro-Brain
        print("   Entrenando Micro-Transformer (5 Epochs)...")
        brain = TransformerTrader()
        brain.create_model(input_shape=(60, 7)) # Reset model
        
        features = ['close', 'rsi', 'bollinger_upper', 'bollinger_lower', 'macd', 'macd_signal', 'volume']
        dataset = df[features].values
        scaled_data = brain.scaler.fit_transform(dataset)
        
        X, y = [], []
        for i in range(60, len(scaled_data) - 200): # Dejar 200 ultimas para test
            X.append(scaled_data[i-60:i])
            # Target: Close[i+1] > Close[i] ?
            is_up = 1 if scaled_data[i+1][0] > scaled_data[i][0] else 0
            y.append(is_up)
            
        X, y = np.array(X), np.array(y)
        
        brain.model.fit(X, y, epochs=5, batch_size=64, verbose=0)
        
        # 4. Simular en Test Set (Ultimas 200)
        print("   Simulando Trading en ultimas 200 velas...")
        balance = 0
        wins = 0
        losses = 0
        
        test_start = len(scaled_data) - 200
        
        for i in range(test_start, len(scaled_data)-1):
            window = scaled_data[i-60:i]
            window = np.expand_dims(window, axis=0)
            
            prob_up = brain.model.predict(window, verbose=0)[0][0]
            
            # Logic
            threshold = 0.52
            
            # MACD Filter
            macd_val = df.iloc[i]['macd']
            macd_sig = df.iloc[i]['macd_signal']
            trend = "BULL" if macd_val > macd_sig else "BEAR"
            
            prediction = None
            if prob_up > threshold and trend == "BULL":
                prediction = "CALL"
            elif prob_up < (1.0 - threshold) and trend == "BEAR":
                prediction = "PUT"
                
            if prediction:
                current_close = df.iloc[i]['close']
                # Expiration check: 
                # Si TF=15s, Duration=1m -> Necesitamos ver el precio 4 velas despues (60/15 = 4)
                steps_ahead = int(60 / config['tf']) 
                
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
            "Config": config['name'],
            "Trades": total,
            "Win Rate": f"{wr:.1f}%",
            "P/L": f"${balance}"
        })

    print("\n=== RESUMEN FINAL ===")
    print(pd.DataFrame(results))

if __name__ == "__main__":
    sim_sweep()
