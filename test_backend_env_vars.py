#!/usr/bin/env python3
"""
Test backend environment variables
"""

import requests
import json

def test_backend_environment():
    """Test backend environment variables"""
    print("🔍 Testing Backend Environment Variables...")
    
    try:
        # Test the info endpoint to see environment status
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

def test_backend_caption_with_debug():
    """Test backend caption creation with debug info"""
    print("\n🔍 Testing Backend Caption Creation with Debug...")
    
    caption_data = {
        "text": "Test caption for environment debug",
        "category": "test",
        "tags": ["debug", "env", "test"]
    }
    
    try:
        response = requests.post(
            "https://threads-bot-dashboard-3.onrender.com/api/captions",
            json=caption_data,
            headers={"Content-Type": "application/json"}
        )
        
        print(f"Backend response: {response.status_code}")
        print(f"Response body: {response.text}")
        
        if response.status_code == 201:
            print("✅ Backend caption creation successful")
            return True
        else:
            print(f"❌ Backend caption creation failed: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Backend test error: {e}")
        return False

def test_direct_supabase_again():
    """Test direct Supabase again to confirm it works"""
    print("\n🔍 Testing Direct Supabase Again...")
    
    supabase_url = "https://perwbmtwutwzsvlirwik.supabase.co"
    service_key = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InBlcndibXR3dXR3enN2bGlyd2lrIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc1NDQwNTU4MiwiZXhwIjoyMDY5OTgxNTgyfQ.fpTpKFrK0Eg60rN7jpWPKKQFTmIrxVlcHY2MMeKx2AE"
    
    headers = {
        'apikey': service_key,
        'Authorization': f'Bearer {service_key}',
        'Content-Type': 'application/json',
        'Prefer': 'return=representation'
    }
    
    caption_data = {
        "text": "Test caption from direct API again",
        "category": "test",
        "tags": ["direct", "again", "test"],
        "used": False
    }
    
    try:
        response = requests.post(
            f"{supabase_url}/rest/v1/captions",
            json=caption_data,
            headers=headers
        )
        
        print(f"Direct Supabase response: {response.status_code}")
        
        if response.status_code == 201:
            print("✅ Direct Supabase insert successful")
            return True
        else:
            print(f"❌ Direct Supabase insert failed: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Direct Supabase test error: {e}")
        return False

def main():
    """Run environment tests"""
    print("🚀 Starting Backend Environment Tests...")
    print("=" * 60)
    
    tests = [
        ("Backend Environment Check", test_backend_environment),
        ("Backend Caption Creation", test_backend_caption_with_debug),
        ("Direct Supabase Test", test_direct_supabase_again)
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
        print("\n💡 The issue is likely:")
        print("1. Backend environment variables not set correctly in Render")
        print("2. Backend is not using the service role key properly")
        print("3. Need to check Render logs for detailed error messages")

if __name__ == "__main__":
    main()
