import pandas as pd
import numpy as np

class MarketAnalyzer:
    def __init__(self):
        pass

    def prepare_data(self, candles):
        """
        Convierte la lista de velas en un DataFrame de Pandas.
        """
        df = pd.DataFrame(candles)
        # Convertir timestamp a datetime si es necesario
        df['from'] = pd.to_datetime(df['from'], unit='s')
        
        # Asegurarse de que los precios sean float
        for col in ['open', 'close', 'min', 'max', 'volume']:
            df[col] = df[col].astype(float)
            
        return df

    def calculate_sma(self, df, period=14, column='close'):
        """
        Calcula la Media Móvil Simple (SMA).
        """
        return df[column].rolling(window=period).mean()

    def calculate_rsi(self, df, period=14, column='close'):
        """
        Calcula el Índice de Fuerza Relativa (RSI).
        """
        delta = df[column].diff(1)
        gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()

        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))
        return rsi

    def calculate_bollinger(self, df, period=20, std_dev=2, column='close'):
        """
        Calcula Bandas de Bollinger.
        """
        sma = df[column].rolling(window=period).mean()
        std = df[column].rolling(window=period).std()
        df['bollinger_upper'] = sma + (std * std_dev)
        df['bollinger_lower'] = sma - (std * std_dev)
        return df

    def calculate_macd(self, df, fast=12, slow=26, signal=9, column='close'):
        """
        Calcula MACD.
        """
        exp1 = df[column].ewm(span=fast, adjust=False).mean()
        exp2 = df[column].ewm(span=slow, adjust=False).mean()
        df['macd'] = exp1 - exp2
        df['macd_signal'] = df['macd'].ewm(span=signal, adjust=False).mean()
        return df

    def calculate_ema(self, df, period=200, column='close'):
        """
        Calcula la Media Móvil Exponencial (EMA).
        """
        return df[column].ewm(span=period, adjust=False).mean()

    def calculate_stochastic(self, df, period=14, smooth_k=3):
        """
        Calcula Oscilador Estocástico (K% y D%).
        """
        low_min = df['min'].rolling(window=period).min()
        high_max = df['max'].rolling(window=period).max()
        
        # %K
        k_percent = 100 * ((df['close'] - low_min) / (high_max - low_min))
        # Smooth K
        k_smooth = k_percent.rolling(window=smooth_k).mean()
        
        return k_smooth

    def calculate_atr(self, df, period=14):
        """
        Calcula el Average True Range (ATR).
        """
        high_low = df['max'] - df['min']
        high_close = np.abs(df['max'] - df['close'].shift())
        low_close = np.abs(df['min'] - df['close'].shift())
        
        ranges = pd.concat([high_low, high_close, low_close], axis=1)
        true_range = ranges.max(axis=1)
        
        return true_range.rolling(window=period).mean()

    def add_technical_indicators(self, df):
        """
        Agrega todos los indicadores técnicos al DataFrame.
        """
        df['rsi'] = self.calculate_rsi(df)
        df = self.calculate_bollinger(df)
        df = self.calculate_macd(df)
        df['ema_200'] = self.calculate_ema(df, period=200)
        df['atr'] = self.calculate_atr(df, period=14)
        df['stoch_k'] = self.calculate_stochastic(df, period=14)
        
        
        
        # Rellenar NaN (generados por las ventanas de los indicadores)
        df.fillna(method='bfill', inplace=True)
        df.fillna(method='ffill', inplace=True)
        return df

    def analyze_market(self, candles):
        """
        Realiza un análisis completo de las velas proporcionadas.
        """
        if not candles:
            return None

        df = self.prepare_data(candles)
        df = self.add_technical_indicators(df)
        
        # Retornar el último registro
        return df.iloc[-1]
