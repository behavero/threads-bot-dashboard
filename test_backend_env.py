#!/usr/bin/env python3
"""
Test backend environment variables
"""

import requests
import json

BACKEND_URL = "https://threads-bot-dashboard-3.onrender.com"

def test_backend_environment():
    """Test backend environment and configuration"""
    print("🔍 Testing Backend Environment...")
    
    try:
        # Test basic health
        response = requests.get(f"{BACKEND_URL}/api/status")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Backend health: {data}")
        else:
            print(f"❌ Backend health failed: {response.status_code}")
            return False
        
        # Test info endpoint
        response = requests.get(f"{BACKEND_URL}/api/info")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Backend info: {data}")
        else:
            print(f"❌ Backend info failed: {response.status_code}")
            return False
        
        # Test getting captions (should work)
        response = requests.get(f"{BACKEND_URL}/api/captions")
        if response.status_code == 200:
            data = response.json()
            captions = data.get('captions', [])
            print(f"✅ Backend captions fetch: {len(captions)} captions")
        else:
            print(f"❌ Backend captions fetch failed: {response.status_code}")
            return False
        
        return True
        
    except Exception as e:
        print(f"❌ Backend environment test error: {e}")
        return False

def test_backend_caption_creation():
    """Test backend caption creation with detailed logging"""
    print("\n🔍 Testing Backend Caption Creation...")
    
    try:
        caption_data = {
            "text": "Test caption with detailed logging",
            "category": "test",
            "tags": ["backend", "test", "logging"]
        }
        
        print(f"📝 Sending caption data: {caption_data}")
        
        response = requests.post(
            f"{BACKEND_URL}/api/captions",
            json=caption_data,
            headers={"Content-Type": "application/json"}
        )
        
        print(f"📝 Response status: {response.status_code}")
        print(f"📝 Response headers: {dict(response.headers)}")
        print(f"📝 Response text: {response.text}")
        
        if response.status_code == 201:
            print("✅ Backend caption creation successful")
            return True
        else:
            print(f"❌ Backend caption creation failed: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Backend caption creation error: {e}")
        return False

def main():
    """Run backend tests"""
    print("🚀 Starting Backend Environment Tests...")
    print("=" * 50)
    
    tests = [
        ("Backend Environment", test_backend_environment),
        ("Backend Caption Creation", test_backend_caption_creation)
    ]
    
    results = []
    
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ {test_name} test crashed: {e}")
            results.append((test_name, False))
    
    print("\n" + "=" * 50)
    print("📊 Backend Test Results:")
    print("=" * 50)
    
    passed = 0
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} {test_name}")
        if result:
            passed += 1
    
    print(f"\n🎯 Summary: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All backend tests passed!")
    else:
        print("⚠️ Some backend tests failed. Check the logs above for details.")

if __name__ == "__main__":
    main()
