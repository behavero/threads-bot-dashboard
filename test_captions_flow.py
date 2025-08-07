#!/usr/bin/env python3
"""
Test script to verify captions data flow
"""

import requests
import json
import os
from datetime import datetime

# Configuration
BACKEND_URL = "https://threads-bot-dashboard-3.onrender.com"
FRONTEND_URL = "https://threads-bot-dashboard-g8bxqd6c0-behaveros-projects.vercel.app"

def test_backend_captions():
    """Test backend captions API"""
    print("🔍 Testing Backend Captions API...")
    
    try:
        # Test getting captions
        response = requests.get(f"{BACKEND_URL}/api/captions")
        if response.status_code == 200:
            data = response.json()
            captions = data.get('captions', [])
            print(f"✅ Backend captions fetched: {len(captions)}")
            
            if captions:
                sample = captions[0]
                print(f"   Sample caption: {sample.get('text', '')[:50]}...")
                print(f"   Category: {sample.get('category', 'N/A')}")
                print(f"   Tags: {sample.get('tags', [])}")
        else:
            print(f"❌ Backend captions failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Backend captions error: {e}")
        return False
    
    return True

def test_backend_caption_creation():
    """Test creating a caption through backend"""
    print("\n🔍 Testing Backend Caption Creation...")
    
    try:
        caption_data = {
            "text": f"Test caption from backend at {datetime.now().isoformat()}",
            "category": "test",
            "tags": ["backend", "test", "automated"]
        }
        
        response = requests.post(
            f"{BACKEND_URL}/api/captions",
            json=caption_data,
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 201:
            print("✅ Backend caption created successfully")
            return True
        else:
            print(f"❌ Backend caption creation failed: {response.status_code} - {response.text}")
            return False
    except Exception as e:
        print(f"❌ Backend caption creation error: {e}")
        return False

def test_frontend_captions():
    """Test frontend captions API"""
    print("\n🔍 Testing Frontend Captions API...")
    
    try:
        # Test getting captions
        response = requests.get(f"{FRONTEND_URL}/api/prompts")
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                prompts = data.get('prompts', [])
                print(f"✅ Frontend captions fetched: {len(prompts)}")
                
                if prompts:
                    sample = prompts[0]
                    print(f"   Sample caption: {sample.get('text', '')[:50]}...")
                    print(f"   Category: {sample.get('category', 'N/A')}")
                    print(f"   Tags: {sample.get('tags', [])}")
                return True
            else:
                print(f"❌ Frontend captions failed: {data.get('error', 'Unknown error')}")
                return False
        else:
            print(f"❌ Frontend captions failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Frontend captions error: {e}")
        return False

def test_frontend_caption_creation():
    """Test creating a caption through frontend"""
    print("\n🔍 Testing Frontend Caption Creation...")
    
    try:
        caption_data = {
            "text": f"Test caption from frontend at {datetime.now().isoformat()}",
            "category": "test",
            "tags": ["frontend", "test", "automated"]
        }
        
        response = requests.post(
            f"{FRONTEND_URL}/api/prompts",
            json=caption_data,
            headers={"Content-Type": "application/json"}
        )
        
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
            return False
    except Exception as e:
        print(f"❌ Frontend caption creation error: {e}")
        return False

def test_csv_upload():
    """Test CSV upload functionality"""
    print("\n🔍 Testing CSV Upload...")
    
    try:
        # Create a test CSV file
        csv_content = """Test caption 1,general,test|automated
Test caption 2,business,professional|work
Test caption 3,humor,funny|entertainment"""
        
        # Test the CSV upload endpoint
        files = {'file': ('test_captions.csv', csv_content, 'text/csv')}
        
        response = requests.post(
            f"{FRONTEND_URL}/api/prompts/upload-csv",
            files=files
        )
        
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                print("✅ CSV upload test successful")
                return True
            else:
                print(f"❌ CSV upload failed: {data.get('error', 'Unknown error')}")
                return False
        else:
            print(f"❌ CSV upload failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ CSV upload error: {e}")
        return False

def main():
    """Run all caption tests"""
    print("🚀 Starting Captions Data Flow Tests...")
    print("=" * 50)
    
    tests = [
        ("Backend Captions API", test_backend_captions),
        ("Backend Caption Creation", test_backend_caption_creation),
        ("Frontend Captions API", test_frontend_captions),
        ("Frontend Caption Creation", test_frontend_caption_creation),
        ("CSV Upload", test_csv_upload)
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
    print("📊 Captions Test Results:")
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
        print("🎉 All caption tests passed! Data flow is working correctly.")
    else:
        print("⚠️ Some caption tests failed. Check the logs above for details.")

if __name__ == "__main__":
    main()
