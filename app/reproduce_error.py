import numpy as np
from app.db_quest import QuestDBManager

db = QuestDBManager()

# Simulate Bot types
price = np.float64(1.05)
confidence = np.float32(0.88)
profit = np.float64(-14.0)
features = np.array([[1.0, 200, 50]], dtype=np.float64)
# Note: features in bot is a LIST of arrays if coming from prepare_data?
# prepare_data returns np.array(X)
# In bot: last_feats = df_analysis[['close', 'volume', 'rsi']].tail(1).values.tolist()
# tolist() converts numpy array to nested list of python types?
# DataFrame.values.tolist() usually converts to python floats if native, but let's check.
# If df has mixed types (int for vol), it refers to object?

features_list = [[np.float64(1.0), np.int64(200), np.float64(50.0)]] # Worst case

print("Trying to save...")
try:
    db.save_trade(
        "EURUSD", 
        price, 
        "CALL", 
        confidence, 
        features_list, 
        "WIN", 
        profit
    )
    print("Success!")
except Exception as e:
    print(f"Failed: {e}")
