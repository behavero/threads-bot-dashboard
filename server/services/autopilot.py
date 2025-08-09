#!/usr/bin/env python3
"""
Autopilot Service
Handles automated posting with per-account cadence and jitter
"""

import os
import random
import logging
import time
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
                    'select': 'id,username,cadence_minutes,jitter_seconds,connection_status,threads_user_id,last_caption_id,error_count,last_error'
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
    
    def pick_caption(self, account: Dict) -> Optional[Dict]:
        """Pick a caption with deduplication (avoid same caption twice in a row)"""
        try:
            last_caption_id = account.get('last_caption_id')
            
            # Build exclusion filter for last used caption
            exclusion_filter = f"id.neq.{last_caption_id}" if last_caption_id else None
            
            # First try to get an unused caption (excluding last used)
            params = {
                'used': 'eq.false',
                'select': 'id,text,category,tags',
                'limit': '10'  # Get a few to choose from
            }
            if exclusion_filter:
                params['and'] = f"({exclusion_filter})"
            
            response = self.db._make_request(
                'GET',
                f"{self.db.supabase_url}/rest/v1/captions",
                params=params
            )
            
            if response.status_code == 200:
                captions = response.json()
                if captions:
                    caption = random.choice(captions)
                    logger.info(f"📝 Picked unused caption: {caption['id']} (avoiding {last_caption_id})")
                    return caption
            
            # If no unused captions, get any caption (excluding last used)
            logger.info("📝 No unused captions, picking any caption (with dedup)")
            params = {'select': 'id,text,category,tags', 'limit': '10'}
            if exclusion_filter:
                params['and'] = f"({exclusion_filter})"
            
            response = self.db._make_request(
                'GET',
                f"{self.db.supabase_url}/rest/v1/captions",
                params=params
            )
            
            if response.status_code == 200:
                captions = response.json()
                if captions:
                    caption = random.choice(captions)
                    logger.info(f"📝 Picked random caption: {caption['id']} (avoiding {last_caption_id})")
                    return caption
            
            # Last resort: get any caption if dedup isn't possible
            if last_caption_id:
                logger.warning("⚠️ Forced to pick any caption (dedup failed)")
                response = self.db._make_request(
                    'GET',
                    f"{self.db.supabase_url}/rest/v1/captions",
                    params={'select': 'id,text,category,tags', 'limit': '1'}
                )
                
                if response.status_code == 200:
                    captions = response.json()
                    if captions:
                        caption = captions[0]
                        logger.info(f"📝 Picked fallback caption: {caption['id']}")
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
        """Post once with retry logic for transient errors"""
        try:
            from services.threads_api import threads_client
            
            account_id = account['id']
            username = account['username']
            caption_text = caption['text']
            image_url = image['url'] if image else None
            
            logger.info(f"📝 Posting for account {account_id} ({username})")
            logger.info(f"📝 Caption: {caption_text[:50]}...")
            if image_url:
                logger.info(f"🖼️ Image: {image_url}")
            
            # First attempt
            success, message = threads_client.post_thread(account, caption_text, image_url)
            
            if success:
                logger.info(f"✅ Post successful on first attempt for account {account_id}")
                return True, message
            
            # Check if error is retryable
            if self._is_retryable_error(message):
                logger.warning(f"⚠️ Transient error for account {account_id}, retrying: {message}")
                
                # Wait 10-20 seconds before retry
                retry_delay = random.randint(10, 20)
                logger.info(f"⏳ Waiting {retry_delay}s before retry for account {account_id}")
                time.sleep(retry_delay)
                
                # Retry attempt
                logger.info(f"🔄 Retrying post for account {account_id}")
                success, message = threads_client.post_thread(account, caption_text, image_url)
                
                if success:
                    logger.info(f"✅ Post successful on retry for account {account_id}")
                    return True, message
                else:
                    logger.error(f"❌ Post failed on retry for account {account_id}: {message}")
                    return False, f"Retry failed: {message}"
            else:
                logger.error(f"❌ Hard error for account {account_id}: {message}")
                return False, message
            
        except Exception as e:
            logger.error(f"❌ Exception during post for account {account.get('id')}: {e}")
            return False, str(e)
    
    def _is_retryable_error(self, error_message: str) -> bool:
        """Determine if an error is worth retrying"""
        retryable_patterns = [
            "timeout",
            "connection",
            "network",
            "502",
            "503", 
            "504",
            "rate limit",
            "temporary",
            "server error",
            "session_error"  # Session might need refresh
        ]
        
        error_lower = error_message.lower()
        return any(pattern in error_lower for pattern in retryable_patterns)
    

    
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
    
    def update_account_posting_stats(self, account_id: int, success: bool, caption_id: Optional[int] = None, error_message: Optional[str] = None) -> bool:
        """Update account posting statistics with resilience tracking"""
        try:
            now = datetime.now()
            update_data = {
                'updated_at': now.isoformat()
            }
            
            if success:
                # Reset error tracking on success
                update_data.update({
                    'last_posted_at': now.isoformat(),
                    'last_caption_id': caption_id,
                    'last_error': None,
                    'error_count': 0
                })
                logger.info(f"✅ Reset error tracking for successful post on account {account_id}")
            else:
                # Handle error case with backoff
                # Get current error count
                account = self.db.get_account_by_id(account_id)
                current_error_count = account.get('error_count', 0) if account else 0
                new_error_count = current_error_count + 1
                
                update_data.update({
                    'last_error': error_message,
                    'error_count': new_error_count
                })
                
                # Apply backoff - 60 minutes for hard errors
                backoff_minutes = 60
                next_run = now + timedelta(minutes=backoff_minutes)
                update_data['next_run_at'] = next_run.isoformat()
                
                logger.warning(f"⚠️ Error #{new_error_count} for account {account_id}, backing off until {next_run}")
            
            return self.db.update_account(account_id, update_data)
            
        except Exception as e:
            logger.error(f"❌ Error updating account stats: {e}")
            return False
    
    def handle_posting_success(self, account_id: int, caption_id: int, image_id: Optional[int]) -> bool:
        """Handle successful posting - update stats and schedule next run"""
        try:
            # Update posting stats (clears errors)
            self.update_account_posting_stats(account_id, True, caption_id)
            
            # Mark caption as used
            self.mark_caption_used(caption_id)
            
            # Schedule next regular run
            account = self.db.get_account_by_id(account_id)
            if account:
                self.schedule_next(account)
            
            logger.info(f"✅ Handled successful posting for account {account_id}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Error handling posting success: {e}")
            return False
    
    def handle_posting_failure(self, account_id: int, error_message: str) -> bool:
        """Handle posting failure - apply backoff and store error"""
        try:
            # Update with error and backoff
            self.update_account_posting_stats(account_id, False, error_message=error_message)
            
            logger.warning(f"⚠️ Handled posting failure for account {account_id}: {error_message}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Error handling posting failure: {e}")
            return False

# Global instance
autopilot_service = AutopilotService()
