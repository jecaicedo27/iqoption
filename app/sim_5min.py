from app.connection import IQConnector
from app.data_manager import DataManager
from app.analysis import MarketAnalyzer
from app.ai_brain import NeuralTraderMultivariable
import pandas as pd
import numpy as np
import time

# Configuración 5 Minutos
ASSET = "EURUSD-OTC"
TIMEFRAME = 5 
AMOUNT_CANDLES = 3000 # ~10 días de datos en 5 min

def sim_5min():
    connector = IQConnector()
    if not connector.connect(): return
    
    # 1. Bajar Data 5 Min
    print(f"Bajando {AMOUNT_CANDLES} velas de 5 min para {ASSET}...")
    candles = connector.api.get_candles(ASSET, TIMEFRAME * 60, AMOUNT_CANDLES, time.time())
    
    df = pd.DataFrame(candles)
    if 'timestamp' in df.columns: df.rename(columns={'timestamp': 'from'}, inplace=True)
    df.sort_values('from', inplace=True)
    
    # 2. Analizar
    analyzer = MarketAnalyzer()
    df = analyzer.prepare_data(df.to_dict('records'))
    df = analyzer.add_technical_indicators(df)
    df.dropna(inplace=True)
    
    # 3. Cargar Cerebro (Usará el cerebro actual, pero aplicado a velas de 5 min)
    # Nota: El cerebro fue entrenado con velas de 1 min, por lo que la "forma" de los patrones podría variar.
    # Pero para una estimación rápida sirve.
    brain = NeuralTraderMultivariable()
    if not brain.load(): return
    
    print("Simulando trading...")
    wins = 0
    losses = 0
    balance = 0
    
    # Iterar
    probs = []
    
    # Need loop manually because predict uses last sequence
    # This is slow but accurate simulation
    # Optimización: Usar model.predict en batch si es posible, pero prepare_data de brain espera 60 steps.
    # Hack rápido: simular ultimas 500 velas (aprox 2 dias)
    
    start_idx = len(df) - 500
    if start_idx < 60: start_idx = 60
    
    for i in range(start_idx, len(df)):
        # Slice de 60 velas anteriores
        sub_df = df.iloc[i-60:i] 
        future_close = df.iloc[i]['close']
        
        prob = brain.predict(sub_df)
        if prob:
            # Lógica Híbrida 5 min (Misma que 1 min)
            macd_val = sub_df.iloc[-1]['macd']
            macd_sig = sub_df.iloc[-1]['macd_signal']
            trend = "BULL" if macd_val > macd_sig else "BEAR"
            
            # Umbral calibrado (usamos el del entrenamiento actual)
            threshold = 0.4928 
            
            action = None
            if prob > threshold and trend == "BULL": action = "CALL"
            if prob < threshold and trend == "BEAR": action = "PUT"
            
            if action:
                current_close = sub_df.iloc[-1]['close']
                won = False
                if action == "CALL" and future_close > current_close: won = True
                if action == "PUT" and future_close < current_close: won = True
                
                if won:
                    wins += 1
                    balance += (100 * 0.87)
                else:
                    losses += 1
                    balance -= 100
                    
    total = wins + losses
    wr = (wins/total*100) if total > 0 else 0
    
    print("\n" + "="*40)
    print(f"RESULTADO SIMULACIÓN 5 MINUTOS ({total} Trades)")
    print("="*40)
    print(f"Ganadas: {wins} | Perdidas: {losses}")
    print(f"Win Rate: {wr:.2f}%")
    print(f"BALANCE: ${balance:.2f}")
    print("="*40)

if __name__ == "__main__":
    sim_5min()
