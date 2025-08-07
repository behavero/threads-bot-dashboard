#!/usr/bin/env python3
"""
Session Manager for Threads API
Handles secure session storage and retrieval with instagrapi compatibility
"""

import os
import json
import time
import shutil
from typing import Optional, Dict, Any
from datetime import datetime, timedelta
import tempfile

class SessionManager:
    """Manages Threads API sessions securely with instagrapi compatibility"""
    
    def __init__(self, sessions_dir: str = None):
        # Use root sessions directory for instagrapi compatibility
        self.sessions_dir = sessions_dir or os.path.join(os.getcwd(), 'sessions')
        self._ensure_sessions_dir()
    
    def _ensure_sessions_dir(self):
        """Ensure sessions directory exists"""
        if not os.path.exists(self.sessions_dir):
            os.makedirs(self.sessions_dir, exist_ok=True)
            print(f"✅ Created sessions directory: {self.sessions_dir}")
    
    def get_session_path(self, username: str) -> str:
        """Get session file path for username (instagrapi format)"""
        safe_username = username.replace('/', '_').replace('\\', '_')
        return os.path.join(self.sessions_dir, f"{safe_username}.json")
    
    def save_instagrapi_session(self, username: str, client) -> bool:
        """Save instagrapi session to file"""
        try:
            session_path = self.get_session_path(username)
            
            # Use instagrapi's built-in session saving
            client.dump_settings(session_path)
            
            print(f"✅ Instagrapi session saved for {username}")
            return True
            
        except Exception as e:
            print(f"❌ Failed to save instagrapi session for {username}: {e}")
            return False
    
    def load_instagrapi_session(self, username: str, client) -> bool:
        """Load instagrapi session from file"""
        try:
            session_path = self.get_session_path(username)
            
            if not os.path.exists(session_path):
                print(f"📁 No session file found for {username}")
                return False
            
            # Use instagrapi's built-in session loading
            client.load_settings(session_path)
            
            print(f"✅ Instagrapi session loaded for {username}")
            return True
            
        except Exception as e:
            print(f"❌ Failed to load instagrapi session for {username}: {e}")
            return False
    
    def session_exists(self, username: str) -> bool:
        """Check if session file exists"""
        session_path = self.get_session_path(username)
        return os.path.exists(session_path)
    
    def delete_session(self, username: str) -> bool:
        """Delete session file"""
        try:
            session_path = self.get_session_path(username)
            if os.path.exists(session_path):
                os.remove(session_path)
                print(f"✅ Session deleted for {username}")
                return True
            return False
        except Exception as e:
            print(f"❌ Failed to delete session for {username}: {e}")
            return False
    
    def get_session_info(self, username: str) -> Optional[Dict[str, Any]]:
        """Get session metadata"""
        try:
            session_path = self.get_session_path(username)
            if not os.path.exists(session_path):
                return None
            
            # Get file stats
            stat = os.stat(session_path)
            
            return {
                "username": username,
                "created_at": datetime.fromtimestamp(stat.st_ctime).isoformat(),
                "modified_at": datetime.fromtimestamp(stat.st_mtime).isoformat(),
                "size": stat.st_size,
                "exists": True
            }
            
        except Exception as e:
            print(f"❌ Failed to get session info for {username}: {e}")
            return None
    
    def list_sessions(self) -> list:
        """List all available sessions"""
        sessions = []
        try:
            for filename in os.listdir(self.sessions_dir):
                if filename.endswith('.json'):
                    username = filename[:-5]  # Remove .json
                    session_info = self.get_session_info(username)
                    if session_info:
                        sessions.append(session_info)
        except Exception as e:
            print(f"❌ Failed to list sessions: {e}")
        
        return sessions
    
    def cleanup_expired_sessions(self, max_age_days: int = 30) -> int:
        """Clean up sessions older than max_age_days"""
        try:
            cleaned_count = 0
            cutoff_time = time.time() - (max_age_days * 24 * 60 * 60)
            
            for filename in os.listdir(self.sessions_dir):
                if filename.endswith('.json'):
                    file_path = os.path.join(self.sessions_dir, filename)
                    file_time = os.path.getmtime(file_path)
                    
                    if file_time < cutoff_time:
                        try:
                            os.remove(file_path)
                            username = filename[:-5]
                            print(f"🧹 Cleaned up expired session for {username}")
                            cleaned_count += 1
                        except Exception as e:
                            print(f"❌ Failed to clean up {filename}: {e}")
            
            print(f"✅ Cleaned up {cleaned_count} expired sessions")
            return cleaned_count
            
        except Exception as e:
            print(f"❌ Failed to cleanup sessions: {e}")
            return 0
    
    def validate_session(self, username: str, client) -> bool:
        """Validate if a session is still working"""
        try:
            if not self.session_exists(username):
                return False
            
            # Try to load and use the session
            if self.load_instagrapi_session(username, client):
                # Try to get user info to validate session
                try:
                    user_info = client.user_info_by_username(username)
                    if user_info:
                        print(f"✅ Session validated for {username}")
                        return True
                except Exception as e:
                    print(f"❌ Session validation failed for {username}: {e}")
                    # Delete invalid session
                    self.delete_session(username)
                    return False
            
            return False
            
        except Exception as e:
            print(f"❌ Error validating session for {username}: {e}")
            return False

# Global session manager instance
session_manager = SessionManager()
