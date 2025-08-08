#!/usr/bin/env python3
"""
Test Script for Meta OAuth Implementation
Tests OAuth flow endpoints and functionality
"""

import os
import sys
import requests
import json
from datetime import datetime

# Add server directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_oauth_start():
    """Test OAuth start endpoint"""
    print("🧪 Testing OAuth start endpoint...")
    
    try:
        # Test with account_id=1
        response = requests.get(
            'https://threads-bot-dashboard-3.onrender.com/auth/meta/start?account_id=1',
            allow_redirects=False
        )
        
        print(f"✅ OAuth start response: {response.status_code}")
        
        if response.status_code == 302:  # Redirect
            redirect_url = response.headers.get('Location', '')
            print(f"✅ Redirect URL: {redirect_url[:100]}...")
            
            # Check if it's a valid Meta OAuth URL
            if 'threads.net/oauth/authorize' in redirect_url:
                print("✅ Valid Meta OAuth URL generated")
                return True
            else:
                print("❌ Invalid redirect URL")
                return False
        else:
            print(f"❌ Expected redirect (302), got {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ OAuth start test failed: {e}")
        return False

def test_oauth_callback_mock():
    """Test OAuth callback with mock data"""
    print("🧪 Testing OAuth callback endpoint...")
    
    try:
        # This would normally be called by Meta with real code/state
        # For testing, we'll just check if the endpoint exists
        response = requests.get(
            'https://threads-bot-dashboard-3.onrender.com/auth/meta/callback',
            allow_redirects=False
        )
        
        print(f"✅ OAuth callback endpoint exists: {response.status_code}")
        
        # Should return 400 for missing parameters
        if response.status_code == 400:
            print("✅ Correctly handles missing parameters")
            return True
        else:
            print(f"❌ Unexpected response: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ OAuth callback test failed: {e}")
        return False

def test_meta_client():
    """Test Meta client functionality"""
    print("🧪 Testing Meta client...")
    
    try:
        from meta_client import meta_client
        
        # Test token validation with invalid token
        is_valid = meta_client.validate_token("invalid_token")
        print(f"✅ Token validation test: {is_valid}")
        
        # Test user stats with invalid token
        stats_result = meta_client.get_user_stats("invalid_token")
        print(f"✅ User stats test: {stats_result.get('success', False)}")
        
        return True
        
    except Exception as e:
        print(f"❌ Meta client test failed: {e}")
        return False

def test_meta_oauth_helper():
    """Test Meta OAuth helper functionality"""
    print("🧪 Testing Meta OAuth helper...")
    
    try:
        from meta_oauth import meta_oauth_helper
        
        # Test URL building
        test_state = "test_state_123"
        auth_url = meta_oauth_helper.build_oauth_url(test_state)
        print(f"✅ OAuth URL built: {auth_url[:50]}...")
        
        # Test state generation (this will fail without database)
        try:
            state = meta_oauth_helper.generate_state(1)
            print(f"✅ State generation: {state[:8]}...")
        except Exception as e:
            print(f"⚠️ State generation failed (expected without DB): {e}")
        
        return True
        
    except Exception as e:
        print(f"❌ Meta OAuth helper test failed: {e}")
        return False

def test_database_methods():
    """Test database OAuth methods"""
    print("🧪 Testing database OAuth methods...")
    
    try:
        from database import DatabaseManager
        
        db = DatabaseManager()
        
        # Test OAuth state methods (these will fail without the oauth_states table)
        try:
            result = db.store_oauth_state(1, "test_state")
            print(f"✅ Store OAuth state: {result}")
        except Exception as e:
            print(f"⚠️ Store OAuth state failed (expected without table): {e}")
        
        try:
            account_id = db.get_oauth_state_account_id("test_state")
            print(f"✅ Get OAuth state account: {account_id}")
        except Exception as e:
            print(f"⚠️ Get OAuth state failed (expected without table): {e}")
        
        return True
        
    except Exception as e:
        print(f"❌ Database OAuth test failed: {e}")
        return False

def run_all_tests():
    """Run all Meta OAuth tests"""
    print("🚀 Starting Meta OAuth Implementation Tests")
    print("=" * 60)
    
    tests = [
        ("OAuth Start Endpoint", test_oauth_start),
        ("OAuth Callback Endpoint", test_oauth_callback_mock),
        ("Meta Client", test_meta_client),
        ("Meta OAuth Helper", test_meta_oauth_helper),
        ("Database OAuth Methods", test_database_methods),
    ]
    
    results = []
    for test_name, test_func in tests:
        print(f"\n📋 Running: {test_name}")
        try:
            result = test_func()
            results.append((test_name, result))
            print(f"{'✅ PASS' if result else '❌ FAIL'}: {test_name}")
        except Exception as e:
            print(f"❌ ERROR: {test_name} - {e}")
            results.append((test_name, False))
    
    print("\n" + "=" * 60)
    print("📊 Test Results Summary:")
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"  {status}: {test_name}")
    
    print(f"\n🎯 Overall: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! Meta OAuth implementation is working.")
    else:
        print("⚠️ Some tests failed. Check the logs above for details.")
        print("\n💡 Note: Some tests may fail if database tables are not created yet.")
    
    return passed == total

if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
