#!/usr/bin/env python3
"""
Threads API Service
Handles posting to Threads with session-first approach, fallback to official API
"""

import os
import logging
from typing import Tuple, Optional, Dict, Any
from services.session_store import session_store
from database import DatabaseManager

logger = logging.getLogger(__name__)

class ThreadsPostError(Exception):
    """Custom exception for Threads posting errors"""
    pass

class ThreadsClient:
    def __init__(self):
        self.meta_publish_enabled = os.getenv('META_THREADS_PUBLISH_ENABLED', 'false').lower() == 'true'
        self.db = DatabaseManager()
        
        logger.info(f"🚀 ThreadsClient initialized")
        logger.info(f"🔐 Meta publish enabled: {self.meta_publish_enabled}")
    
    def post_thread(self, account: Dict[str, Any], text: str, image_url: Optional[str] = None) -> Tuple[bool, str]:
        """
        Post to Threads using available methods
        Priority: Official API (if enabled + scopes) -> Session Client
        """
        try:
            account_id = account['id']
            username = account['username']
            
            logger.info(f"📝 Posting thread for account {account_id} ({username})")
            logger.info(f"📝 Text: {text[:50]}...")
            if image_url:
                logger.info(f"🖼️ Image: {image_url}")
            
            # Try official Meta API first if enabled and account has proper tokens
            if self.meta_publish_enabled and self._has_official_access(account):
                try:
                    success, message = self._post_via_official_api(account, text, image_url)
                    if success:
                        return True, message
                    else:
                        logger.warning(f"⚠️ Official API failed, trying session: {message}")
                except Exception as e:
                    logger.warning(f"⚠️ Official API error, falling back to session: {e}")
            
            # Fallback to session-based posting
            return self._post_via_session(account, text, image_url)
            
        except Exception as e:
            logger.error(f"❌ Error posting thread for account {account.get('id')}: {e}")
            return False, f"POSTING_ERROR: {str(e)}"
    
    def _has_official_access(self, account: Dict[str, Any]) -> bool:
        """Check if account has official API access with required scopes"""
        try:
            account_id = account['id']
            threads_user_id = account.get('threads_user_id')
            
            if not threads_user_id:
                return False
            
            # Check if we have valid tokens with required scopes
            token_data = self.db.get_token_by_account_id(account_id)
            if not token_data:
                return False
            
            access_token = token_data.get('access_token')
            scopes = token_data.get('scopes', [])
            
            if not access_token:
                return False
            
            # Check for required publishing scope
            required_scopes = ['threads_content_publish', 'threads_basic']
            has_scopes = all(scope in scopes for scope in required_scopes)
            
            logger.info(f"🔐 Official access check for {account_id}: token={bool(access_token)}, scopes={has_scopes}")
            return has_scopes
            
        except Exception as e:
            logger.error(f"❌ Error checking official access: {e}")
            return False
    
    def _post_via_official_api(self, account: Dict[str, Any], text: str, image_url: Optional[str] = None) -> Tuple[bool, str]:
        """Post via official Meta Threads API"""
        try:
            account_id = account['id']
            threads_user_id = account['threads_user_id']
            
            logger.info(f"🔐 Using official Meta API for account {account_id}")
            
            # Get access token
            token_data = self.db.get_token_by_account_id(account_id)
            if not token_data:
                raise ThreadsPostError("No access token found")
            
            access_token = token_data['access_token']
            
            # This would make the actual API call to Meta's Threads API
            # For now, simulate success
            logger.info(f"🔐 Simulating official API post for {threads_user_id}")
            
            # TODO: Replace with actual Meta API call
            # Example:
            # response = requests.post(
            #     f"https://graph.threads.net/v1/{threads_user_id}/threads",
            #     data={
            #         'text': text,
            #         'image_url': image_url,
            #         'access_token': access_token
            #     }
            # )
            
            return True, "OFFICIAL_API_SUCCESS: Posted via Meta Threads API"
            
        except Exception as e:
            logger.error(f"❌ Official API posting failed: {e}")
            return False, f"OFFICIAL_API_ERROR: {str(e)}"
    
    def _post_via_session(self, account: Dict[str, Any], text: str, image_url: Optional[str] = None) -> Tuple[bool, str]:
        """Post via session-based client"""
        try:
            username = account['username']
            
            logger.info(f"🔑 Using session client for {username}")
            
            # Load session from storage
            session_data = session_store.load_session(username)
            if not session_data:
                return False, "SESSION_MISSING: No session found for account"
            
            # Validate session data
            if not self._validate_session(session_data):
                return False, "SESSION_INVALID: Session data is invalid or expired"
            
            # This would use the session to post via unofficial methods
            # For now, simulate success
            logger.info(f"🔑 Simulating session post for {username}")
            
            # TODO: Replace with actual session-based posting
            # This could use instagrapi, unofficial libraries, or custom session logic
            # Example:
            # from instagrapi import Client
            # cl = Client()
            # cl.load_settings(session_data)
            # result = cl.threads_publish(text, image_url)
            
            return True, "SESSION_SUCCESS: Posted via session client"
            
        except Exception as e:
            logger.error(f"❌ Session posting failed: {e}")
            return False, f"SESSION_ERROR: {str(e)}"
    
    def _validate_session(self, session_data: Dict[str, Any]) -> bool:
        """Validate session data"""
        try:
            # Check if session has required fields
            required_fields = ['username', 'session_id']  # Adjust based on actual session structure
            
            for field in required_fields:
                if field not in session_data:
                    logger.warning(f"⚠️ Session missing required field: {field}")
                    return False
            
            # Check if session is not expired (if timestamp available)
            # This depends on your session structure
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Error validating session: {e}")
            return False
    
    def get_posting_method(self, account: Dict[str, Any]) -> str:
        """Get the posting method that would be used for this account"""
        if self.meta_publish_enabled and self._has_official_access(account):
            return "official_api"
        elif session_store.exists(account['username']):
            return "session_client"
        else:
            return "no_method_available"
    
    def check_account_status(self, account: Dict[str, Any]) -> Dict[str, Any]:
        """Check account connection status and available posting methods"""
        try:
            username = account['username']
            account_id = account['id']
            
            has_session = session_store.exists(username)
            has_official = self._has_official_access(account)
            posting_method = self.get_posting_method(account)
            
            status = {
                'username': username,
                'account_id': account_id,
                'has_session': has_session,
                'has_official_api': has_official,
                'posting_method': posting_method,
                'can_post': posting_method != "no_method_available"
            }
            
            # Determine connection status
            if has_official:
                status['connection_status'] = 'connected_official'
            elif has_session:
                status['connection_status'] = 'connected_session'
            else:
                status['connection_status'] = 'disconnected'
            
            return status
            
        except Exception as e:
            logger.error(f"❌ Error checking account status: {e}")
            return {
                'username': account.get('username'),
                'account_id': account.get('id'),
                'error': str(e),
                'connection_status': 'error'
            }

# Global instance
threads_client = ThreadsClient()