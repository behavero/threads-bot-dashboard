#!/usr/bin/env python3
"""
Database Test Script for Threads Bot
Tests Supabase database operations
"""

import os
import sys
from datetime import datetime

# Add the server directory to the path so we can import database module
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from database import DatabaseManager

def test_database_connection():
    """Test basic database connection"""
    print("🔍 Testing database connection...")
    
    try:
        db = DatabaseManager()
        print(f"✅ DatabaseManager initialized")
        print(f"📊 Supabase URL: {db.supabase_url}")
        print(f"📊 Headers configured: {list(db.headers.keys())}")
        return True
    except Exception as e:
        print(f"❌ Database connection failed: {e}")
        return False

def test_account_operations():
    """Test account-related database operations"""
    print("\n🔍 Testing account operations...")
    
    try:
        db = DatabaseManager()
        
        # Test getting accounts
        accounts = db.get_active_accounts()
        print(f"✅ Retrieved {len(accounts)} active accounts")
        
        if accounts:
            # Test getting account by username
            first_account = accounts[0]
            username = first_account.get('username')
            if username:
                account_by_username = db.get_account_by_username(username)
                if account_by_username:
                    print(f"✅ Successfully retrieved account by username: {username}")
                else:
                    print(f"⚠️ Could not retrieve account by username: {username}")
        
        return True
    except Exception as e:
        print(f"❌ Account operations failed: {e}")
        return False

def test_content_operations():
    """Test content-related database operations"""
    print("\n🔍 Testing content operations...")
    
    try:
        db = DatabaseManager()
        
        # Test getting captions
        captions = db.get_all_captions()
        print(f"✅ Retrieved {len(captions)} captions")
        
        # Test getting images
        images = db.get_all_images()
        print(f"✅ Retrieved {len(images)} images")
        
        # Test getting unused content
        unused_caption = db.get_unused_caption()
        if unused_caption:
            print(f"✅ Found unused caption: {unused_caption.get('id')}")
        else:
            print("⚠️ No unused captions found")
        
        unused_image = db.get_unused_image()
        if unused_image:
            print(f"✅ Found unused image: {unused_image.get('id')}")
        else:
            print("⚠️ No unused images found")
        
        return True
    except Exception as e:
        print(f"❌ Content operations failed: {e}")
        return False

def test_session_operations():
    """Test session-related database operations"""
    print("\n🔍 Testing session operations...")
    
    try:
        db = DatabaseManager()
        
        # Get an account to test session operations
        accounts = db.get_active_accounts()
        if not accounts:
            print("⚠️ No accounts found for session testing")
            return True
        
        test_account = accounts[0]
        account_id = test_account.get('id')
        
        if account_id:
            # Test getting session data
            session_data = db.get_session_data(account_id)
            if session_data:
                print(f"✅ Found session data for account {account_id}")
            else:
                print(f"⚠️ No session data found for account {account_id}")
            
            # Test saving session data (with dummy data)
            test_session = {"test": "session_data", "timestamp": datetime.now().isoformat()}
            success = db.save_session_data(account_id, test_session)
            if success:
                print(f"✅ Successfully saved test session data for account {account_id}")
            else:
                print(f"⚠️ Failed to save test session data for account {account_id}")
        
        return True
    except Exception as e:
        print(f"❌ Session operations failed: {e}")
        return False

def test_posting_history():
    """Test posting history operations"""
    print("\n🔍 Testing posting history operations...")
    
    try:
        db = DatabaseManager()
        
        # Get posting history
        history = db.get_posting_history()
        print(f"✅ Retrieved {len(history)} posting history records")
        
        if history:
            print("📊 Sample posting history:")
            for record in history[:3]:  # Show first 3 records
                print(f"  - Account {record.get('account_id')}: {record.get('status')} at {record.get('created_at')}")
        
        return True
    except Exception as e:
        print(f"❌ Posting history operations failed: {e}")
        return False

def run_database_tests():
    """Run all database tests"""
    print("🧪 Database Test Suite")
    print("=" * 50)
    
    tests = [
        ("Database Connection", test_database_connection),
        ("Account Operations", test_account_operations),
        ("Content Operations", test_content_operations),
        ("Session Operations", test_session_operations),
        ("Posting History", test_posting_history)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n📋 Running: {test_name}")
        try:
            if test_func():
                passed += 1
                print(f"✅ {test_name} PASSED")
            else:
                print(f"❌ {test_name} FAILED")
        except Exception as e:
            print(f"❌ {test_name} FAILED with exception: {e}")
    
    print("\n" + "=" * 50)
    print("📊 DATABASE TEST RESULTS")
    print("=" * 50)
    print(f"Total Tests: {total}")
    print(f"✅ Passed: {passed}")
    print(f"❌ Failed: {total - passed}")
    print(f"Success Rate: {(passed/total)*100:.1f}%")
    
    if passed == total:
        print("\n🎉 All database tests passed!")
    else:
        print(f"\n⚠️ {total - passed} database test(s) failed")

if __name__ == "__main__":
    run_database_tests()
