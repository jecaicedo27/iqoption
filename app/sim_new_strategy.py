import time
import json
import os
import sys
from groq import Groq
from iqoptionapi.stable_api import IQ_Option
from app.config import EMAIL, PASSWORD, GROQ_API_KEY, DEFAULT_ASSET
import pandas as pd

# Setup
client = Groq(api_key=GROQ_API_KEY)
MODEL_NAME = "llama-3.1-8b-instant"

def get_market_data(api, asset, count=120): # Get 2 hours to have enough context for the first simulation step
    print(f"Fetching data for {asset}...")
    candles = api.get_candles(asset, 60, count, time.time())
    return candles

def analyze_with_groq(context_candles):
    # Construct the exact same prompt as the bot
    prompt = f"""
    Act as a Quantitative Systematic Trader. 
    
    DATA (Last 60 mins):
    {context_candles}
    
    TASK: Analyze the market data to predict the direction for the NEXT candle (1 minute).
    
    STRATEGY GUIDELINES:
    1. **FOLLOW THE TREND**: This is an OTC market. Trends persist. DO NOT bet on reversals unless there is a massive rejection wick.
    2. **MOMENTUM**: If the last 3 candles are same color, assume continuation.
    3. **AVOID CALLS IN DOWNTRENDS**: If price is making lower lows, ONLY trade PUT or WAIT.
    4. **AVOID PUTS IN UPTRENDS**: If price is making higher highs, ONLY trade CALL or WAIT.
    5. **REVERSAL CONFIRMATION**: If betting on a reversal (e.g., CALL after downtrend), you MUST wait for a GREEN candle to close first. Never catch a falling knife.
    
    OUTPUT FORMAT (Strict JSON):
    {{
      "ACTION": "CALL" | "PUT" | "WAIT",
      "CONFIDENCE": 80-100,
      "REASON": "Short explanation"
    }}
    """
    
    try:
        completion = client.chat.completions.create(
            model=MODEL_NAME,
            messages=[
                {"role": "system", "content": "You are a disciplined AI Trader specialized in Binary Options."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.1,
            max_tokens=150,
            response_format={"type": "json_object"}
        )
        content = completion.choices[0].message.content
        # Extract JSON
        start = content.find('{')
        end = content.rfind('}') + 1
        json_str = content[start:end]
        return json.loads(json_str)
    except Exception as e:
        print(f"Error AI: {e}")
        print(f"⚠️ RAW CONTENT: {content[:200]}...") # Debug: Print first 200 chars
        return {"ACTION": "WAIT", "CONFIDENCE": 0}

def run_simulation():
    api = IQ_Option(EMAIL, PASSWORD)
    api.connect()
    
    # We need the last 60-70 candles to simulate the last HOUR
    # Let's fetch 120 candles, and simulate the last 30 minutes to be fast (30 API calls)
    # The user asked for "last hour", so let's try 40 candles (40 mins) to balance speed/coverage
    
    all_candles = get_market_data(api, DEFAULT_ASSET, 100) 
    
    # Standardize data format
    clean_data = []
    for c in all_candles:
        clean_data.append({
            #"id": c['id'],
            "open": c['open'],
            "close": c['close'],
            "high": c['max'],
            "low": c['min'],
            "volume": c['volume'],
            # "at": c['from'] 
        })
        
    print(f"\n🚀 SIMULATING STRATEGY ON LAST 40 MINUTES ({DEFAULT_ASSET})...")
    print(f"Strategy: Trend Follow + Reversal Confirmation\n")
    
    wins = 0
    losses = 0
    total_trades = 0
    balance = 1000 # Virtual starting balance
    
    # Iterate through the data like a sliding window
    # We need at least ~30 candles of context for the AI
    context_size = 30
    
    # Start simulating from index 30 up to len-1
    # Check prediction at 'i' against result at 'i+1'
    
    history_start = len(clean_data) - 40 # Last 40 mins
    
    for i in range(history_start, len(clean_data) - 1):
        # Context is everything before i
        context = clean_data[i-context_size : i+1] 
        # Target is i+1 (Next candle)
        target_candle = clean_data[i+1]
        
        # Convert context to compact JSON string
        context_str = json.dumps(context[-20:]) # Send last 20 candles to AI to save tokens/speed
        
        # Ask AI
        decision = analyze_with_groq(context_str)
        action = decision.get("ACTION", "WAIT")
        conf = decision.get("CONFIDENCE", 0)
        
        actual_move = "GREEN" if target_candle['close'] > target_candle['open'] else "RED"
        if target_candle['close'] == target_candle['open']: actual_move = "DOJI"
        
        print(f"Min {i}: AI says {action} ({conf}%) | Actual: {actual_move}", end="")
        
        if action != "WAIT" and conf >= 75:
            total_trades += 1
            is_win = False
            
            if action == "CALL" and actual_move == "GREEN":
                is_win = True
            elif action == "PUT" and actual_move == "RED":
                is_win = True
                
            if is_win:
                wins += 1
                balance += 85 # 85% payout
                print(" => ✅ WIN")
            else:
                losses += 1
                balance -= 100
                print(" => ❌ LOSS")
        else:
            print(" => ⏭️ SKIP")
            
        # Small delay to respect rate limits if needed (Groq is fast though)
        # time.sleep(0.5) 

    print("\n" + "="*40)
    print("📊 SIMULATION RESULTS")
    print("="*40)
    print(f"Total Trades: {total_trades}")
    print(f"Wins: {wins}")
    print(f"Losses: {losses}")
    print(f"Win Rate: {(wins/total_trades*100) if total_trades > 0 else 0:.1f}%")
    print(f"Net Profit (Virtual): ${balance - 1000}")
    print("="*40)

if __name__ == "__main__":
    run_simulation()
