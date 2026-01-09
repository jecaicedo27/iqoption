import sys
from questdb.ingress import Sender, IngressError, TimestampNanos
import pandas as pd
import time
import requests
import io
import csv
import os

class QuestDBManager:
    def __init__(self, host='localhost', ilp_port=9009, rest_port=9000):
        self.host = host
        self.ilp_port = ilp_port
        self.rest_port = rest_port
        # Note: QuestDB default ILP port is 9009
        
    def save_to_csv_backup(self, asset, direction, amount, confidence, market_data, trade_id, ai_reason, timestamp):
        try:
            file_exists = os.path.isfile("trades_backup.csv")
            ts_str = str(timestamp) if timestamp else str(time.time())
            
            with open("trades_backup.csv", "a", newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                if not file_exists:
                    writer.writerow(["timestamp", "trade_id", "asset", "direction", "amount", "confidence", "ai_reason", "market_data"])
                
                writer.writerow([ts_str, trade_id, asset, direction, amount, confidence, ai_reason, str(market_data)])
                print("✅ Trade saved to CSV BACKUP (Safe!)")
        except Exception as e:
            print(f"❌ CRITICAL CSV ERROR: {e}")

    def save_trade(self, asset, direction, amount, confidence, market_data, trade_id="", result="PENDING", profit=0.0, timestamp=None, ai_reason=""):
        """
        Guarda trade con TODOS los datos para entrenamiento (incluyendo snapshot del mercado).
        """
        try:
            # Use Sender.from_conf for TCP ILP
            conf = f'tcp::addr={self.host}:{self.ilp_port};'
            with Sender.from_conf(conf) as sender:
                # Handle Timestamp
                if timestamp:
                    ts = TimestampNanos(int(timestamp * 1e9))
                else:
                    ts = TimestampNanos.now()
                
                sender.row(
                    'trades_memory',
                    symbols={
                        'asset': str(asset), 
                        'direction': str(direction),
                        'result': str(result),
                        'model_id': "Gemini_Pro_Real",
                        'trade_id': str(trade_id) # ✅ Storing ID symbol
                    },
                    columns={
                        'amount': float(amount),
                        'confidence': float(confidence),
                        'profit': float(profit),
                        'ai_reason': str(ai_reason)[:255],
                        'market_data': str(market_data) # ✅ DATOS CRÍTICOS PARA ENTRENAMIENTO
                    },
                    at=ts
                )
                sender.flush()
                print(f"✅ Trade guardado en DB para entrenamiento: {direction} | Conf: {confidence}%")
        except (IngressError, Exception) as e:
            print(f"⚠️ DB Save Error: {e}. Switching to CSV Backup...")
            self.save_to_csv_backup(asset, direction, amount, confidence, market_data, trade_id, ai_reason, timestamp)
    
    def update_trade_result(self, trade_id, result, profit):
        """
        Actualiza el resultado de un trade existente usando REST API.
        """
        try:
            # Use UPDATE query via REST matches by trade_id
            query = f"""
            UPDATE trades_memory 
            SET result = '{result}', profit = {profit}
            WHERE trade_id = '{trade_id}'
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
