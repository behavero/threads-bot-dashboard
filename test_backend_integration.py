#!/usr/bin/env python3
"""
Test backend integration for captions
"""

import requests
import json

def test_backend_captions_api():
    """Test backend captions API"""
    print("🔍 Testing Backend Captions API...")
    
    # Test GET captions
    try:
        response = requests.get("https://threads-bot-dashboard-3.onrender.com/api/captions")
        
        if response.status_code == 200:
            data = response.json()
            captions = data.get('captions', [])
            print(f"✅ Backend GET captions successful: {len(captions)} captions")
            return True
        else:
            print(f"❌ Backend GET captions failed: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Backend GET captions error: {e}")
        return False

def test_backend_add_caption():
    """Test adding a caption via backend"""
    print("\n🔍 Testing Backend Add Caption...")
    
    caption_data = {
        "text": "Test caption from backend integration",
        "category": "test",
        "tags": ["backend", "integration", "test"]
    }
    
    try:
        response = requests.post(
            "https://threads-bot-dashboard-3.onrender.com/api/captions",
            json=caption_data,
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 201:
            data = response.json()
            print("✅ Backend add caption successful")
            return True
        else:
            print(f"❌ Backend add caption failed: {response.status_code}")
            print(f"Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Backend add caption error: {e}")
        return False

def test_backend_csv_upload():
    """Test CSV upload via backend"""
    print("\n🔍 Testing Backend CSV Upload...")
    
    # Create a simple CSV content
    csv_content = """Test caption 1,general,"tag1|tag2"
Test caption 2,business,"business|professional"
Test caption 3,personal,"personal|life"
"""
    
    try:
        # Create a file-like object
        files = {'file': ('test.csv', csv_content, 'text/csv')}
        
        response = requests.post(
            "https://threads-bot-dashboard-3.onrender.com/api/captions/upload-csv",
            files=files
        )
        
        if response.status_code == 201:
            data = response.json()
            print(f"✅ Backend CSV upload successful: {data.get('count', 0)} captions")
            return True
        else:
            print(f"❌ Backend CSV upload failed: {response.status_code}")
            print(f"Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Backend CSV upload error: {e}")
        return False

def main():
    """Run backend integration tests"""
    print("🚀 Starting Backend Integration Tests...")
    print("=" * 60)
    
    tests = [
        ("Backend GET Captions", test_backend_captions_api),
        ("Backend Add Caption", test_backend_add_caption),
        ("Backend CSV Upload", test_backend_csv_upload)
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
        print("🎉 All backend tests passed! Backend integration is working perfectly.")
        print("\n💡 Next steps:")
        print("1. Disable all Vercel protection settings")
        print("2. Test the frontend in the browser")
        print("3. The frontend should now work by calling the backend directly")
    else:
        print("⚠️ Some backend tests failed. Check the backend deployment.")

if __name__ == "__main__":
    main()
