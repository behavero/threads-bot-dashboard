#!/usr/bin/env python3
"""
Instagrapi Login Handler
Handles persistent session-based login for Threads accounts
"""

import os
import time
from typing import Dict, Any, Optional
from session_manager import session_manager

def login_with_session(username: str, password: str, verification_code: str = None) -> Dict[str, Any]:
    """
    Login to Threads using instagrapi with session management
    
    Args:
        username: Instagram username
        password: Instagram password
        verification_code: Optional 6-digit verification code
    
    Returns:
        Dict with login result and user info
    """
    try:
        from instagrapi import Client
        from instagrapi.exceptions import (
            ClientLoginRequired, 
            ClientError,
            ClientChallengeRequired,
            ClientCheckpointRequired,
            ClientTwoFactorRequired
        )
        
        print(f"🔐 Attempting login for {username}...")
        
        # Initialize client
        client = Client()
        client.delay_range = [1, 3]
        
        # Check if session exists and try to use it
        session_file = session_manager.get_session_path(username)
        
        if os.path.exists(session_file) and not verification_code:
            print(f"📁 Found existing session for {username}, attempting to reuse...")
            
            try:
                # Load existing session
                session_manager.load_instagrapi_session(username, client)
                
                # Validate session by getting user info
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
                # Delete invalid session
                session_manager.delete_session(username)
                # Continue with fresh login
        
        # If verification code is provided, handle challenge completion
        if verification_code:
            print(f"📧 Processing verification code for {username}")
            return _complete_challenge(username, verification_code, client)
        
        # Attempt fresh login
        print(f"🔐 Performing fresh login for {username}...")
        
        try:
            client.login(username, password)
            print(f"✅ Login successful for {username}")
            
            # Get user info
            user_info = client.user_info_by_username(username)
            
            # Save session
            session_manager.save_instagrapi_session(username, client)
            
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
            
    except ImportError as e:
        print(f"❌ Instagrapi not available: {e}")
        return {
            "success": False,
            "error": f"Instagrapi not available: {str(e)}"
        }, 500
    except Exception as e:
        print(f"❌ Error in login_with_session: {e}")
        return {
            "success": False,
            "error": str(e)
        }, 500

def _complete_challenge(username: str, code: str, client) -> Dict[str, Any]:
    """Complete challenge verification"""
    try:
        print(f"📧 Completing challenge for {username} with code: {code}")
        
        # Complete the challenge
        client.challenge_resolve(code)
        print(f"✅ Challenge completed for {username}")
        
        # Get user info
        user_info = client.user_info_by_username(username)
        
        # Save session
        session_manager.save_instagrapi_session(username, client)
        
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
        from instagrapi import Client
        
        client = Client()
        return session_manager.validate_session(username, client)
        
    except Exception as e:
        print(f"❌ Error validating session for {username}: {e}")
        return False

def cleanup_sessions(max_age_days: int = 30) -> int:
    """Clean up expired sessions"""
    return session_manager.cleanup_expired_sessions(max_age_days)
