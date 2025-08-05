"""
Database operations manager for Enhanced Threads Bot
Handles CRUD operations for captions, images, and accounts
"""

import asyncio
import logging
from typing import List, Dict, Any, Optional
from datetime import datetime
from pathlib import Path
import json
from config.db import get_async_connection, get_sync_session
from sqlalchemy import text

logger = logging.getLogger(__name__)

class DatabaseOperations:
    """Database operations for the bot"""
    
    @staticmethod
    async def get_captions() -> List[str]:
        """Get all active captions from database"""
        try:
            async with get_async_connection() as conn:
                result = await conn.execute(text("""
                    SELECT text FROM captions 
                    WHERE is_active = TRUE 
                    ORDER BY created_at DESC
                """))
                captions = [row[0] for row in result.fetchall()]
                logger.info(f"✅ Retrieved {len(captions)} captions from database")
                return captions
        except Exception as e:
            logger.error(f"❌ Failed to get captions from database: {e}")
            # Fallback to file-based captions
            return await DatabaseOperations._get_captions_fallback()
    
    @staticmethod
    async def add_caption(text: str) -> bool:
        """Add a new caption to database"""
        try:
            async with get_async_connection() as conn:
                await conn.execute(text("""
                    INSERT INTO captions (text, created_at, updated_at)
                    VALUES (:text, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)
                """), {"text": text})
                logger.info(f"✅ Added caption to database: {text[:50]}...")
                return True
        except Exception as e:
            logger.error(f"❌ Failed to add caption to database: {e}")
            return False
    
    @staticmethod
    async def update_caption(caption_id: int, text: str) -> bool:
        """Update a caption in database"""
        try:
            async with get_async_connection() as conn:
                await conn.execute(text("""
                    UPDATE captions 
                    SET text = :text, updated_at = CURRENT_TIMESTAMP
                    WHERE id = :id
                """), {"text": text, "id": caption_id})
                logger.info(f"✅ Updated caption {caption_id} in database")
                return True
        except Exception as e:
            logger.error(f"❌ Failed to update caption in database: {e}")
            return False
    
    @staticmethod
    async def delete_caption(caption_id: int) -> bool:
        """Delete a caption from database (soft delete)"""
        try:
            async with get_async_connection() as conn:
                await conn.execute(text("""
                    UPDATE captions 
                    SET is_active = FALSE, updated_at = CURRENT_TIMESTAMP
                    WHERE id = :id
                """), {"id": caption_id})
                logger.info(f"✅ Deleted caption {caption_id} from database")
                return True
        except Exception as e:
            logger.error(f"❌ Failed to delete caption from database: {e}")
            return False
    
    @staticmethod
    async def get_images() -> List[Dict[str, Any]]:
        """Get all active images from database"""
        try:
            async with get_async_connection() as conn:
                result = await conn.execute(text("""
                    SELECT id, filename, file_path, file_size, mime_type, 
                           last_used, use_count, created_at
                    FROM images 
                    WHERE is_active = TRUE 
                    ORDER BY created_at DESC
                """))
                images = []
                for row in result.fetchall():
                    images.append({
                        'id': row[0],
                        'filename': row[1],
                        'file_path': row[2],
                        'file_size': row[3],
                        'mime_type': row[4],
                        'last_used': row[5],
                        'use_count': row[6],
                        'created_at': row[7]
                    })
                logger.info(f"✅ Retrieved {len(images)} images from database")
                return images
        except Exception as e:
            logger.error(f"❌ Failed to get images from database: {e}")
            # Fallback to file-based images
            return await DatabaseOperations._get_images_fallback()
    
    @staticmethod
    async def add_image(filename: str, file_path: str, file_size: int = None, mime_type: str = None) -> bool:
        """Add a new image to database"""
        try:
            async with get_async_connection() as conn:
                await conn.execute(text("""
                    INSERT INTO images (filename, file_path, file_size, mime_type, created_at)
                    VALUES (:filename, :file_path, :file_size, :mime_type, CURRENT_TIMESTAMP)
                """), {
                    "filename": filename,
                    "file_path": file_path,
                    "file_size": file_size,
                    "mime_type": mime_type
                })
                logger.info(f"✅ Added image to database: {filename}")
                return True
        except Exception as e:
            logger.error(f"❌ Failed to add image to database: {e}")
            return False
    
    @staticmethod
    async def update_image_usage(image_id: int) -> bool:
        """Update image usage statistics"""
        try:
            async with get_async_connection() as conn:
                await conn.execute(text("""
                    UPDATE images 
                    SET last_used = CURRENT_TIMESTAMP, use_count = use_count + 1
                    WHERE id = :id
                """), {"id": image_id})
                return True
        except Exception as e:
            logger.error(f"❌ Failed to update image usage: {e}")
            return False
    
    @staticmethod
    async def delete_image(image_id: int) -> bool:
        """Delete an image from database (soft delete)"""
        try:
            async with get_async_connection() as conn:
                await conn.execute(text("""
                    UPDATE images 
                    SET is_active = FALSE
                    WHERE id = :id
                """), {"id": image_id})
                logger.info(f"✅ Deleted image {image_id} from database")
                return True
        except Exception as e:
            logger.error(f"❌ Failed to delete image from database: {e}")
            return False
    
    @staticmethod
    async def get_accounts() -> List[Dict[str, Any]]:
        """Get all enabled accounts from database"""
        try:
            async with get_async_connection() as conn:
                result = await conn.execute(text("""
                    SELECT id, username, email, password, enabled, description,
                           posting_schedule, posting_config, fingerprint_config
                    FROM accounts 
                    WHERE enabled = TRUE
                    ORDER BY created_at DESC
                """))
                accounts = []
                for row in result.fetchall():
                    accounts.append({
                        'id': row[0],
                        'username': row[1],
                        'email': row[2],
                        'password': row[3],
                        'enabled': row[4],
                        'description': row[5],
                        'posting_schedule': json.loads(row[6]) if row[6] else {},
                        'posting_config': json.loads(row[7]) if row[7] else {},
                        'fingerprint_config': json.loads(row[8]) if row[8] else {}
                    })
                logger.info(f"✅ Retrieved {len(accounts)} accounts from database")
                return accounts
        except Exception as e:
            logger.error(f"❌ Failed to get accounts from database: {e}")
            # Fallback to file-based accounts
            return await DatabaseOperations._get_accounts_fallback()
    
    @staticmethod
    async def add_account(account_data: Dict[str, Any]) -> bool:
        """Add a new account to database"""
        try:
            async with get_async_connection() as conn:
                await conn.execute(text("""
                    INSERT INTO accounts (username, email, password, description,
                                       posting_schedule, posting_config, fingerprint_config)
                    VALUES (:username, :email, :password, :description,
                           :posting_schedule, :posting_config, :fingerprint_config)
                """), {
                    "username": account_data['username'],
                    "email": account_data['email'],
                    "password": account_data['password'],
                    "description": account_data.get('description', ''),
                    "posting_schedule": json.dumps(account_data.get('posting_schedule', {})),
                    "posting_config": json.dumps(account_data.get('posting_config', {})),
                    "fingerprint_config": json.dumps(account_data.get('fingerprint_config', {}))
                })
                logger.info(f"✅ Added account to database: {account_data['username']}")
                return True
        except Exception as e:
            logger.error(f"❌ Failed to add account to database: {e}")
            return False
    
    @staticmethod
    async def update_account(account_id: int, account_data: Dict[str, Any]) -> bool:
        """Update an account in database"""
        try:
            async with get_async_connection() as conn:
                await conn.execute(text("""
                    UPDATE accounts 
                    SET username = :username, email = :email, password = :password,
                        description = :description, posting_schedule = :posting_schedule,
                        posting_config = :posting_config, fingerprint_config = :fingerprint_config,
                        updated_at = CURRENT_TIMESTAMP
                    WHERE id = :id
                """), {
                    "id": account_id,
                    "username": account_data['username'],
                    "email": account_data['email'],
                    "password": account_data['password'],
                    "description": account_data.get('description', ''),
                    "posting_schedule": json.dumps(account_data.get('posting_schedule', {})),
                    "posting_config": json.dumps(account_data.get('posting_config', {})),
                    "fingerprint_config": json.dumps(account_data.get('fingerprint_config', {}))
                })
                logger.info(f"✅ Updated account {account_id} in database")
                return True
        except Exception as e:
            logger.error(f"❌ Failed to update account in database: {e}")
            return False
    
    @staticmethod
    async def record_posting(account_id: int, caption_id: int = None, 
                           image_id: int = None, success: bool = True, 
                           error_message: str = None, user_agent: str = None) -> bool:
        """Record a posting attempt in database"""
        try:
            async with get_async_connection() as conn:
                await conn.execute(text("""
                    INSERT INTO posting_history (account_id, caption_id, image_id, 
                                              success, error_message, user_agent)
                    VALUES (:account_id, :caption_id, :image_id, 
                           :success, :error_message, :user_agent)
                """), {
                    "account_id": account_id,
                    "caption_id": caption_id,
                    "image_id": image_id,
                    "success": success,
                    "error_message": error_message,
                    "user_agent": user_agent
                })
                return True
        except Exception as e:
            logger.error(f"❌ Failed to record posting: {e}")
            return False
    
    # Fallback methods for when database is unavailable
    @staticmethod
    async def _get_captions_fallback() -> List[str]:
        """Fallback to file-based captions"""
        try:
            with open('assets/captions.txt', 'r', encoding='utf-8') as f:
                captions = [line.strip() for line in f if line.strip()]
            logger.info(f"📄 Using fallback captions from file: {len(captions)} captions")
            return captions
        except Exception as e:
            logger.error(f"❌ Fallback captions failed: {e}")
            return []
    
    @staticmethod
    async def _get_images_fallback() -> List[Dict[str, Any]]:
        """Fallback to file-based images"""
        try:
            images_dir = Path('assets/images/')
            images = []
            if images_dir.exists():
                for image_file in images_dir.iterdir():
                    if image_file.suffix.lower() in {'.jpg', '.jpeg', '.png', '.gif'}:
                        images.append({
                            'id': len(images) + 1,
                            'filename': image_file.name,
                            'file_path': str(image_file),
                            'file_size': image_file.stat().st_size,
                            'mime_type': f'image/{image_file.suffix.lower()[1:]}',
                            'last_used': None,
                            'use_count': 0,
                            'created_at': datetime.fromtimestamp(image_file.stat().st_mtime)
                        })
            logger.info(f"📄 Using fallback images from directory: {len(images)} images")
            return images
        except Exception as e:
            logger.error(f"❌ Fallback images failed: {e}")
            return []
    
    @staticmethod
    async def _get_accounts_fallback() -> List[Dict[str, Any]]:
        """Fallback to file-based accounts"""
        try:
            with open('config/accounts.json', 'r', encoding='utf-8') as f:
                accounts = json.load(f)
            logger.info(f"📄 Using fallback accounts from file: {len(accounts)} accounts")
            return accounts
        except Exception as e:
            logger.error(f"❌ Fallback accounts failed: {e}")
            return [] 