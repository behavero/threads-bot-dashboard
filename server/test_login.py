#!/usr/bin/env python3
"""
Test script for Threads login functionality
"""

import requests
import json

def test_login():
    """Test the login endpoint"""
    url = "https://threads-bot-dashboard-3.onrender.com/api/accounts/login"
    
    # Test data (replace with real credentials for testing)
    test_data = {
        "username": "test_username",
        "password": "test_password"
    }
    
    print("🧪 Testing Threads login endpoint...")
    print(f"📡 URL: {url}")
    print(f"📝 Data: {json.dumps(test_data, indent=2)}")
    
    try:
        response = requests.post(url, json=test_data, headers={
            'Content-Type': 'application/json'
        })
        
        print(f"📊 Status Code: {response.status_code}")
        print(f"📊 Response Headers: {dict(response.headers)}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Success Response: {json.dumps(data, indent=2)}")
        else:
            data = response.json()
            print(f"❌ Error Response: {json.dumps(data, indent=2)}")
            
    except Exception as e:
        print(f"❌ Request failed: {e}")

if __name__ == "__main__":
    test_login()
