import pandas as pd
import google.generativeai as genai
import time
# from app.config import GOOGLE_API_KEY


# Configurar modelo igual que el bot en vivo
genai.configure(api_key="AIzaSyD3x7u6GNSLNIVXN8OuE3euORi9wZDcy6c")
model = genai.GenerativeModel('gemini-pro-latest')

def ask_gemini_sim(df_window):
    latest = df_window.to_string(index=False)
    prompt = f"""
    Act as a Quantitative Systematic Trader. Analyze these 1 minute candles for EURUSD-op.
    
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
    except:
        return "WAIT"

def run_validation():
    print("🚀 VALIDANDO SIMULADOR vs REALIDAD")
    
    # Cargar datos históricos descargados (24h)
    df = pd.read_csv('candles_24h.csv')
    df = df.sort_values('from')
    print(f"✅ Datos cargados: {len(df)} velas")
    
    # Simular una ventana de 1 hora (random o específica) donde sabemos que hubo actividad
    # Tomemos las 14:00 donde sabemos que hubo muchos trades reales
    
    # Filtrar para empezar a las 14:00 (timestamp aprox) - Ajustar según tus datos
    # Como no tengo el timestamp exacto a mano, tomaré una muestra de 10 ventanas consecutivas
    # para ver si DISPARA o SE QUEDA CALLADO.
    
    print("\n🔍 Probando 5 ventanas consecutivas...")
    
    start_idx = 800 # Un punto medio arbitrario
    
    for i in range(5):
        window = df.iloc[start_idx+i : start_idx+i+60]
        
        print(f"\n--- Ventana {i+1} ---")
        response = ask_gemini_sim(window)
        print(f"🤖 Respuesta Gemini: {response[:100]}...")
        
        if "CALL" in response.upper() or "PUT" in response.upper():
            print("✅ ¡SEÑAL DETECTADA! (El simulador funciona)")
        else:
            print("💤 WAIT (Silencio)")
            
    print("\nCONCLUSIÓN:")
    print("Si viste 'SEÑAL DETECTADA', el simulador está vivo.")
    print("Si todo fue 'WAIT', el simulador NO está replicando la agresividad del bot en vivo.")

if __name__ == "__main__":
    run_validation()
