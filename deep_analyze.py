import requests
import pandas as pd
import numpy as np

QUESTDB_URL = "http://localhost:9000/exec"

def analyze():
    query = "SELECT * FROM trades_memory WHERE timestamp >= '2026-01-07T00:00:00.000000Z' ORDER BY timestamp"
    r = requests.get(QUESTDB_URL, params={'query': query})
    data = r.json()
    cols = [c['name'] for c in data['columns']]
    df = pd.DataFrame(data['dataset'], columns=cols)
    df['timestamp'] = pd.to_datetime(df['timestamp'])
    
    # 1. Stats by hour
    df['hour'] = df['timestamp'].dt.hour
    hourly = df.groupby('hour').agg(
        trades=('result', 'count'),
        wins=('result', lambda x: (x == 'WIN').sum()),
        profit=('profit', 'sum')
    )
    hourly['win_rate'] = (hourly['wins'] / hourly['trades'] * 100)
    
    print("--- ANÁLISIS POR HORA (HOY) ---")
    print(hourly.to_string())
    
    # 2. Key Reason analysis
    print("\n--- RAZONES DE 'WIN' (Top 3) ---")
    wins = df[df['result'] == 'WIN']['ai_reason'].dropna().head(3)
    for r in wins:
        print(f"✅ {r[:150]}...")
        
    print("\n--- RAZONES DE 'LOSS' (Top 3) ---")
    losses = df[df['result'] == 'LOSS']['ai_reason'].dropna().head(3)
    for r in losses:
        print(f"❌ {r[:150]}...")

if __name__ == "__main__":
    analyze()
