#!/usr/bin/env python3
"""
Test Script for Threads API Integration
Tests OAuth flow, posting, and scheduling functionality
"""

import os
import sys
import requests
import json
from datetime import datetime, timedelta

# Add server directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_health_check():
    """Test health check endpoint"""
    print("🧪 Testing health check...")
    
    try:
        response = requests.get('https://threads-bot-dashboard-3.onrender.com/api/health')
        data = response.json()
        
        print(f"✅ Health check: {data}")
        return data.get('ok', False)
    except Exception as e:
        print(f"❌ Health check failed: {e}")
        return False

def test_oauth_start():
    """Test OAuth start endpoint"""
    print("🧪 Testing OAuth start...")
    
    try:
        response = requests.post(
            'https://threads-bot-dashboard-3.onrender.com/auth/meta/start',
            json={
                'account_id': 1,
                'username': 'test_user'
            }
        )
        data = response.json()
        
        print(f"✅ OAuth start: {data}")
        return data.get('ok', False)
    except Exception as e:
        print(f"❌ OAuth start failed: {e}")
        return False

def test_threads_post():
    """Test Threads posting endpoint"""
    print("🧪 Testing Threads post...")
    
    try:
        response = requests.post(
            'https://threads-bot-dashboard-3.onrender.com/threads/post',
            json={
                'account_id': 1,
                'text': 'Test post from Threads API integration! 🚀',
                'media_urls': []
            }
        )
        data = response.json()
        
        print(f"✅ Threads post: {data}")
        return data.get('ok', False)
    except Exception as e:
        print(f"❌ Threads post failed: {e}")
        return False

def test_scheduler_status():
    """Test scheduler status endpoint"""
    print("🧪 Testing scheduler status...")
    
    try:
        response = requests.get('https://threads-bot-dashboard-3.onrender.com/scheduler/status')
        data = response.json()
        
        print(f"✅ Scheduler status: {data}")
        return data.get('ok', False)
    except Exception as e:
        print(f"❌ Scheduler status failed: {e}")
        return False

def test_schedule_post():
    """Test scheduling a post"""
    print("🧪 Testing schedule post...")
    
    try:
        scheduled_time = (datetime.now() + timedelta(minutes=5)).isoformat()
        response = requests.post(
            'https://threads-bot-dashboard-3.onrender.com/threads/schedule',
            json={
                'account_id': 1,
                'scheduled_for': scheduled_time,
                'caption_id': 1
            }
        )
        data = response.json()
        
        print(f"✅ Schedule post: {data}")
        return data.get('ok', False)
    except Exception as e:
        print(f"❌ Schedule post failed: {e}")
        return False

def test_account_info():
    """Test getting account info"""
    print("🧪 Testing account info...")
    
    try:
        response = requests.get('https://threads-bot-dashboard-3.onrender.com/threads/accounts/1/posts')
        data = response.json()
        
        print(f"✅ Account info: {data}")
        return data.get('ok', False)
    except Exception as e:
        print(f"❌ Account info failed: {e}")
        return False

def run_all_tests():
    """Run all tests"""
    print("🚀 Starting Threads API Integration Tests")
    print("=" * 50)
    
    tests = [
        ("Health Check", test_health_check),
        ("OAuth Start", test_oauth_start),
        ("Threads Post", test_threads_post),
        ("Scheduler Status", test_scheduler_status),
        ("Schedule Post", test_schedule_post),
        ("Account Info", test_account_info),
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
    
    print("\n" + "=" * 50)
    print("📊 Test Results Summary:")
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"  {status}: {test_name}")
    
    print(f"\n🎯 Overall: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! Threads API integration is working.")
    else:
        print("⚠️ Some tests failed. Check the logs above for details.")
    
    return passed == total

if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
