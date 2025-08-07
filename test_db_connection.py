#!/usr/bin/env python3
"""
Test database connection and schema
"""

import os
import requests
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def test_database_connection():
    """Test the database connection"""
    print("🔍 Testing Database Connection...")
    
    supabase_url = os.getenv('SUPABASE_URL')
    supabase_key = os.getenv('SUPABASE_KEY')
    
    print(f"Supabase URL: {supabase_url}")
    print(f"Supabase Key exists: {bool(supabase_key)}")
    
    if not supabase_url or not supabase_key:
        print("❌ Missing Supabase credentials")
        return False
    
    headers = {
        'apikey': supabase_key,
        'Authorization': f'Bearer {supabase_key}',
        'Content-Type': 'application/json',
        'Prefer': 'return=representation'
    }
    
    try:
        # Test connection by getting captions
        response = requests.get(
            f"{supabase_url}/rest/v1/captions",
            headers=headers
        )
        
        print(f"Response status: {response.status_code}")
        print(f"Response text: {response.text[:200]}")
        
        if response.status_code == 200:
            captions = response.json()
            print(f"✅ Database connection successful")
            print(f"✅ Captions count: {len(captions)}")
            return True
        else:
            print(f"❌ Database connection failed: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Database connection error: {e}")
        return False

def test_caption_insertion():
    """Test inserting a caption"""
    print("\n🔍 Testing Caption Insertion...")
    
    supabase_url = os.getenv('SUPABASE_URL')
    supabase_key = os.getenv('SUPABASE_KEY')
    
    headers = {
        'apikey': supabase_key,
        'Authorization': f'Bearer {supabase_key}',
        'Content-Type': 'application/json',
        'Prefer': 'return=representation'
    }
    
    caption_data = {
        "text": "Test caption from direct API",
        "category": "test",
        "tags": ["test", "direct"],
        "used": False
    }
    
    try:
        response = requests.post(
            f"{supabase_url}/rest/v1/captions",
            json=caption_data,
            headers=headers
        )
        
        print(f"Response status: {response.status_code}")
        print(f"Response text: {response.text}")
        
        if response.status_code == 201:
            print("✅ Caption insertion successful")
            return True
        else:
            print(f"❌ Caption insertion failed: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Caption insertion error: {e}")
        return False

def test_schema():
    """Test the database schema"""
    print("\n🔍 Testing Database Schema...")
    
    supabase_url = os.getenv('SUPABASE_URL')
    supabase_key = os.getenv('SUPABASE_KEY')
    
    headers = {
        'apikey': supabase_key,
        'Authorization': f'Bearer {supabase_key}',
        'Content-Type': 'application/json'
    }
    
    try:
        # Test getting table information
        response = requests.get(
            f"{supabase_url}/rest/v1/captions?select=*&limit=1",
            headers=headers
        )
        
        print(f"Schema test response status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            if data:
                sample = data[0]
                print(f"✅ Schema test successful")
                print(f"   Available fields: {list(sample.keys())}")
                return True
            else:
                print("✅ Schema test successful (no data)")
                return True
        else:
            print(f"❌ Schema test failed: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Schema test error: {e}")
        return False

def main():
    """Run all database tests"""
    print("🚀 Starting Database Tests...")
    print("=" * 50)
    
    tests = [
        ("Database Connection", test_database_connection),
        ("Database Schema", test_schema),
        ("Caption Insertion", test_caption_insertion)
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
    print("📊 Database Test Results:")
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
        print("🎉 All database tests passed!")
    else:
        print("⚠️ Some database tests failed. Check the logs above for details.")

if __name__ == "__main__":
    main()
