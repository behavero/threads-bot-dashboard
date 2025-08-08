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
        account_data = {
            "username": username,
            "description": description,
            "status": "enabled",
            "provider": "direct" if not cfg.is_configured else "meta_oauth",
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
