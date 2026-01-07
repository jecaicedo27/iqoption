import pandas as pd
import numpy as np
import time
from app.ai_transformer import TransformerTrader
from app.analysis import MarketAnalyzer

def sim_martingale():
    # 1. Cargar Datos
    print("Cargando datos de mercado (10k velas)...")
    df = pd.read_csv("market_data_real.csv")
    
    # 2. Cargar IA
    brain = TransformerTrader()
    if not brain.load():
        print("Error: No hay cerebro Transformer.")
        return

    analyzer = MarketAnalyzer()
    
    # 3. Preparar Features
    print("Preparando features...")
    # Emulamos el proceso del bot
    df = analyzer.add_technical_indicators(df)
    df.fillna(method='bfill', inplace=True)
    df.fillna(method='ffill', inplace=True)
    
    # Scaling
    features = ['close', 'rsi', 'bollinger_upper', 'bollinger_lower', 'macd', 'macd_signal', 'volume']
    dataset = df[features].values
    scaled_dataset = brain.scaler.transform(dataset)
    
    # Config Martingala
    initial_balance = 10000
    balance = initial_balance
    base_bet = 100
    current_bet = base_bet
    max_bet = 5000 # Safety cap? Or All in? Let's say user has deep pockets but IQ limits per trade.
    
    wins = 0
    losses = 0
    max_drawdown = 0
    
    print("\n=== SIMULACIÓN MARTINGALA (TRANSFORMER) ===")
    
    # Loop de Simulación
    # Empezamos desde index 60
    for i in range(60, len(df)-1):
        # Contexto
        window = scaled_dataset[i-60:i]
        window = np.expand_dims(window, axis=0) # (1, 60, 7)
        
        # Predicción
        prob_up = brain.model.predict(window, verbose=0)[0][0]
        
        current_close = df.iloc[i]['close']
        next_close = df.iloc[i+1]['close'] # Futuro real 1m despues
        
        # Logica Trend MACD
        macd_val = df.iloc[i]['macd']
        macd_sig = df.iloc[i]['macd_signal']
        trend = "BULL" if macd_val > macd_sig else "BEAR"
        
        threshold = 0.52
        
        trade_taken = False
        prediction = None # "CALL" or "PUT"
        
        if prob_up > threshold and trend == "BULL":
            prediction = "CALL"
            trade_taken = True
        elif prob_up < (1.0 - threshold) and trend == "BEAR":
            prediction = "PUT"
            trade_taken = True
            
        if trade_taken:
            # Evaluar Resultado
            won = False
            if prediction == "CALL":
                won = next_close > current_close
            else:
                won = next_close < current_close
            
            # Resultado Martingala
            if won:
                # Ganas ~87%
                profit = current_bet * 0.87
                balance += profit
                wins += 1
                # Reset bet
                current_bet = base_bet
                # print(f"WIN | +${profit:.2f} | Bal: {balance:.2f}")
            else:
                # Pierdes 100%
                loss = current_bet
                balance -= loss
                losses += 1
                # Martingale: Double trade
                current_bet *= 2.1 # Para cubrir y ganar
                # print(f"LOSS | -${loss:.2f} | Bal: {balance:.2f} | Next Bet: {current_bet}")
                
            if balance < 0:
                print(f"💀 QUIEBRA DE CUENTA en vela {i} (Bet necesaria: {current_bet})")
                break
                
            if balance > 2000000: # Si hacemos millones, parar
                 print(f"🚀 MILLONARIO en vela {i}")
                 break

    print("\n=== RESULTADOS FINALES ===")
    print(f"Balance Inicial: ${initial_balance}")
    print(f"Balance Final:   ${balance:.2f}")
    print(f"Profit Neto:     ${balance - initial_balance:.2f}")
    print(f"Win/Loss:        {wins}/{losses}")
    if losses > 0:
        print(f"Win Rate:        {wins/(wins+losses)*100:.2f}%")
    else:
        print("Win Rate: 100%")

if __name__ == "__main__":
    sim_martingale()
