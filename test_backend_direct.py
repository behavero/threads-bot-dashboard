#!/usr/bin/env python3
"""
Test backend request exactly as the backend would do it
"""

import requests
import json
import os

def test_backend_exact_request():
    """Test the exact same request the backend would make"""
    print("🔍 Testing Backend Exact Request...")
    
    # Use the same environment variables the backend would use
    supabase_url = "https://perwbmtwutwzsvlirwik.supabase.co"
    service_key = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InBlcndibXR3dXR3enN2bGlyd2lrIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc1NDQwNTU4MiwiZXhwIjoyMDY5OTgxNTgyfQ.fpTpKFrK0Eg60rN7jpWPKKQFTmIrxVlcHY2MMeKx2AE"
    
    headers = {
        'apikey': service_key,
        'Authorization': f'Bearer {service_key}',
        'Content-Type': 'application/json',
        'Prefer': 'return=representation'
    }
    
    caption_data = {
        "text": "Test caption from exact backend request",
        "category": "test",
        "tags": ["exact", "backend", "test"],
        "used": False
    }
    
    print(f"📝 Request URL: {supabase_url}/rest/v1/captions")
    print(f"📝 Headers: {headers}")
    print(f"📝 Data: {caption_data}")
    
    try:
        response = requests.post(
            f"{supabase_url}/rest/v1/captions",
            json=caption_data,
            headers=headers
        )
        
        print(f"📝 Response status: {response.status_code}")
        print(f"📝 Response text: {response.text}")
        print(f"📝 Response headers: {dict(response.headers)}")
        
        if response.status_code == 201:
            print("✅ Exact backend request successful")
            return True
        else:
            print(f"❌ Exact backend request failed: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Exact backend request error: {e}")
        return False

def test_backend_vs_direct():
    """Compare backend vs direct requests"""
    print("\n🔍 Comparing Backend vs Direct Requests...")
    
    # Test backend
    backend_response = requests.post(
        "https://threads-bot-dashboard-3.onrender.com/api/captions",
        json={"text": "Backend test", "category": "test", "tags": ["backend"]},
        headers={"Content-Type": "application/json"}
    )
    
    print(f"Backend response: {backend_response.status_code}")
    print(f"Backend body: {backend_response.text}")
    
    # Test direct
    supabase_url = "https://perwbmtwutwzsvlirwik.supabase.co"
    service_key = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InBlcndibXR3dXR3enN2bGlyd2lrIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc1NDQwNTU4MiwiZXhwIjoyMDY5OTgxNTgyfQ.fpTpKFrK0Eg60rN7jpWPKKQFTmIrxVlcHY2MMeKx2AE"
    
    headers = {
        'apikey': service_key,
        'Authorization': f'Bearer {service_key}',
        'Content-Type': 'application/json',
        'Prefer': 'return=representation'
    }
    
    direct_response = requests.post(
        f"{supabase_url}/rest/v1/captions",
        json={"text": "Direct test", "category": "test", "tags": ["direct"], "used": False},
        headers=headers
    )
    
    print(f"Direct response: {direct_response.status_code}")
    print(f"Direct body: {direct_response.text}")
    
    return backend_response.status_code == 201, direct_response.status_code == 201

def main():
    """Run comparison tests"""
    print("🚀 Starting Backend vs Direct Comparison Tests...")
    print("=" * 60)
    
    # Test exact backend request
    exact_result = test_backend_exact_request()
    
    # Test comparison
    backend_success, direct_success = test_backend_vs_direct()
    
    print("\n" + "=" * 60)
    print("📊 Test Results:")
    print("=" * 60)
    
    print(f"{'✅ PASS' if exact_result else '❌ FAIL'} Exact Backend Request")
    print(f"{'✅ PASS' if backend_success else '❌ FAIL'} Backend API")
    print(f"{'✅ PASS' if direct_success else '❌ FAIL'} Direct Supabase")
    
    if exact_result and not backend_success:
        print("\n💡 The issue is in the backend code, not the database")
        print("Backend should work but doesn't - check backend logs")
    elif not exact_result:
        print("\n💡 The issue is with the database request itself")
        print("Even direct requests are failing")

if __name__ == "__main__":
    main()
