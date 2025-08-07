#!/usr/bin/env python3
"""
Simple test to check frontend accessibility
"""

import requests

FRONTEND_URL = "https://threads-bot-dashboard-g8bxqd6c0-behaveros-projects.vercel.app"

def test_frontend_access():
    """Test if frontend is accessible"""
    print("🔍 Testing Frontend Access...")
    
    try:
        # Test basic page access
        response = requests.get(FRONTEND_URL)
        print(f"✅ Frontend accessible: {response.status_code}")
        
        # Test API endpoints directly
        api_endpoints = [
            "/api/prompts",
            "/api/images",
            "/api/test-supabase"
        ]
        
        for endpoint in api_endpoints:
            try:
                response = requests.get(f"{FRONTEND_URL}{endpoint}")
                print(f"✅ {endpoint}: {response.status_code}")
                if response.status_code == 200:
                    data = response.json()
                    print(f"   Data: {data.get('success', 'unknown')}")
            except Exception as e:
                print(f"❌ {endpoint}: {e}")
                
    except Exception as e:
        print(f"❌ Frontend access error: {e}")

if __name__ == "__main__":
    test_frontend_access()
