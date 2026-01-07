from app.connection import IQConnector
import time

def test_5m_digital():
    print("🚀 Connecting to IQ Option (5m Digital Test)...")
    connector = IQConnector()
    if not connector.connect(): return

    asset = "EURUSD"
    print(f"🎯 Target: {asset} (Real Market)")
    
    # Try Digital Spot 5 minutes
    # Digital spots usually come in 1m, 5m, 15m
    # Duration in minutes: 5
    
    print("\n💸 Attempting Digital Call (5 min)...")
    try:
        # Note: digital_spot buy often takes duration in minutes
        check, id = connector.api.buy_digital_spot(asset, 1, "call", 5)
        
        if check:
             print(f"✅ SUCCESS! 5-min Digital Trade Placed. ID: {id}")
             print("💡 CONCLUSION: We CAN trade Real Market on 5-min timeframe!")
        else:
             print(f"❌ Failed 5-min Digital.")
             
             # Double check 15m Digital
             print("\n💸 Attempting Digital Call (15 min)...")
             check2, id2 = connector.api.buy_digital_spot(asset, 1, "call", 15)
             if check2:
                 print(f"✅ SUCCESS! 15-min Digital Trade Placed. ID: {id2}")
             else:
                 print("❌ Failed 15-min Digital too.")
                 
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_5m_digital()
