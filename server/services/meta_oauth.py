#!/usr/bin/env python3
"""
Meta OAuth Service
Handles OAuth flows for Threads API authentication
"""

import os
import logging
import requests
from typing import Optional, Dict, Any
from datetime import datetime, timedelta
from urllib.parse import urlencode

logger = logging.getLogger(__name__)

class MetaOAuthService:
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
        
        self.graph_api_base = 'https://graph.threads.net/'
        self.auth_base = 'https://www.threads.net'
        
        # Meta permissions for Threads API access
        self.scopes = [
            'instagram_basic',
            'instagram_content_publish',
            'pages_read_engagement',
            'pages_show_list',
        ]
        
        logger.info("✅ MetaOAuthService initialized (OAuth configured: {})".format(self.oauth_configured))
    
    def build_auth_url(self, account_id: int, username: str) -> str:
        """Build OAuth authorization URL"""
        if not self.oauth_configured:
            raise ValueError("OAuth not configured - use direct account creation instead")
            
        try:
            params = {
                'client_id': self.app_id,
                'redirect_uri': self.redirect_uri,
                'response_type': 'code',
                'scope': ','.join(self.scopes),
                'state': str(account_id),  # Pass account_id as state
            }
            
            auth_url = f"{self.auth_base}/oauth/authorize?{urlencode(params)}"
            logger.info(f"🔗 Built auth URL for account {account_id} ({username})")
            return auth_url
            
        except Exception as e:
            logger.error(f"❌ Error building auth URL: {e}")
            raise
    
    def exchange_code_for_tokens(self, code: str, account_id: int) -> Dict[str, Any]:
        """Exchange authorization code for access tokens"""
        try:
            logger.info(f"🔄 Exchanging code for tokens for account {account_id}")
            
            # Exchange code for access token
            token_url = f"{self.graph_api_base}oauth/access_token"
            token_data = {
                'client_id': self.app_id,
                'client_secret': self.app_secret,
                'grant_type': 'authorization_code',
                'redirect_uri': self.redirect_uri,
                'code': code,
            }
            
            response = requests.post(token_url, data=token_data)
            
            if not response.ok:
                logger.error(f"❌ Token exchange failed: {response.status_code} - {response.text}")
                raise Exception(f"Token exchange failed: {response.text}")
            
            token_info = response.json()
            access_token = token_info.get('access_token')
            
            if not access_token:
                logger.error("❌ No access token in response")
                raise Exception("No access token received")
            
            # Get token details
            token_details = self._get_token_details(access_token)
            
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
            }
            
            logger.info(f"✅ Token exchange successful for account {account_id}")
            return result
            
        except Exception as e:
            logger.error(f"❌ Error exchanging code for tokens: {e}")
            raise
    
    def _get_token_details(self, access_token: str) -> Dict[str, Any]:
        """Get details about the access token"""
        try:
            url = f"{self.graph_api_base}debug_token"
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
            
            token_url = f"{self.graph_api_base}oauth/access_token"
            token_data = {
                'client_id': self.app_id,
                'client_secret': self.app_secret,
                'grant_type': 'fb_exchange_token',
                'fb_exchange_token': refresh_token,
            }
            
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
    
    def validate_token(self, access_token: str) -> bool:
        """Validate if an access token is still valid"""
        try:
            url = f"{self.graph_api_base}debug_token"
            params = {
                'input_token': access_token,
                'access_token': f"{self.app_id}|{self.app_secret}",
            }
            
            response = requests.get(url, params=params)
            
            if not response.ok:
                return False
            
            data = response.json().get('data', {})
            expires_at = data.get('expires_at')
            
            if expires_at:
                # Check if token is expired
                expiration_time = datetime.fromtimestamp(expires_at)
                return datetime.now() < expiration_time
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Error validating token: {e}")
            return False

# Global instance
meta_oauth_service = MetaOAuthService()
