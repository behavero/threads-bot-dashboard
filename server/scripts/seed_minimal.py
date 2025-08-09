#!/usr/bin/env python3
"""
Minimal Seed Script for Threads Bot Development
File: server/scripts/seed_minimal.py

Creates minimal demo data for testing autopilot functionality:
- 2 demo captions
- 2 demo images  
- 1 demo account with autopilot enabled (5min cadence)

Usage:
  cd server
  python scripts/seed_minimal.py
"""

import os
import sys
import logging
from datetime import datetime, timedelta

# Add parent directory to path to import from server
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database import DatabaseManager
from dotenv import load_dotenv

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def load_environment():
    """Load environment variables"""
    env_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), '.env')
    if os.path.exists(env_path):
        load_dotenv(env_path)
        logger.info(f"📄 Loaded environment from {env_path}")
    else:
        logger.warning(f"⚠️ No .env file found at {env_path}")
    
    # Check required env vars
    required_vars = ['SUPABASE_URL', 'SUPABASE_SERVICE_ROLE_KEY']
    missing_vars = [var for var in required_vars if not os.getenv(var)]
    
    if missing_vars:
        logger.error(f"❌ Missing environment variables: {missing_vars}")
        sys.exit(1)
    
    logger.info("✅ Environment variables loaded successfully")

def seed_captions(db: DatabaseManager) -> list:
    """Create demo captions if they don't exist"""
    logger.info("📝 Seeding demo captions...")
    
    demo_captions = [
        {
            'text': '🚀 Building something amazing with AI! The future is now and it\'s incredibly exciting. What are you working on today? #AI #Innovation #TechLife',
            'category': 'tech',
            'tags': ['AI', 'Innovation', 'TechLife', 'Future']
        },
        {
            'text': '☕ Monday morning motivation! 💪 Starting the week with fresh energy and big goals. Small steps lead to big achievements. What\'s your Monday goal? #MondayMotivation #Goals #Success',
            'category': 'motivation',  
            'tags': ['MondayMotivation', 'Goals', 'Success', 'Productivity']
        }
    ]
    
    created_captions = []
    
    for caption_data in demo_captions:
        try:
            # Check if similar caption already exists
            existing = db.get_all_captions()
            if any(cap['text'][:30] == caption_data['text'][:30] for cap in existing):
                logger.info(f"📝 Caption already exists: {caption_data['text'][:50]}...")
                continue
            
            caption_id = db.add_caption(
                text=caption_data['text'],
                category=caption_data['category'],
                tags=caption_data['tags']
            )
            
            if caption_id:
                created_captions.append(caption_id)
                logger.info(f"✅ Created caption {caption_id}: {caption_data['text'][:50]}...")
            else:
                logger.error(f"❌ Failed to create caption: {caption_data['text'][:50]}...")
                
        except Exception as e:
            logger.error(f"❌ Error creating caption: {e}")
    
    logger.info(f"📝 Caption seeding complete. Created: {len(created_captions)}")
    return created_captions

def seed_images(db: DatabaseManager) -> list:
    """Create demo images if they don't exist"""
    logger.info("🖼️ Seeding demo images...")
    
    demo_images = [
        {
            'url': 'https://images.unsplash.com/photo-1518709268805-4e9042af2176?w=800&h=600&fit=crop',
            'filename': 'tech_workspace.jpg'
        },
        {
            'url': 'https://images.unsplash.com/photo-1506905925346-21bda4d32df4?w=800&h=600&fit=crop',
            'filename': 'mountain_sunrise.jpg'
        }
    ]
    
    created_images = []
    
    for image_data in demo_images:
        try:
            # Check if image already exists by URL
            existing = db.get_all_images()
            if any(img['url'] == image_data['url'] for img in existing):
                logger.info(f"🖼️ Image already exists: {image_data['filename']}")
                continue
            
            image_id = db.add_image(
                url=image_data['url'],
                filename=image_data['filename']
            )
            
            if image_id:
                created_images.append(image_id)
                logger.info(f"✅ Created image {image_id}: {image_data['filename']}")
            else:
                logger.error(f"❌ Failed to create image: {image_data['filename']}")
                
        except Exception as e:
            logger.error(f"❌ Error creating image: {e}")
    
    logger.info(f"🖼️ Image seeding complete. Created: {len(created_images)}")
    return created_images

