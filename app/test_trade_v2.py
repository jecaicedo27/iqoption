from app.connection import IQConnector
from app.trader import OrderManager
from app.config import DEFAULT_ASSET

def test_trade_v2():
    print("Iniciando prueba V2...")
    
    connector = IQConnector()
    if not connector.connect():
        return

    trader = OrderManager(connector.api)
    
    # 1. Intentar Binaria
    print("\n--- PRUEBA BINARIA ---")
    if trader.buy(DEFAULT_ASSET, "call", 1, 1):
        print("EXITO: Binaria CALL abierta.")
    else:
        print("FALLO: Binaria no se pudo abrir.")
        
        # 2. Si falla, intentar Digital
        print("\n--- PRUEBA DIGITAL ---")
        # Nota: Digitales a veces requieren subscribirse al instrumento primero
        connector.api.subscribe_strike_list(DEFAULT_ASSET, 1)
        if trader.buy_digital(DEFAULT_ASSET, "call", 1, 1):
            print("EXITO: Digital CALL abierta.")
        else:
            print("FALLO: Digital no se pudo abrir.")

if __name__ == "__main__":
    test_trade_v2()
