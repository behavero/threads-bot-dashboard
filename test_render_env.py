#!/usr/bin/env python3
"""
Test Render environment variables
"""

import requests
import json

def test_render_environment():
    """Test if Render has the correct environment variables"""
    print("🔍 Testing Render Environment Variables...")
    
    try:
        # Test the info endpoint which should show environment status
        response = requests.get("https://threads-bot-dashboard-3.onrender.com/api/info")
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Backend info: {data}")
            
            # Check if Supabase is connected
            if data.get('supabase_connected'):
                print("✅ Supabase is connected")
                return True
            else:
                print("❌ Supabase is not connected")
                return False
        else:
            print(f"❌ Backend info failed: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Backend test error: {e}")
        return False

def test_caption_creation_with_logs():
    """Test caption creation and get detailed logs"""
    print("\n🔍 Testing Caption Creation with Detailed Logs...")
    
    caption_data = {
        "text": "Test caption for environment check",
        "category": "test",
        "tags": ["env", "test"]
    }
    
    try:
        response = requests.post(
            "https://threads-bot-dashboard-3.onrender.com/api/captions",
            json=caption_data,
            headers={"Content-Type": "application/json"}
        )
        
        print(f"Response status: {response.status_code}")
        print(f"Response body: {response.text}")
        
        if response.status_code == 201:
            print("✅ Caption created successfully")
            return True
        else:
            print(f"❌ Caption creation failed: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Caption creation error: {e}")
        return False

def main():
    """Run environment tests"""
    print("🚀 Starting Render Environment Tests...")
    print("=" * 60)
    
    tests = [
        ("Render Environment Check", test_render_environment),
        ("Caption Creation Test", test_caption_creation_with_logs)
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
    
    if passed < total:
        print("\n💡 To fix the environment issues:")
        print("1. Go to your Render dashboard")
        print("2. Find your 'threads-bot-dashboard-3' service")
        print("3. Go to Environment → Environment Variables")
        print("4. Add these variables:")
        print("   - SUPABASE_URL = https://perwbmtwutwzsvlirwik.supabase.co")
        print("   - SUPABASE_KEY = [your service role key]")
        print("5. Redeploy the service")

if __name__ == "__main__":
    main()
