#!/usr/bin/env python3
"""
Quick Test Script for Threads Bot API
Simple verification of core functionality
"""

import requests
import json
from datetime import datetime

def test_endpoint(url: str, method: str = "GET", data: dict = None) -> dict:
    """Test a single endpoint"""
    try:
        if method == "GET":
            response = requests.get(url)
        elif method == "POST":
            response = requests.post(url, json=data, headers={'Content-Type': 'application/json'})
        else:
            return {"success": False, "error": f"Unsupported method: {method}"}
        
        if response.status_code == 200:
            return {"success": True, "data": response.json()}
        else:
            return {"success": False, "error": f"HTTP {response.status_code}: {response.text}"}
    except Exception as e:
        return {"success": False, "error": str(e)}

def run_quick_tests():
    """Run quick tests"""
    base_url = "https://threads-bot-dashboard-3.onrender.com"
    
    print("🧪 Quick API Tests")
    print("=" * 40)
    
    # Test 1: Health endpoint
    print("1. Testing health endpoint...")
    health_result = test_endpoint(f"{base_url}/api/health")
    if health_result["success"]:
        print("   ✅ Health endpoint working")
    else:
        print(f"   ❌ Health endpoint failed: {health_result['error']}")
    
    # Test 2: Accounts endpoint
    print("2. Testing accounts endpoint...")
    accounts_result = test_endpoint(f"{base_url}/api/accounts")
    if accounts_result["success"]:
        accounts = accounts_result["data"].get("accounts", [])
        print(f"   ✅ Accounts endpoint working - {len(accounts)} accounts found")
    else:
        print(f"   ❌ Accounts endpoint failed: {accounts_result['error']}")
    
    # Test 3: Captions endpoint
    print("3. Testing captions endpoint...")
    captions_result = test_endpoint(f"{base_url}/api/captions")
    if captions_result["success"]:
        captions = captions_result["data"].get("captions", [])
        print(f"   ✅ Captions endpoint working - {len(captions)} captions found")
    else:
        print(f"   ❌ Captions endpoint failed: {captions_result['error']}")
    
    # Test 4: Images endpoint
    print("4. Testing images endpoint...")
    images_result = test_endpoint(f"{base_url}/api/images")
    if images_result["success"]:
        images = images_result["data"].get("images", [])
        print(f"   ✅ Images endpoint working - {len(images)} images found")
    else:
        print(f"   ❌ Images endpoint failed: {images_result['error']}")
    
    # Test 5: Login endpoint (with test credentials)
    print("5. Testing login endpoint...")
    login_data = {"username": "test_user", "password": "test_pass"}
    login_result = test_endpoint(f"{base_url}/api/accounts/login", "POST", login_data)
    if login_result["success"]:
        data = login_result["data"]
        if data.get("success"):
            print("   ✅ Login endpoint working (test credentials)")
        else:
            print(f"   ⚠️ Login endpoint working but test credentials failed: {data.get('error')}")
    else:
        print(f"   ❌ Login endpoint failed: {login_result['error']}")
    
    print("\n" + "=" * 40)
    print("✅ Quick tests completed!")

if __name__ == "__main__":
    run_quick_tests()
