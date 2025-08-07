#!/usr/bin/env python3
"""
Test Supabase connection and environment variables
"""

import requests
import json
import os

# Supabase configuration
SUPABASE_URL = "https://perwbmtwutwzsvlirwik.supabase.co"
SUPABASE_ANON_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InBlcndibXR3dXR3enN2bGlyd2lrIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTQ0MDU1ODIsImV4cCI6MjA2OTk4MTU4Mn0.ACJ6v7w4brocGyhC3hlsWI_huE3-3kSdQjLSCijw56o"
SUPABASE_SERVICE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InBlcndibXR3dXR3enN2bGlyd2lrIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc1NDQwNTU4MiwiZXhwIjoyMDY5OTgxNTgyfQ.fpTpKFrK0Eg60rN7jpWPKKQFTmIrxVlcHY2MMeKx2AE"

def test_supabase_direct():
    """Test direct Supabase connection"""
    print("🔍 Testing Direct Supabase Connection...")
    
    headers = {
        'apikey': SUPABASE_ANON_KEY,
        'Authorization': f'Bearer {SUPABASE_ANON_KEY}',
        'Content-Type': 'application/json'
    }
    
    try:
        # Test fetching captions
        response = requests.get(
            f"{SUPABASE_URL}/rest/v1/captions",
            headers=headers
        )
        
        print(f"Supabase direct response: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Supabase direct connection successful: {len(data)} captions")
            return True
        else:
            print(f"❌ Supabase direct connection failed: {response.status_code}")
            print(f"Response: {response.text[:200]}")
            return False
            
    except Exception as e:
        print(f"❌ Supabase direct test error: {e}")
        return False

def test_supabase_service_role():
    """Test Supabase with service role key"""
    print("\n🔍 Testing Supabase with Service Role...")
    
    headers = {
        'apikey': SUPABASE_SERVICE_KEY,
        'Authorization': f'Bearer {SUPABASE_SERVICE_KEY}',
        'Content-Type': 'application/json'
    }
    
    try:
        # Test fetching captions
        response = requests.get(
            f"{SUPABASE_URL}/rest/v1/captions",
            headers=headers
        )
        
        print(f"Supabase service role response: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Supabase service role connection successful: {len(data)} captions")
            return True
        else:
            print(f"❌ Supabase service role connection failed: {response.status_code}")
            print(f"Response: {response.text[:200]}")
            return False
            
    except Exception as e:
        print(f"❌ Supabase service role test error: {e}")
        return False

def test_frontend_simple():
    """Test frontend with simple request"""
    print("\n🔍 Testing Frontend Simple Request...")
    
    try:
        response = requests.get("https://threads-bot-dashboard-g8bxqd6c0-behaveros-projects.vercel.app/api/test-simple")
        print(f"Frontend simple response: {response.status_code}")
        
        if response.status_code == 200:
            print("✅ Frontend simple request successful")
            return True
        else:
            print(f"❌ Frontend simple request failed: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Frontend simple test error: {e}")
        return False

def main():
    """Run all tests"""
    print("🚀 Starting Supabase Connection Tests...")
    print("=" * 60)
    
    tests = [
        ("Supabase Direct Connection", test_supabase_direct),
        ("Supabase Service Role", test_supabase_service_role),
        ("Frontend Simple Request", test_frontend_simple)
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

if __name__ == "__main__":
    main()
