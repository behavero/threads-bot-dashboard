#!/usr/bin/env python3
"""
Test RLS bypass and database operations
"""

import requests
import json

def test_direct_supabase_insert():
    """Test direct Supabase insert with service role"""
    print("🔍 Testing Direct Supabase Insert with Service Role...")
    
    supabase_url = "https://perwbmtwutwzsvlirwik.supabase.co"
    service_key = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InBlcndibXR3dXR3enN2bGlyd2lrIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc1NDQwNTU4MiwiZXhwIjoyMDY5OTgxNTgyfQ.fpTpKFrK0Eg60rN7jpWPKKQFTmIrxVlcHY2MMeKx2AE"
    
    headers = {
        'apikey': service_key,
        'Authorization': f'Bearer {service_key}',
        'Content-Type': 'application/json',
        'Prefer': 'return=representation'
    }
    
    caption_data = {
        "text": "Test caption from direct API",
        "category": "test",
        "tags": ["direct", "test"],
        "used": False
    }
    
    try:
        response = requests.post(
            f"{supabase_url}/rest/v1/captions",
            json=caption_data,
            headers=headers
        )
        
        print(f"Direct Supabase response: {response.status_code}")
        print(f"Response body: {response.text}")
        
        if response.status_code == 201:
            print("✅ Direct Supabase insert successful")
            return True
        else:
            print(f"❌ Direct Supabase insert failed: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Direct Supabase test error: {e}")
        return False

def test_backend_with_service_role():
    """Test backend with service role key"""
    print("\n🔍 Testing Backend with Service Role...")
    
    caption_data = {
        "text": "Test caption from backend service role",
        "category": "test",
        "tags": ["backend", "service", "test"]
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

def test_rls_policies():
    """Test RLS policies by checking table structure"""
    print("\n🔍 Testing RLS Policies...")
    
    supabase_url = "https://perwbmtwutwzsvlirwik.supabase.co"
    service_key = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InBlcndibXR3dXR3enN2bGlyd2lrIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc1NDQwNTU4MiwiZXhwIjoyMDY5OTgxNTgyfQ.fpTpKFrK0Eg60rN7jpWPKKQFTmIrxVlcHY2MMeKx2AE"
    
    headers = {
        'apikey': service_key,
        'Authorization': f'Bearer {service_key}',
        'Content-Type': 'application/json'
    }
    
    try:
        # Check table structure
        response = requests.get(
            f"{supabase_url}/rest/v1/captions?select=*&limit=1",
            headers=headers
        )
        
        print(f"Table structure response: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            if data:
                sample = data[0]
                print(f"✅ Table accessible. Sample record: {sample}")
                print(f"Columns: {list(sample.keys())}")
                return True
            else:
                print("✅ Table accessible but empty")
                return True
        else:
            print(f"❌ Table access failed: {response.status_code}")
            print(f"Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ RLS test error: {e}")
        return False

def main():
    """Run RLS tests"""
    print("🚀 Starting RLS and Database Tests...")
    print("=" * 60)
    
    tests = [
        ("Direct Supabase Insert", test_direct_supabase_insert),
        ("Backend Service Role", test_backend_with_service_role),
        ("RLS Policies Check", test_rls_policies)
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
        print("\n💡 If RLS tests are failing:")
        print("1. Check Supabase RLS policies for captions table")
        print("2. Ensure service role has proper permissions")
        print("3. Verify table structure matches expectations")

if __name__ == "__main__":
    main()
