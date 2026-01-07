import csv
import time
import os
from app.connection import IQConnector
from app.config import DEFAULT_ASSET, DEFAULT_TIMEFRAME

DATA_FILE = "market_data.csv"

def collect_data(candles_to_fetch=10000):
    print(f"Iniciando recolección de datos ({candles_to_fetch} velas)...")
    
    connector = IQConnector()
    if not connector.connect():
        return

    # IQ Option permite bajar max 1000 velas por request
    # Necesitamos iterar hacia atrás
    
    end_time = time.time()
    all_candles = []
    
    # Descargar en bloques de 1000
    while len(all_candles) < candles_to_fetch:
        print(f"Descargando bloque... (Total actual: {len(all_candles)})")
        # Fix: Usar DEFAULT_TIMEFRAME directo (5s)
        candles = connector.api.get_candles(DEFAULT_ASSET, DEFAULT_TIMEFRAME, 1000, end_time)
        
        if not candles:
            break
            
        all_candles.extend(candles)
        
        # Actualizar end_time al tiempo de la vela mas vieja - 1 segundo
        end_time = candles[0]['from'] - 1
        
        time.sleep(1) # Respetar API limits

    print(f"Datos descargados: {len(all_candles)} registros.")
    
    # Guardar en CSV
    # Campos disponibles: id, from, at, to, open, close, min, max, volume
    headers = ['timestamp', 'open', 'close', 'min', 'max', 'volume']
    
    # Ordenar por tiempo ascendente (el API devuelve descendente o bloques mezclados a veces)
    all_candles.sort(key=lambda x: x['from'])
    
    with open(DATA_FILE, mode='w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(headers)
        
        for c in all_candles:
            writer.writerow([
                c['from'], c['open'], c['close'], c['min'], c['max'], c['volume']
            ])

    print(f"Datos guardados en {DATA_FILE}")

if __name__ == "__main__":
    collect_data()
