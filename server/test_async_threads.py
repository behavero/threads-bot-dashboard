#!/usr/bin/env python3
"""
Test async ThreadsAPI implementation
"""

import asyncio

async def test_async_threads_api():
    """Test async ThreadsAPI"""
    try:
        from threads_api_real import RealThreadsAPI
        print("✅ RealThreadsAPI imported successfully")
        
        # Create API instance
        api = RealThreadsAPI()
        print("✅ RealThreadsAPI created")
        
        # Test login (this will fail with test credentials, but should not crash)
        result = await api.login('test_user', 'test_password')
        print(f"Login result: {result}")
        
        # Clean up
        await api.logout()
        print("✅ Test completed successfully")
        
        return True
        
    except Exception as e:
        print(f"❌ Error testing async ThreadsAPI: {e}")
        return False

def main():
    """Run the test"""
    print("🧪 Testing async ThreadsAPI...")
    result = asyncio.run(test_async_threads_api())
    
    if result:
        print("✅ Async ThreadsAPI test successful")
    else:
        print("❌ Async ThreadsAPI test failed")

if __name__ == "__main__":
    main()
