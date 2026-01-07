import pandas as pd
import numpy as np
from app.ai_brain import NeuralTraderMultivariable
from app.analysis import MarketAnalyzer
from app.config import DEFAULT_AMOUNT

def backtest(csv_path="market_data.csv", limit_rows=1440):
    print(f"--- INICIANDO BACKTEST (Simulación de {limit_rows} minutos) ---")
    
    # 1. Cargar datos
    df_raw = pd.read_csv(csv_path)
    if 'timestamp' in df_raw.columns:
        df_raw.rename(columns={'timestamp': 'from'}, inplace=True)
    
    print(f"Datos totales disponibles: {len(df_raw)} velas.")
    
    # 2. Procesar Indicadores (Igual que en Training/Bot)
    analyzer = MarketAnalyzer()
    df = analyzer.prepare_data(df_raw.to_dict('records'))
    df = analyzer.add_technical_indicators(df)
    df.dropna(inplace=True)
    
    # Seleccionar solo la porción para testear (ej. último día)
    # Si limit_rows es None, usa todo.
    if limit_rows and len(df) > limit_rows:
        df_test = df.iloc[-limit_rows:].reset_index(drop=True)
    else:
        df_test = df.reset_index(drop=True)
        
    print(f"Testeando sobre las últimas {len(df_test)} velas...")

    # 3. Cargar Cerebro
    brain = NeuralTraderMultivariable()
    if not brain.load():
        print("No hay modelo entrenado.")
        return

    # 4. Simulación Loop
    balance = 0
    wins = 0
    losses = 0
    skipped = 0
    
    # Necesitamos iterar y alimentar al cerebro con la ventana de contexto
    # La IA necesita 'sequence_length' (60) velas anteriores.
    # Así que empezamos desde el índice 60.
    
    seq_len = brain.sequence_length
    
    # Pre-calcular predicciones en batch es más rápido, pero haremos loop para simular lógica exacta
    # Optimización: Predict acepta batch. Podemos pasarle todo el array formateado.
    
    # Preparar datos para predict
    # predict espera un dataframe reciente para sacar la ultima secuencia.
    # PERO, podemos usar el método interno model.predict con un array masivo X_test.
    
    print("Generando predicciones masivas...")
    features = ['close', 'rsi', 'bollinger_upper', 'bollinger_lower', 'macd', 'macd_signal', 'volume']
    existing_features = [f for f in features if f in df_test.columns]
    
    dataset = df_test[existing_features].values
    scaled_data = brain.scaler.transform(dataset)
    
    X_test = []
    # Indices correspondientes a cada predicción
    indices = [] 
    
    for i in range(seq_len, len(scaled_data)):
        X_test.append(scaled_data[i-seq_len:i])
        indices.append(i)
        
    X_test = np.array(X_test)
    
    # Predicciones (Probabilidad de que SUBA en i+1 ? No, el modelo se entrenó:
    # Input: [i-60 : i] -> Target: Close[i] > Close[i-1] ?
    # ENTONCES: Al pasarle [i-60 : i], la predicción es para el movimiento de vela 'i' respecto a 'i-1'?
    # REVISAR TRAIN:
    # X.append(scaled[i-seq:i])
    # y.append(1 if scaled[i] > scaled[i-1])
    #
    # O SEA: El X termina en i-1 (exclusivo en python slice?)
    # scaled[i-seq:i] toma desde i-seq hasta i-1.
    # Y predecimos si i es mayor que i-1.
    #
    # CORRECTO.
    # Entonces, en tiempo real estamos en vela 'T'. Pasamos las ultimas 60 (T-59 a T).
    # Predecimos T+1.
    
    probs = brain.model.predict(X_test, verbose=1)
    
    print("\nEvaluando resultados...")
    
    for k, idx in enumerate(indices):
        # idx es el índice de la vela que estamos prediciendo que pasará (Target)
        # La vela 'idx' ya ocurrió en el histórico, así que podemos verificar.
        
        prob_up = probs[k][0]
        
        current_close = df_test.iloc[idx-1]['close'] # Precio en el momento de tomar decisión
        future_close = df_test.iloc[idx]['close']    # Precio resultado (1 min después)
        
        # Lógica del Bot (Híbrido: IA + Tendencia MACD)
        # Replicando exactamente la lógica de bot.py
        
        # Obtener estado del MACD (Trend) - Ya calculado en df_test?
        # df_test tiene las columnas 'macd' y 'macd_signal'
        macd_val = df_test.iloc[idx-1]['macd']
        macd_sig = df_test.iloc[idx-1]['macd_signal']
        trend = "BULL" if macd_val > macd_sig else "BEAR"
        
        ai_threshold_center = 0.4928
        action = None
        
        # CALL: IA > Promedio AND Tendencia Alcista
        if prob_up > ai_threshold_center and trend == "BULL":
            action = "CALL"
            
        # PUT: IA < Promedio AND Tendencia Bajista
        elif prob_up < ai_threshold_center and trend == "BEAR":
            action = "PUT"
            
        if action:
            payout = 0.87 # Promedio IQ Option
            profit = 0
            
            is_win = False
            if action == "CALL":
                if future_close > current_close:
                    is_win = True
            elif action == "PUT":
                if future_close < current_close:
                    is_win = True
            
            # Nota: Empates (Doji) suelen perder o devolver en IQ. Asumimos perdida.
            
            if is_win:
                wins += 1
                profit = DEFAULT_AMOUNT * payout
                balance += profit
                # print(f"Row {idx}: WIN {action} (Prob {prob_up:.2f})")
            else:
                losses += 1
                profit = -DEFAULT_AMOUNT
                balance += profit
                # print(f"Row {idx}: LOSS {action} (Prob {prob_up:.2f})")
        else:
            skipped += 1

    total_trades = wins + losses
    win_rate = (wins / total_trades * 100) if total_trades > 0 else 0
    
    print("\n" + "="*40)
    print(f"RESULTADOS BACKTEST ({len(df_test)} minutos analizados)")
    print("="*40)
    
    # Estadísticas de Probabilidad
    all_probs = [p[0] for p in probs]
    if all_probs:
        print(f"Probabilidad Mínima: {min(all_probs):.4f}")
        print(f"Probabilidad Máxima: {max(all_probs):.4f}")
        print(f"Probabilidad Promedio: {np.mean(all_probs):.4f}")
        print("-" * 40)

    print(f"Operaciones Totales: {total_trades}")
    print(f"Ganadas (ITM):       {wins}")
    print(f"Perdidas (OTM):      {losses}")
    print(f"Tasa de Acierto:     {win_rate:.2f}%")
    print(f"Skipped (Indecisión):{skipped}")
    print("-" * 40)
    print(f"MONTO POR TRADE:     ${DEFAULT_AMOUNT}")
    print(f"BALANCE FINAL (P/L): ${balance:.2f} USD")
    print("="*40)
    
    if balance > 0:
        print("¡RESULTADO POSITIVO! 🤑")
    else:
        print("RESULTADO NEGATIVO 📉 (Necesitamos ajustar umbrales o entrenar más)")

if __name__ == "__main__":
    backtest()
