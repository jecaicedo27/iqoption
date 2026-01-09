import sqlite3
import pandas as pd
from datetime import datetime

conn = sqlite3.connect('trading_bot.db')

try:
    df = pd.read_sql_query("SELECT * FROM trades ORDER BY timestamp DESC LIMIT 20", conn)
    
    if df.empty:
        print("📭 No hay operaciones registradas aún en la nueva DB.")
    else:
        print(f"📊 ÚLTIMAS OPERACIONES ({len(df)}):")
        wins = 0
        losses = 0
        pnl = 0
        
        for index, row in df.iterrows():
            ts = datetime.fromtimestamp(row['timestamp']).strftime('%H:%M:%S')
            res = row['result']
            profit = row['profit']
            asset = row['asset']
            direction = row['direction']
            
            pnl += profit
            emoji = "⏳"
            if res == "WIN": 
                wins += 1
                emoji = "✅"
            elif res == "LOSS": 
                losses += 1
                emoji = "❌"
            elif res == "PENDING":
                emoji = "⏳"
            
            print(f"{ts} | {asset} | {direction} | {emoji} {res} (${profit})")
            
        print("-" * 30)
        print(f"🏆 WINS: {wins} | 💀 LOSSES: {losses}")
        print(f"💰 P&L TOTAL (Últimas 20): ${pnl:.2f}")

except Exception as e:
    print(f"Error: {e}")
finally:
    conn.close()
