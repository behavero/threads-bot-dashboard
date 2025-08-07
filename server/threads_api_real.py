#!/usr/bin/env python3
"""
Real Threads API Implementation
Uses threads-api library with async support
"""

import asyncio
import time
import random
from typing import Optional, Dict, Any
from datetime import datetime

try:
    from threads_api.src.threads_api import ThreadsAPI
    print("✅ Real Threads API imported successfully")
except ImportError as e:
    print(f"❌ Failed to import Threads API: {e}")
    print("💡 Install with: pip install threads-api==1.2.0")
    ThreadsAPI = None

class RealThreadsAPI:
    """Real Threads API implementation using threads-api library"""
    
    def __init__(self, use_instagrapi: bool = True):
        self.api = None
        self.logged_in = False
        self.username = None
        self.user_id = None
        self.use_instagrapi = use_instagrapi
        self.loop = None
        
        if ThreadsAPI is None:
            raise ImportError("Threads API not available. Install with: pip install threads-api==1.2.0")
    
    async def _ensure_api(self):
        """Ensure API is initialized in async context"""
        if self.api is None:
            self.api = ThreadsAPI()
            print(f"✅ ThreadsAPI initialized for {self.username}")
    
    async def login(self, username: str, password: str) -> bool:
        """Login to Threads using Instagram credentials"""
        try:
            print(f"🔐 Attempting login for {username}...")
            
            # Initialize Threads API in async context
            await self._ensure_api()
            self.username = username
            
            # Login with Instagram credentials
            login_result = await self.api.login(username, password)
            
            if login_result:
                self.logged_in = True
                
                # Get user info
                try:
                    me = await self.api.get_user_profile(username)
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
            error_msg = str(e)
            print(f"❌ Login error for {username}: {error_msg}")
            
            # Handle specific Instagram security errors
            if "You've Been Logged Out" in error_msg or "login_required" in error_msg:
                print(f"🔒 Account security check required for {username}")
                return False
            elif "ChallengeChoice.EMAIL" in error_msg or "Enter code" in error_msg:
                print(f"📧 Email verification required for {username}")
                return False
            elif "checkpoint" in error_msg.lower():
                print(f"🛡️ Account checkpoint required for {username}")
                return False
            elif "2FA" in error_msg or "two-factor" in error_msg.lower():
                print(f"🔐 Two-factor authentication required for {username}")
                return False
            else:
                print(f"❌ Unknown login error for {username}")
                return False
    
    async def get_me(self) -> Optional[Dict[str, Any]]:
        """Get current user information"""
        if not self.logged_in or not self.api:
            print("❌ Not logged in")
            return None
        
        try:
            await self._ensure_api()
            me = await self.api.get_user_profile(self.username)
            return me
        except Exception as e:
            print(f"❌ Error getting user info: {e}")
            return None
    
    async def post(self, text: str) -> bool:
        """Post text content to Threads"""
        if not self.logged_in or not self.api:
            print("❌ Not logged in")
            return False
        
        try:
            print(f"📝 Posting text: {text[:50]}...")
            
            await self._ensure_api()
            # Post text content
            result = await self.api.post(text)
            
            if result:
                print(f"✅ Text post successful for {self.username}")
                return True
            else:
                print(f"❌ Text post failed for {self.username}")
                return False
                
        except Exception as e:
            print(f"❌ Error posting text: {e}")
            return False
    
    async def post_with_image(self, text: str, image_url: str) -> bool:
        """Post image content to Threads"""
        if not self.logged_in or not self.api:
            print("❌ Not logged in")
            return False
        
        try:
            print(f"📸 Posting with image: {text[:50]}... | {image_url}")
            
            # For now, fall back to text-only post since image posting might need different approach
            # TODO: Implement proper image posting when threads-api supports it
            print(f"⚠️ Image posting not yet implemented, posting text only")
            return await self.post(text)
            
        except Exception as e:
            print(f"❌ Error posting with image: {e}")
            return False
    
    async def logout(self):
        """Logout from Threads"""
        if self.api:
            try:
                await self.api.close_gracefully()
                print(f"✅ Logged out {self.username}")
            except Exception as e:
                print(f"⚠️ Logout error: {e}")
        
        self.logged_in = False
        self.username = None
        self.user_id = None
        self.api = None

# Global instance for testing
threads_api_instance = None

async def get_threads_api(use_instagrapi: bool = True) -> Optional[RealThreadsAPI]:
    """Get a Threads API instance"""
    global threads_api_instance
    
    if threads_api_instance is None:
        try:
            threads_api_instance = RealThreadsAPI(use_instagrapi=use_instagrapi)
        except ImportError as e:
            print(f"❌ Cannot create Threads API: {e}")
            return None
    
    return threads_api_instance
