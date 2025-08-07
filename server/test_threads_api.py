#!/usr/bin/env python3
"""
Test ThreadsAPI functionality
"""

import asyncio

async def test_threads_api():
    """Test ThreadsAPI in async context"""
    try:
        from threads_api.src.threads_api import ThreadsAPI
        print("✅ ThreadsAPI imported successfully")
        
        # Initialize in async context
        api = ThreadsAPI()
        print("✅ ThreadsAPI initialized in async context")
        
        # Test login (this would require real credentials)
        # result = await api.login("username", "password")
        # print(f"Login result: {result}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error testing ThreadsAPI: {e}")
        return False

def main():
    """Run the test"""
    print("🧪 Testing ThreadsAPI...")
    result = asyncio.run(test_threads_api())
    
    if result:
        print("✅ ThreadsAPI test successful")
    else:
        print("❌ ThreadsAPI test failed")

if __name__ == "__main__":
    main()
