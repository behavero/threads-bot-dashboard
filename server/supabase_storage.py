#!/usr/bin/env python3
"""
Supabase Storage Client for Session Management
Handles session storage in Supabase Storage instead of local files
"""

import os
import json
import tempfile
import base64
from typing import Optional, Dict, Any
from datetime import datetime
from supabase import create_client, Client

class SupabaseStorageManager:
    """Manages Threads API sessions in Supabase Storage"""
    
    def __init__(self):
        self.supabase_url = os.getenv("SUPABASE_URL")
        self.supabase_key = os.getenv("SUPABASE_SERVICE_ROLE_KEY")
        self.session_bucket = "sessions"
        
        if not self.supabase_url or not self.supabase_key:
            raise ValueError("SUPABASE_URL and SUPABASE_SERVICE_ROLE_KEY must be set")
        
        self.supabase: Client = create_client(self.supabase_url, self.supabase_key)
        self._ensure_bucket_exists()
    
    def _ensure_bucket_exists(self):
        """Ensure the sessions bucket exists in Supabase Storage"""
        try:
            # List buckets to check if sessions bucket exists
            buckets = self.supabase.storage.list_buckets()
            bucket_names = [bucket.name for bucket in buckets]
            
            if self.session_bucket not in bucket_names:
                print(f"📦 Creating sessions bucket in Supabase Storage...")
                # Create bucket with public access for session files
                self.supabase.storage.create_bucket(
                    self.session_bucket,
                    public=True,
                    file_size_limit=5242880,  # 5MB limit
                    allowed_mime_types=['application/json']
                )
                print(f"✅ Created sessions bucket: {self.session_bucket}")
            else:
                print(f"✅ Sessions bucket exists: {self.session_bucket}")
                
        except Exception as e:
            print(f"⚠️ Could not verify bucket existence: {e}")
            print("📝 Please ensure 'sessions' bucket exists in Supabase Storage dashboard")
    
    def _get_session_filename(self, username: str) -> str:
        """Get safe filename for session storage"""
        safe_username = username.replace('/', '_').replace('\\', '_').replace(' ', '_')
        return f"{safe_username}.json"
    
    def save_instagrapi_session(self, username: str, client) -> bool:
        """Save instagrapi session to Supabase Storage"""
        try:
            # Create temporary file for instagrapi to dump settings
            with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as temp_file:
                temp_path = temp_file.name
            
            # Use instagrapi's built-in session saving to temp file
            client.dump_settings(temp_path)
            
            # Read the session data
            with open(temp_path, 'r') as f:
                session_data = f.read()
            
            # Clean up temp file
            os.unlink(temp_path)
            
            # Upload to Supabase Storage
            filename = self._get_session_filename(username)
            
            # Add metadata to session data
            session_with_meta = {
                "username": username,
                "session_data": session_data,
                "created_at": datetime.now().isoformat(),
                "last_used": datetime.now().isoformat()
            }
            
            # Convert to JSON string
            session_json = json.dumps(session_with_meta, indent=2)
            
            # Upload to Supabase Storage
            result = self.supabase.storage.from_(self.session_bucket).upload(
                path=filename,
                file=session_json.encode('utf-8'),
                file_options={"content-type": "application/json"}
            )
            
            print(f"✅ Session saved to Supabase Storage for {username}")
            return True
            
        except Exception as e:
            print(f"❌ Failed to save session to Supabase Storage for {username}: {e}")
            return False
    
    def load_instagrapi_session(self, username: str, client) -> bool:
        """Load instagrapi session from Supabase Storage"""
        try:
            filename = self._get_session_filename(username)
            
            # Download from Supabase Storage
            result = self.supabase.storage.from_(self.session_bucket).download(filename)
            
            if not result:
                print(f"📁 No session file found in Supabase Storage for {username}")
                return False
            
            # Parse session data
            session_json = result.decode('utf-8')
            session_data = json.loads(session_json)
            
            # Extract the actual session data
            actual_session_data = session_data.get("session_data", session_json)
            
            # Create temporary file for instagrapi to load settings
            with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as temp_file:
                temp_path = temp_file.name
                temp_file.write(actual_session_data)
            
            # Use instagrapi's built-in session loading
            client.load_settings(temp_path)
            
            # Clean up temp file
            os.unlink(temp_path)
            
            # Update last_used timestamp
            session_data["last_used"] = datetime.now().isoformat()
            self._update_session_metadata(username, session_data)
            
            print(f"✅ Session loaded from Supabase Storage for {username}")
            return True
            
        except Exception as e:
            print(f"❌ Failed to load session from Supabase Storage for {username}: {e}")
            return False
    
    def _update_session_metadata(self, username: str, session_data: Dict[str, Any]):
        """Update session metadata in Supabase Storage"""
        try:
            filename = self._get_session_filename(username)
            session_json = json.dumps(session_data, indent=2)
            
            self.supabase.storage.from_(self.session_bucket).update(
                path=filename,
                file=session_json.encode('utf-8'),
                file_options={"content-type": "application/json"}
            )
        except Exception as e:
            print(f"⚠️ Failed to update session metadata for {username}: {e}")
    
    def session_exists(self, username: str) -> bool:
        """Check if session file exists in Supabase Storage"""
        try:
            filename = self._get_session_filename(username)
            files = self.supabase.storage.from_(self.session_bucket).list()
            return any(file.name == filename for file in files)
        except Exception as e:
            print(f"❌ Error checking session existence for {username}: {e}")
            return False
    
    def delete_session(self, username: str) -> bool:
        """Delete session file from Supabase Storage"""
        try:
            filename = self._get_session_filename(username)
            self.supabase.storage.from_(self.session_bucket).remove([filename])
            print(f"✅ Session deleted from Supabase Storage for {username}")
            return True
        except Exception as e:
            print(f"❌ Failed to delete session from Supabase Storage for {username}: {e}")
            return False
    
    def get_session_info(self, username: str) -> Optional[Dict[str, Any]]:
        """Get session metadata from Supabase Storage"""
        try:
            filename = self._get_session_filename(username)
            
            # Download session file
            result = self.supabase.storage.from_(self.session_bucket).download(filename)
            
            if not result:
                return None
            
            session_data = json.loads(result.decode('utf-8'))
            
            return {
                "username": session_data.get("username"),
                "created_at": session_data.get("created_at"),
                "last_used": session_data.get("last_used"),
                "exists": True,
                "size": len(result)
            }
            
        except Exception as e:
            print(f"❌ Failed to get session info for {username}: {e}")
            return None
    
    def list_sessions(self) -> list:
        """List all available sessions in Supabase Storage"""
        sessions = []
        try:
            files = self.supabase.storage.from_(self.session_bucket).list()
            
            for file in files:
                if file.name.endswith('.json'):
                    username = file.name[:-5]  # Remove .json
                    session_info = self.get_session_info(username)
                    if session_info:
                        sessions.append(session_info)
                        
        except Exception as e:
            print(f"❌ Failed to list sessions: {e}")
        
        return sessions
    
    def cleanup_expired_sessions(self, max_age_days: int = 30) -> int:
        """Clean up expired sessions from Supabase Storage"""
        try:
            cleaned_count = 0
            cutoff_time = datetime.now().timestamp() - (max_age_days * 24 * 60 * 60)
            
            files = self.supabase.storage.from_(self.session_bucket).list()
            
            for file in files:
                if file.name.endswith('.json'):
                    try:
                        # Get session info to check age
                        username = file.name[:-5]
                        session_info = self.get_session_info(username)
                        
                        if session_info and session_info.get("created_at"):
                            created_time = datetime.fromisoformat(session_info["created_at"]).timestamp()
                            
                            if created_time < cutoff_time:
                                self.delete_session(username)
                                print(f"🧹 Cleaned up expired session for {username}")
                                cleaned_count += 1
                                
                    except Exception as e:
                        print(f"❌ Failed to clean up {file.name}: {e}")
            
            print(f"✅ Cleaned up {cleaned_count} expired sessions from Supabase Storage")
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

# Global Supabase Storage manager instance
supabase_storage_manager = SupabaseStorageManager()
