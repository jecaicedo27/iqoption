from app.connection import IQConnector
import json

def check_account_status():
    print("🚀 Connecting to fetch Profile Status...")
    connector = IQConnector()
    if not connector.connect():
        print("❌ Connection Failed")
        return

    print("🔍 Fetching Profile Data...")
    try:
        # get_profile_ansyc is a wrapper in our IQ_Option class
        profile = connector.api.get_profile_ansyc()
        
        # Select key fields for verification check
        check_fields = [
            "name", "email", "is_activated", "kyc_status", 
            "verification_state", "kyc_confirmed", "is_successful"
        ]
        
        status_report = {}
        for field in profile:
            if any(k in field.lower() for k in ["verify", "kyc", "status", "confirm", "active"]):
                status_report[field] = profile[field]
        
        print("\n--- ACCOUNT STATUS REPORT ---")
        print(json.dumps(status_report, indent=4))
        
        # Also check specific balance types and permissions if available
        if "balances" in profile:
            print(f"\nBalances found: {len(profile['balances'])}")
            
        print("\n--- FULL FILTERED METADATA ---")
        # Print only relevant fields to avoid leaking PII if any
        for key in ["is_activated", "kyc", "status", "need_verification"]:
            if key in profile:
                 print(f"{key}: {profile[key]}")

    except Exception as e:
        print(f"Error fetching status: {e}")

if __name__ == "__main__":
    check_account_status()
