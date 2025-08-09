#!/usr/bin/env python3
"""
Authentication Routes
Handles Meta OAuth flow for Threads API
"""

import os
import logging
from flask import Blueprint, request, jsonify, redirect
from services.meta_oauth import MetaOAuthService
from database import DatabaseManager
from datetime import datetime

logger = logging.getLogger(__name__)

auth = Blueprint('auth', __name__)

@auth.route('/auth/meta/start', methods=['GET'])
def start_oauth():
    """Start Meta OAuth flow for an account"""
    try:
        account_id = request.args.get('account_id')
        if not account_id:
            return jsonify({
                "ok": False,
                "error": "account_id parameter is required"
            }), 400
        
        # Get account from database
        db = DatabaseManager()
        account = db.get_account_by_id(int(account_id))
        
        if not account:
            return jsonify({
                "ok": False,
                "error": "Account not found"
            }), 404
        
        # Initialize OAuth service
        oauth_service = MetaOAuthService()
        
        if not oauth_service.oauth_configured:
            return jsonify({
                "ok": False,
                "error": "OAuth not configured on this server"
            }), 503
        
        # Debug: Log OAuth configuration
        logger.info(f"🔍 OAuth config - App ID: {oauth_service.app_id[:8] if oauth_service.app_id else 'None'}...")
        logger.info(f"🔍 OAuth config - Redirect URI: {oauth_service.redirect_uri}")
        
        # Generate OAuth URL
        auth_url = oauth_service.build_auth_url(int(account_id), account['username'])
        
        logger.info(f"🔗 Starting OAuth flow for account {account_id}: {account['username']}")
        logger.info(f"🔗 Redirect URL: {auth_url}")
        
        # Redirect to Meta OAuth
        return redirect(auth_url)
        
    except Exception as e:
        logger.error(f"❌ Error starting OAuth: {e}")
        return jsonify({
            "ok": False,
            "error": str(e)
        }), 500

@auth.route('/auth/meta/callback', methods=['POST'])
def handle_oauth_callback():
    """Handle OAuth callback from Meta"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({
                "ok": False,
                "error": "No JSON data provided"
            }), 400
        
        code = data.get('code')
        account_id = data.get('account_id')
        
        if not code or not account_id:
            return jsonify({
                "ok": False,
                "error": "Missing required parameters"
            }), 400
        
        # Get account from database
        db = DatabaseManager()
        account = db.get_account_by_id(int(account_id))
        
        if not account:
            return jsonify({
                "ok": False,
                "error": "Account not found"
            }), 404
        
        # Exchange code for tokens
        oauth_service = MetaOAuthService()
        tokens_or_error = oauth_service.exchange_code_for_tokens(code, int(account_id))
        
        if tokens_or_error.get('success'):
            # Store tokens and update account status
            token_data = tokens_or_error.get('tokens', {})
            
            # Update account with token information
            update_data = {
                'connection_status': 'connected_official',
                'threads_user_id': token_data.get('user_id'),
                'updated_at': datetime.now().isoformat()
            }
            
            # Store access token
            success = db.store_access_token(int(account_id), token_data)
            
            if success:
                db.update_account(int(account_id), update_data)
                
                logger.info(f"✅ OAuth completed successfully for account {account_id}")
                
                return jsonify({
                    "ok": True,
                    "account_id": account_id,
                    "message": "OAuth completed successfully"
                }), 200
            else:
                return jsonify({
                    "ok": False,
                    "error": "Failed to store access token"
                }), 500
        else:
            error_msg = tokens_or_error.get('error', 'Unknown error')
            logger.error(f"❌ OAuth failed for account {account_id}: {error_msg}")
            return jsonify({
                "ok": False,
                "error": f"OAuth failed: {error_msg}"
            }), 400
        
    except Exception as e:
        logger.error(f"❌ Error in OAuth callback: {e}")
        return jsonify({
            "ok": False,
            "error": str(e)
        }), 500
