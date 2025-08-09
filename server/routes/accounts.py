#!/usr/bin/env python3
"""
Account Routes
Handles account management with Meta OAuth (legacy login removed)
"""

import os
import logging
from datetime import datetime
from flask import Blueprint, request, jsonify
from database import DatabaseManager

logger = logging.getLogger(__name__)

accounts = Blueprint('accounts', __name__)

@accounts.route('/api/accounts/login', methods=['POST'])
def login_account():
    """Account creation - requires Meta OAuth in production"""
    try:
        from config.env import load_meta_oauth_config, missing_oauth_vars
        import os
        
        # Check OAuth configuration
        cfg = load_meta_oauth_config()
        missing = missing_oauth_vars(cfg)
        ENV = os.environ.get("APP_ENV", os.environ.get("ENV", "development")).lower()
        
        # Fail hard in production if OAuth not configured
        if missing and ENV in ("production", "staging"):
            return jsonify({
                "ok": False,
                "error": f"Direct creation disabled in {ENV}. Missing OAuth vars: {', '.join(missing)}"
            }), 400
        
        data = request.get_json()
        if not data:
            return jsonify({
                "ok": False,
                "error": "No JSON data provided"
            }), 400
        
        username = data.get('username')
        description = data.get('description', '')
        
        if not username:
            return jsonify({
                "ok": False,
                "error": "Username is required"
            }), 400
        
        logger.info(f"🔐 Creating account for username: {username}")
        
        # Create account in database
        db = DatabaseManager()
        
        # Check connection status
        from services.session_store import session_store
        has_session = session_store.exists(username)
        connection_status = "connected_session" if has_session else "disconnected"
        
        account_data = {
            "username": username,
            "description": description,
            "status": "enabled",
            "provider": "direct" if not cfg.is_configured else "meta_oauth",
            "connection_status": connection_status,
            "created_at": datetime.now().isoformat()
        }
        
        account_id = db.add_account(account_data)
        
        if account_id:
            logger.info(f"✅ Account created successfully for {username}")
            return jsonify({
                "ok": True,
                "account": {
                    "id": account_id,
                    "username": username,
                    "description": description,
                    "status": "enabled",
                    "provider": account_data["provider"]
                },
                "message": "Account created successfully"
            }), 201
        else:
            logger.error(f"❌ Failed to create account for {username}")
            return jsonify({
                "ok": False,
                "error": "Failed to create account"
            }), 500
            
    except Exception as e:
        logger.error(f"❌ Error creating account: {e}")
        return jsonify({
            "ok": False,
            "error": str(e)
        }), 500

@accounts.route('/api/accounts/verify', methods=['POST'])
def verify_account():
    """Simple account verification - no Meta authentication required"""
    return jsonify({
        "ok": True,
        "message": "Account verification not required for direct connection"
    }), 200

@accounts.route('/api/accounts/test-login', methods=['GET'])
def test_login():
    """Legacy test login endpoint - use Meta OAuth instead"""
    return jsonify({
        "ok": False,
        "error": "Legacy test login removed. Please use Meta OAuth flow to connect your Threads account.",
        "oauth_required": True
    }), 400

@accounts.route('/api/accounts/<int:account_id>/session', methods=['POST'])
def upload_session(account_id):
    """Upload session file for an account"""
    try:
        if 'session_file' not in request.files:
            return jsonify({
                "ok": False,
                "error": "No session file provided"
            }), 400
        
        file = request.files['session_file']
        if file.filename == '':
            return jsonify({
                "ok": False,
                "error": "No file selected"
            }), 400
        
        # Get account
        db = DatabaseManager()
        account = db.get_account_by_id(account_id)
        if not account:
            return jsonify({
                "ok": False,
                "error": "Account not found"
            }), 404
        
        username = account['username']
        
        # Parse session data
        try:
            import json
            session_data = json.loads(file.read().decode('utf-8'))
        except Exception as e:
            return jsonify({
                "ok": False,
                "error": f"Invalid session file format: {str(e)}"
            }), 400
        
        # Save session
        from services.session_store import session_store
        if session_store.save_session(username, session_data):
            # Update account connection status
            db.update_account(account_id, {
                'connection_status': 'connected_session',
                'updated_at': datetime.now().isoformat()
            })
            
            logger.info(f"✅ Session uploaded for account {account_id} ({username})")
            return jsonify({
                "ok": True,
                "account_id": account_id,
                "username": username,
                "message": "Session uploaded successfully"
            }), 200
        else:
            return jsonify({
                "ok": False,
                "error": "Failed to save session"
            }), 500
            
    except Exception as e:
        logger.error(f"❌ Error uploading session: {e}")
        return jsonify({
            "ok": False,
            "error": str(e)
        }), 500

@accounts.route('/api/accounts/<int:account_id>/status', methods=['GET'])
def check_account_status(account_id):
    """Check account connection status and posting capabilities"""
    try:
        # Get account
        db = DatabaseManager()
        account = db.get_account_by_id(account_id)
        if not account:
            return jsonify({
                "ok": False,
                "error": "Account not found"
            }), 404
        
        # Check status using ThreadsClient
        from services.threads_api import threads_client
        status = threads_client.check_account_status(account)
        
        return jsonify({
            "ok": True,
            "status": status
        }), 200
        
    except Exception as e:
        logger.error(f"❌ Error checking account status: {e}")
        return jsonify({
            "ok": False,
            "error": str(e)
        }), 500

@accounts.route('/api/accounts/<int:account_id>', methods=['PATCH'])
def update_account(account_id):
    """Update account settings (autopilot, cadence, etc.)"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({
                "ok": False,
                "error": "No JSON data provided"
            }), 400
        
        # Get account
        db = DatabaseManager()
        account = db.get_account_by_id(account_id)
        if not account:
            return jsonify({
                "ok": False,
                "error": "Account not found"
            }), 404
        
        # Build update data
        update_data = {}
        
        if 'autopilot_enabled' in data:
            update_data['autopilot_enabled'] = bool(data['autopilot_enabled'])
        
        if 'cadence_minutes' in data:
            cadence = int(data['cadence_minutes'])
            if cadence not in [5, 10, 15, 30, 60, 120, 180, 240]:
                return jsonify({
                    "ok": False,
                    "error": "Invalid cadence value"
                }), 400
            update_data['cadence_minutes'] = cadence
        
        if 'description' in data:
            update_data['description'] = data['description']
        
        if update_data:
            update_data['updated_at'] = datetime.now().isoformat()
            
            if db.update_account(account_id, update_data):
                return jsonify({
                    "ok": True,
                    "message": "Account updated successfully"
                }), 200
            else:
                return jsonify({
                    "ok": False,
                    "error": "Failed to update account"
                }), 500
        else:
            return jsonify({
                "ok": True,
                "message": "No changes made"
            }), 200
            
    except Exception as e:
        logger.error(f"❌ Error updating account: {e}")
        return jsonify({
            "ok": False,
            "error": str(e)
        }), 500
