import time
from app.config import DEFAULT_AMOUNT, MAX_TRADES_DAILY

class OrderManager:
    def __init__(self, api):
        self.api = api
        self.trades_today = 0

    def buy(self, asset, action, amount=DEFAULT_AMOUNT, duration=1):
        """
        Intenta comprar binaria (turbo/binary).
        """
        if self.trades_today >= MAX_TRADES_DAILY:
            print("Límite diario alcanzado.")
            return False

        print(f"Intento Binary/Turbo: {action.upper()} en {asset} (${amount})...")
        check, id = self.api.buy(amount, asset, action, duration)
        if check:
            print(f"Orden Binaria Ejecutada! ID: {id}")
            self.trades_today += 1
            return True
        else:
            print("Fallo en Binaria.")
            return False

    def buy_digital(self, asset, action, amount=DEFAULT_AMOUNT, duration=1):
        """
        Intenta comprar opción digital.
        """
        if self.trades_today >= MAX_TRADES_DAILY:
            return False

        print(f"Intento Digital: {action.upper()} en {asset} (${amount})...")
        # ACTION debe ser 'call' o 'put'
        # duration en digitales suele ser 1, 5, 15 (minutos)
        
        id = self.api.buy_digital_spot(asset, amount, action, duration)
        
        # buy_digital_spot a veces retorna el ID directamente o check?
        # En esta librería suele retornar el ID si funciona, o algo Falsey si falla.
        # Pero a veces lanza excepción.
        
        if id:
            print(f"Orden Digital Ejecutada! ID: {id}")
            self.trades_today += 1
            return True
        else:
            print("Fallo en Digital.")
            return False
