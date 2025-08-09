#!/usr/bin/env python3
"""
Test runner for seed script (without actually seeding)
Validates environment and database connection
"""

import os
import sys
import logging

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database import DatabaseManager
from dotenv import load_dotenv

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_environment():
    """Test environment variables"""
    logger.info("🔧 Testing environment...")
    
    env_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), '.env')
    if os.path.exists(env_path):
        load_dotenv(env_path)
        logger.info(f"✅ Found .env file: {env_path}")
    else:
        logger.warning(f"⚠️ No .env file found: {env_path}")
    
    required_vars = ['SUPABASE_URL', 'SUPABASE_SERVICE_ROLE_KEY']
    for var in required_vars:
        if os.getenv(var):
            logger.info(f"✅ {var}: configured")
        else:
            logger.error(f"❌ {var}: missing")
            return False
    
    return True

def test_database():
    """Test database connection"""
    logger.info("📊 Testing database connection...")
    
    try:
        db = DatabaseManager()
        accounts = db.get_accounts()
        captions = db.get_all_captions()
        images = db.get_all_images()
        
        logger.info(f"✅ Database connected successfully")
        logger.info(f"📊 Current data: {len(accounts)} accounts, {len(captions)} captions, {len(images)} images")
        return True
        
    except Exception as e:
        logger.error(f"❌ Database connection failed: {e}")
        return False

def main():
    """Test runner"""
    logger.info("🧪 Testing seed script prerequisites...")
    
    env_ok = test_environment()
    db_ok = test_database()
    
    if env_ok and db_ok:
        logger.info("🎉 All tests passed! Ready to run seed_minimal.py")
        logger.info("💡 Run: python scripts/seed_minimal.py")
    else:
        logger.error("❌ Tests failed. Fix issues above before seeding.")
        sys.exit(1)

if __name__ == "__main__":
    main()
