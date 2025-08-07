#!/usr/bin/env python3
"""
Session Manager for Threads API
Handles secure session storage and retrieval
"""

import os
import json
import time
from typing import Optional, Dict, Any
from datetime import datetime
import tempfile

class SessionManager:
    """Manages Threads API sessions securely"""
    
    def __init__(self, sessions_dir: str = None):
        self.sessions_dir = sessions_dir or os.path.join(os.getcwd(), 'server', 'sessions')
        self._ensure_sessions_dir()
    
    def _ensure_sessions_dir(self):
        """Ensure sessions directory exists"""
        if not os.path.exists(self.sessions_dir):
            os.makedirs(self.sessions_dir, exist_ok=True)
            print(f"✅ Created sessions directory: {self.sessions_dir}")
    
    def get_session_path(self, username: str) -> str:
        """Get session file path for username"""
        safe_username = username.replace('/', '_').replace('\\', '_')
        return os.path.join(self.sessions_dir, f"{safe_username}.json")
    
    def save_session(self, username: str, session_data: Dict[str, Any]) -> bool:
        """Save session data to file"""
        try:
            session_path = self.get_session_path(username)
            
            # Add metadata
            session_with_meta = {
                "username": username,
                "session_data": session_data,
                "created_at": datetime.now().isoformat(),
                "last_used": datetime.now().isoformat()
            }
            
            # Save to temporary file first, then move (atomic operation)
            with tempfile.NamedTemporaryFile(mode='w', delete=False, dir=self.sessions_dir) as temp_file:
                json.dump(session_with_meta, temp_file, indent=2)
                temp_path = temp_file.name
            
            # Move to final location
            os.replace(temp_path, session_path)
            
            print(f"✅ Session saved for {username}")
            return True
            
        except Exception as e:
            print(f"❌ Failed to save session for {username}: {e}")
            return False
    
    def load_session(self, username: str) -> Optional[Dict[str, Any]]:
        """Load session data from file"""
        try:
            session_path = self.get_session_path(username)
            
            if not os.path.exists(session_path):
                print(f"📁 No session file found for {username}")
                return None
            
            with open(session_path, 'r') as f:
                session_data = json.load(f)
            
            # Update last_used timestamp
            session_data["last_used"] = datetime.now().isoformat()
            self.save_session(username, session_data["session_data"])
            
            print(f"✅ Session loaded for {username}")
            return session_data["session_data"]
            
        except Exception as e:
            print(f"❌ Failed to load session for {username}: {e}")
            return None
    
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
    
    def session_exists(self, username: str) -> bool:
        """Check if session file exists"""
        session_path = self.get_session_path(username)
        return os.path.exists(session_path)
    
    def get_session_info(self, username: str) -> Optional[Dict[str, Any]]:
        """Get session metadata without loading full session"""
        try:
            session_path = self.get_session_path(username)
            if not os.path.exists(session_path):
                return None
            
            with open(session_path, 'r') as f:
                session_data = json.load(f)
            
            return {
                "username": session_data.get("username"),
                "created_at": session_data.get("created_at"),
                "last_used": session_data.get("last_used"),
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

# Global session manager instance
session_manager = SessionManager()
