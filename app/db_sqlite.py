import sqlite3
import json
import time
import pandas as pd
import os

DB_FILE = "trading_bot.db"

class SQLiteManager:
    def __init__(self, db_path=DB_FILE):
        self.db_path = db_path
        self._init_db()

    def _init_db(self):
        """Initialize the database schema if not exists"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Create Trades Table
            cursor.execute('''
            CREATE TABLE IF NOT EXISTS trades (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                trade_id TEXT UNIQUE,
                timestamp REAL,
                asset TEXT,
                direction TEXT,
                amount REAL,
                confidence REAL,
                ai_reason TEXT,
                market_data TEXT,
                result TEXT DEFAULT 'PENDING',
                profit REAL DEFAULT 0.0,
                model_id TEXT
            )
            ''')
            
            conn.commit()
            conn.close()
            print(f"✅ SQLite Database initialized: {self.db_path}")
        except Exception as e:
            print(f"❌ SQLite Init Error: {e}")

    def save_trade(self, asset, direction, amount, confidence, market_data, trade_id="", result="PENDING", profit=0.0, timestamp=None, ai_reason=""):
        """Save trade execution data"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            if not timestamp:
                timestamp = time.time()
                
            # Serialize market data if list/dict
            if isinstance(market_data, (list, dict)):
                market_data = json.dumps(market_data)

            cursor.execute('''
            INSERT INTO trades (trade_id, timestamp, asset, direction, amount, confidence, ai_reason, market_data, result, profit, model_id)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                str(trade_id), 
                float(timestamp), 
                str(asset), 
                str(direction), 
                float(amount), 
                float(confidence), 
                str(ai_reason), 
                str(market_data), 
                str(result), 
                float(profit),
                "Groq_LLaMA_3"
            ))
            
            conn.commit()
            conn.close()
            print(f"✅ Trade saved to SQLite: {trade_id}")
            return True
            
        except Exception as e:
            print(f"❌ SQLite Save Error: {e}")
            return False

    def update_trade_result(self, trade_id, result, profit):
        """Update the result of a closed trade"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
            UPDATE trades 
            SET result = ?, profit = ?
            WHERE trade_id = ?
            ''', (str(result), float(profit), str(trade_id)))
            
            if cursor.rowcount > 0:
                print(f"✅ Result updated in SQLite: {result} | ${profit}")
            else:
                print(f"⚠️ Warning: Trade ID {trade_id} not found for update.")
                
            conn.commit()
            conn.close()
            
        except Exception as e:
            print(f"❌ SQLite Update Error: {e}")

    def get_training_data(self):
        """Fetch all trades for training"""
        try:
            conn = sqlite3.connect(self.db_path)
            df = pd.read_sql_query("SELECT * FROM trades WHERE result != 'PENDING'", conn)
            conn.close()
            return df
        except Exception as e:
            print(f"❌ Error fetching training data: {e}")
            return pd.DataFrame()

if __name__ == "__main__":
    db = SQLiteManager()
    # Test
    # db.save_trade("TEST", "CALL", 10, 0.99, "{}", "test_id_123", ai_reason="Test")
    # db.update_trade_result("test_id_123", "WIN", 8.5)
