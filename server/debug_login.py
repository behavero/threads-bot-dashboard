#!/usr/bin/env python3
"""
Debug login script to test Threads API with detailed error information
"""

import asyncio
import traceback

async def debug_login(username: str, password: str):
    """Debug login with detailed error information"""
    try:
        from threads_api_real import RealThreadsAPI
        print("✅ RealThreadsAPI imported successfully")
        
        # Create API instance
        api = RealThreadsAPI()
        print("✅ RealThreadsAPI created")
        
        # Test login with detailed error handling
        print(f"🔐 Attempting login for {username}...")
        result = await api.login(username, password)
        print(f"Login result: {result}")
        
        if result:
            # Get user info
            user_info = await api.get_me()
            print(f"User info: {user_info}")
        else:
            print("❌ Login failed")
        
        # Clean up
        await api.logout()
        print("✅ Test completed")
        
        return result
        
    except Exception as e:
        print(f"❌ Error during login: {e}")
        print(f"❌ Traceback: {traceback.format_exc()}")
        return False

def main():
    """Run the debug test"""
    print("🧪 Debugging Threads API login...")
    
    # Test with the provided credentials
    username = "Lanavalentine.official"
    password = "k3s632007@"
    
    result = asyncio.run(debug_login(username, password))
    
    if result:
        print("✅ Login successful!")
    else:
        print("❌ Login failed - check error details above")

if __name__ == "__main__":
    main()
