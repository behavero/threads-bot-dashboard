#!/usr/bin/env python3
"""
Account Routes
Handles account login, verification, and management with proper JSON responses
"""

import os
import logging
from datetime import datetime
from flask import Blueprint, request, jsonify
from database import DatabaseManager
from services.threads_client import threads_client_service

logger = logging.getLogger(__name__)

accounts = Blueprint('accounts', __name__)

@accounts.route('/api/accounts/login', methods=['POST'])
def login_account():
    """Login to Threads account with session management"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({
                "ok": False,
                "error": "No JSON data provided"
            }), 400
        
        username = data.get('username')
        password = data.get('password')
        otp_code = data.get('otp_code')
        
        if not username or not password:
            return jsonify({
                "ok": False,
                "error": "Username and password are required"
            }), 400
        
        logger.info(f"🔐 Login attempt for username: {username}")
        
        # Get client with session management
        client, result = threads_client_service.get_client(username, password, otp_code)
        
        if result["success"]:
            # Get user info for account details
            try:
                user_info = client.user_info_by_username(username)
                account_data = {
                    "username": username,
                    "description": f"Connected account for {username}",
                    "status": "enabled",
                    "is_active": True,
                    "last_login": datetime.now().isoformat()
                }
                
                # Upsert account to database
                db = DatabaseManager()
                account_id = db.add_account(username, password, session_data=result)
                
                if account_id:
                    logger.info(f"✅ Account saved to database for {username}")
                    return jsonify({
                        "ok": True,
                        "account": {
                            "id": account_id,
                            "username": username,
                            "status": "enabled",
                            "last_login": account_data["last_login"],
                            "session_reused": result.get("session_reused", False)
                        },
                        "message": result["message"]
                    }), 200
                else:
                    logger.error(f"❌ Failed to save account to database for {username}")
                    return jsonify({
                        "ok": False,
                        "error": "Failed to save account"
                    }), 500
                    
            except Exception as e:
                logger.error(f"❌ Error getting user info for {username}: {e}")
                return jsonify({
                    "ok": False,
                    "error": "Failed to get account information"
                }), 500
        else:
            # Handle challenge or error
            if result.get("needs_code"):
                logger.info(f"📧 Challenge required for {username}: {result['type']}")
                return jsonify({
                    "ok": False,
                    "needs_code": True,
                    "type": result["type"],
                    "message": result["message"],
                    "error": result["error"]
                }), 401
            else:
                logger.error(f"❌ Login failed for {username}: {result['error']}")
                return jsonify({
                    "ok": False,
                    "error": result["error"]
                }), 401
                
    except Exception as e:
        logger.error(f"❌ Unexpected error in login_account: {e}")
        return jsonify({
            "ok": False,
            "error": "Internal server error"
        }), 500

@accounts.route('/api/accounts/verify', methods=['POST'])
def verify_account():
    """Verify account with OTP code"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({
                "ok": False,
                "error": "No JSON data provided"
            }), 400
        
        username = data.get('username')
        password = data.get('password')
        otp_code = data.get('otp_code')
        
        if not all([username, password, otp_code]):
            return jsonify({
                "ok": False,
                "error": "Username, password, and OTP code are required"
            }), 400
        
        logger.info(f"📧 Verification attempt for username: {username}")
        
        # Get client with OTP code
        client, result = threads_client_service.get_client(username, password, otp_code)
        
        if result["success"]:
            # Get user info for account details
            try:
                user_info = client.user_info_by_username(username)
                account_data = {
                    "username": username,
                    "description": f"Connected account for {username}",
                    "status": "enabled",
                    "is_active": True,
                    "last_login": datetime.now().isoformat()
                }
                
                # Upsert account to database
                db = DatabaseManager()
                account_id = db.add_account(username, password, session_data=result)
                
                if account_id:
                    logger.info(f"✅ Account verified and saved for {username}")
                    return jsonify({
                        "ok": True,
                        "account": {
                            "id": account_id,
                            "username": username,
                            "status": "enabled",
                            "last_login": account_data["last_login"]
                        },
                        "message": "Account verified successfully"
                    }), 200
                else:
                    logger.error(f"❌ Failed to save verified account for {username}")
                    return jsonify({
                        "ok": False,
                        "error": "Failed to save account"
                    }), 500
                    
            except Exception as e:
                logger.error(f"❌ Error getting user info for verified {username}: {e}")
                return jsonify({
                    "ok": False,
                    "error": "Failed to get account information"
                }), 500
        else:
            logger.error(f"❌ Verification failed for {username}: {result['error']}")
            return jsonify({
                "ok": False,
                "error": result["error"]
            }), 401
                
    except Exception as e:
        logger.error(f"❌ Unexpected error in verify_account: {e}")
        return jsonify({
            "ok": False,
            "error": "Internal server error"
        }), 500

@accounts.route('/api/accounts/test-login', methods=['GET'])
def test_login():
    """Test login endpoint for development"""
    try:
        username = request.args.get('u')
        password = request.args.get('p')
        
        if not username or not password:
            return jsonify({
                "ok": False,
                "error": "Username (u) and password (p) parameters required"
            }), 400
        
        logger.info(f"🧪 Test login for username: {username}")
        
        # Get client without OTP
        client, result = threads_client_service.get_client(username, password)
        
        if result["success"]:
            return jsonify({
                "ok": True,
                "message": "Test login successful",
                "session_reused": result.get("session_reused", False)
            }), 200
        else:
            if result.get("needs_code"):
                return jsonify({
                    "ok": False,
                    "needs_code": True,
                    "type": result["type"],
                    "message": result["message"]
                }), 401
            else:
                return jsonify({
                    "ok": False,
                    "error": result["error"]
                }), 401
                
    except Exception as e:
        logger.error(f"❌ Unexpected error in test_login: {e}")
        return jsonify({
            "ok": False,
            "error": "Internal server error"
        }), 500
