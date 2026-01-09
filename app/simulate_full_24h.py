import pandas as pd
import google.generativeai as genai
import time
import re
# from app.config import GOOGLE_API_KEY

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
    print("🚀 INICIANDO SIMULACIÓN COMPLETA (24 HORAS)...")
    
    # Cargar datos
    try:
        df = pd.read_csv('candles_24h.csv')
        df['from'] = pd.to_datetime(df['from'], unit='s')
        df = df.sort_values('from').reset_index(drop=True)
    except:
        print("❌ No se encontró candles_24h.csv")
        return

    print(f"📊 Datos totales: {len(df)} velas")
    print(f"📅 Rango: {df['from'].iloc[0]} -> {df['from'].iloc[-1]}")
    
    wins = 0
    losses = 0
    pushes = 0
    balance = 0
    trades_count = 0
    
    # Empezamos en vela 60 para tener contexto
    # Step = 3 para velocidad (analiza cada 3 mins) -> aprox 300 llamadas a API
    step = 3 
    
    for i in range(60, len(df)-1, step):
        t_start = time.time()
        
        window = df.iloc[i-60:i]
        target_candle = df.iloc[i]
        
        # Simular delay de red/API pequeñísimo
        # Llamar a Gemini
        try:
            response = ask_gemini(window)
            action, confidence = parse_response(response)
        except:
            action = "WAIT"
            confidence = 0
        
        if action in ["CALL", "PUT"] and confidence >= 70:
            trades_count += 1
            result = "PENDING"
            pl = 0
            
            # Resultado real (vela siguiente)
            # En binarias reales, entramos al cierre de vela i-1 y el resultado es vela i
            # Aquí 'window' llega hasta i-1, así que predecimos vela i.
            # Comparamos cierre de vela i (target) vs cierre de vela i-1 (last known)
            
            open_price = target_candle['open'] # Precio apertura vela actual (entrada)
            close_price = target_candle['close'] # Precio cierre vela actual (salida)
            
            # Ojo: En IQ entras y expira en 1 min.
            # Básicamente: Si CALL, Close > Open de esa vela
            
            if action == "CALL":
                if close_price > open_price:
                    result = "WIN"
                    pl = 3320
                    wins += 1
                elif close_price < open_price:
                    result = "LOSS"
                    pl = -4000
                    losses += 1
                else: 
                    result = "PUSH"
                    pushes += 1
                    
            elif action == "PUT":
                if close_price < open_price:
                    result = "WIN"
                    pl = 3320
                    wins += 1
                elif close_price > open_price:
                    result = "LOSS"
                    pl = -4000
                    losses += 1
                else:
                    result = "PUSH"
                    pushes += 1
            
            balance += pl
            symbol = "✅" if result == "WIN" else "❌" if result == "LOSS" else "aa"
            print(f"⏰ {target_candle['from'].strftime('%H:%M')} | {action} ({confidence}%) | {symbol} {result} | Bal: {balance:+}")
        else:
            # print(f".", end="", flush=True) # Progreso mudo
            pass
            
        # Control de velocidad para no saturar API
        time.sleep(0.5)

    trade_total = wins + losses + pushes
    wr = (wins / (wins+losses) * 100) if (wins+losses) > 0 else 0
    
    print("\n" + "="*60)
    print("📊 RESULTADOS SIMULACIÓN 24H (Muestreo cada 3 min)")
    print("="*60)
    print(f"Total Trades Simulados: {trade_total}")
    print(f"✅ Wins: {wins}")
    print(f"❌ Losses: {losses}")
    print(f"📈 Win Rate: {wr:.2f}%")
    print(f"💰 P&L Proyectado: ${balance:+,} COP")
    print("="*60)

if __name__ == "__main__":
    run_simulation()
