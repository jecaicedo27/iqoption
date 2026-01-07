import os
import random
import numpy as np
import pandas as pd
import tensorflow as tf
from tensorflow.keras.models import Sequential, load_model
from tensorflow.keras.layers import LSTM, Dense, Dropout, Input
from tensorflow.keras.callbacks import EarlyStopping
from sklearn.preprocessing import MinMaxScaler
import joblib

# Semilla Global para Estabilidad "Guaracha"
SEED = 42
os.environ['PYTHONHASHSEED'] = str(SEED)
random.seed(SEED)
np.random.seed(SEED)
tf.random.set_seed(SEED)

class NeuralTraderMultivariable:
    def __init__(self, sequence_length=60):
        self.sequence_length = sequence_length
        self.model = None
        self.scaler = MinMaxScaler(feature_range=(0, 1))
        # Usamos extensión .keras nativa para evitar warnings, pero mantenemos soporte legacy
        self.model_path = "model_guaracha.keras" 
        self.scaler_path = "scaler_guaracha.pkl"

    def create_model(self, input_shape):
        model = Sequential()
        model.add(Input(shape=input_shape))
        
        # Arquitectura "Guaracha Strong" (Más robusta)
        # return_sequences=True pasa la secuencia completa a la siguiente capa LSTM
        model.add(LSTM(128, return_sequences=True))
        model.add(Dropout(0.3)) # Evita memorizar ruido (Overfitting)
        
        # Segunda capa LSTM
        model.add(LSTM(64, return_sequences=False))
        model.add(Dropout(0.3))
        
        # Capas Densas para decisión
        model.add(Dense(32, activation='relu'))
        model.add(Dense(1, activation='sigmoid')) # Probabilidad 0 a 1
        
        model.compile(optimizer='adam', loss='binary_crossentropy', metrics=['accuracy'])
        self.model = model
        return model

    def prepare_data(self, df):
        # Seleccionar features multivariables
        features = ['close', 'rsi', 'bollinger_upper', 'bollinger_lower', 'macd', 'macd_signal', 'volume']
        
        # Filtrar solo las columnas que existen
        present_features = [f for f in features if f in df.columns]
        
        dataset = df[present_features].values
        
        # Escalar
        # IMPORTANTE: Si ya tenemos scaler entrenado (self.scaler), ¿deberíamos re-entrenarlo?
        # En training: SI. En prediction: NO.
        # Esta función es ambigua. Asumimos uso para TRAINING por defecto si fit_transform.
        # Para evitar líos, usaremos fit_transform aquí y asumiremos que al cargar modelo se carga el scaler.
        
        if hasattr(self.scaler, 'n_features_in_'):
            # Si ya está ajustado (ej. predicción), usamos transform
            # PERO en training queremos re-ajustar.
            # Riesgo: Si llamamos prepare_data en train, sobreescribimos. Bien.
            try:
                # Intento transform primero si es predicción...? No, mejor explicit
                scaled_data = self.scaler.fit_transform(dataset)
            except:
                scaled_data = self.scaler.fit_transform(dataset)
        else:
            scaled_data = self.scaler.fit_transform(dataset)
        
        X, y = [], []
        for i in range(self.sequence_length, len(scaled_data)):
            X.append(scaled_data[i-self.sequence_length:i])
            
            # Target: 1 si el precio de cierre actual > precio de cierre anterior
            # scaled_data[i] es el tiempo T. scaled_data[i-1] es T-1.
            # Queremos predecir si T > T-1 basándonos en ventana T-60 a T-1.
            # X[i] contiene data de i-60 a i-1.
            # Y[i] contiene respuesta de i > i-1.
            
            is_up = 1 if scaled_data[i][0] > scaled_data[i-1][0] else 0
            y.append(is_up)
            
        return np.array(X), np.array(y)

    def train(self, csv_path):
        from app.analysis import MarketAnalyzer
        print("Cargando y procesando datos (Modo Guaracha Strong)...")
        df_raw = pd.read_csv(csv_path)
        
        if 'timestamp' in df_raw.columns:
            df_raw.rename(columns={'timestamp': 'from'}, inplace=True)
            
        analyzer = MarketAnalyzer()
        df = analyzer.prepare_data(df_raw.to_dict('records'))
        df = analyzer.add_technical_indicators(df)
        df.dropna(inplace=True) 
        
        # Reiniciar scaler para entrenamiento nuevo
        self.scaler = MinMaxScaler(feature_range=(0, 1))
        
        X, y = self.prepare_data(df)
        
        print(f"Features: {X.shape[2]} (Forma: {X.shape})")
        print(f"Entrenando con {len(X)} muestras...")
        
        self.create_model((X.shape[1], X.shape[2]))
        
        # Callbacks para entrenamiento profesional
        early_stopping = EarlyStopping(
            monitor='loss', 
            patience=5, 
            restore_best_weights=True
        )
        
        self.model.fit(
            X, y, 
            epochs=50, # Más épocas para aprender bien
            batch_size=32, 
            callbacks=[early_stopping],
            verbose=1
        )
        
        self.model.save(self.model_path)
        joblib.dump(self.scaler, self.scaler_path)
        print("Cerebro Fortalecido guardado.")

    def load(self):
        # Intentar cargar .keras primero
        if os.path.exists(self.model_path) and os.path.exists(self.scaler_path):
            self.model = load_model(self.model_path)
            self.scaler = joblib.load(self.scaler_path)
            return True
        # Soporte legacy
        elif os.path.exists("model_guaracha.h5") and os.path.exists(self.scaler_path):
             self.model = load_model("model_guaracha.h5")
             self.scaler = joblib.load(self.scaler_path)
             return True
        return False

    def predict(self, df):
        if not self.model or not self.scaler:
            return None
            
        features = ['close', 'rsi', 'bollinger_upper', 'bollinger_lower', 'macd', 'macd_signal', 'volume']
        present_features = [f for f in features if f in df.columns]
        
        if len(df) < self.sequence_length:
            return None
            
        dataset = df[present_features].values
        
        # IMPORTANTE: Usar transform, NO fit_transform (usar la escala del entrenamiento)
        # El scaler debe haber sido cargado previamente con load()
        try:
            scaled_data = self.scaler.transform(dataset)
        except Exception as e:
            print(f"Error scaling data: {e}. Scaler params: {self.scaler.n_features_in_} vs Input: {dataset.shape[1]}")
            return None
        
        last_sequence = scaled_data[-self.sequence_length:]
        last_sequence = np.reshape(last_sequence, (1, self.sequence_length, last_sequence.shape[1]))
        
        prediction = self.model.predict(last_sequence, verbose=0)
        return prediction[0][0]
