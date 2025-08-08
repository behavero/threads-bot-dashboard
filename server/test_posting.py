#!/usr/bin/env python3
"""
Test Script for Posting Functionality
Tests manual posting and scheduler endpoints
"""

import os
import sys
import requests
import json
from datetime import datetime, timedelta

# Add server directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_manual_post():
    """Test manual posting endpoint"""
    print("🧪 Testing manual post endpoint...")
    
    try:
        response = requests.post(
            'https://threads-bot-dashboard-3.onrender.com/threads/post',
            json={
                'account_id': 1,
                'text': 'Test post from Threads API! 🚀',
                'image_id': None
            }
        )
        
        data = response.json()
        print(f"✅ Manual post response: {data}")
        
        if data.get('ok'):
            print(f"✅ Post successful! Thread ID: {data.get('thread_id')}")
            return True
        else:
            print(f"❌ Post failed: {data.get('error')}")
            return False
            
    except Exception as e:
        print(f"❌ Manual post test failed: {e}")
        return False

def test_scheduler_run():
    """Test scheduler run endpoint"""
    print("🧪 Testing scheduler run endpoint...")
    
    try:
        response = requests.post(
            'https://threads-bot-dashboard-3.onrender.com/scheduler/run',
            json={}
        )
        
        data = response.json()
        print(f"✅ Scheduler run response: {data}")
        
        if data.get('ok'):
            processed = data.get('processed', 0)
            print(f"✅ Scheduler completed! Processed {processed} posts")
            return True
        else:
            print(f"❌ Scheduler failed: {data.get('error')}")
            return False
            
    except Exception as e:
        print(f"❌ Scheduler test failed: {e}")
        return False

def test_scheduler_status():
    """Test scheduler status endpoint"""
    print("🧪 Testing scheduler status endpoint...")
    
    try:
        response = requests.get(
            'https://threads-bot-dashboard-3.onrender.com/scheduler/status'
        )
        
        data = response.json()
        print(f"✅ Scheduler status: {data}")
        
        if data.get('ok'):
            pending = data.get('pending_count', 0)
            print(f"✅ Scheduler status retrieved! {pending} pending posts")
            return True
        else:
            print(f"❌ Scheduler status failed: {data.get('error')}")
            return False
            
    except Exception as e:
        print(f"❌ Scheduler status test failed: {e}")
        return False

def test_schedule_post():
    """Test scheduling a post"""
    print("🧪 Testing schedule post endpoint...")
    
    try:
        # Schedule for 2 minutes from now
        scheduled_time = (datetime.now() + timedelta(minutes=2)).isoformat()
        
        response = requests.post(
            'https://threads-bot-dashboard-3.onrender.com/threads/schedule',
            json={
                'account_id': 1,
                'scheduled_for': scheduled_time,
                'caption_id': 1,
                'image_id': None
            }
        )
        
        data = response.json()
        print(f"✅ Schedule post response: {data}")
        
        if data.get('ok'):
            print(f"✅ Post scheduled for {scheduled_time}")
            return True
        else:
            print(f"❌ Schedule post failed: {data.get('error')}")
            return False
            
    except Exception as e:
        print(f"❌ Schedule post test failed: {e}")
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

def run_all_tests():
    """Run all posting tests"""
    print("🚀 Starting Posting Functionality Tests")
    print("=" * 60)
    
    tests = [
        ("Meta Client", test_meta_client),
        ("Manual Post", test_manual_post),
        ("Schedule Post", test_schedule_post),
        ("Scheduler Status", test_scheduler_status),
        ("Scheduler Run", test_scheduler_run),
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
        print("🎉 All tests passed! Posting functionality is working.")
    else:
        print("⚠️ Some tests failed. Check the logs above for details.")
        print("\n💡 Note: Some tests may fail if accounts are not connected or tokens are invalid.")
    
    return passed == total

if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