def seed_demo_account(db: DatabaseManager) -> int:
    """Create or update demo account with autopilot enabled"""
    logger.info("👤 Setting up demo account...")
    
    demo_username = "demo_autopilot"
    
    try:
        # Check if demo account already exists
        existing_accounts = db.get_accounts()
        demo_account = next((acc for acc in existing_accounts if acc['username'] == demo_username), None)
        
        if demo_account:
            account_id = demo_account['id']
            logger.info(f"👤 Demo account already exists: {account_id}")
        else:
            # Create new demo account
            account_data = {
                'username': demo_username,
                'description': 'Demo account for testing autopilot functionality',
                'status': 'enabled',
                'provider': 'direct',
                'connection_status': 'connected_session',  # Assume we have a session
                'created_at': datetime.now().isoformat()
            }
            
            account_id = db.add_account(account_data)
            if not account_id:
                logger.error("❌ Failed to create demo account")
                return None
            
            logger.info(f"✅ Created demo account: {account_id}")
        
        # Enable autopilot with 5-minute cadence
        now = datetime.now()
        next_run = now + timedelta(minutes=2)  # Start in 2 minutes for immediate testing
        
        autopilot_data = {
            'autopilot_enabled': True,
            'cadence_minutes': 5,
            'jitter_seconds': 30,
            'next_run_at': next_run.isoformat(),
            'connection_status': 'connected_session',
            'last_error': None,
            'error_count': 0,
            'updated_at': now.isoformat()
        }
        
        if db.update_account(account_id, autopilot_data):
            logger.info(f"✅ Enabled autopilot for account {account_id}")
            logger.info(f"⏰ Next run scheduled for: {next_run}")
        else:
            logger.error(f"❌ Failed to enable autopilot for account {account_id}")
        
        return account_id
        
    except Exception as e:
        logger.error(f"❌ Error setting up demo account: {e}")
        return None

def verify_seed_data(db: DatabaseManager):
    """Verify that seed data was created successfully"""
    logger.info("🔍 Verifying seed data...")
    
    try:
        # Check captions
        captions = db.get_all_captions()
        logger.info(f"📝 Total captions: {len(captions)}")
        
        # Check images
        images = db.get_all_images()
        logger.info(f"🖼️ Total images: {len(images)}")
        
        # Check accounts with autopilot
        accounts = db.get_accounts()
        autopilot_accounts = [acc for acc in accounts if acc.get('autopilot_enabled')]
        logger.info(f"🤖 Autopilot-enabled accounts: {len(autopilot_accounts)}")
        
        if autopilot_accounts:
            for acc in autopilot_accounts:
                logger.info(f"  👤 {acc['username']} - Cadence: {acc.get('cadence_minutes', 'N/A')}min - Next: {acc.get('next_run_at', 'N/A')}")
        
        # Summary
        logger.info("✅ Seed data verification complete!")
        logger.info(f"📊 Summary: {len(captions)} captions, {len(images)} images, {len(autopilot_accounts)} autopilot accounts")
        
    except Exception as e:
        logger.error(f"❌ Error verifying seed data: {e}")

def main():
    """Main seed function"""
    logger.info("🌱 Starting minimal seed for Threads Bot...")
    
    try:
        # Load environment
        load_environment()
        
        # Initialize database
        db = DatabaseManager()
        logger.info("📊 Database connection established")
        
        # Seed data
        created_captions = seed_captions(db)
        created_images = seed_images(db)
        demo_account_id = seed_demo_account(db)
        
        # Verify results
        verify_seed_data(db)
        
        # Final summary
        logger.info("🎉 Minimal seed completed successfully!")
        logger.info("🚀 Ready to test autopilot functionality!")
        logger.info("")
        logger.info("📋 Next steps:")
        logger.info("  1. Run the backend: python start.py")
        logger.info("  2. Trigger autopilot: POST /autopilot/tick")
        logger.info("  3. Check status: GET /autopilot/status")
        logger.info("  4. View dashboard: http://localhost:3000")
        
    except Exception as e:
        logger.error(f"❌ Seed failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
