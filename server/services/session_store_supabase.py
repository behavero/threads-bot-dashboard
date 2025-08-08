#!/usr/bin/env python3
"""
Session Store for Supabase Storage
Handles saving and loading instagrapi sessions to/from Supabase Storage
"""

import os
import json
import hashlib
import tempfile
import logging
import requests
from typing import Optional, Dict, Any
from instagrapi import Client

logger = logging.getLogger(__name__)

class SupabaseSessionStore:
    def __init__(self):
        self.supabase_url = os.getenv('SUPABASE_URL')
        self.supabase_key = os.getenv('SUPABASE_SERVICE_ROLE_KEY')
        
        if not self.supabase_url or not self.supabase_key:
            raise ValueError("Missing Supabase credentials for session storage")
        
        self.headers = {
            'apikey': self.supabase_key,
            'Authorization': f'Bearer {self.supabase_key}',
            'Content-Type': 'application/json'
        }
        
        self.bucket_name = 'sessions'
        logger.info("✅ SupabaseSessionStore initialized")
    
    def _get_user_path(self, username: str) -> str:
        """Generate a stable path for user sessions"""
        # Create a stable hash of the username for the folder
        user_hash = hashlib.sha256(username.encode()).hexdigest()[:16]
        return f"{user_hash}/settings.json"
    
    def _ensure_bucket_exists(self) -> bool:
        """Ensure the sessions bucket exists"""
        try:
            # Check if bucket exists
            response = requests.get(
                f"{self.supabase_url}/storage/v1/bucket/{self.bucket_name}",
                headers=self.headers
            )
            
            if response.status_code == 200:
                logger.info(f"✅ Bucket '{self.bucket_name}' exists")
                return True
            elif response.status_code == 404:
                # Create bucket
                bucket_data = {
                    "name": self.bucket_name,
                    "public": False,
                    "allowed_mime_types": ["application/json"],
                    "file_size_limit": 1048576  # 1MB
                }
                
                create_response = requests.post(
                    f"{self.supabase_url}/storage/v1/bucket",
                    json=bucket_data,
                    headers=self.headers
                )
                
                if create_response.status_code == 200:
                    logger.info(f"✅ Created bucket '{self.bucket_name}'")
                    return True
                else:
                    logger.error(f"❌ Failed to create bucket: {create_response.text}")
                    return False
            else:
                logger.error(f"❌ Unexpected response checking bucket: {response.status_code}")
                return False
                
        except Exception as e:
            logger.error(f"❌ Error ensuring bucket exists: {e}")
            return False
    
    def save_session_to_supabase(self, username: str, client: Client) -> bool:
        """Save instagrapi session to Supabase Storage"""
        try:
            logger.info(f"💾 Saving session for username: {username}")
            
            # Ensure bucket exists
            if not self._ensure_bucket_exists():
                logger.error("❌ Could not ensure bucket exists")
                return False
            
            # Get client settings
            settings = client.get_settings()
            if not settings:
                logger.warning("⚠️ No settings to save")
                return False
            
            # Create temporary file for settings
            with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as temp_file:
                json.dump(settings, temp_file, indent=2)
                temp_file_path = temp_file.name
            
            try:
                # Read the file content
                with open(temp_file_path, 'rb') as f:
                    file_content = f.read()
                
                # Upload to Supabase Storage
                user_path = self._get_user_path(username)
                
                response = requests.post(
                    f"{self.supabase_url}/storage/v1/object/{self.bucket_name}/{user_path}",
                    data=file_content,
                    headers={
                        **self.headers,
                        'Content-Type': 'application/json'
                    }
                )
                
                if response.status_code == 200:
                    logger.info(f"✅ Session saved for {username}")
                    return True
                else:
                    logger.error(f"❌ Failed to save session: {response.status_code} - {response.text}")
                    return False
                    
            finally:
                # Clean up temp file
                if os.path.exists(temp_file_path):
                    os.unlink(temp_file_path)
                    
        except Exception as e:
            logger.error(f"❌ Error saving session for {username}: {e}")
            return False
    
    def load_session_from_supabase(self, username: str) -> Optional[Dict[str, Any]]:
        """Load instagrapi session from Supabase Storage"""
        try:
            logger.info(f"📂 Loading session for username: {username}")
            
            user_path = self._get_user_path(username)
            
            # Download from Supabase Storage
            response = requests.get(
                f"{self.supabase_url}/storage/v1/object/{self.bucket_name}/{user_path}",
                headers=self.headers
            )
            
            if response.status_code == 200:
                # Parse the settings
                settings = response.json()
                logger.info(f"✅ Session loaded for {username}")
                return settings
            elif response.status_code == 404:
                logger.info(f"📂 No session found for {username}")
                return None
            else:
                logger.error(f"❌ Failed to load session: {response.status_code} - {response.text}")
                return None
                
        except Exception as e:
            logger.error(f"❌ Error loading session for {username}: {e}")
            return None
    
    def session_exists_in_supabase(self, username: str) -> bool:
        """Check if a session exists for the username"""
        try:
            user_path = self._get_user_path(username)
            
            response = requests.head(
                f"{self.supabase_url}/storage/v1/object/{self.bucket_name}/{user_path}",
                headers=self.headers
            )
            
            return response.status_code == 200
            
        except Exception as e:
            logger.error(f"❌ Error checking session existence for {username}: {e}")
            return False
    
    def delete_session_from_supabase(self, username: str) -> bool:
        """Delete session from Supabase Storage"""
        try:
            logger.info(f"🗑️ Deleting session for username: {username}")
            
            user_path = self._get_user_path(username)
            
            response = requests.delete(
                f"{self.supabase_url}/storage/v1/object/{self.bucket_name}/{user_path}",
                headers=self.headers
            )
            
            if response.status_code == 200:
                logger.info(f"✅ Session deleted for {username}")
                return True
            elif response.status_code == 404:
                logger.info(f"📂 No session to delete for {username}")
                return True  # Consider it successful if nothing to delete
            else:
                logger.error(f"❌ Failed to delete session: {response.status_code} - {response.text}")
                return False
                
        except Exception as e:
            logger.error(f"❌ Error deleting session for {username}: {e}")
            return False
    
    def list_sessions_from_supabase(self) -> list:
        """List all sessions in the bucket"""
        try:
            response = requests.get(
                f"{self.supabase_url}/storage/v1/object/list/{self.bucket_name}",
                headers=self.headers
            )
            
            if response.status_code == 200:
                data = response.json()
                return data.get('data', [])
            else:
                logger.error(f"❌ Failed to list sessions: {response.status_code} - {response.text}")
                return []
                
        except Exception as e:
            logger.error(f"❌ Error listing sessions: {e}")
            return []

# Global instance
session_store = SupabaseSessionStore()
