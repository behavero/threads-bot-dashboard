#!/usr/bin/env python3
"""
Test script to verify data flow between frontend, backend, and Supabase
"""

import requests
import json
import os
from datetime import datetime

# Configuration
BACKEND_URL = "https://threads-bot-dashboard-3.onrender.com"
FRONTEND_URL = "https://threads-bot-dashboard-g8bxqd6c0-behaveros-projects.vercel.app"

def test_backend_health():
    """Test backend health and basic functionality"""
    print("🔍 Testing Backend Health...")
    
    try:
        # Test basic health endpoint
        response = requests.get(f"{BACKEND_URL}/api/status")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Backend Status: {data.get('status')}")
            print(f"✅ Bot Running: {data.get('bot_running')}")
        else:
            print(f"❌ Backend health check failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Backend connection error: {e}")
        return False
    
    return True

def test_backend_database():
    """Test backend database operations"""
    print("\n🔍 Testing Backend Database Operations...")
    
    try:
        # Test getting captions
        response = requests.get(f"{BACKEND_URL}/api/captions")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Captions fetched: {len(data.get('captions', []))}")
        else:
            print(f"❌ Failed to fetch captions: {response.status_code}")
        
        # Test getting images
        response = requests.get(f"{BACKEND_URL}/api/images")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Images fetched: {len(data.get('images', []))}")
        else:
            print(f"❌ Failed to fetch images: {response.status_code}")
        
        # Test getting accounts
        response = requests.get(f"{BACKEND_URL}/api/accounts")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Accounts fetched: {len(data.get('accounts', []))}")
        else:
            print(f"❌ Failed to fetch accounts: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Database test error: {e}")
        return False
    
    return True

def test_frontend_api():
    """Test frontend API endpoints"""
    print("\n🔍 Testing Frontend API...")
    
    try:
        # Test getting captions from frontend
        response = requests.get(f"{FRONTEND_URL}/api/prompts")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Frontend captions: {len(data.get('prompts', []))}")
        else:
            print(f"❌ Frontend captions failed: {response.status_code}")
        
        # Test getting images from frontend
        response = requests.get(f"{FRONTEND_URL}/api/images")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Frontend images: {len(data.get('images', []))}")
        else:
            print(f"❌ Frontend images failed: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Frontend API test error: {e}")
        return False
    
    return True

def test_caption_creation():
    """Test creating a caption through the backend"""
    print("\n🔍 Testing Caption Creation...")
    
    try:
        caption_data = {
            "text": f"Test caption created at {datetime.now().isoformat()}",
            "category": "test",
            "tags": ["test", "automated"]
        }
        
        response = requests.post(
            f"{BACKEND_URL}/api/captions",
            json=caption_data,
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 201:
            print("✅ Caption created successfully")
            return True
        else:
            print(f"❌ Caption creation failed: {response.status_code} - {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Caption creation error: {e}")
        return False

def test_image_creation():
    """Test creating an image record through the backend"""
    print("\n🔍 Testing Image Creation...")
    
    try:
        image_data = {
            "url": "https://example.com/test-image.jpg",
            "filename": "test-image.jpg",
            "size": 1024,
            "type": "image/jpeg"
        }
        
        response = requests.post(
            f"{BACKEND_URL}/api/images",
            json=image_data,
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 201:
            print("✅ Image record created successfully")
            return True
        else:
            print(f"❌ Image creation failed: {response.status_code} - {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Image creation error: {e}")
        return False

def test_statistics():
    """Test getting statistics"""
    print("\n🔍 Testing Statistics...")
    
    try:
        response = requests.get(f"{BACKEND_URL}/api/stats")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Statistics retrieved:")
            print(f"   - Total accounts: {data.get('total_accounts', 0)}")
            print(f"   - Total captions: {data.get('total_captions', 0)}")
            print(f"   - Total images: {data.get('total_images', 0)}")
            print(f"   - Bot status: {data.get('bot_status', 'unknown')}")
            return True
        else:
            print(f"❌ Statistics failed: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Statistics error: {e}")
        return False

def main():
    """Run all tests"""
    print("🚀 Starting Data Flow Tests...")
    print("=" * 50)
    
    tests = [
        ("Backend Health", test_backend_health),
        ("Backend Database", test_backend_database),
        ("Frontend API", test_frontend_api),
        ("Caption Creation", test_caption_creation),
        ("Image Creation", test_image_creation),
        ("Statistics", test_statistics)
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
    print("📊 Test Results:")
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
        print("🎉 All tests passed! Data flow is working correctly.")
    else:
        print("⚠️ Some tests failed. Check the logs above for details.")

if __name__ == "__main__":
    main()
