from app.ai_brain import NeuralTraderMultivariable

def main():
    print("Iniciando proceso de entrenamiento IA GUARACHA (Multivariable)...")
    brain = NeuralTraderMultivariable()
    
    # Entrenar con el dataset existente
    brain.train("market_data.csv")
    
    print("Entrenamiento Guaracha finalizado.")

if __name__ == "__main__":
    main()
