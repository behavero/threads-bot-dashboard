#!/usr/bin/env python3
"""
Login Manager for Threads Accounts
Handles login with session restoration and saving
"""

from session_store import load_session_from_supabase, save_session_to_supabase, session_exists_in_supabase
from instagrapi import Client
from instagrapi.exceptions import (
    ClientLoginRequired, 
    ClientError,
    ClientChallengeRequired,
    ClientCheckpointRequired,
    ClientTwoFactorRequired
)
from typing import Dict, Any, Optional
import time

def login_or_restore_session(username: str, password: str, verification_code: str = None) -> Dict[str, Any]:
    """
    Login to Threads with session restoration
    
    Args:
        username: Instagram username
        password: Instagram password
        verification_code: Optional 6-digit verification code
    
    Returns:
        Dict with login result and user info
    """
    try:
        print(f"🔐 Attempting login for {username}...")
        
        # If verification code is provided, handle challenge completion
        if verification_code:
            print(f"📧 Processing verification code for {username}")
            return _complete_challenge_with_session(username, verification_code)
        
        # Try to load existing session first
        client = load_session_from_supabase(username)
        
        if client:
            print(f"📁 Found existing session for {username}, attempting to reuse...")
            
            try:
                # Try to validate session by getting user info
                user_info = client.user_info_by_username(username)
                if user_info:
                    print(f"✅ Session is valid for {username}")
                    return {
                        "success": True,
                        "message": "Login successful (session reused)",
                        "user_info": {
                            "username": user_info.username,
                            "followers": user_info.follower_count,
                            "posts": user_info.media_count,
                            "full_name": user_info.full_name,
                            "biography": user_info.biography,
                            "is_private": user_info.is_private,
                            "is_verified": user_info.is_verified
                        },
                        "session_reused": True,
                        "api_used": "instagrapi"
                    }
            except Exception as e:
                print(f"⚠️ Session invalid for {username}: {e}")
                # Continue with fresh login
        
        # Perform fresh login
        print(f"🔐 Performing fresh login for {username}...")
        client = Client()
        client.delay_range = [1, 3]
        
        try:
            client.login(username, password)
            print(f"✅ Login successful for {username}")
            
            # Get user info
            user_info = client.user_info_by_username(username)
            
            # Save session
            save_session_to_supabase(username, client)
            
            return {
                "success": True,
                "message": "Login successful",
                "user_info": {
                    "username": user_info.username,
                    "followers": user_info.follower_count,
                    "posts": user_info.media_count,
                    "full_name": user_info.full_name,
                    "biography": user_info.biography,
                    "is_private": user_info.is_private,
                    "is_verified": user_info.is_verified
                },
                "session_reused": False,
                "api_used": "instagrapi"
            }
            
        except ClientChallengeRequired as e:
            print(f"📧 Challenge required for {username}: {e}")
            
            # Store challenge context for verification
            challenge_context = {
                "username": username,
                "password": password,
                "client": client,
                "challenge_type": "email",  # Default to email
                "created_at": time.time()
            }
            
            return {
                "success": False,
                "status": "challenge_required",
                "message": "Verification code required",
                "error": "Please check your email for a 6-digit verification code",
                "challenge_context": challenge_context,
                "requires_verification": True,
                "verification_type": "email",
                "api_used": "instagrapi"
            }, 401
            
        except ClientCheckpointRequired as e:
            print(f"🛡️ Checkpoint required for {username}: {e}")
            return {
                "success": False,
                "message": "Account checkpoint required",
                "error": "Account needs manual verification",
                "requires_checkpoint": True,
                "api_used": "instagrapi"
            }, 401
            
        except ClientTwoFactorRequired as e:
            print(f"🔐 Two-factor authentication required for {username}: {e}")
            return {
                "success": False,
                "message": "Two-factor authentication required",
                "error": "Please complete 2FA verification",
                "requires_2fa": True,
                "api_used": "instagrapi"
            }, 401
            
        except ClientLoginRequired as e:
            print(f"❌ Login failed for {username}: {e}")
            return {
                "success": False,
                "message": "Login failed",
                "error": "Invalid username or password",
                "api_used": "instagrapi"
            }, 401
            
        except Exception as e:
            print(f"❌ Unexpected login error for {username}: {e}")
            return {
                "success": False,
                "message": "Login error",
                "error": str(e),
                "api_used": "instagrapi"
            }, 500
            
    except Exception as e:
        print(f"❌ Error in login_or_restore_session: {e}")
        return {
            "success": False,
            "error": str(e)
        }, 500

def _complete_challenge_with_session(username: str, code: str) -> Dict[str, Any]:
    """Complete challenge verification and save session"""
    try:
        print(f"📧 Completing challenge for {username} with code: {code}")
        
        # Create new client for challenge completion
        client = Client()
        client.delay_range = [1, 3]
        
        # Complete the challenge
        client.challenge_resolve(code)
        print(f"✅ Challenge completed for {username}")
        
        # Get user info
        user_info = client.user_info_by_username(username)
        
        # Save session
        save_session_to_supabase(username, client)
        
        return {
            "success": True,
            "message": "Verification successful",
            "user_info": {
                "username": user_info.username,
                "followers": user_info.follower_count,
                "posts": user_info.media_count,
                "full_name": user_info.full_name,
                "biography": user_info.biography,
                "is_private": user_info.is_private,
                "is_verified": user_info.is_verified
            },
            "api_used": "instagrapi"
        }
        
    except Exception as e:
        print(f"❌ Challenge completion failed: {e}")
        return {
            "success": False,
            "message": "Verification failed",
            "error": f"Invalid verification code: {str(e)}",
            "api_used": "instagrapi"
        }, 400

def validate_session(username: str) -> bool:
    """Validate if a session exists and is working"""
    try:
        client = load_session_from_supabase(username)
        if not client:
            return False
        
        # Try to get user info to validate session
        try:
            user_info = client.user_info_by_username(username)
            if user_info:
                print(f"✅ Session validated for {username}")
                return True
        except Exception as e:
            print(f"❌ Session validation failed for {username}: {e}")
            # Delete invalid session
            from session_store import delete_session_from_supabase
            delete_session_from_supabase(username)
            return False
        
        return False
        
    except Exception as e:
        print(f"❌ Error validating session for {username}: {e}")
        return False
