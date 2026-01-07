from app.ai_transformer import TransformerTrader

if __name__ == "__main__":
    print("=== INICIANDO ENTRENAMIENTO TRANSFORMER (NEXT GEN) ===")
    brain = TransformerTrader()
    # Entrenar con datos REALES (EURUSD)
    # Estos mismos datos dieron 52% con LSTM. ¿Cuánto dará el Transformer?
    brain.train("market_data_real.csv")
