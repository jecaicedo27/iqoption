import pandas as pd
import google.generativeai as genai
import requests
from app.config import GOOGLE_API_KEY

genai.configure(api_key=GOOGLE_API_KEY)
# Use 2.0 Flash as in the main bot
model = genai.GenerativeModel('gemini-2.0-flash-exp')

QUESTDB_URL = "http://localhost:9000/exec"

def test():
    # 2:30 AM (approx index 90 in the 1-3 AM range)
    query = "SELECT * FROM candles_history WHERE asset = 'EURUSD-op' AND timestamp >= '2026-01-07T01:30:00Z' AND timestamp <= '2026-01-07T02:30:00Z' ORDER BY timestamp ASC"
    r = requests.get(QUESTDB_URL, params={'query': query})
    data = r.json()
    cols = [c['name'] for c in data['columns']]
    df = pd.DataFrame(data['dataset'], columns=cols)
    
    latest = df.tail(60)[['timestamp', 'open', 'high', 'low', 'close', 'volume']]
    
    prompt = f"""
    Act as a Quantitative Systematic Trader. Analyze these 60s candles for EURUSD-op.
    
    DATA (Last 1 hour):
    {latest.to_string(index=False)}
    
    TASK: Identify High Probability setups for the next 1 minute.
    
    CRITERIA: Look for strong trend continuations or clear reversals at key levels.
    Analyze Volume, Close Price, and recent Volatility.
    
    RESPONSE FORMAT:
    ACTION: [CALL, PUT, or WAIT]
    CONFIDENCE: [0-100]
    REASON: [Short logical explanation]
    """
    
    print("--- PROMPT ---")
    print(prompt)
    
    print("\n--- RESPONSE ---")
    print(model.generate_content(prompt).text)

if __name__ == "__main__":
    test()
