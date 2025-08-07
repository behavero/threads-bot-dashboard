#!/usr/bin/env python3
"""
Test captions API with Vercel protection bypass
"""

import requests
import json
from datetime import datetime

# Configuration
FRONTEND_URL = "https://threads-bot-dashboard-g8bxqd6c0-behaveros-projects.vercel.app"
BACKEND_URL = "https://threads-bot-dashboard-3.onrender.com"

# Add your protection bypass secret here (replace with your actual secret)
PROTECTION_BYPASS_SECRET = "H8DTho5Qi6iBblInCT0OCYM09DcaF1ul"  # Your actual Vercel bypass secret

def test_frontend_with_bypass():
    """Test frontend API with protection bypass"""
    print("🔍 Testing Frontend API with Protection Bypass...")
    
    headers = {
        'x-vercel-protection-bypass': PROTECTION_BYPASS_SECRET,
        'Content-Type': 'application/json'
    }
    
    try:
        # Test getting captions
        response = requests.get(f"{FRONTEND_URL}/api/prompts", headers=headers)
        print(f"Frontend captions response: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                prompts = data.get('prompts', [])
                print(f"✅ Frontend captions fetched: {len(prompts)} captions")
                return True
            else:
                print(f"❌ Frontend captions failed: {data.get('error', 'Unknown error')}")
                return False
        else:
            print(f"❌ Frontend captions failed: {response.status_code}")
            print(f"Response: {response.text[:200]}")
            return False
            
    except Exception as e:
        print(f"❌ Frontend test error: {e}")
        return False

def test_frontend_caption_creation_with_bypass():
    """Test creating a caption through frontend with bypass"""
    print("\n🔍 Testing Frontend Caption Creation with Bypass...")
    
    headers = {
        'x-vercel-protection-bypass': PROTECTION_BYPASS_SECRET,
        'Content-Type': 'application/json'
    }
    
    caption_data = {
        "text": f"Test caption with bypass at {datetime.now().isoformat()}",
        "category": "test",
        "tags": ["frontend", "bypass", "test"]
    }
    
    try:
        response = requests.post(
            f"{FRONTEND_URL}/api/prompts",
            json=caption_data,
            headers=headers
        )
        
        print(f"Frontend caption creation response: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                print("✅ Frontend caption created successfully")
                return True
            else:
                print(f"❌ Frontend caption creation failed: {data.get('error', 'Unknown error')}")
                return False
        else:
            print(f"❌ Frontend caption creation failed: {response.status_code}")
            print(f"Response: {response.text[:200]}")
            return False
            
    except Exception as e:
        print(f"❌ Frontend caption creation error: {e}")
        return False

def test_backend_caption_creation():
    """Test backend caption creation"""
    print("\n🔍 Testing Backend Caption Creation...")
    
    caption_data = {
        "text": f"Test caption from backend at {datetime.now().isoformat()}",
        "category": "test",
        "tags": ["backend", "test"]
    }
    
    try:
        response = requests.post(
            f"{BACKEND_URL}/api/captions",
            json=caption_data,
            headers={"Content-Type": "application/json"}
        )
        
        print(f"Backend caption creation response: {response.status_code}")
        
        if response.status_code == 201:
            print("✅ Backend caption created successfully")
            return True
        else:
            print(f"❌ Backend caption creation failed: {response.status_code}")
            print(f"Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Backend caption creation error: {e}")
        return False

def main():
    """Run all tests"""
    print("🚀 Starting Captions Tests with Protection Bypass...")
    print("=" * 60)
    print(f"Using bypass secret: {PROTECTION_BYPASS_SECRET}")
    print("=" * 60)
    
    tests = [
        ("Frontend API with Bypass", test_frontend_with_bypass),
        ("Frontend Caption Creation with Bypass", test_frontend_caption_creation_with_bypass),
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
        print("🎉 All tests passed! Captions data flow is working correctly.")
    else:
        print("⚠️ Some tests failed. Check the logs above for details.")
        print("\n💡 If frontend tests are failing, make sure to:")
        print("1. Add the protection bypass secret in Vercel")
        print("2. Update the PROTECTION_BYPASS_SECRET variable in this script")

if __name__ == "__main__":
    main()
