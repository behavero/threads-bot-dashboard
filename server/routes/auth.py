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
        
        # Generate OAuth URL with proper state handling
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

@auth.route('/auth/meta/callback', methods=['GET', 'POST'])
def handle_oauth_callback():
    """Handle OAuth callback from Meta - supports both GET (redirect) and POST (API)"""
    try:
        # Handle GET request (Meta OAuth redirect)
        if request.method == 'GET':
            code = request.args.get('code')
            state = request.args.get('state')
            error = request.args.get('error')
            error_description = request.args.get('error_description', '')
            
            # Check for OAuth errors
            if error:
                error_message = f"OAuth error: {error}"
                if error_description:
                    error_message += f" - {error_description}"
                
                logger.error(f"❌ Meta OAuth error: {error} - {error_description}")
                
                # Redirect to frontend with error
                frontend_url = os.getenv('APP_BASE_URL', 'https://threads-bot-dashboard.vercel.app')
                redirect_url = f"{frontend_url}/accounts?status=error&message={error_message}"
                return redirect(redirect_url)
            
            if not code or not state:
                logger.error("❌ OAuth callback missing code or state")
                frontend_url = os.getenv('APP_BASE_URL', 'https://threads-bot-dashboard.vercel.app')
                redirect_url = f"{frontend_url}/accounts?status=error&message=Invalid OAuth response"
                return redirect(redirect_url)
            
            account_id = state  # state contains account_id
            
        # Handle POST request (API call)
        else:
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
        
        # Common processing for both GET and POST
        db = DatabaseManager()
        account = db.get_account_by_id(int(account_id))
        
        if not account:
            if request.method == 'GET':
                frontend_url = os.getenv('APP_BASE_URL', 'https://threads-bot-dashboard.vercel.app')
                redirect_url = f"{frontend_url}/accounts?status=error&message=Account not found"
                return redirect(redirect_url)
            else:
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
                'oauth_status': 'connected',
                'updated_at': datetime.now().isoformat()
            }
            
            # Store access token
            success = db.store_access_token(int(account_id), token_data)
            
            if success:
                db.update_account(int(account_id), update_data)
                
                logger.info(f"✅ OAuth completed successfully for account {account_id}")
                
                if request.method == 'GET':
                    frontend_url = os.getenv('APP_BASE_URL', 'https://threads-bot-dashboard.vercel.app')
                    redirect_url = f"{frontend_url}/accounts?status=success&message=Account connected successfully"
                    return redirect(redirect_url)
                else:
                    return jsonify({
                        "ok": True,
                        "account_id": account_id,
                        "message": "OAuth completed successfully"
                    }), 200
            else:
                error_msg = "Failed to store access token"
                if request.method == 'GET':
                    frontend_url = os.getenv('APP_BASE_URL', 'https://threads-bot-dashboard.vercel.app')
                    redirect_url = f"{frontend_url}/accounts?status=error&message={error_msg}"
                    return redirect(redirect_url)
                else:
                    return jsonify({
                        "ok": False,
                        "error": error_msg
                    }), 500
        else:
            error_msg = tokens_or_error.get('error', 'Unknown error')
            
            # Update account with OAuth error status
            update_data = {
                'oauth_status': f'error: {error_msg}',
                'updated_at': datetime.now().isoformat()
            }
            db.update_account(int(account_id), update_data)
            
            logger.error(f"❌ OAuth failed for account {account_id}: {error_msg}")
            
            if request.method == 'GET':
                frontend_url = os.getenv('APP_BASE_URL', 'https://threads-bot-dashboard.vercel.app')
                redirect_url = f"{frontend_url}/accounts?status=error&message=OAuth failed: {error_msg}"
                return redirect(redirect_url)
            else:
                return jsonify({
                    "ok": False,
                    "error": f"OAuth failed: {error_msg}"
                }), 400
        
    except Exception as e:
        logger.error(f"❌ Error in OAuth callback: {e}")
        
        if request.method == 'GET':
            frontend_url = os.getenv('APP_BASE_URL', 'https://threads-bot-dashboard.vercel.app')
            redirect_url = f"{frontend_url}/accounts?status=error&message=OAuth system error"
            return redirect(redirect_url)
        else:
            return jsonify({
                "ok": False,
                "error": str(e)
            }), 500
