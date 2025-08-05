#!/usr/bin/env python3
"""
Environment setup and validation script
"""

import os
from dotenv import load_dotenv

def check_environment():
    """Check if all required environment variables are set"""
    load_dotenv()
    
    required_vars = [
        'SUPABASE_URL',
        'SUPABASE_KEY'
    ]
    
    missing_vars = []
    
    print("🔍 Checking environment variables...")
    
    for var in required_vars:
        value = os.getenv(var)
        if value:
            print(f"✅ {var}: {'*' * len(value)} (hidden)")
        else:
            print(f"❌ {var}: NOT SET")
            missing_vars.append(var)
    
    if missing_vars:
        print(f"\n⚠️ Missing environment variables: {', '.join(missing_vars)}")
        print("Please set these in your Render/Railway environment variables:")
        print("\nFor Render:")
        print("1. Go to your service dashboard")
        print("2. Click on 'Environment' tab")
        print("3. Add the missing variables")
        print("\nRequired variables:")
        print("SUPABASE_URL=https://perwbmtwutwzsvlirwik.supabase.co")
        print("SUPABASE_KEY=your-supabase-key")
        return False
    else:
        print("\n✅ All environment variables are set!")
        return True

def test_database_connection():
    """Test database connection"""
    try:
        from database import DatabaseManager
        db = DatabaseManager()
        print("✅ Database connection successful")
        return True
    except Exception as e:
        print(f"❌ Database connection failed: {e}")
        return False

if __name__ == "__main__":
    print("🚀 Threads Bot Environment Setup")
    print("=" * 40)
    
    env_ok = check_environment()
    
    if env_ok:
        print("\n🔍 Testing database connection...")
        db_ok = test_database_connection()
        
        if db_ok:
            print("\n🎉 Environment is ready!")
            print("You can now start the bot with: python start.py")
        else:
            print("\n❌ Database connection failed")
            print("Please check your Supabase credentials")
    else:
        print("\n❌ Environment not ready")
        print("Please set the missing environment variables") 