#!/usr/bin/env python3
"""
Database initialization script
Populates the database with initial data from files
"""

import asyncio
import json
import logging
from pathlib import Path
from config.db import init_database
from core.db_manager import DatabaseOperations

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def init_database_data():
    """Initialize database with data from files"""
    try:
        # Initialize database connection and tables
        await init_database()
        logger.info("✅ Database initialized")
        
        # Load captions from file and add to database
        captions_file = Path('assets/captions.txt')
        if captions_file.exists():
            with open(captions_file, 'r', encoding='utf-8') as f:
                captions = [line.strip() for line in f if line.strip()]
            
            logger.info(f"📝 Found {len(captions)} captions in file")
            for caption in captions:
                success = await DatabaseOperations.add_caption(caption)
                if success:
                    logger.info(f"✅ Added caption: {caption[:50]}...")
                else:
                    logger.warning(f"⚠️  Failed to add caption: {caption[:50]}...")
        
        # Load images from directory and add to database
        images_dir = Path('assets/images/')
        if images_dir.exists():
            image_extensions = {'.jpg', '.jpeg', '.png', '.gif'}
            images = []
            
            for file_path in images_dir.iterdir():
                if file_path.is_file() and file_path.suffix.lower() in image_extensions:
                    images.append(file_path)
            
            logger.info(f"📸 Found {len(images)} images in directory")
            for image_path in images:
                success = await DatabaseOperations.add_image(
                    filename=image_path.name,
                    file_path=str(image_path),
                    file_size=image_path.stat().st_size,
                    mime_type=f'image/{image_path.suffix.lower()[1:]}'
                )
                if success:
                    logger.info(f"✅ Added image: {image_path.name}")
                else:
                    logger.warning(f"⚠️  Failed to add image: {image_path.name}")
        
        # Load accounts from file and add to database
        accounts_file = Path('config/accounts.json')
        if accounts_file.exists():
            with open(accounts_file, 'r', encoding='utf-8') as f:
                accounts = json.load(f)
            
            logger.info(f"👤 Found {len(accounts)} accounts in file")
            for account_data in accounts:
                success = await DatabaseOperations.add_account(account_data)
                if success:
                    logger.info(f"✅ Added account: {account_data.get('username', 'Unknown')}")
                else:
                    logger.warning(f"⚠️  Failed to add account: {account_data.get('username', 'Unknown')}")
        
        logger.info("🎉 Database initialization completed successfully!")
        
    except Exception as e:
        logger.error(f"❌ Database initialization failed: {e}")
        raise

async def main():
    """Main function"""
    logger.info("🚀 Starting database initialization...")
    await init_database_data()

if __name__ == "__main__":
    asyncio.run(main()) 