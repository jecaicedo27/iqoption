import pandas as pd
import requests
import json

QUESTDB_URL = "http://localhost:9000/exec"

def get_last_trades():
    query = "SELECT * FROM trades ORDER BY timestamp DESC LIMIT 5"
    try:
        r = requests.get(QUESTDB_URL, params={'query': query})
        data = r.json()
        
        if 'dataset' in data:
            columns = [c['name'] for c in data['columns']]
            df = pd.DataFrame(data['dataset'], columns=columns)
            
            print("📊 ULTIMAS 5 OPERACIONES EN DB:\n")
            for index, row in df.iterrows():
                print(f"🆔 ID: {row.get('trade_id', 'N/A')}")
                print(f"⏰ Time: {row.get('timestamp', 'N/A')}")
                print(f"💰 Asset: {row.get('asset', 'N/A')} | {row.get('direction', 'N/A').upper()}")
                print(f"🧠 Confidence: {row.get('confidence', 'N/A')}%")
                print(f"📝 Reason (Preview): {str(row.get('ai_reason', ''))[:100]}...")
                print("-" * 50)
        else:
            print("⚠️ No hay datos o respuesta vacía.")
            print(data)
            
    except Exception as e:
        print(f"❌ Error conectando a DB: {e}")

if __name__ == "__main__":
    get_last_trades()
