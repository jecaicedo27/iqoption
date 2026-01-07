import os

# Credentials
EMAIL = os.getenv("IQ_EMAIL", "kaicedosb@gmail.com")
PASSWORD = os.getenv("IQ_PASSWORD", "Jhonk1987*-*@#$")

# Trading Settings
ACCOUNT_TYPE = "REAL"  # Switched to REAL funds
DEFAULT_ASSET = "EURUSD-op" # Real Forex Market (Non-OTC)
DEFAULT_TIMEFRAME = 60  # 1 Minute (More stable for analysis)
DEFAULT_AMOUNT = 4000 # Approx $1 USD (Min unit)

# Risk Management
MAX_TRADES_DAILY = 10
STOP_LOSS = 50       # Stop global (si se pierde esto en total, parar)
TAKE_PROFIT = 100    # Meta global
