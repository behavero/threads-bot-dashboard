#!/usr/bin/env python3
"""
Meta Client for Threads API
Handles posting and user stats via official Threads API
"""

import os
import logging
import requests
from typing import Optional, Dict, Any, List
from datetime import datetime

logger = logging.getLogger(__name__)

class MetaClient:
    def __init__(self):
        self.base_url = "https://graph.threads.net/"
        self.api_version = os.getenv('GRAPH_API_VERSION', 'v1.0')
        self.api_url = f"{self.base_url}{self.api_version}/"
        
        logger.info("✅ MetaClient initialized")
    
    def post_thread(self, token: str, text: str, image_url: Optional[str] = None) -> Dict[str, Any]:
        """Post a thread via Threads API"""
        try:
            logger.info(f"📝 Posting thread with text: {text[:50]}...")
            
            # Build post parameters
            params = {
                'text': text,
            }
            
            # Add image if provided
            if image_url:
                params['media_url'] = image_url
            
            # Create post
            url = f"{self.api_url}me/threads"
            headers = {
                'Authorization': f'Bearer {token}',
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
            
            logger.info(f"✅ Post created successfully, container: {container_id}")
            
            # Publish the post
            publish_result = self._publish_post(token, container_id)
            
            return {
                'success': True,
                'container_id': container_id,
                'thread_id': publish_result.get('thread_id'),
                'status': 'published'
            }
            
        except Exception as e:
            logger.error(f"❌ Error posting thread: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def _publish_post(self, token: str, container_id: str) -> Dict[str, Any]:
        """Publish a created post"""
        try:
            logger.info(f"🚀 Publishing post {container_id}")
            
            url = f"{self.api_url}me/threads_publish"
            headers = {
                'Authorization': f'Bearer {token}',
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
            
            logger.info(f"✅ Post published successfully, thread: {thread_id}")
            
            return {
                'success': True,
                'thread_id': thread_id
            }
            
        except Exception as e:
            logger.error(f"❌ Error publishing post: {e}")
            raise
    
    def get_user_stats(self, token: str) -> Dict[str, Any]:
        """Get user statistics from Threads API"""
        try:
            logger.info("📊 Getting user stats")
            
            url = f"{self.api_url}me"
            headers = {
                'Authorization': f'Bearer {token}',
            }
            
            params = {
                'fields': 'id,username,threads_biography,threads_profile_picture_url,follower_count',
            }
            
            response = requests.get(url, params=params, headers=headers)
            
            if not response.ok:
                logger.error(f"❌ User stats failed: {response.status_code} - {response.text}")
                raise Exception(f"User stats failed: {response.text}")
            
            user_data = response.json()
            
            # Get recent posts for engagement stats
            posts_data = self._get_recent_posts(token)
            
            stats = {
                'user_id': user_data.get('id'),
                'username': user_data.get('username'),
                'biography': user_data.get('threads_biography'),
                'profile_picture': user_data.get('threads_profile_picture_url'),
                'follower_count': user_data.get('follower_count', 0),
                'recent_posts': posts_data.get('posts', []),
                'total_posts': len(posts_data.get('posts', [])),
            }
            
            logger.info(f"✅ User stats retrieved for {user_data.get('username', 'unknown')}")
            return {
                'success': True,
                'data': stats
            }
            
        except Exception as e:
            logger.error(f"❌ Error getting user stats: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def _get_recent_posts(self, token: str, limit: int = 10) -> Dict[str, Any]:
        """Get recent posts for engagement analysis"""
        try:
            url = f"{self.api_url}me/threads"
            headers = {
                'Authorization': f'Bearer {token}',
            }
            
            params = {
                'fields': 'id,text,media_type,media_url,permalink,timestamp,likes,replies,reposts,quotes,views',
                'limit': limit,
            }
            
            response = requests.get(url, params=params, headers=headers)
            
            if not response.ok:
                logger.error(f"❌ Recent posts failed: {response.status_code} - {response.text}")
                return {'posts': []}
            
            data = response.json()
            posts = data.get('data', [])
            
            # Calculate engagement metrics
            total_likes = sum(post.get('likes', 0) for post in posts)
            total_replies = sum(post.get('replies', 0) for post in posts)
            total_reposts = sum(post.get('reposts', 0) for post in posts)
            total_quotes = sum(post.get('quotes', 0) for post in posts)
            total_views = sum(post.get('views', 0) for post in posts)
            
            return {
                'posts': posts,
                'engagement': {
                    'total_likes': total_likes,
                    'total_replies': total_replies,
                    'total_reposts': total_reposts,
                    'total_quotes': total_quotes,
                    'total_views': total_views,
                    'avg_engagement': (total_likes + total_replies + total_reposts + total_quotes) / max(len(posts), 1)
                }
            }
            
        except Exception as e:
            logger.error(f"❌ Error getting recent posts: {e}")
            return {'posts': []}
    
    def validate_token(self, token: str) -> bool:
        """Validate if a token is still valid"""
        try:
            url = f"{self.api_url}me"
            headers = {
                'Authorization': f'Bearer {token}',
            }
            
            response = requests.get(url, headers=headers)
            return response.ok
            
        except Exception as e:
            logger.error(f"❌ Error validating token: {e}")
            return False

# Global instance
meta_client = MetaClient()
