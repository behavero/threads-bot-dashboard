#!/usr/bin/env python3
"""
Real Threads API Implementation
Uses threads-api library with instagrapi for authentication
"""

import time
import random
from typing import Optional, Dict, Any
from datetime import datetime

try:
    from threads import ThreadsAPI
    print("✅ Real Threads API imported successfully")
except ImportError as e:
    print(f"❌ Failed to import Threads API: {e}")
    print("💡 Install with: pip install threads-api==0.0.8")
    ThreadsAPI = None

class RealThreadsAPI:
    """Real Threads API implementation using threads-api library"""
    
    def __init__(self, use_instagrapi: bool = True):
        self.api = None
        self.logged_in = False
        self.username = None
        self.user_id = None
        self.use_instagrapi = use_instagrapi
        
        if ThreadsAPI is None:
            raise ImportError("Threads API not available. Install with: pip install threads-api==0.0.8")
    
    def login(self, username: str, password: str) -> bool:
        """Login to Threads using Instagram credentials"""
        try:
            print(f"🔐 Attempting login for {username}...")
            
            # Initialize Threads API with instagrapi
            self.api = ThreadsAPI(use_instagrapi=self.use_instagrapi)
            
            # Login with Instagram credentials
            login_result = self.api.login(username, password)
            
            if login_result:
                self.logged_in = True
                self.username = username
                
                # Get user info
                try:
                    me = self.api.get_me()
                    if me:
                        self.user_id = me.get('pk') or me.get('id')
                        print(f"✅ Successfully logged in as {username} (ID: {self.user_id})")
                    else:
                        print(f"✅ Logged in as {username} (no user info available)")
                except Exception as e:
                    print(f"⚠️ Logged in but couldn't get user info: {e}")
                
                return True
            else:
                print(f"❌ Login failed for {username}")
                return False
                
        except Exception as e:
            print(f"❌ Login error for {username}: {str(e)}")
            return False
    
    def get_me(self) -> Optional[Dict[str, Any]]:
        """Get current user information"""
        if not self.logged_in or not self.api:
            print("❌ Not logged in")
            return None
        
        try:
            me = self.api.get_me()
            return me
        except Exception as e:
            print(f"❌ Error getting user info: {e}")
            return None
    
    def post(self, text: str) -> bool:
        """Post text content to Threads"""
        if not self.logged_in or not self.api:
            print("❌ Not logged in")
            return False
        
        try:
            print(f"📝 Posting text: {text[:50]}...")
            
            # Post text content
            result = self.api.post(text)
            
            if result:
                print(f"✅ Text post successful for {self.username}")
                return True
            else:
                print(f"❌ Text post failed for {self.username}")
                return False
                
        except Exception as e:
            print(f"❌ Error posting text: {e}")
            return False
    
    def post_with_image(self, text: str, image_url: str) -> bool:
        """Post image content to Threads"""
        if not self.logged_in or not self.api:
            print("❌ Not logged in")
            return False
        
        try:
            print(f"📸 Posting with image: {text[:50]}... | {image_url}")
            
            # For now, fall back to text-only post since image posting might need different approach
            # TODO: Implement proper image posting when threads-api supports it
            print(f"⚠️ Image posting not yet implemented, posting text only")
            return self.post(text)
            
        except Exception as e:
            print(f"❌ Error posting with image: {e}")
            return False
    
    def logout(self):
        """Logout from Threads"""
        if self.api:
            try:
                self.api.logout()
                print(f"✅ Logged out {self.username}")
            except Exception as e:
                print(f"⚠️ Logout error: {e}")
        
        self.logged_in = False
        self.username = None
        self.user_id = None
        self.api = None

# Global instance for testing
threads_api_instance = None

def get_threads_api(use_instagrapi: bool = True) -> Optional[RealThreadsAPI]:
    """Get a Threads API instance"""
    global threads_api_instance
    
    if threads_api_instance is None:
        try:
            threads_api_instance = RealThreadsAPI(use_instagrapi=use_instagrapi)
        except ImportError as e:
            print(f"❌ Cannot create Threads API: {e}")
            return None
    
    return threads_api_instance
