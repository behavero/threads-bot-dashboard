#!/usr/bin/env python3
"""
Test frontend API with OPTIONS allowlist
"""

import requests
import json

def test_frontend_api_with_options():
    """Test frontend API after OPTIONS allowlist is enabled"""
    print("🔍 Testing Frontend API with OPTIONS Allowlist...")
    
    # Test GET request
    try:
        response = requests.get("https://threads-bot-dashboard-g8bxqd6c0-behaveros-projects.vercel.app/api/prompts")
        print(f"Frontend GET response: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                prompts = data.get('prompts', [])
                print(f"✅ Frontend GET successful: {len(prompts)} captions")
                return True
            else:
                print(f"❌ Frontend GET failed: {data.get('error', 'Unknown error')}")
                return False
        else:
            print(f"❌ Frontend GET failed: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Frontend GET error: {e}")
        return False

def test_frontend_post_with_options():
    """Test frontend POST request after OPTIONS allowlist"""
    print("\n🔍 Testing Frontend POST with OPTIONS Allowlist...")
    
    caption_data = {
        "text": "Test caption with OPTIONS allowlist",
        "category": "test",
        "tags": ["options", "allowlist", "test"]
    }
    
    try:
        response = requests.post(
            "https://threads-bot-dashboard-g8bxqd6c0-behaveros-projects.vercel.app/api/prompts",
            json=caption_data,
            headers={"Content-Type": "application/json"}
        )
        
        print(f"Frontend POST response: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                print("✅ Frontend POST successful")
                return True
            else:
                print(f"❌ Frontend POST failed: {data.get('error', 'Unknown error')}")
                return False
        else:
            print(f"❌ Frontend POST failed: {response.status_code}")
            print(f"Response: {response.text[:200]}")
            return False
            
    except Exception as e:
        print(f"❌ Frontend POST error: {e}")
        return False

def test_backend_direct():
    """Test backend directly"""
    print("\n🔍 Testing Backend Direct...")
    
    caption_data = {
        "text": "Test caption from backend direct",
        "category": "test",
        "tags": ["backend", "direct", "test"]
    }
    
    try:
        response = requests.post(
            "https://threads-bot-dashboard-3.onrender.com/api/captions",
            json=caption_data,
            headers={"Content-Type": "application/json"}
        )
        
        print(f"Backend response: {response.status_code}")
        
        if response.status_code == 201:
            print("✅ Backend direct successful")
            return True
        else:
            print(f"❌ Backend direct failed: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Backend direct error: {e}")
        return False

def main():
    """Run OPTIONS allowlist tests"""
    print("🚀 Starting OPTIONS Allowlist Tests...")
    print("=" * 60)
    print("💡 Make sure to enable OPTIONS Allowlist in Vercel first!")
    print("=" * 60)
    
    tests = [
        ("Frontend GET with OPTIONS", test_frontend_api_with_options),
        ("Frontend POST with OPTIONS", test_frontend_post_with_options),
        ("Backend Direct", test_backend_direct)
    ]
    
    results = []
    
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ {test_name} test crashed: {e}")
            results.append((test_name, False))
    
    print("\n" + "=" * 60)
    print("📊 Test Results:")
    print("=" * 60)
    
    passed = 0
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} {test_name}")
        if result:
            passed += 1
    
    print(f"\n🎯 Summary: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! OPTIONS Allowlist fixed the issue!")
    else:
        print("⚠️ Some tests failed. Check OPTIONS Allowlist configuration.")

if __name__ == "__main__":
    main()
