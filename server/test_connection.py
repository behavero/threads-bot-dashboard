#!/usr/bin/env python3
"""
Test script to verify Supabase connection and table access
"""

import os
from dotenv import load_dotenv
from database import DatabaseManager

# Load environment variables
load_dotenv()

def test_supabase_connection():
    """Test Supabase connection and table access"""
    print("🔍 Testing Supabase Connection...")

    try:
        # Test environment variables (using new Supabase-Vercel integration)
        supabase_url = os.getenv("SUPABASE_URL")
        supabase_key = os.getenv("SUPABASE_SERVICE_ROLE_KEY") or os.getenv("SUPABASE_KEY")

        print(f"✅ Supabase URL: {supabase_url}")
        print(f"✅ Supabase Key: {'*' * 10}{supabase_key[-4:] if supabase_key else 'NOT SET'}")
        
        # Test database connection
        db = DatabaseManager()
        print("✅ DatabaseManager initialized successfully")
        
        # Test table access
        print("\n📊 Testing Table Access...")
        
        # Test accounts table
        try:
            accounts = db.get_active_accounts()
            print(f"✅ Accounts table: {len(accounts)} accounts found")
        except Exception as e:
            print(f"❌ Accounts table error: {e}")
        
        # Test captions table
        try:
            captions = db.get_all_captions()
            print(f"✅ Captions table: {len(captions)} captions found")
        except Exception as e:
            print(f"❌ Captions table error: {e}")
        
        # Test images table
        try:
            images = db.get_all_images()
            print(f"✅ Images table: {len(images)} images found")
        except Exception as e:
            print(f"❌ Images table error: {e}")
        
        # Test posting_history table
        try:
            history = db.get_posting_history()
            print(f"✅ Posting history table: {len(history)} records found")
        except Exception as e:
            print(f"❌ Posting history table error: {e}")
        
        # Test statistics
        try:
            stats = db.get_statistics()
            print(f"✅ Statistics: {stats}")
        except Exception as e:
            print(f"❌ Statistics error: {e}")
        
        print("\n🎉 All tests completed!")
        
    except Exception as e:
        print(f"❌ Connection test failed: {e}")

if __name__ == "__main__":
    test_supabase_connection() 