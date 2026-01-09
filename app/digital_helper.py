def buy_digital(api, asset, action, amount):
    """Execute a Digital Option trade"""
    try:
        # Digital options usually use expiration 1m (PT1M) or 5m (PT5M)
        # We try 1 minute ("PT1M") first
        expiration = "PT1M" 
        
        # Action needs to be "call" or "put" lower case
        action = action.lower()
        
        # Execute digital buy
        # api.buy_digital_spot(active, amount, action, duration)
        check, id = api.buy_digital_spot(asset, amount, action, 1) 
        
        if check:
            return True, id
        else:
            # Try 5 minute ("PT5M") if 1m fails
            check, id = api.buy_digital_spot(asset, amount, action, 5)
            if check:
                return True, id
            else:
                return False, id # id contains error
                
    except Exception as e:
        return False, str(e)
