import requests
import pandas as pd
import json

QUESTDB_URL = "http://localhost:9000/exec"

def get_recent_trades():
    query = "SELECT * FROM trades_memory ORDER BY timestamp DESC LIMIT 15"
    try:
        r = requests.get(QUESTDB_URL, params={'query': query})
        r.raise_for_status()
        data = r.json()
        
        if 'dataset' in data and data['dataset']:
            columns = [c['name'] for c in data['columns']]
            df = pd.DataFrame(data['dataset'], columns=columns)
            
            print(f"📊 Columnas encontradas: {columns}")
            
            # Select only existing columns to avoid error
            cols_to_show = ['timestamp', 'asset', 'direction', 'result', 'profit']
            if 'trade_id' in columns:
                cols_to_show.append('trade_id')
            
            print("\n✅ ÚLTIMAS 15 OPERACIONES EN BASE DE DATOS:")
            print(df[cols_to_show].to_string(index=False))
            
            # Verify market_data presence
            if 'market_data' in df.columns:
                print("\n✅ COLUMNA 'market_data' DETECTADA (Datos de velas guardados)")
            else:
                print("\n❌ ALERTA: NO SE ENCONTRÓ COLUMNA 'market_data'")
                
        else:
            print("⚠️ La tabla 'trades_memory' parece estar vacía o no tiene datos recientes.")
            
    except Exception as e:
        print(f"❌ Error consultando QuestDB: {e}")

if __name__ == "__main__":
    get_recent_trades()
