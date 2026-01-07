import time
import pandas as pd
import numpy as np
from iqoptionapi.stable_api import IQ_Option
from app.config import EMAIL, PASSWORD, DEFAULT_ASSET, DEFAULT_TIMEFRAME
from app.analysis import MarketAnalyzer
from app.db_quest import QuestDBManager
import sys

# Silence warnings
import warnings
warnings.filterwarnings("ignore")

def collect_and_store():
    print(f"🚀 Starting 24h Data Collection for {DEFAULT_ASSET} (15s)...")
    
    # 1. Connect
    api = IQ_Option(EMAIL, PASSWORD)
    check, reason = api.connect()
    if not check:
        print(f"❌ Connection failed: {reason}")
        sys.exit(1)
        
    print("✅ Connected to IQ Option")
    
    # 2. Calculate needed candles
    # 24 hours * 60 mins * 4 (15s) = 5760 candles
    # Let's get 6000 to be safe and have warmup for RSI
    TOTAL_CANDLES = 6000
    CHUNK_SIZE = 1000
    
    all_candles = []
    end_time = time.time()
    
    print(f"📊 Requesting {TOTAL_CANDLES} candles in chunks...")
    
    while len(all_candles) < TOTAL_CANDLES:
        try:
            # Get CHUNK
            print(f"   Fetching chunk ending {time.ctime(end_time)}...")
            candles = api.get_candles(DEFAULT_ASSET, 15, CHUNK_SIZE, end_time)
            
            if not candles:
                print("   ⚠️ No candles returned, stopping.")
                break
                
            # Prepend to keep order (we are going backwards)
            all_candles = candles + all_candles
            
            # Update end_time for next batch (oldest candle 'from')
            end_time = candles[0]['from']
            
            # Rate limit
            time.sleep(0.5)
            
        except Exception as e:
            print(f"   ⚠️ Error fetching chunk: {e}")
            break
            
    # Remove duplicates if any
    # Convert to DF
    df = pd.DataFrame(all_candles)
    df = df.drop_duplicates(subset=['from'])
    df = df.sort_values(by='from').reset_index(drop=True)
    
    print(f"✅ Retrieved {len(df)} unique candles.")
    
    # 3. Add Indicators
    print("🧠 Calculating Technical Indicators...")
    analyzer = MarketAnalyzer()
    
    # Prepare data converts types
    df = analyzer.prepare_data(df.to_dict('records'))
    df = analyzer.add_technical_indicators(df)
    
    # Drop NaNs created by indicators (first ~14-200 rows)
    df = df.dropna()
    print(f"✅ Data processed. Final Clean Rows: {len(df)}")
    
    # 4. Save to QuestDB
    print("💾 Saving to QuestDB (Table: training_data)...")
    db = QuestDBManager()
    
    # We will simulate 'saving trades' or just insert raw market data?
    # Logic: The USER wants to 'train the network'.
    # The network needs: Features (Close, Vol, RSI) -> Target (Win next candle?)
    # QuestDBManager usually has 'save_trade'. 
    # capturing 'market_data' row by row is inefficient using 'save_trade'.
    # We should use a specialized method or just loop efficiently.
    # But wait, QuestDBManager doesn't have a 'save_candle' method yet.
    # I will add a simplified inline insertion here using Sender directly.
    
    from questdb.ingress import Sender, TimestampNanos
    
    conf = f'tcp::addr={db.host}:{db.ilp_port};'
    
    with Sender.from_conf(conf) as sender:
        for index, row in df.iterrows():
            # Timestamp from Pandas (is already datetime64[ns])
            # .value gives nanoseconds as int
            ts_nanos = TimestampNanos(row['from'].value)
            
            sender.row(
                'market_training', # New Table Name
                symbols={
                    'asset': DEFAULT_ASSET,
                },
                columns={
                    'open': row['open'],
                    'close': row['close'],
                    'min': row['min'],
                    'max': row['max'],
                    'volume': int(row['volume']),
                    'rsi': row['rsi'],
                    'ema_200': row['ema_200'],
                    # Add features for training
                },
                at=ts_nanos
            )
            
        sender.flush()
        
    print("✅ Successfully saved to QuestDB 'market_training'")
    print("Sample Data:")
    print(df[['from', 'close', 'volume', 'rsi']].tail())

if __name__ == "__main__":
    collect_and_store()
