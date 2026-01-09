import google.generativeai as genai
import os
from app.config import GOOGLE_API_KEY

genai.configure(api_key=GOOGLE_API_KEY)
model = genai.GenerativeModel('gemini-2.0-flash-exp')

def ask_for_history():
    prompt = """
    User wants to know: "What was the very first prompt used for this trading bot project about 2-3 days ago?".
    The project is a Quantitative Systematic Trader for EURUSD on IQ Option.
    
    If you (Gemini) have access to the conversation history or project initialization instructions from 2 days ago, please provide the EXACT text of that first prompt.
    """
    try:
        response = model.generate_content(prompt)
        print("--- RESPONSE FROM GEMINI ---")
        print(response.text)
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    ask_for_history()
