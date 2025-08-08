#!/usr/bin/env python3
"""
Threads API Service
Handles posting and content management via official Threads API
"""

import os
import logging
import requests
from typing import Optional, Dict, Any, List
from datetime import datetime
from .meta_oauth import meta_oauth_service

logger = logging.getLogger(__name__)

class ThreadsAPIService:
    def __init__(self):
        self.graph_api_base = 'https://graph.threads.net/'
        self.api_version = os.getenv('GRAPH_API_VERSION', 'v1.0')
        self.base_url = f"{self.graph_api_base}{self.api_version}/"
        
        logger.info("✅ ThreadsAPIService initialized")
    
    def _get_access_token(self, account_id: int) -> Optional[str]:
        """Get valid access token for account"""
        try:
            from database import DatabaseManager
            db = DatabaseManager()
            
            # Get token from database
            token_data = db.get_token_by_account_id(account_id)
            if not token_data:
                logger.warning(f"⚠️ No token found for account {account_id}")
                return None
            
            access_token = token_data.get('access_token')
            if not access_token:
                logger.warning(f"⚠️ No access token for account {account_id}")
                return None
            
            # Check if token is valid
            if meta_oauth_service.validate_token(access_token):
                logger.info(f"✅ Valid token found for account {account_id}")
                return access_token
            
            # Try to refresh token
            refresh_token = token_data.get('refresh_token')
            if refresh_token:
                try:
                    new_token_data = meta_oauth_service.refresh_access_token(refresh_token, account_id)
                    db.update_token(account_id, new_token_data)
                    logger.info(f"✅ Token refreshed for account {account_id}")
                    return new_token_data.get('access_token')
                except Exception as e:
                    logger.error(f"❌ Token refresh failed for account {account_id}: {e}")
                    return None
            
            logger.warning(f"⚠️ No valid token for account {account_id}")
            return None
            
        except Exception as e:
            logger.error(f"❌ Error getting access token for account {account_id}: {e}")
            return None
    
    def create_post(self, account_id: int, text: str, media_urls: Optional[List[str]] = None, 
                   reply_to_id: Optional[str] = None, quote_post_id: Optional[str] = None) -> Dict[str, Any]:
        """Create a new post via Threads API"""
        try:
            access_token = self._get_access_token(account_id)
            if not access_token:
                raise Exception("No valid access token")
            
            logger.info(f"📝 Creating post for account {account_id}")
            
            # Build post parameters
            params = {
                'text': text,
            }
            
            # Add media if provided
            if media_urls and len(media_urls) > 0:
                if len(media_urls) == 1:
                    params['media_url'] = media_urls[0]
                else:
                    # Handle multiple media (carousel)
                    params['media_type'] = 'CAROUSEL'
                    params['children'] = [{'media_url': url} for url in media_urls]
            
            # Add reply configuration
            if reply_to_id:
                params['reply_to_id'] = reply_to_id
                params['reply_control'] = 'FOLLOWERS'
            
            # Add quote post
            if quote_post_id:
                params['quote_post_id'] = quote_post_id
            
            # Create post
            url = f"{self.base_url}me/threads"
            headers = {
                'Authorization': f'Bearer {access_token}',
                'Content-Type': 'application/json',
            }
            
            response = requests.post(url, json=params, headers=headers)
            
            if not response.ok:
                logger.error(f"❌ Post creation failed: {response.status_code} - {response.text}")
                raise Exception(f"Post creation failed: {response.text}")
            
            post_data = response.json()
            container_id = post_data.get('id')
            
            if not container_id:
                raise Exception("No container ID received")
            
            logger.info(f"✅ Post created successfully for account {account_id}, container: {container_id}")
            
            return {
                'success': True,
                'container_id': container_id,
                'status': 'created',
            }
            
        except Exception as e:
            logger.error(f"❌ Error creating post for account {account_id}: {e}")
            return {
                'success': False,
                'error': str(e),
            }
    
    def publish_post(self, account_id: int, container_id: str) -> Dict[str, Any]:
        """Publish a created post"""
        try:
            access_token = self._get_access_token(account_id)
            if not access_token:
                raise Exception("No valid access token")
            
            logger.info(f"🚀 Publishing post {container_id} for account {account_id}")
            
            url = f"{self.base_url}me/threads_publish"
            headers = {
                'Authorization': f'Bearer {access_token}',
                'Content-Type': 'application/json',
            }
            
            params = {
                'creation_id': container_id,
            }
            
            response = requests.post(url, json=params, headers=headers)
            
            if not response.ok:
                logger.error(f"❌ Post publishing failed: {response.status_code} - {response.text}")
                raise Exception(f"Post publishing failed: {response.text}")
            
            publish_data = response.json()
            thread_id = publish_data.get('id')
            
            if not thread_id:
                raise Exception("No thread ID received")
            
            logger.info(f"✅ Post published successfully for account {account_id}, thread: {thread_id}")
            
            return {
                'success': True,
                'thread_id': thread_id,
                'status': 'published',
            }
            
        except Exception as e:
            logger.error(f"❌ Error publishing post for account {account_id}: {e}")
            return {
                'success': False,
                'error': str(e),
            }
    
    def post_with_media(self, account_id: int, text: str, media_urls: List[str], 
                       reply_to_id: Optional[str] = None) -> Dict[str, Any]:
        """Create and publish a post with media"""
        try:
            # First create the post
            create_result = self.create_post(account_id, text, media_urls, reply_to_id)
            
            if not create_result['success']:
                return create_result
            
            container_id = create_result['container_id']
            
            # Then publish it
            publish_result = self.publish_post(account_id, container_id)
            
            if not publish_result['success']:
                return publish_result
            
            return {
                'success': True,
                'thread_id': publish_result['thread_id'],
                'status': 'published',
            }
            
        except Exception as e:
            logger.error(f"❌ Error posting with media for account {account_id}: {e}")
            return {
                'success': False,
                'error': str(e),
            }
    
    def get_account_info(self, account_id: int) -> Dict[str, Any]:
        """Get account information from Threads API"""
        try:
            access_token = self._get_access_token(account_id)
            if not access_token:
                raise Exception("No valid access token")
            
            logger.info(f"📊 Getting account info for account {account_id}")
            
            url = f"{self.base_url}me"
            headers = {
                'Authorization': f'Bearer {access_token}',
            }
            
            params = {
                'fields': 'id,username,threads_biography,threads_profile_picture_url,follower_count',
            }
            
            response = requests.get(url, params=params, headers=headers)
            
            if not response.ok:
                logger.error(f"❌ Account info failed: {response.status_code} - {response.text}")
                raise Exception(f"Account info failed: {response.text}")
            
            account_data = response.json()
            
            logger.info(f"✅ Account info retrieved for account {account_id}")
            
            return {
                'success': True,
                'data': account_data,
            }
            
        except Exception as e:
            logger.error(f"❌ Error getting account info for account {account_id}: {e}")
            return {
                'success': False,
                'error': str(e),
            }
    
    def get_post_insights(self, account_id: int, thread_id: str) -> Dict[str, Any]:
        """Get insights for a specific post"""
        try:
            access_token = self._get_access_token(account_id)
            if not access_token:
                raise Exception("No valid access token")
            
            logger.info(f"📈 Getting insights for thread {thread_id}")
            
            url = f"{self.base_url}{thread_id}/insights"
            headers = {
                'Authorization': f'Bearer {access_token}',
            }
            
            params = {
                'metric': 'likes,replies,reposts,quotes,views',
            }
            
            response = requests.get(url, params=params, headers=headers)
            
            if not response.ok:
                logger.error(f"❌ Insights failed: {response.status_code} - {response.text}")
                raise Exception(f"Insights failed: {response.text}")
            
            insights_data = response.json()
            
            logger.info(f"✅ Insights retrieved for thread {thread_id}")
            
            return {
                'success': True,
                'data': insights_data,
            }
            
        except Exception as e:
            logger.error(f"❌ Error getting insights for thread {thread_id}: {e}")
            return {
                'success': False,
                'error': str(e),
            }

# Global instance
threads_api_service = ThreadsAPIService()
