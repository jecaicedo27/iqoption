import pandas as pd
import numpy as np
from app.ai_transformer import TransformerTrader
from app.analysis import MarketAnalyzer

def sim_robust():
    print("Cargando datos (10k velas)...")
    df = pd.read_csv("market_data_real.csv")
    
    brain = TransformerTrader()
    if not brain.load():
        print("Error: No Brain.")
        return

    analyzer = MarketAnalyzer()
    
    print("Calculando Indicadores (EMA 200, ATR, MACD)...")
    # Esto ya llama a calculate_ema y calculate_atr internamente gracias al update anterior
    df = analyzer.add_technical_indicators(df)
    
    # Scaling
    features = ['close', 'rsi', 'bollinger_upper', 'bollinger_lower', 'macd', 'macd_signal', 'volume']
    
    # Preparar Dataset Escalado
    # Importante: El scaler espera features puros.
    # El análisis añade otras columnas (ema_200, atr) que NO van al scaler del transformer,
    # pero se usan para FLITRAR la decisión.
    
    dataset_for_ai = df[features].values
    scaled_dataset = brain.scaler.transform(dataset_for_ai)
    
    # Simular ultimas 12 Hora (720 min)
    start_index = len(df) - 720
    if start_index < 200: start_index = 200 # Need warm up for EMA 200
    
    balance = 0
    wins = 0
    losses = 0
    skipped_choppy = 0
    skipped_trend = 0
    
    print(f"\n=== SIMULACIÓN ROBUSTA (Ultimas {len(df)-start_index} Velas / ~12h) ===")
    
    for i in range(start_index, len(df)-1):
        # Contexto IA (60 velas)
        window = scaled_dataset[i-60:i]
        window = np.expand_dims(window, axis=0)
        
        # 1. Predicción IA
        prob_up = brain.model.predict(window, verbose=0)[0][0]
        
        # 2. Datos Filtros
        row = df.iloc[i]
        current_close = row['close']
        ema_200 = row['ema_200']
        atr = row['atr']
        macd_val = row['macd']
        macd_sig = row['macd_signal']
        
        # 3. Filtros
        # A. Choppiness
        min_volatility = 0.00005
        if atr < min_volatility:
            skipped_choppy += 1
            # print(f"Skip Choppy (ATR {atr:.6f})")
            continue
            
        # B. Trend (EMA & MACD)
        trend_ema = "BULL" if current_close > ema_200 else "BEAR"
        trend_macd = "BULL" if macd_val > macd_sig else "BEAR"
        
        trend_final = "BULL" if trend_ema == "BULL" and trend_macd == "BULL" else \
                      "BEAR" if trend_ema == "BEAR" and trend_macd == "BEAR" else "MIXED"
                      
        threshold = 0.52
        amount = 100
        payout = 0.87
        
        prediction = None
        
        # CALL
        if prob_up > threshold:
            if trend_final == "BULL":
                prediction = "CALL"
            else:
                skipped_trend += 1
                
        # PUT
        elif prob_up < (1.0 - threshold):
            if trend_final == "BEAR":
                prediction = "PUT"
            else:
                skipped_trend += 1
                
        # Evaluar Resultado
        if prediction:
            next_close = df.iloc[i+1]['close']
            won = False
            if prediction == "CALL":
                won = next_close > current_close
            else:
                won = next_close < current_close
                
            if won:
                balance += (amount * payout)
                wins += 1
            else:
                balance -= amount
                losses += 1
                
    print("\n=== RESULTADOS ===")
    print(f"Trades Tomados: {wins + losses}")
    print(f"Trades Omitidos (Choppy/ATR): {skipped_choppy}")
    print(f"Trades Omitidos (Contra-Tendencia): {skipped_trend}")
    print(f"Wins: {wins} | Losses: {losses}")
    if (wins+losses) > 0:
        print(f"Win Rate: {wins/(wins+losses)*100:.2f}%")
    print(f"Ganancia Neta (P&L): ${balance:.2f}")

if __name__ == "__main__":
    sim_robust()
