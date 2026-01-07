import google.generativeai as genai
import pandas as pd
import time
import os

# Configuration
GOOGLE_API_KEY = "AIzaSyD3x7u6GNSLNIVXN8OuE3euORi9wZDcy6c"
genai.configure(api_key=GOOGLE_API_KEY)
model = genai.GenerativeModel('gemini-1.5-flash')

def test_connection():
    print("Listing Available Models...")
    try:
        for m in genai.list_models():
            if 'generateContent' in m.supported_generation_methods:
                print(f"Model: {m.name}")
        return True
    except Exception as e:
        print(f"❌ Gemini Connection Failed: {e}")
        return False

if __name__ == "__main__":
    test_connection()
