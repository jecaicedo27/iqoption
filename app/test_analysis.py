import pandas as pd
from app.analysis import MarketAnalyzer

def test_analysis():
    print("Iniciando prueba de análisis...")
    
    # Datos simulados (tendencia alcista)
    mock_candles = [
        {'from': 1600000000, 'open': 1.1000, 'close': 1.1010, 'min': 1.0990, 'max': 1.1020, 'volume': 100},
        {'from': 1600000060, 'open': 1.1010, 'close': 1.1020, 'min': 1.1000, 'max': 1.1030, 'volume': 110},
        {'from': 1600000120, 'open': 1.1020, 'close': 1.1040, 'min': 1.1010, 'max': 1.1050, 'volume': 120},
        {'from': 1600000180, 'open': 1.1040, 'close': 1.1030, 'min': 1.1020, 'max': 1.1050, 'volume': 90},
        {'from': 1600000240, 'open': 1.1030, 'close': 1.1050, 'min': 1.1020, 'max': 1.1060, 'volume': 130},
        # Añadir más datos si es necesario para indicadores de largo periodo (RSI necesita ~14)
    ]
    
    # Generar más datos para llenar el periodo de 14
    base_time = 1600000300
    base_price = 1.1050
    for i in range(20):
        mock_candles.append({
            'from': base_time + (i * 60),
            'open': base_price,
            'close': base_price + 0.0010, # Subiendo
            'min': base_price - 0.0005,
            'max': base_price + 0.0015,
            'volume': 100
        })
        base_price += 0.0010

    analyzer = MarketAnalyzer()
    
    # Probar preparación de datos
    df = analyzer.prepare_data(mock_candles)
    print(f"DataFrame creado con {len(df)} filas.")
    
    # Probar análisis completo
    result = analyzer.analyze_market(mock_candles)
    
    print("\nResultados del último periodo:")
    print(f"Precio Cierre: {result['close']}")
    print(f"SMA (14): {result['sma_14']:.5f}")
    print(f"RSI (14): {result['rsi_14']:.2f}")

    if not pd.isna(result['rsi_14']):
        print("Cálculo de RSI exitoso.")
    else:
        print("RSI es NaN (pueden faltar datos).")

if __name__ == "__main__":
    test_analysis()
