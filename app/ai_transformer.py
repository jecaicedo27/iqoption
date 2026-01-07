import os
import random
import numpy as np
import pandas as pd
import tensorflow as tf
from tensorflow.keras.models import Sequential, Model, load_model
from tensorflow.keras.layers import Input, Dense, Dropout, LayerNormalization, MultiHeadAttention, GlobalAveragePooling1D, Conv1D
from tensorflow.keras.callbacks import EarlyStopping
from sklearn.preprocessing import MinMaxScaler
import joblib
from app.ai_brain import NeuralTraderMultivariable

# Semilla Global
SEED = 42
os.environ['PYTHONHASHSEED'] = str(SEED)
random.seed(SEED)
np.random.seed(SEED)
tf.random.set_seed(SEED)

class TransformerTrader(NeuralTraderMultivariable):
    def __init__(self, sequence_length=10):
        # NOTE: Reduced Sequence Length to 10 (as used in training 2.5 min context)
        super().__init__(sequence_length)
        self.model_path = "model_quest_24h.keras"
        self.scaler_path = "scaler_quest.pkl"

    def add_time_features(self, df):
        # Ensure timestamp is datetime
        if not pd.api.types.is_datetime64_any_dtype(df['from']):
            df['timestamp'] = pd.to_datetime(df['from'], unit='s')
        else:
             df['timestamp'] = df['from']
             
        # Extract features
        hour = df['timestamp'].dt.hour
        minute = df['timestamp'].dt.minute
        
        # Cyclic Encoding
        df['hour_sin'] = np.sin(2 * np.pi * hour / 24)
        df['hour_cos'] = np.cos(2 * np.pi * hour / 24)
        df['min_sin'] = np.sin(2 * np.pi * minute / 60)
        df['min_cos'] = np.cos(2 * np.pi * minute / 60)
        return df

    def predict(self, df):
        if not self.model or not self.scaler:
            return None
            
        # 1. Add Time Features
        df = self.add_time_features(df)
            
        # 2. Calculate Percentage Changes (Match Training Logic)
        df['price_pct'] = df['close'].pct_change()
        df['vol_pct'] = df['volume'].pct_change()
        df.fillna(0, inplace=True)

        features = ['price_pct', 'vol_pct', 'rsi', 'hour_sin', 'hour_cos', 'min_sin', 'min_cos']
        
        # Validar existence
        for f in features:
            if f not in df.columns:
                print(f"Feature missing: {f}")
                return None
        
        # Check Length
        if len(df) < self.sequence_length:
            return None
            
        # Extract Data
        dataset = df[features].values
        
        # Scale
        try:
            scaled_data = self.scaler.transform(dataset)
        except Exception as e:
            print(f"Error scaling: {e}")
            return None
        
        # Create Sequence (Last N)
        last_sequence = scaled_data[-self.sequence_length:]
        
        # Reshape (1, 10, 7)
        last_sequence = np.reshape(last_sequence, (1, self.sequence_length, last_sequence.shape[1]))
        
        prediction = self.model.predict(last_sequence, verbose=0)
        return prediction[0][0]
