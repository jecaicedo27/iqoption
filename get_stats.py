import requests
import pandas as pd

QUESTDB_URL = "http://localhost:9000/exec"

def get_stats():
    query = "SELECT result, profit FROM trades_memory WHERE timestamp >= '2026-01-07T00:00:00.000000Z'"
    try:
        r = requests.get(QUESTDB_URL, params={'query': query})
        r.raise_for_status()
        data = r.json()
        
        if 'dataset' in data and data['dataset']:
            columns = [c['name'] for c in data['columns']]
            df = pd.DataFrame(data['dataset'], columns=columns)
            
            total_trades = len(df)
            wins = len(df[df['result'] == 'WIN'])
            losses = len(df[df['result'] == 'LOSS'])
            pushes = len(df[df['result'] == 'PUSH'])
            total_profit = df['profit'].sum()
            
            print("--- ESTADÍSTICAS HOY (7 ENE) ---")
            print(f"Total Trades: {total_trades}")
            print(f"Wins: {wins}")
            print(f"Losses: {losses}")
            print(f"Pushes/Pending: {total_trades - wins - losses}")
            print(f"P&L Total: ${total_profit:,.2f} COP")
            
            wr = (wins / (wins + losses) * 100) if (wins + losses) > 0 else 0
            print(f"Win Rate: {wr:.2f}%")
        else:
            print("No se encontraron trades hoy.")
            
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    get_stats()
