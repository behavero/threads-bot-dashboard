#!/usr/bin/env python3
"""
Autopilot Service
Handles automated posting with per-account cadence and jitter
"""

import os
import random
import logging
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Tuple
from database import DatabaseManager

logger = logging.getLogger(__name__)

class AutopilotService:
    def __init__(self):
        self.db = DatabaseManager()
        self.max_per_tick = int(os.getenv('POSTING_MAX_PER_TICK', '5'))
        self.default_cadence = int(os.getenv('POSTING_DEFAULT_CADENCE_MIN', '10'))
        self.meta_publish_enabled = os.getenv('META_THREADS_PUBLISH_ENABLED', 'false').lower() == 'true'
        
        logger.info(f"🚀 AutopilotService initialized")
        logger.info(f"📊 Max per tick: {self.max_per_tick}")
        logger.info(f"⏰ Default cadence: {self.default_cadence} minutes")
        logger.info(f"🔐 Meta publish enabled: {self.meta_publish_enabled}")
    
    def due_accounts(self, now: datetime) -> List[Dict]:
        """Fetch accounts that are due for posting"""
        try:
            logger.info(f"🔍 Fetching due accounts at {now}")
            
            # Get accounts with autopilot enabled and next_run_at <= now
            response = self.db._make_request(
                'GET',
                f"{self.db.supabase_url}/rest/v1/accounts",
                params={
                    'autopilot_enabled': 'eq.true',
                    'next_run_at': f'lte.{now.isoformat()}',
                    'select': 'id,username,cadence_minutes,jitter_seconds,connection_status,threads_user_id'
                }
            )
            
            if response.status_code == 200:
                accounts = response.json()
                logger.info(f"✅ Found {len(accounts)} due accounts")
                return accounts[:self.max_per_tick]  # Limit to max_per_tick
            else:
                logger.error(f"❌ Failed to fetch due accounts: {response.status_code}")
                return []
                
        except Exception as e:
            logger.error(f"❌ Error fetching due accounts: {e}")
            return []
    
    def schedule_next(self, account: Dict) -> bool:
        """Schedule next run for an account with cadence + jitter"""
        try:
            account_id = account['id']
            cadence_minutes = account.get('cadence_minutes', self.default_cadence)
            jitter_seconds = account.get('jitter_seconds', 60)
            
            # Calculate next run time
            now = datetime.now()
            base_interval = timedelta(minutes=cadence_minutes)
            jitter = timedelta(seconds=random.randint(0, jitter_seconds))
            next_run = now + base_interval + jitter
            
            logger.info(f"📅 Scheduling next run for account {account_id}: {next_run}")
            
            # Update account with next run time
            update_data = {
                'next_run_at': next_run.isoformat(),
                'updated_at': now.isoformat()
            }
            
            return self.db.update_account(account_id, update_data)
            
        except Exception as e:
            logger.error(f"❌ Error scheduling next run for account {account.get('id')}: {e}")
            return False
    
    def pick_caption(self) -> Optional[Dict]:
        """Pick an unused caption, or random if none available"""
        try:
            # First try to get an unused caption
            response = self.db._make_request(
                'GET',
                f"{self.db.supabase_url}/rest/v1/captions",
                params={
                    'used': 'eq.false',
                    'select': 'id,text,category,tags',
                    'limit': '1'
                }
            )
            
            if response.status_code == 200:
                captions = response.json()
                if captions:
                    caption = captions[0]
                    logger.info(f"📝 Picked unused caption: {caption['id']}")
                    return caption
            
            # If no unused captions, get a random one
            logger.info("📝 No unused captions, picking random caption")
            response = self.db._make_request(
                'GET',
                f"{self.db.supabase_url}/rest/v1/captions",
                params={
                    'select': 'id,text,category,tags',
                    'limit': '1'
                }
            )
            
            if response.status_code == 200:
                captions = response.json()
                if captions:
                    caption = random.choice(captions)
                    logger.info(f"📝 Picked random caption: {caption['id']}")
                    return caption
            
            logger.warning("⚠️ No captions available")
            return None
            
        except Exception as e:
            logger.error(f"❌ Error picking caption: {e}")
            return None
    
    def pick_image(self) -> Optional[Dict]:
        """Pick a random image and bump use count"""
        try:
            response = self.db._make_request(
                'GET',
                f"{self.db.supabase_url}/rest/v1/images",
                params={
                    'select': 'id,url,filename,use_count',
                    'limit': '50'  # Get a pool to choose from
                }
            )
            
            if response.status_code == 200:
                images = response.json()
                if images:
                    # Pick random image
                    image = random.choice(images)
                    image_id = image['id']
                    
                    # Bump use count
                    new_count = (image.get('use_count', 0) or 0) + 1
                    update_data = {'use_count': new_count}
                    
                    if self.db.update_image_use_count(image_id, update_data):
                        logger.info(f"🖼️ Picked image {image_id}, use count: {new_count}")
                        return image
                    else:
                        logger.warning(f"⚠️ Failed to update image use count for {image_id}")
                        return image  # Return anyway
            
            logger.warning("⚠️ No images available")
            return None
            
        except Exception as e:
            logger.error(f"❌ Error picking image: {e}")
            return None
    
    def post_once(self, account: Dict, caption: Dict, image: Optional[Dict] = None) -> Tuple[bool, str]:
        """Post once using available methods"""
        try:
            account_id = account['id']
            username = account['username']
            caption_text = caption['text']
            image_url = image['url'] if image else None
            
            logger.info(f"📝 Posting for account {account_id} ({username})")
            logger.info(f"📝 Caption: {caption_text[:50]}...")
            if image_url:
                logger.info(f"🖼️ Image: {image_url}")
            
            # Try official Meta API first if enabled
            if self.meta_publish_enabled and account.get('threads_user_id'):
                success, message = self._post_via_meta_api(account, caption_text, image_url)
                if success:
                    return True, message
            
            # Fallback to session-based posting
            success, message = self._post_via_session(account, caption_text, image_url)
            return success, message
            
        except Exception as e:
            logger.error(f"❌ Error posting for account {account.get('id')}: {e}")
            return False, str(e)
    
    def _post_via_meta_api(self, account: Dict, caption_text: str, image_url: Optional[str]) -> Tuple[bool, str]:
        """Post via official Meta Threads API"""
        try:
            # This would use the official Meta API
            # For now, return success as placeholder
            logger.info(f"🔐 Using Meta API for account {account['id']}")
            return True, "Posted via Meta API (placeholder)"
            
        except Exception as e:
            logger.error(f"❌ Meta API posting failed: {e}")
            return False, f"Meta API error: {str(e)}"
    
    def _post_via_session(self, account: Dict, caption_text: str, image_url: Optional[str]) -> Tuple[bool, str]:
        """Post via session-based client"""
        try:
            username = account['username']
            
            # Check if session exists
            session_data = self.db.get_session_data(account['id'])
            if not session_data:
                return False, "No session data available"
            
            # This would use the session to post
            # For now, return success as placeholder
            logger.info(f"🔑 Using session for account {account['id']}")
            return True, "Posted via session (placeholder)"
            
        except Exception as e:
            logger.error(f"❌ Session posting failed: {e}")
            return False, f"Session error: {str(e)}"
    
    def record_posting_history(self, account_id: int, caption_id: int, image_id: Optional[int], 
                              success: bool, message: str) -> bool:
        """Record posting attempt in history"""
        try:
            status = 'posted' if success else 'failed'
            thread_id = None  # Would be set by actual posting
            
            return self.db.record_posting_history(
                account_id=account_id,
                caption_id=caption_id,
                image_id=image_id,
                thread_id=thread_id,
                status=status
            )
            
        except Exception as e:
            logger.error(f"❌ Error recording posting history: {e}")
            return False
    
    def mark_caption_used(self, caption_id: int) -> bool:
        """Mark caption as used"""
        try:
            return self.db.mark_caption_used(caption_id)
        except Exception as e:
            logger.error(f"❌ Error marking caption used: {e}")
            return False
    
    def update_account_posting_stats(self, account_id: int, success: bool) -> bool:
        """Update account posting statistics"""
        try:
            now = datetime.now()
            update_data = {
                'last_posted_at': now.isoformat() if success else None,
                'updated_at': now.isoformat()
            }
            
            return self.db.update_account(account_id, update_data)
            
        except Exception as e:
            logger.error(f"❌ Error updating account stats: {e}")
            return False

# Global instance
autopilot_service = AutopilotService()
