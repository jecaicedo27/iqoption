import time
import pandas as pd
import numpy as np
from iqoptionapi.stable_api import IQ_Option
from app.config import EMAIL, PASSWORD, DEFAULT_ASSET, DEFAULT_TIMEFRAME
from app.analysis import MarketAnalyzer
from app.db_quest import QuestDBManager
import sys
import warnings

warnings.filterwarnings("ignore")

def collect_and_store():
    print(f"🚀 Starting 1 MONTH Data Collection for {DEFAULT_ASSET} (15s)...")
    
    # 1. Connect
    api = IQ_Option(EMAIL, PASSWORD)
    check, reason = api.connect()
    if not check:
        print(f"❌ Connection failed: {reason}")
        sys.exit(1)
        
    print("✅ Connected to IQ Option")
    
    # 2. Calculate needed candles
    # 30 days * 24 hours * 60 mins * 4 (15s) = 172,800
    TOTAL_CANDLES = 85000 # Limit to what we know exists
    CHUNK_SIZE = 1000
    SAVE_INTERVAL = 5000
    
    all_candles = []
    end_time = time.time()
    
    print(f"📊 Requesting {TOTAL_CANDLES} candles in chunks...")
    
    batch_count = 0
    saved_count = 0
    
    # We will accumulate in memory but save periodically? 
    # Actually, appending to 'all_candles' is fine for 80k. 
    # But let's just break if we catch the recursion error (duplicate timestamps).
    
    last_end_time = 0
    
    while len(all_candles) < TOTAL_CANDLES:
        try:
            # Get CHUNK
            candles = api.get_candles(DEFAULT_ASSET, 15, CHUNK_SIZE, end_time)
            
            if not candles:
                break
                
            # Check for loop (if end_time isn't moving backwards)
            new_end_time = candles[0]['from']
            if new_end_time == last_end_time:
                print("   ⚠️ Loop detected (End of Data). Stopping.")
                break
            last_end_time = new_end_time
                
            # Prepend to keep order
            all_candles = candles + all_candles
            batch_count += 1
            
            # Update end_time
            end_time = new_end_time
            first_date = time.ctime(end_time)
            
            # Progress Bar
            progress = len(all_candles) / TOTAL_CANDLES * 100
            print(f"   [{progress:.1f}%] Fetched batch {batch_count}. Oldest: {first_date} | Total: {len(all_candles)}")
            
            # Rate limit/Sleep
            time.sleep(0.3)
            
        except Exception as e:
            print(f"   ⚠️ Error fetching chunk: {e}")
            break
            
    # Remove duplicates
    df = pd.DataFrame(all_candles)
    df = df.drop_duplicates(subset=['from'])
    df = df.sort_values(by='from').reset_index(drop=True)
    
    print(f"✅ Retrieved {len(df)} unique candles.")
    
    # 3. Add Indicators
    print("🧠 Calculating Technical Indicators...")
    analyzer = MarketAnalyzer()
    
    df = analyzer.prepare_data(df.to_dict('records'))
    df = analyzer.add_technical_indicators(df)
    
    df = df.dropna()
    print(f"✅ Data processed. Final Clean Rows: {len(df)}")
    
    # 4. Save to QuestDB
    print("💾 Saving to QuestDB (Table: market_training)...")
    db = QuestDBManager()
    
    from questdb.ingress import Sender, TimestampNanos
    conf = f'tcp::addr={db.host}:{db.ilp_port};'
    
    with Sender.from_conf(conf) as sender:
        for index, row in df.iterrows():
            ts_nanos = TimestampNanos(row['from'].value)
            sender.row(
                'market_training',
                symbols={'asset': DEFAULT_ASSET},
                columns={
                    'open': row['open'],
                    'close': row['close'],
                    'min': row['min'],
                    'max': row['max'],
                    'volume': int(row['volume']),
                    'rsi': row['rsi'],
                    'ema_200': row['ema_200']
                },
                at=ts_nanos
            )
        sender.flush()
        
    print("✅ Successfully saved 1 MONTH of data!")

if __name__ == "__main__":
    collect_and_store()
