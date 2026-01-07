import sys
from questdb.ingress import Sender, IngressError, TimestampNanos
import pandas as pd
import time
import requests
import io

class QuestDBManager:
    def __init__(self, host='localhost', ilp_port=9009, rest_port=9000):
        self.host = host
        self.ilp_port = ilp_port
        self.rest_port = rest_port
        # Note: QuestDB default ILP port is 9009
        
    def save_trade(self, asset, price, prediction, confidence, features, result=None, profit=0.0, timestamp=None, model_name="Unknown"):
        """
        Guarda una operación en QuestDB usando ILP (Alta Velocidad).
        """
        try:
            # Use Sender.from_conf for TCP ILP
            conf = f'tcp::addr={self.host}:{self.ilp_port};'
            with Sender.from_conf(conf) as sender:
                # Features formatting (as string or individual columns?)
                # To be useful for training, we should save critical features as columns
                # or the entire vector as a string blob.
                # For "Re-training from errors", we need the exact input vector.
                
                # Features is usually a list of recent values.
                # Let's save 3 key inputs: Close, Vol, RSI (last values)
                # But actually we operate on sequences. Saving 60 candles is heavy.
                # Better: Save the 'snapshot' of the moment.
                
                # For now, simplistic structure:
                # Sanitize Features
                close_v = float(features[-1][0]) if len(features) > 0 else 0.0
                vol_v = int(features[-1][1]) if len(features) > 0 else 0
                rsi_v = float(features[-1][2]) if len(features) > 0 else 0.0
                
                # Handle Timestamp
                if timestamp:
                    # Convert float seconds to nanoseconds int and wrap
                    ts = TimestampNanos(int(timestamp * 1e9))
                else:
                    ts = TimestampNanos.now()
                
                sender.row(
                    'trades_memory',
                    symbols={
                        'asset': str(asset), 
                        'prediction': str(prediction), 
                        'result': str(result),
                        'model_id': str(model_name) # NEW: Bot Identity
                    },
                    columns={
                        'price': float(price),
                        'confidence': float(confidence),
                        'profit': float(profit),
                        'features_json': str(features), # Backup
                        'close_val': close_v, 
                        'vol_val': vol_v,
                        'rsi_val': rsi_v
                    },
                    at=ts
                )
                sender.flush()
                print(f"✅ Trade guardado en QuestDB: {asset} | {prediction} | Conf: {confidence:.2f}")
        except IngressError as e:
            print(f"⚠️ QuestDB Error: {e}")
        except Exception as e:
            print(f"⚠️ DB Error: {e}")
    
    def update_trade_result(self, asset, timestamp, result, profit):
        """
        Actualiza el resultado de un trade existente usando REST API.
        """
        try:
            # Convert timestamp to microseconds for QuestDB
            ts_micros = int(timestamp * 1e6)
            
            # Use UPDATE query via REST
            query = f"""
            UPDATE trades_memory 
            SET result = '{result}', profit = {profit}
            WHERE asset = '{asset}' 
            AND timestamp = '{ts_micros}'
            """
            
            url = f"http://{self.host}:{self.rest_port}/exec"
            response = requests.get(url, params={"query": query})
            
            if response.status_code == 200:
                print(f"✅ Resultado actualizado: {result} | P&L: ${profit:+.0f}")
            else:
                print(f"⚠️ Error actualizando resultado: {response.text}")
                
        except Exception as e:
            print(f"⚠️ Error al actualizar: {e}")
    
    def get_training_data(self, valid_only=True):
        """
        Descarga datos de entrenamiento desde QuestDB (REST API -> Pandas).
        """
        query = "SELECT * FROM trades_memory"
        if valid_only:
            query += " WHERE result != 'None'"
            
        try:
            r = requests.get(f"http://{self.host}:{self.rest_port}/exec", params={'query': query, 'fmt': 'csv'})
            if r.status_code == 200:
                df = pd.read_csv(io.StringIO(r.text))
                return df
            else:
                print(f"Error Querying QuestDB: {r.text}")
                return None
        except Exception as e:
            print(f"Connection Error: {e}")
            return None

if __name__ == "__main__":
    db = QuestDBManager()
    # Test Save
    db.save_trade("EURUSD", 1.05, "CALL", 0.88, [[1.0, 200, 50]], "WIN", 85.0)
    print("Test Insert Done. Checking...")
    time.sleep(1)
    df = db.get_training_data(valid_only=False)
    print(df)
