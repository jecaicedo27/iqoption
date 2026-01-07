import time
import sys
from app.connection import IQConnector
from app.config import DEFAULT_ASSET, DEFAULT_TIMEFRAME, DEFAULT_AMOUNT
from app.data_manager import DataManager
from app.analysis import MarketAnalyzer
from app.ai_transformer import TransformerTrader # IMPORTANTE: Usamos el Transformer

from app.db_quest import QuestDBManager

def run_bot():
    # 1. Conexión
    connector = IQConnector()
    if not connector.connect():
        print("Error crítico de conexión. Saliendo.")
        sys.exit(1)
    
    # 2. Componentes
    data_manager = DataManager(connector.api)
    analyzer = MarketAnalyzer()
    
    # DB MANAGER (Trade Memory)
    try:
        db_memory = QuestDBManager()
        print("🔗 Conectado a QuestDB (Memoria de Elefante)")
    except Exception as e:
        print(f"Error conectando a DB: {e}. Continuando sin memoria.")
        db_memory = None
    
    # CEREBRO: TRANSFORMER (Next Gen)
    brain = TransformerTrader()
    print("Cargando Cerebro Transformer (Multi-Head Attention)...")
    
    if not brain.load():
        print("Error: No se encontró el modelo Transformer entrenado (model_transformer.keras).")
        # Fallback o entrenar? Debería estar.
        sys.exit(1)
        
    trader = connector.api # Acceso directo para buy
    
    print(f"Iniciando TRANSFORMER BOT para {DEFAULT_ASSET}...")
    
    # Loop
    while True:
        try:
            # A. Obtener Velas (Necesitamos 60 para el contexto)
            # El Transformer necesita ver la secuencia exacta
            candles = data_manager.get_candles(amount=60) # Optimize fetch
            
            # B. Analizar
            last_candle_analysis = analyzer.analyze_market(candles)
            if last_candle_analysis is None:
                time.sleep(1)
                continue
                
            # C. Predicción IA
            # Reconvertir candles a DF para pasar al brain
            df_analysis = analyzer.prepare_data(candles)
            # Ya no necesitamos add_technical_indicators complejos, el prepare_data maneja selection
            # Pero analysis.py tiene add_technical_indicators que transformer usa?
            # Revisemos transformer.prepare_data: usa ['close', 'volume', 'rsi']
            # RSI viene de add_technical_indicators.
            df_analysis = analyzer.add_technical_indicators(df_analysis)
            df_analysis.dropna(inplace=True)
            
            prob_up = brain.predict(df_analysis)
            
            if prob_up:
                current_close = last_candle_analysis['close']
                
                # ESTRATEGIA: CONFÍANZA PURA (VOLUME FOCUSED)
                # Eliminamos filtros externos (MACD/EMA) porque producían "Parálisis".
                # El Transformer ya ve (Precio, Volumen, RSI).
                
                print(f"[{time.strftime('%H:%M:%S')}] P:{current_close:.2f} | TRANSF:{prob_up:.4f}")   

                # LÓGICA TRANSFORMER (STANDARD)
                # El Transformer ve patrones complejos. Confiamos en su señal.
                # Threshold: 0.52 (Basado en training acc).
                
                threshold = 0.52
                
                trade_type = None
                trade_id = None
                
                # ... (Trade execution block)
                if True: # Siempre evaluamos
                    entry_time = time.time() # Capture trade time EXACTLY
                    
                    # CALL
                    if prob_up > threshold:
                        print(f">>> CALL TRIGGER ({prob_up:.4f}) 🚀")
                        trade_type = "CALL"
                        check, id = trader.buy(DEFAULT_AMOUNT, DEFAULT_ASSET, "call", 1) # 1m Turbo
                        if check:
                            print(f"Orden Enviada (5m): {id}")
                            trade_id = id
                            time.sleep(13) 
                        else:
                            print("Fallo Binary. (Digital DESHABILITADO por Bug de Hang)")
                            # id_dig = trader.buy_digital_spot(DEFAULT_ASSET, DEFAULT_AMOUNT, "call", 1) ...
                            time.sleep(1)
                    
                    # PUT
                    elif prob_up < (1.0 - threshold):
                        print(f">>> PUT TRIGGER ({prob_up:.4f}) 🔻")
                        trade_type = "PUT"
                        check, id = trader.buy(DEFAULT_AMOUNT, DEFAULT_ASSET, "put", 1) # 1m Turbo
                        if check:
                            print(f"Orden Enviada (5m): {id}")
                            trade_id = id
                            time.sleep(13)
                        else:
                            print("Fallo Binary. (Digital DESHABILITADO por Bug de Hang)")
                            # id_dig = trader.buy_digital_spot(DEFAULT_ASSET, DEFAULT_AMOUNT, "put", 1) ...
                            time.sleep(1)
                                
                # RECORD TO QUESTDB
                if trade_id and db_memory:
                    print("⏳ Esperando resultado para guardar en Memoria...")
                    time.sleep(50) # Completar el minuto
                    
                    win_amount = trader.check_win_v3(trade_id)
                    
                    # CORRECCIÓN PROFIT:
                    # check_win_v3 retorna el beneficio neto (ej: 87.0) en caso de win.
                    # Si es loss retorna 0.
                    # ANTES: win_amount - DEFAULT_AMOUNT (87 - 100 = -13). ERROR.
                    # AHORA: Usamos win_amount directo si > 0.
                    
                    result = "WIN" if win_amount > 0 else "LOSS"
                    profit = win_amount if win_amount > 0 else -DEFAULT_AMOUNT
                    
                    print(f"📝 Guardando en QuestDB: {result} (${profit:.2f})")
                    
                    last_feats = df_analysis[['close', 'volume', 'rsi']].tail(1).values.tolist()
                    
                    # Debug Volume
                    vol_debug = last_feats[0][1]
                    if vol_debug == 0:
                        print("⚠️ WARNING: Volume is 0. Check Data Feed.")
                    
                    db_memory.save_trade(
                        asset=DEFAULT_ASSET,
                        price=current_close,
                        prediction=trade_type,
                        confidence=prob_up,
                        features=last_feats,
                        result=result,
                        profit=profit,
                        timestamp=entry_time # Send exact entry time
                    )
                                    
            time.sleep(1) # Ciclo rápido
            
        except KeyboardInterrupt:
            break
        except Exception as e:
            print(f"Error en loop: {e}")
            time.sleep(5)

if __name__ == "__main__":
    run_bot()
