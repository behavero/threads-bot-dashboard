#!/usr/bin/env python3
"""
ThreadsClient Service
Unified service for Threads/Instagram authentication with session management
"""

import os
import logging
import tempfile
import json
from typing import Optional, Dict, Any, Tuple
from instagrapi import Client
from instagrapi.exceptions import (
    ClientLoginRequired,
    ClientError,
    ClientChallengeRequired,
    ClientCheckpointRequired,
    ClientTwoFactorRequired
)

from .session_store_supabase import session_store

logger = logging.getLogger(__name__)

class ThreadsClientService:
    def __init__(self):
        self.session_store = session_store
        logger.info("✅ ThreadsClientService initialized")
    
    def get_client(self, username: str, password: str, otp_code: Optional[str] = None) -> Tuple[Client, Dict[str, Any]]:
        """
        Get a configured Threads client with session management
        
        Args:
            username: Instagram username
            password: Instagram password
            otp_code: Optional OTP code for challenges
            
        Returns:
            Tuple of (Client, result_dict)
            
        Raises:
            Exception with structured error info for challenges
        """
        try:
            logger.info(f"🔐 Getting client for username: {username}")
            
            # Try to load existing session first
            session_settings = self.session_store.load_session_from_supabase(username)
            
            if session_settings:
                logger.info(f"📂 Found existing session for {username}, attempting to reuse")
                client = self._create_client_with_session(session_settings)
                
                # Test if session is still valid
                if self._test_session_validity(client, username):
                    logger.info(f"✅ Session is valid for {username}")
                    return client, {
                        "success": True,
                        "session_reused": True,
                        "message": "Login successful (session reused)"
                    }
                else:
                    logger.info(f"⚠️ Session invalid for {username}, proceeding with fresh login")
            
            # Perform fresh login
            logger.info(f"🔐 Performing fresh login for {username}")
            client = self._create_client()
            
            # Handle login with potential challenges
            result = self._perform_login(client, username, password, otp_code)
            
            if result["success"]:
                # Save session after successful login
                if self.session_store.save_session_to_supabase(username, client):
                    logger.info(f"💾 Session saved for {username}")
                else:
                    logger.warning(f"⚠️ Failed to save session for {username}")
            
            return client, result
            
        except Exception as e:
            logger.error(f"❌ Error in get_client for {username}: {e}")
            raise
    
    def _create_client(self) -> Client:
        """Create a new instagrapi client"""
        client = Client()
        client.delay_range = [1, 3]
        return client
    
    def _create_client_with_session(self, session_settings: Dict[str, Any]) -> Client:
        """Create client and load session settings"""
        client = self._create_client()
        client.set_settings(session_settings)
        return client
    
    def _test_session_validity(self, client: Client, username: str) -> bool:
        """Test if the session is still valid"""
        try:
            # Try to get user info to test session
            user_info = client.user_info_by_username(username)
            return user_info is not None
        except Exception as e:
            logger.warning(f"⚠️ Session validation failed for {username}: {e}")
            return False
    
    def _perform_login(self, client: Client, username: str, password: str, otp_code: Optional[str] = None) -> Dict[str, Any]:
        """Perform login with challenge handling"""
        try:
            if otp_code:
                logger.info(f"📧 Processing OTP code for {username}")
                # Handle challenge completion
                client.challenge_resolve(otp_code)
                logger.info(f"✅ Challenge completed for {username}")
                
                return {
                    "success": True,
                    "session_reused": False,
                    "message": "Login successful (challenge completed)"
                }
            else:
                # Perform initial login
                client.login(username, password)
                logger.info(f"✅ Login successful for {username}")
                
                return {
                    "success": True,
                    "session_reused": False,
                    "message": "Login successful"
                }
                
        except ClientChallengeRequired as e:
            logger.info(f"📧 Challenge required for {username}: {e}")
            return {
                "success": False,
                "needs_code": True,
                "type": "email",  # Default to email
                "message": "Verification code required",
                "error": "Please check your email for a 6-digit verification code"
            }
            
        except ClientTwoFactorRequired as e:
            logger.info(f"🔐 Two-factor authentication required for {username}: {e}")
            return {
                "success": False,
                "needs_code": True,
                "type": "totp",
                "message": "Two-factor authentication required",
                "error": "Please enter your 2FA code"
            }
            
        except ClientCheckpointRequired as e:
            logger.info(f"🛡️ Checkpoint required for {username}: {e}")
            return {
                "success": False,
                "needs_code": False,
                "message": "Account checkpoint required",
                "error": "Account needs manual verification"
            }
            
        except ClientLoginRequired as e:
            logger.info(f"❌ Login failed for {username}: {e}")
            return {
                "success": False,
                "needs_code": False,
                "message": "Login failed",
                "error": "Invalid username or password"
            }
            
        except Exception as e:
            error_str = str(e)
            if "ForwardRef._evaluate()" in error_str or "recursive_guard" in error_str:
                logger.error(f"❌ ForwardRef._evaluate() error during login: {error_str}")
                return {
                    "success": False,
                    "needs_code": False,
                    "message": "Pydantic compatibility error",
                    "error": "System compatibility issue. Please contact support."
                }
            else:
                logger.error(f"❌ Unexpected login error for {username}: {e}")
                return {
                    "success": False,
                    "needs_code": False,
                    "message": "Login error",
                    "error": str(e)
                }
    
    def validate_session(self, username: str) -> bool:
        """Validate if a session exists and is valid"""
        try:
            session_settings = self.session_store.load_session_from_supabase(username)
            if not session_settings:
                return False
            
            client = self._create_client_with_session(session_settings)
            return self._test_session_validity(client, username)
            
        except Exception as e:
            logger.error(f"❌ Error validating session for {username}: {e}")
            return False
    
    def delete_session(self, username: str) -> bool:
        """Delete session for a username"""
        try:
            return self.session_store.delete_session_from_supabase(username)
        except Exception as e:
            logger.error(f"❌ Error deleting session for {username}: {e}")
            return False

# Global instance
threads_client_service = ThreadsClientService()
