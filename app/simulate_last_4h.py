import pandas as pd
import google.generativeai as genai
import time
import re
# from app.config import GOOGLE_API_KEY # Hardcoded for script safety

GOOGLE_API_KEY = "AIzaSyD3x7u6GNSLNIVXN8OuE3euORi9wZDcy6c"
genai.configure(api_key=GOOGLE_API_KEY)
model = genai.GenerativeModel('gemini-pro-latest')

def ask_gemini(df_window):
    latest = df_window.tail(60).to_string(index=False)
    prompt = f"""
    Act as a Quantitative Systematic Trader. Analyze these 60 candles for EURUSD-op (1 min timeframe).
    
    DATA (Last 1 hour):
    {latest}
    
    TASK: Identify High Probability setups for the next 1 minute.
    
    CRITERIA: Look for strong trend continuations or clear reversals at key levels.
    Analyze Volume, Close Price, and recent Volatility.
    
    RESPONSE FORMAT:
    ACTION: [CALL, PUT, or WAIT]
    CONFIDENCE: [0-100]
    REASON: [Short logical explanation]
    """
    try:
        response = model.generate_content(prompt)
        return response.text.strip()
    except Exception as e:
        return f"Error: {e}"

def parse_response(text):
    raw_upper = text.upper()
    action = "WAIT"
    confidence = 0.0
    
    if "ACTION: CALL" in raw_upper or '"ACTION": "CALL"' in raw_upper: action = "CALL"
    elif "ACTION: PUT" in raw_upper or '"ACTION": "PUT"' in raw_upper: action = "PUT"
    
    match = re.search(r'CONFIDENCE[:\s]+(\d+)', text, re.IGNORECASE)
    if match: confidence = float(match.group(1))
    
    return action, confidence

def run_simulation():
    print("🚀 INICIANDO SIMULACIÓN (Últimas 4 horas de datos)...")
    
    # Cargar datos
    try:
        df = pd.read_csv('candles_24h.csv')
        df['from'] = pd.to_datetime(df['from'], unit='s')
        df = df.sort_values('from').reset_index(drop=True)
    except:
        print("❌ No se encontró candles_24h.csv")
        return

    # Usar las últimas 250 velas (approx 4 horas + contexto)
    # Necesitamos 60 de contexto + 1 para predecir
    total_candles = len(df)
    start_index = max(0, total_candles - 300) 
    
    dataset = df.iloc[start_index:].reset_index(drop=True)
    print(f"📊 Datos cargados: {len(dataset)} velas (de {dataset['from'].iloc[0]} a {dataset['from'].iloc[-1]})")
    
    trades = []
    wins = 0
    losses = 0
    pushes = 0
    balance = 0
    
    # Loop de simulación
    # Vamos a iterar hasta len(dataset) - 2 (para tener resultado futuro)
    # Saltamos de 2 en 2 para simular trades no superpuestos y ahorrar tiempo
    step = 2 
    
    for i in range(60, len(dataset)-1, step):
        # Ventana de 60 velas pasadas
        window = dataset.iloc[i-60:i]
        
        # Vela objetivo (la que intentamos predecir) es la 'i'
        target_candle = dataset.iloc[i]
        next_close = target_candle['close']
        current_close = window.iloc[-1]['close']
        
        # Consultar IA
        response = ask_gemini(window)
        action, confidence = parse_response(response)
        
        # Lógica de Trading (Umbral 70%)
        if action in ["CALL", "PUT"] and confidence >= 70:
            result = "PENDING"
            pl = 0
            
            if action == "CALL":
                if next_close > current_close:
                    result = "WIN"
                    pl = 3320 # 83% de 4000
                    wins += 1
                elif next_close < current_close:
                    result = "LOSS"
                    pl = -4000
                    losses += 1
                else:
                    result = "PUSH"
                    pushes += 1
                    
            elif action == "PUT":
                if next_close < current_close:
                    result = "WIN"
                    pl = 3320
                    wins += 1
                elif next_close > current_close:
                    result = "LOSS"
                    pl = -4000
                    losses += 1
                else:
                    result = "PUSH"
                    pushes += 1
            
            balance += pl
            print(f"⏰ {target_candle['from'].strftime('%H:%M')} | {action} ({confidence}%) | {result} | Balance: {balance:+}")
            trades.append(result)
        else:
            print(f"⏰ {target_candle['from'].strftime('%H:%M')} | WAIT ({confidence}%)")
            
        time.sleep(1) # Evitar rate limit

    # Resultados Finales
    total = wins + losses + pushes
    wr = (wins / (wins+losses) * 100) if (wins+losses) > 0 else 0
    
    print("\n" + "="*60)
    print("📊 RESULTADOS SIMULACIÓN (Últimas ~4h)")
    print("="*60)
    print(f"Total Trades: {total}")
    print(f"✅ Wins: {wins}")
    print(f"❌ Losses: {losses}")
    print(f"⚪ Pushes: {pushes}")
    print(f"📈 Win Rate: {wr:.2f}%")
    print(f"💰 P&L Estimado: ${balance:+,} COP")
    print("="*60)

if __name__ == "__main__":
    run_simulation()
