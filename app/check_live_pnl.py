import sys
import time
import json
from datetime import datetime, date
from iqoptionapi.stable_api import IQ_Option
from app.config import EMAIL, PASSWORD, ACCOUNT_TYPE

def check_pnl():
    print("🔌 Connecting to retrieve P&L...")
    api = IQ_Option(EMAIL, PASSWORD)
    if not api.connect():
        print("❌ Connection Failed")
        return

    api.change_balance(ACCOUNT_TYPE)
    print(f"✅ Connected. Balance Type: {ACCOUNT_TYPE}")
    
    # Get today's timestamp (midnight)
    today = date.today()
    midnight_ts = int(time.mktime(today.timetuple()))
    
    print("📊 Fetching trade history...")
    
    total_profit = 0.0
    wins = 0
    losses = 0
    trades = 0
    
    types_to_check = ["digital-option", "binary-option", "turbo-option", "fx-option"]
    
    for inst_type in types_to_check:
        print(f" ... Checking {inst_type}")
        try:
            res = api.get_position_history_v2(inst_type, 100, 0, 0, 0)
            
            history = []
            if isinstance(res, tuple):
                 if res[0] == True:
                     history = res[1]['positions']
            elif isinstance(res, dict):
                 if res.get('isSuccessful'):
                     history = res['msg']['positions']
            
            if not history:
                 # print(f"   [Empty]")
                 pass
            else:
                for trade in history:
                    # filter by time > midnight
                    close_time = trade['close_time'] / 1000 # ms to s
                    if close_time > midnight_ts:
                         pl = float(trade['close_profit']) - float(trade['invest'])
                         raw_id = trade.get('active_id') or trade.get('instrument_active_id')
                         res_str = "WIN" if pl > 0 else "LOSS"
                         print(f"   {inst_type.upper()} | {datetime.fromtimestamp(close_time)} | ID:{raw_id} | {res_str} (${pl:.2f})")
                         total_profit += pl
                         trades += 1
                         if pl > 0: wins += 1
                         elif pl < 0: losses += 1
        except Exception:
            pass
            
    print(" ... Checking Generic Binary (get_optioninfo_v2)")
    try:
        res_bin = api.get_optioninfo_v2(50)
        if res_bin and isinstance(res_bin, dict):
             print(f"DEBUG: Found {len(res_bin)} Generic entries")
             for oid, data in res_bin.items():
                 # Handle stringified JSON
                 if isinstance(data, str):
                     try:
                         data = json.loads(data)
                     except json.JSONDecodeError:
                         pass 
                 
                 trade_list = []
                 # Case 1: 'closed_options' list
                 if isinstance(data, dict):
                     if 'closed_options' in data:
                         trade_list = data['closed_options']
                     else:
                         # Case 2: Individual item logic
                         trade_list = [data]
                 
                 for trade in trade_list:
                     # Handle nested Msg if single item
                     if 'msg' in trade:
                         trade = trade['msg']

                     # Determine timestamp
                     c_time = trade.get('close_time') or trade.get('created') or 0
                     if c_time > 1000000000000: c_time /= 1000
                     
                     if c_time > midnight_ts:
                        
                        invest = float(trade.get('amount', 0))
                        win = trade.get('win', '') 
                        # profit_amount sometimes string or float
                        profit_amount = float(trade.get('profit_amount', 0))
                        
                        pl = 0
                        status = "UNKNOWN"
                        
                        if win == 'win':
                            pl = profit_amount - invest
                            # Fallback if profit_amount is 0 but win is 'win' (common in test)
                            if pl == -invest: pl = invest * 0.83 
                            status = "WIN"
                            wins += 1
                        elif win == 'lose':
                            pl = -invest
                            status = "LOSS"
                            losses += 1
                        else:
                            # Skip open or invalid
                            continue

                        print(f"   BINARY-GEN | {datetime.fromtimestamp(c_time)} | {trade.get('id')} | {status} (${pl:.2f})")
                        trades += 1
                        total_profit += pl

    except Exception as e:
        print(f"   ⚠️ Error checking Generic Binary: {e}")

    print("\n" + "="*30)
    print(f"💰 LIVE SESSION REPORT (Since Midnight)")
    print(f"Total Trades Found: {trades}")
    print(f"Wins: {wins}")
    print(f"Losses: {losses}")
    print(f"Win Rate: {(wins/trades*100) if trades>0 else 0:.1f}%")
    print(f"NET PROFIT (Approx): ${total_profit:.2f}")
    print("="*30)

if __name__ == "__main__":
    check_pnl()
