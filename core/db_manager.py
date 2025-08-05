"""
Database operations manager for Enhanced Threads Bot
Handles CRUD operations for captions, images, and accounts using Supabase
"""

import asyncio
import logging
from typing import List, Dict, Any, Optional
from datetime import datetime
from pathlib import Path
import json
from config.db import get_async_connection, get_sync_session, get_supabase_client
from sqlalchemy import text

logger = logging.getLogger(__name__)

class DatabaseOperations:
    """Database operations for the bot using Supabase with PostgreSQL fallback"""
    
    @staticmethod
    async def get_captions() -> List[str]:
        """Get all active captions from Supabase with fallback"""
        try:
            # Try Supabase first
            supabase = get_supabase_client()
            response = supabase.table('captions').select('text').eq('is_active', True).execute()
            captions = [row['text'] for row in response.data]
            logger.info(f"✅ Retrieved {len(captions)} captions from Supabase")
            return captions
        except Exception as e:
            logger.error(f"❌ Failed to get captions from Supabase: {e}")
            # Fallback to PostgreSQL
            try:
                async with get_async_connection() as conn:
                    result = await conn.execute(text("""
                        SELECT text FROM captions 
                        WHERE is_active = TRUE 
                        ORDER BY created_at DESC
                    """))
                    captions = [row[0] for row in result.fetchall()]
                    logger.info(f"✅ Retrieved {len(captions)} captions from PostgreSQL (fallback)")
                    return captions
            except Exception as e:
                logger.error(f"❌ Failed to get captions from PostgreSQL: {e}")
                # Fallback to file-based captions
                return await DatabaseOperations._get_captions_fallback()
    
    @staticmethod
    async def add_caption(text: str) -> bool:
        """Add a new caption to Supabase with fallback"""
        try:
            # Try Supabase first
            supabase = get_supabase_client()
            response = supabase.table('captions').insert({
                'text': text,
                'created_at': datetime.now().isoformat(),
                'updated_at': datetime.now().isoformat(),
                'is_active': True
            }).execute()
            logger.info(f"✅ Added caption to Supabase: {text[:50]}...")
            return True
        except Exception as e:
            logger.error(f"❌ Failed to add caption to Supabase: {e}")
            # Fallback to PostgreSQL
            try:
                async with get_async_connection() as conn:
                    await conn.execute(text("""
                        INSERT INTO captions (text, created_at, updated_at)
                        VALUES (:text, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)
                    """), {"text": text})
                    logger.info(f"✅ Added caption to PostgreSQL (fallback): {text[:50]}...")
                    return True
            except Exception as e:
                logger.error(f"❌ Failed to add caption to PostgreSQL: {e}")
                return False
    
    @staticmethod
    async def update_caption(caption_id: int, text: str) -> bool:
        """Update a caption in Supabase with fallback"""
        try:
            # Try Supabase first
            supabase = get_supabase_client()
            response = supabase.table('captions').update({
                'text': text,
                'updated_at': datetime.now().isoformat()
            }).eq('id', caption_id).execute()
            logger.info(f"✅ Updated caption {caption_id} in Supabase")
            return True
        except Exception as e:
            logger.error(f"❌ Failed to update caption in Supabase: {e}")
            # Fallback to PostgreSQL
            try:
                async with get_async_connection() as conn:
                    await conn.execute(text("""
                        UPDATE captions 
                        SET text = :text, updated_at = CURRENT_TIMESTAMP
                        WHERE id = :id
                    """), {"text": text, "id": caption_id})
                    logger.info(f"✅ Updated caption {caption_id} in PostgreSQL (fallback)")
                    return True
            except Exception as e:
                logger.error(f"❌ Failed to update caption in PostgreSQL: {e}")
                return False
    
    @staticmethod
    async def delete_caption(caption_id: int) -> bool:
        """Delete a caption from Supabase with fallback (soft delete)"""
        try:
            # Try Supabase first
            supabase = get_supabase_client()
            response = supabase.table('captions').update({
                'is_active': False,
                'updated_at': datetime.now().isoformat()
            }).eq('id', caption_id).execute()
            logger.info(f"✅ Deleted caption {caption_id} from Supabase")
            return True
        except Exception as e:
            logger.error(f"❌ Failed to delete caption from Supabase: {e}")
            # Fallback to PostgreSQL
            try:
                async with get_async_connection() as conn:
                    await conn.execute(text("""
                        UPDATE captions 
                        SET is_active = FALSE, updated_at = CURRENT_TIMESTAMP
                        WHERE id = :id
                    """), {"id": caption_id})
                    logger.info(f"✅ Deleted caption {caption_id} from PostgreSQL (fallback)")
                    return True
            except Exception as e:
                logger.error(f"❌ Failed to delete caption from PostgreSQL: {e}")
                return False
    
    @staticmethod
    async def get_images() -> List[Dict[str, Any]]:
        """Get all active images from Supabase with fallback"""
        try:
            # Try Supabase first
            supabase = get_supabase_client()
            response = supabase.table('images').select('*').eq('is_active', True).execute()
            images = []
            for row in response.data:
                images.append({
                    'id': row['id'],
                    'filename': row['filename'],
                    'file_path': row['file_path'],
                    'file_size': row['file_size'],
                    'mime_type': row['mime_type'],
                    'last_used': row['last_used'],
                    'use_count': row['use_count'],
                    'created_at': row['created_at']
                })
            logger.info(f"✅ Retrieved {len(images)} images from Supabase")
            return images
        except Exception as e:
            logger.error(f"❌ Failed to get images from Supabase: {e}")
            # Fallback to PostgreSQL
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
                    logger.info(f"✅ Retrieved {len(images)} images from PostgreSQL (fallback)")
                    return images
            except Exception as e:
                logger.error(f"❌ Failed to get images from PostgreSQL: {e}")
                # Fallback to file-based images
                return await DatabaseOperations._get_images_fallback()
    
    @staticmethod
    async def add_image(filename: str, file_path: str, file_size: int = None, mime_type: str = None) -> bool:
        """Add a new image to Supabase with fallback"""
        try:
            # Try Supabase first
            supabase = get_supabase_client()
            response = supabase.table('images').insert({
                'filename': filename,
                'file_path': file_path,
                'file_size': file_size,
                'mime_type': mime_type,
                'created_at': datetime.now().isoformat(),
                'use_count': 0,
                'is_active': True
            }).execute()
            logger.info(f"✅ Added image to Supabase: {filename}")
            return True
        except Exception as e:
            logger.error(f"❌ Failed to add image to Supabase: {e}")
            # Fallback to PostgreSQL
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
                    logger.info(f"✅ Added image to PostgreSQL (fallback): {filename}")
                    return True
            except Exception as e:
                logger.error(f"❌ Failed to add image to PostgreSQL: {e}")
                return False
    
    @staticmethod
    async def update_image_usage(image_id: int) -> bool:
        """Update image usage statistics in Supabase with fallback"""
        try:
            # Try Supabase first
            supabase = get_supabase_client()
            response = supabase.table('images').update({
                'last_used': datetime.now().isoformat(),
                'use_count': supabase.table('images').select('use_count').eq('id', image_id).execute().data[0]['use_count'] + 1
            }).eq('id', image_id).execute()
            return True
        except Exception as e:
            logger.error(f"❌ Failed to update image usage in Supabase: {e}")
            # Fallback to PostgreSQL
            try:
                async with get_async_connection() as conn:
                    await conn.execute(text("""
                        UPDATE images 
                        SET last_used = CURRENT_TIMESTAMP, use_count = use_count + 1
                        WHERE id = :id
                    """), {"id": image_id})
                    return True
            except Exception as e:
                logger.error(f"❌ Failed to update image usage in PostgreSQL: {e}")
                return False
    
    @staticmethod
    async def delete_image(image_id: int) -> bool:
        """Delete an image from Supabase with fallback (soft delete)"""
        try:
            # Try Supabase first
            supabase = get_supabase_client()
            response = supabase.table('images').update({
                'is_active': False
            }).eq('id', image_id).execute()
            logger.info(f"✅ Deleted image {image_id} from Supabase")
            return True
        except Exception as e:
            logger.error(f"❌ Failed to delete image from Supabase: {e}")
            # Fallback to PostgreSQL
            try:
                async with get_async_connection() as conn:
                    await conn.execute(text("""
                        UPDATE images 
                        SET is_active = FALSE
                        WHERE id = :id
                    """), {"id": image_id})
                    logger.info(f"✅ Deleted image {image_id} from PostgreSQL (fallback)")
                    return True
            except Exception as e:
                logger.error(f"❌ Failed to delete image from PostgreSQL: {e}")
                return False
    
    @staticmethod
    async def get_accounts() -> List[Dict[str, Any]]:
        """Get all enabled accounts from Supabase with fallback"""
        try:
            # Try Supabase first
            supabase = get_supabase_client()
            response = supabase.table('accounts').select('*').eq('enabled', True).execute()
            accounts = []
            for row in response.data:
                accounts.append({
                    'id': row['id'],
                    'username': row['username'],
                    'email': row['email'],
                    'password': row['password'],
                    'enabled': row['enabled'],
                    'description': row['description'],
                    'posting_schedule': json.loads(row['posting_schedule']) if row['posting_schedule'] else {},
                    'posting_config': json.loads(row['posting_config']) if row['posting_config'] else {},
                    'fingerprint_config': json.loads(row['fingerprint_config']) if row['fingerprint_config'] else {}
                })
            logger.info(f"✅ Retrieved {len(accounts)} accounts from Supabase")
            return accounts
        except Exception as e:
            logger.error(f"❌ Failed to get accounts from Supabase: {e}")
            # Fallback to PostgreSQL
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
                    logger.info(f"✅ Retrieved {len(accounts)} accounts from PostgreSQL (fallback)")
                    return accounts
            except Exception as e:
                logger.error(f"❌ Failed to get accounts from PostgreSQL: {e}")
                # Fallback to file-based accounts
                return await DatabaseOperations._get_accounts_fallback()
    
    @staticmethod
    async def add_account(account_data: Dict[str, Any]) -> bool:
        """Add a new account to Supabase with fallback"""
        try:
            # Try Supabase first
            supabase = get_supabase_client()
            response = supabase.table('accounts').insert({
                'username': account_data['username'],
                'email': account_data['email'],
                'password': account_data['password'],
                'description': account_data.get('description', ''),
                'posting_schedule': json.dumps(account_data.get('posting_schedule', {})),
                'posting_config': json.dumps(account_data.get('posting_config', {})),
                'fingerprint_config': json.dumps(account_data.get('fingerprint_config', {})),
                'enabled': True,
                'created_at': datetime.now().isoformat(),
                'updated_at': datetime.now().isoformat()
            }).execute()
            logger.info(f"✅ Added account to Supabase: {account_data['username']}")
            return True
        except Exception as e:
            logger.error(f"❌ Failed to add account to Supabase: {e}")
            # Fallback to PostgreSQL
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
                    logger.info(f"✅ Added account to PostgreSQL (fallback): {account_data['username']}")
                    return True
            except Exception as e:
                logger.error(f"❌ Failed to add account to PostgreSQL: {e}")
                return False
    
    @staticmethod
    async def record_posting(account_id: int, caption_id: int = None, 
                           image_id: int = None, success: bool = True, 
                           error_message: str = None, user_agent: str = None) -> bool:
        """Record a posting attempt in Supabase with fallback"""
        try:
            # Try Supabase first
            supabase = get_supabase_client()
            response = supabase.table('posting_history').insert({
                'account_id': account_id,
                'caption_id': caption_id,
                'image_id': image_id,
                'success': success,
                'error_message': error_message,
                'user_agent': user_agent,
                'posted_at': datetime.now().isoformat()
            }).execute()
            return True
        except Exception as e:
            logger.error(f"❌ Failed to record posting in Supabase: {e}")
            # Fallback to PostgreSQL
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
                logger.error(f"❌ Failed to record posting in PostgreSQL: {e}")
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