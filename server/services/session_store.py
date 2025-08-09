#!/usr/bin/env python3
"""
Session Store Service
Handles session storage and retrieval using Supabase Storage
"""

import os
import json
import logging
import requests
from typing import Optional, Dict, Any

logger = logging.getLogger(__name__)

class SessionStore:
    def __init__(self):
        self.supabase_url = os.getenv('SUPABASE_URL')
        self.supabase_key = os.getenv('SUPABASE_SERVICE_ROLE_KEY')
        self.bucket_name = 'sessions'
        
        if not self.supabase_url or not self.supabase_key:
            raise ValueError("Missing Supabase credentials for session storage")
        
        self.headers = {
            'Authorization': f'Bearer {self.supabase_key}',
            'Content-Type': 'application/json'
        }
        
        logger.info("✅ SessionStore initialized")
    
    def exists(self, username: str) -> bool:
        """Check if session exists for username"""
        try:
            file_path = f"{username}.json"
            
            response = requests.get(
                f"{self.supabase_url}/storage/v1/object/info/{self.bucket_name}/{file_path}",
                headers=self.headers
            )
            
            exists = response.status_code == 200
            logger.info(f"🔍 Session exists for {username}: {exists}")
            return exists
            
        except Exception as e:
            logger.error(f"❌ Error checking session existence for {username}: {e}")
            return False
    
    def load_session(self, username: str) -> Optional[Dict[Any, Any]]:
        """Load session data for username"""
        try:
            file_path = f"{username}.json"
            
            response = requests.get(
                f"{self.supabase_url}/storage/v1/object/{self.bucket_name}/{file_path}",
                headers=self.headers
            )
            
            if response.status_code == 200:
                session_data = response.json()
                logger.info(f"✅ Loaded session for {username}")
                return session_data
            elif response.status_code == 404:
                logger.info(f"📂 No session found for {username}")
                return None
            else:
                logger.error(f"❌ Failed to load session for {username}: {response.status_code}")
                return None
                
        except Exception as e:
            logger.error(f"❌ Error loading session for {username}: {e}")
            return None
    
    def save_session(self, username: str, session_data: Dict[Any, Any]) -> bool:
        """Save session data for username"""
        try:
            file_path = f"{username}.json"
            
            # Convert session data to JSON
            session_json = json.dumps(session_data, indent=2)
            
            # Upload to Supabase Storage
            files = {
                'file': (file_path, session_json, 'application/json')
            }
            
            headers_upload = {
                'Authorization': f'Bearer {self.supabase_key}'
            }
            
            response = requests.post(
                f"{self.supabase_url}/storage/v1/object/{self.bucket_name}/{file_path}",
                files=files,
                headers=headers_upload
            )
            
            if response.status_code in [200, 201]:
                logger.info(f"✅ Saved session for {username}")
                return True
            else:
                # Try updating if it already exists
                response = requests.put(
                    f"{self.supabase_url}/storage/v1/object/{self.bucket_name}/{file_path}",
                    files=files,
                    headers=headers_upload
                )
                
                if response.status_code == 200:
                    logger.info(f"✅ Updated session for {username}")
                    return True
                else:
                    logger.error(f"❌ Failed to save session for {username}: {response.status_code}")
                    return False
                
        except Exception as e:
            logger.error(f"❌ Error saving session for {username}: {e}")
            return False
    
    def delete_session(self, username: str) -> bool:
        """Delete session for username"""
        try:
            file_path = f"{username}.json"
            
            response = requests.delete(
                f"{self.supabase_url}/storage/v1/object/{self.bucket_name}/{file_path}",
                headers=self.headers
            )
            
            if response.status_code in [200, 204]:
                logger.info(f"✅ Deleted session for {username}")
                return True
            else:
                logger.error(f"❌ Failed to delete session for {username}: {response.status_code}")
                return False
                
        except Exception as e:
            logger.error(f"❌ Error deleting session for {username}: {e}")
            return False
    
    def list_sessions(self) -> list:
        """List all available sessions"""
        try:
            response = requests.get(
                f"{self.supabase_url}/storage/v1/object/list/{self.bucket_name}",
                headers=self.headers
            )
            
            if response.status_code == 200:
                objects = response.json()
                sessions = [obj['name'].replace('.json', '') for obj in objects if obj['name'].endswith('.json')]
                logger.info(f"📂 Found {len(sessions)} sessions")
                return sessions
            else:
                logger.error(f"❌ Failed to list sessions: {response.status_code}")
                return []
                
        except Exception as e:
            logger.error(f"❌ Error listing sessions: {e}")
            return []

# Global instance
session_store = SessionStore()
