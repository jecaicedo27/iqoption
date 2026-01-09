from iqoptionapi.stable_api import IQ_Option
from app.config import EMAIL, PASSWORD

api = IQ_Option(EMAIL, PASSWORD)
api.connect()
print(dir(api))
