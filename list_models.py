import google.generativeai as genai
from app.config import GOOGLE_API_KEY
import os

try:
    genai.configure(api_key=GOOGLE_API_KEY)
    print("Listing models...")
    for m in genai.list_models():
        if 'generateContent' in m.supported_generation_methods:
            print(f"Model: {m.name}")
except Exception as e:
    print(f"Error: {e}")
