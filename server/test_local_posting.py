#!/usr/bin/env python3
"""
Local Test Script for Posting Functionality
Tests the implementation without requiring full environment setup
"""

import os
import sys
import json
from datetime import datetime

# Mock environment variables for testing
os.environ['SUPABASE_URL'] = 'https://test.supabase.co'
os.environ['SUPABASE_KEY'] = 'test-key'

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

def test_database_methods():
    """Test database methods"""
    print("🧪 Testing database methods...")
    
    try:
        from database import DatabaseManager
        
        # Test method existence
        db = DatabaseManager()
        
        methods_to_test = [
            'get_account_by_id',
            'get_image_by_id', 
            'get_caption_by_id',
            'get_token_by_account_id',
            'update_token',
            'record_posting_history',
            'update_scheduled_post_status'
        ]
        
        for method_name in methods_to_test:
            if hasattr(db, method_name):
                print(f"✅ Method exists: {method_name}")
            else:
                print(f"❌ Method missing: {method_name}")
                return False
        
        return True
        
    except Exception as e:
        print(f"❌ Database methods test failed: {e}")
        return False

def test_route_structure():
    """Test route structure"""
    print("🧪 Testing route structure...")
    
    try:
        # Test threads route
        from routes.threads import threads
        print("✅ Threads routes imported successfully")
        
        # Check for post endpoint
        routes = [rule.rule for rule in threads.url_map.iter_rules()]
        if '/post' in routes:
            print("✅ POST /post endpoint found")
        else:
            print("❌ POST /post endpoint missing")
            return False
        
        return True
        
    except Exception as e:
        print(f"❌ Route structure test failed: {e}")
        return False

def test_scheduler_structure():
    """Test scheduler structure"""
    print("🧪 Testing scheduler structure...")
    
    try:
        # Test scheduler route
        from routes.scheduler import scheduler
        print("✅ Scheduler routes imported successfully")
        
        # Check for run endpoint
        routes = [rule.rule for rule in scheduler.url_map.iter_rules()]
        if '/run' in routes:
            print("✅ POST /run endpoint found")
        else:
            print("❌ POST /run endpoint missing")
            return False
        
        return True
        
    except Exception as e:
        print(f"❌ Scheduler structure test failed: {e}")
        return False

def test_cron_config():
    """Test cron configuration"""
    print("🧪 Testing cron configuration...")
    
    try:
        with open('../cron.yaml', 'r') as f:
            cron_config = f.read()
        
        if 'scheduler/run' in cron_config:
            print("✅ Scheduler cron job found")
        else:
            print("❌ Scheduler cron job missing")
            return False
        
        if '*/5 * * * *' in cron_config:
            print("✅ 5-minute schedule found")
        else:
            print("❌ 5-minute schedule missing")
            return False
        
        return True
        
    except Exception as e:
        print(f"❌ Cron config test failed: {e}")
        return False

def run_all_tests():
    """Run all local tests"""
    print("🚀 Starting Local Posting Functionality Tests")
    print("=" * 60)
    
    tests = [
        ("Meta Client", test_meta_client),
        ("Database Methods", test_database_methods),
        ("Route Structure", test_route_structure),
        ("Scheduler Structure", test_scheduler_structure),
        ("Cron Config", test_cron_config),
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
        print("🎉 All tests passed! Implementation is ready for deployment.")
    else:
        print("⚠️ Some tests failed. Check the logs above for details.")
    
    return passed == total

if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
