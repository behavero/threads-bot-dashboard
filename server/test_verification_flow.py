#!/usr/bin/env python3
"""
Test verification flow simulation
"""

import asyncio
import json

async def test_verification_flow():
    """Test the verification flow simulation"""
    try:
        from threads_api_real import RealThreadsAPI
        print("✅ RealThreadsAPI imported successfully")
        
        # Test 1: Initial login (should trigger verification)
        print("\n🔐 Test 1: Initial login")
        api = RealThreadsAPI(use_instagrapi=True)
        result = await api.login("test_user", "test_password")
        print(f"Login result: {json.dumps(result, indent=2)}")
        
        # Test 2: Submit verification code
        if result.get("requires_verification"):
            print("\n📧 Test 2: Submit verification code")
            verification_result = await api.submit_verification_code("123456")
            print(f"Verification result: {json.dumps(verification_result, indent=2)}")
        
        # Test 3: Login with verification code
        print("\n🔐 Test 3: Login with verification code")
        api2 = RealThreadsAPI(use_instagrapi=True)
        result_with_code = await api2.login("test_user", "test_password", "123456")
        print(f"Login with code result: {json.dumps(result_with_code, indent=2)}")
        
        # Clean up
        await api.logout()
        await api2.logout()
        print("\n✅ Test completed successfully")
        
        return True
        
    except Exception as e:
        print(f"❌ Error testing verification flow: {e}")
        return False

if __name__ == "__main__":
    asyncio.run(test_verification_flow())
