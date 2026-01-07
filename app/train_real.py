from app.ai_brain import NeuralTraderMultivariable

# Create a subclass or modify naming to save to different file
# Or just instantiate and change path manually
class RealTrader(NeuralTraderMultivariable):
    def __init__(self):
        super().__init__()
        self.model_path = "model_real.keras"
        self.scaler_path = "scaler_real.pkl"

if __name__ == "__main__":
    brain = RealTrader()
    # Train on REAL data
    brain.train("market_data_real.csv")
