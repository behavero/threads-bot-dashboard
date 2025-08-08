#!/usr/bin/env python3
"""
Meta OAuth Helpers
Handles OAuth URL building and state management for Meta Threads API
"""

import os
import secrets
import logging
from datetime import datetime, timedelta
from urllib.parse import urlencode
from typing import Optional, Dict, Any
from database import DatabaseManager

logger = logging.getLogger(__name__)

class MetaOAuthHelper:
    def __init__(self):
        from config.env import load_meta_oauth_config
        cfg = load_meta_oauth_config()
        
        self.app_id = cfg.app_id
        self.app_secret = cfg.app_secret
        self.redirect_uri = cfg.redirect_uri
        self.app_base_url = os.getenv('APP_BASE_URL')
        
        # Use centralized config validation
        self.oauth_configured = cfg.is_configured
        
        if not self.oauth_configured:
            logger.warning("⚠️ Meta OAuth not configured - using direct account creation")
        
        # Threads API scopes (minimal for publishing)
        self.scopes = [
            'threads_basic',
            'threads_content_publish',
            'threads_manage_insights',
            'threads_manage_replies',
            'threads_read_replies',
        ]
        
        logger.info("✅ MetaOAuthHelper initialized (OAuth configured: {})".format(self.oauth_configured))
    
    def build_oauth_url(self, state: str) -> str:
        """Build Meta OAuth URL with required parameters"""
        if not self.oauth_configured:
            raise ValueError("OAuth not configured - use direct account creation instead")
            
        try:
            params = {
                'client_id': self.app_id,
                'redirect_uri': self.redirect_uri,
                'response_type': 'code',
                'scope': ','.join(self.scopes),
                'state': state,
            }
            
            auth_url = f"https://www.facebook.com/dialog/oauth?{urlencode(params)}"
            logger.info(f"🔗 Built OAuth URL with state: {state[:8]}...")
            return auth_url
            
        except Exception as e:
            logger.error(f"❌ Error building OAuth URL: {e}")
            raise
    
    def generate_state(self, account_id: int) -> str:
        """Generate secure state token for CSRF protection"""
        try:
            # Generate random state
            state = secrets.token_urlsafe(32)
            
            # Store in database
            db = DatabaseManager()
            if db.store_oauth_state(account_id, state):
                logger.info(f"✅ Generated and stored OAuth state for account {account_id}")
                return state
            else:
                raise Exception("Failed to store OAuth state")
                
        except Exception as e:
            logger.error(f"❌ Error generating OAuth state: {e}")
            raise
    
    def validate_state(self, state: str) -> Optional[int]:
        """Validate and retrieve account_id from state"""
        try:
            db = DatabaseManager()
            account_id = db.get_oauth_state_account_id(state)
            
            if account_id:
                # Delete used state
                db.delete_oauth_state(state)
                logger.info(f"✅ Validated OAuth state for account {account_id}")
                return account_id
            else:
                logger.warning(f"⚠️ Invalid OAuth state: {state[:8]}...")
                return None
                
        except Exception as e:
            logger.error(f"❌ Error validating OAuth state: {e}")
            return None
    
    def exchange_code_for_tokens(self, code: str) -> Dict[str, Any]:
        """Exchange authorization code for access tokens"""
        try:
            logger.info("🔄 Exchanging code for tokens")
            
            # Exchange code for access token
            token_url = "https://graph.threads.net/oauth/access_token"
            token_data = {
                'client_id': self.app_id,
                'client_secret': self.app_secret,
                'grant_type': 'authorization_code',
                'redirect_uri': self.redirect_uri,
                'code': code,
            }
            
            import requests
            response = requests.post(token_url, data=token_data)
            
            if not response.ok:
                logger.error(f"❌ Token exchange failed: {response.status_code} - {response.text}")
                raise Exception(f"Token exchange failed: {response.text}")
            
            token_info = response.json()
            access_token = token_info.get('access_token')
            
            if not access_token:
                logger.error("❌ No access token in response")
                raise Exception("No access token received")
            
            # Get token details and user info
            token_details = self._get_token_details(access_token)
            user_info = self._get_user_info(access_token)
            
            # Calculate expiration
            expires_in = token_info.get('expires_in', 0)
            expires_at = datetime.now() + timedelta(seconds=expires_in) if expires_in > 0 else None
            
            result = {
                'access_token': access_token,
                'refresh_token': token_info.get('refresh_token'),
                'expires_at': expires_at.isoformat() if expires_at else None,
                'scopes': token_details.get('scopes', []),
                'user_id': token_details.get('user_id'),
                'app_id': token_details.get('app_id'),
                'username': user_info.get('username'),
                'threads_user_id': user_info.get('id'),
            }
            
            logger.info(f"✅ Token exchange successful for user {user_info.get('username', 'unknown')}")
            return result
            
        except Exception as e:
            logger.error(f"❌ Error exchanging code for tokens: {e}")
            raise
    
    def _get_token_details(self, access_token: str) -> Dict[str, Any]:
        """Get details about the access token"""
        try:
            import requests
            
            url = "https://graph.threads.net/debug_token"
            params = {
                'input_token': access_token,
                'access_token': f"{self.app_id}|{self.app_secret}",
            }
            
            response = requests.get(url, params=params)
            
            if not response.ok:
                logger.error(f"❌ Token debug failed: {response.status_code} - {response.text}")
                return {}
            
            data = response.json().get('data', {})
            
            return {
                'user_id': data.get('user_id'),
                'app_id': data.get('app_id'),
                'scopes': data.get('scopes', []),
                'expires_at': data.get('expires_at'),
                'issued_at': data.get('issued_at'),
            }
            
        except Exception as e:
            logger.error(f"❌ Error getting token details: {e}")
            return {}
    
    def refresh_access_token(self, refresh_token: str, account_id: int) -> Dict[str, Any]:
        """Refresh an access token using refresh token"""
        try:
            logger.info(f"🔄 Refreshing token for account {account_id}")
            
            token_url = "https://graph.threads.net/oauth/access_token"
            token_data = {
                'client_id': self.app_id,
                'client_secret': self.app_secret,
                'grant_type': 'fb_exchange_token',
                'fb_exchange_token': refresh_token,
            }
            
            import requests
            response = requests.post(token_url, data=token_data)
            
            if not response.ok:
                logger.error(f"❌ Token refresh failed: {response.status_code} - {response.text}")
                raise Exception(f"Token refresh failed: {response.text}")
            
            token_info = response.json()
            access_token = token_info.get('access_token')
            
            if not access_token:
                logger.error("❌ No access token in refresh response")
                raise Exception("No access token received from refresh")
            
            # Get token details
            token_details = self._get_token_details(access_token)
            
            # Calculate expiration
            expires_in = token_info.get('expires_in', 0)
            expires_at = datetime.now() + timedelta(seconds=expires_in) if expires_in > 0 else None
            
            result = {
                'access_token': access_token,
                'refresh_token': token_info.get('refresh_token', refresh_token),  # Keep old refresh token if new one not provided
                'expires_at': expires_at.isoformat() if expires_at else None,
                'scopes': token_details.get('scopes', []),
                'user_id': token_details.get('user_id'),
                'app_id': token_details.get('app_id'),
            }
            
            logger.info(f"✅ Token refresh successful for account {account_id}")
            return result
            
        except Exception as e:
            logger.error(f"❌ Error refreshing token: {e}")
            raise
    
    def _get_user_info(self, access_token: str) -> Dict[str, Any]:
        """Get user information from Threads API"""
        try:
            import requests
            
            url = "https://graph.threads.net/me"
            headers = {
                'Authorization': f'Bearer {access_token}',
            }
            
            params = {
                'fields': 'id,username,threads_biography,threads_profile_picture_url',
            }
            
            response = requests.get(url, params=params, headers=headers)
            
            if not response.ok:
                logger.error(f"❌ User info failed: {response.status_code} - {response.text}")
                return {}
            
            user_data = response.json()
            
            return {
                'id': user_data.get('id'),
                'username': user_data.get('username'),
                'biography': user_data.get('threads_biography'),
                'profile_picture': user_data.get('threads_profile_picture_url'),
            }
            
        except Exception as e:
            logger.error(f"❌ Error getting user info: {e}")
            return {}

# Global instance
meta_oauth_helper = MetaOAuthHelper()
