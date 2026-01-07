from BinomoAPI import BinomoAPI
from app.config import EMAIL, PASSWORD
import asyncio
import logging

# Enable logging
logging.basicConfig(level=logging.INFO)

async def test_connection():
    print(f"Testing Binomo Connection for {EMAIL}...")
    
    try:
        # 1. Login via HTTP Static Method
        print("Logging in via HTTP...")
        # Note: BinomoAPI.login is synchronous
        login_response = BinomoAPI.login(EMAIL, PASSWORD)
        
        if login_response:
            print(f"✅ HTTP Login Successful! Token: {login_response.authtoken[:10]}...")
            
            # 2. Create Client from Response
            client = BinomoAPI.create_from_login(login_response)
            
            # 3. Connect via WebSocket
            print("Connecting WebSocket...")
            await client.connect()
            
            print("✅ WebSocket Connected!")
            
            # 4. Get Balance
            # Balance might be cached or async
            balance = await client.get_balance()
            print(f"💰 Balance: {balance.amount/100} {balance.currency}")
            
            await client.close()
            
        else:
            print("❌ HTTP Login returned None")

    except Exception as e:
        print(f"❌ Test Failed: {e}")

if __name__ == "__main__":
    asyncio.run(test_connection())
