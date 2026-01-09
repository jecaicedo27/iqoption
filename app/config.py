import os

# Credentials
EMAIL = os.getenv("IQ_EMAIL", "kaicedosb@gmail.com")
PASSWORD = os.getenv("IQ_PASSWORD", "Jhonk1987*-*@#$")

# Trading Settings
ACCOUNT_TYPE = "PRACTICE"  # Switched to PRACTICE
DEFAULT_ASSET = "EURUSD-op" # Switched to op per user request
DEFAULT_TIMEFRAME = 1  # 1 Minute
DEFAULT_AMOUNT = 100 # Back to $100 for Practice

# Risk Management
MAX_TRADES_DAILY = 10
STOP_LOSS = 50       # Stop global (si se pierde esto en total, parar)
TAKE_PROFIT = 100    # Meta global

# AI Credentials
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
