import sqlite3
import pandas as pd
from datetime import datetime
from tabulate import tabulate

conn = sqlite3.connect('trading_bot.db')

try:
    # Get all trades from the last few hours
    # We filter out PENDING to focus on closed trades
    df = pd.read_sql_query("SELECT * FROM trades WHERE result IN ('WIN', 'LOSS') ORDER BY timestamp DESC LIMIT 100", conn)
    
    if df.empty:
        print("📭 No hay operaciones CERRADAS (WIN/LOSS) registradas aún en la nueva DB.")
    else:
        # Prepare table data
        table_data = []
        wins = 0
        losses = 0
        pnl = 0
        
        for index, row in df.iterrows():
            ts = datetime.fromtimestamp(row['timestamp']).strftime('%H:%M:%S')
            res = row['result']
            profit_val = row['profit']
            asset = row['asset']
            direction = row['direction'].upper()
            ai_conf = row['confidence']
            
            pnl += profit_val
            
            res_icon = "✅ WIN" if res == "WIN" else "❌ LOSS"
            profit_str = f"+${profit_val:.2f}" if profit_val > 0 else f"-${abs(profit_val):.2f}"
            
            if res == "WIN": wins += 1
            else: losses += 1
            
            table_data.append([ts, asset, direction, f"{ai_conf}%", res_icon, profit_str])
            
        # Calculate metrics
        total = wins + losses
        win_rate = (wins / total * 100) if total > 0 else 0
        
        print(f"\n📊 REPORTE DE RENDIMIENTO (Últimas {total} Ops)")
        print("="*65)
        print(tabulate(table_data, headers=["Hora", "Activo", "Dir", "Conf", "Resultado", "P&L"], tablefmt="grid"))
        print("="*65)
        print(f"🏆 GANADAS: {wins}  |  💀 PERDIDAS: {losses}")
        print(f"🎯 EFECTIVIDAD: {win_rate:.1f}%")
        print(f"💰 P&L NETO: ${pnl:.2f}")
        print("="*65)

except Exception as e:
    print(f"Error: {e}")
finally:
    conn.close()
