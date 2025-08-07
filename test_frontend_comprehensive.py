#!/usr/bin/env python3
"""
Comprehensive frontend API test
"""

import requests
import json

def test_frontend_simple():
    """Test the simple test endpoint"""
    print("🔍 Testing Frontend Simple Endpoint...")
    
    try:
        response = requests.get("https://threads-bot-dashboard-g8bxqd6c0-behaveros-projects.vercel.app/api/test-simple")
        print(f"Simple endpoint response: {response.status_code}")
        
        if response.status_code == 200:
            print("✅ Simple endpoint works")
            return True
        else:
            print(f"❌ Simple endpoint failed: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Simple endpoint error: {e}")
        return False

def test_frontend_with_bypass():
    """Test frontend with protection bypass"""
    print("\n🔍 Testing Frontend with Protection Bypass...")
    
    headers = {
        'x-vercel-protection-bypass': 'H8DTho5Qi6iBblInCT0OCYM09DcaF1ul',
        'Content-Type': 'application/json'
    }
    
    try:
        response = requests.get(
            "https://threads-bot-dashboard-g8bxqd6c0-behaveros-projects.vercel.app/api/prompts",
            headers=headers
        )
        print(f"Frontend with bypass response: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                print("✅ Frontend with bypass works")
                return True
            else:
                print(f"❌ Frontend with bypass failed: {data.get('error')}")
                return False
        else:
            print(f"❌ Frontend with bypass failed: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Frontend with bypass error: {e}")
        return False

def test_frontend_post_with_bypass():
    """Test frontend POST with bypass"""
    print("\n🔍 Testing Frontend POST with Bypass...")
    
    headers = {
        'x-vercel-protection-bypass': 'H8DTho5Qi6iBblInCT0OCYM09DcaF1ul',
        'Content-Type': 'application/json'
    }
    
    caption_data = {
        "text": "Test caption with bypass",
        "category": "test",
        "tags": ["bypass", "test"]
    }
    
    try:
        response = requests.post(
            "https://threads-bot-dashboard-g8bxqd6c0-behaveros-projects.vercel.app/api/prompts",
            json=caption_data,
            headers=headers
        )
        print(f"Frontend POST with bypass response: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                print("✅ Frontend POST with bypass works")
                return True
            else:
                print(f"❌ Frontend POST with bypass failed: {data.get('error')}")
                return False
        else:
            print(f"❌ Frontend POST with bypass failed: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Frontend POST with bypass error: {e}")
        return False

def test_backend_confirmation():
    """Confirm backend is working"""
    print("\n🔍 Confirming Backend is Working...")
    
    caption_data = {
        "text": "Backend confirmation test",
        "category": "test",
        "tags": ["backend", "confirmation"]
    }
    
    try:
        response = requests.post(
            "https://threads-bot-dashboard-3.onrender.com/api/captions",
            json=caption_data,
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 201:
            print("✅ Backend confirmation successful")
            return True
        else:
            print(f"❌ Backend confirmation failed: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Backend confirmation error: {e}")
        return False

def main():
    """Run comprehensive frontend tests"""
    print("🚀 Starting Comprehensive Frontend Tests...")
    print("=" * 60)
    
    tests = [
        ("Frontend Simple", test_frontend_simple),
        ("Frontend with Bypass", test_frontend_with_bypass),
        ("Frontend POST with Bypass", test_frontend_post_with_bypass),
        ("Backend Confirmation", test_backend_confirmation)
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
        print("🎉 All tests passed! Everything is working!")
    elif passed >= 2:
        print("⚠️ Most tests passed. Backend is working, frontend needs attention.")
        print("\n💡 For frontend issues:")
        print("1. Check Vercel OPTIONS Allowlist configuration")
        print("2. Verify protection bypass secret is correct")
        print("3. Consider temporarily disabling Vercel protection")
    else:
        print("❌ Most tests failed. Check configuration.")

if __name__ == "__main__":
    main()
