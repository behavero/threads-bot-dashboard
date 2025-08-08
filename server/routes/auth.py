#!/usr/bin/env python3
"""
OAuth Routes for Meta Threads API
Handles OAuth flow for connecting Threads accounts
"""

from flask import Blueprint, request, jsonify, redirect
import logging
import os
from datetime import datetime
from meta_oauth import meta_oauth_helper
from meta_client import meta_client
from database import DatabaseManager

logger = logging.getLogger(__name__)
auth = Blueprint('auth', __name__)

@auth.route('/meta/start', methods=['GET'])
def start_oauth():
    """Start OAuth flow for an account"""
    try:
        account_id = request.args.get('account_id')
        
        if not account_id:
            return jsonify({
                'ok': False,
                'error': 'Missing account_id parameter'
            }), 400
        
        try:
            account_id = int(account_id)
        except ValueError:
            return jsonify({
                'ok': False,
                'error': 'Invalid account_id parameter'
            }), 400
        
        logger.info(f"🔗 Starting OAuth flow for account {account_id}")
        
        # Generate secure state token
        state = meta_oauth_helper.generate_state(account_id)
        
        # Build OAuth URL
        auth_url = meta_oauth_helper.build_oauth_url(state)
        
        logger.info(f"✅ Redirecting to Meta OAuth for account {account_id}")
        return redirect(auth_url)
        
    except Exception as e:
        logger.error(f"❌ Error starting OAuth: {e}")
        return jsonify({
            'ok': False,
            'error': str(e)
        }), 500

@auth.route('/meta/callback', methods=['GET'])
def oauth_callback():
    """Handle OAuth callback and exchange code for tokens"""
    try:
        code = request.args.get('code')
        state = request.args.get('state')
        error = request.args.get('error')
        
        if error:
            logger.error(f"❌ OAuth error: {error}")
            return redirect(f"https://threads-bot-dashboard-frnnc7lw4-behaveros-projects.vercel.app/accounts?error=oauth_denied&message={error}")
        
        if not code or not state:
            logger.error("❌ Missing code or state in OAuth callback")
            return redirect(f"https://threads-bot-dashboard-frnnc7lw4-behaveros-projects.vercel.app/accounts?error=oauth_invalid")
        
        logger.info(f"🔄 Processing OAuth callback with state: {state[:8]}...")
        
        # Validate state and get account_id
        account_id = meta_oauth_helper.validate_state(state)
        if not account_id:
            logger.error("❌ Invalid OAuth state")
            return redirect(f"https://threads-bot-dashboard-frnnc7lw4-behaveros-projects.vercel.app/accounts?error=oauth_invalid_state")
        
        logger.info(f"🔄 Processing OAuth callback for account {account_id}")
        
        # Exchange code for tokens
        token_data = meta_oauth_helper.exchange_code_for_tokens(code)
        
        # Save tokens to database
        db = DatabaseManager()
        if db.save_token(account_id, token_data):
            # Update account with Meta provider info
            update_data = {
                'status': 'connected',
                'threads_user_id': token_data.get('threads_user_id'),
                'ig_user_id': token_data.get('user_id'),
                'provider': 'meta',
                'updated_at': datetime.now().isoformat()
            }
            
            # Update username if we got it from Meta
            if token_data.get('username'):
                update_data['username'] = token_data.get('username')
            
            db.update_account(account_id, update_data)
            
            logger.info(f"✅ OAuth completed successfully for account {account_id}")
            
            return redirect(f"https://threads-bot-dashboard-frnnc7lw4-behaveros-projects.vercel.app/accounts?connected=success&account_id={account_id}")
        else:
            logger.error(f"❌ Failed to save tokens for account {account_id}")
            return redirect(f"https://threads-bot-dashboard-frnnc7lw4-behaveros-projects.vercel.app/accounts?error=oauth_save_failed")
        
    except Exception as e:
        logger.error(f"❌ Error in OAuth callback: {e}")
        return redirect(f"https://threads-bot-dashboard-frnnc7lw4-behaveros-projects.vercel.app/accounts?error=oauth_exception&message={str(e)}")

@auth.route('/meta/refresh', methods=['GET', 'DELETE'])
def refresh_oauth():
    """Refresh or revoke OAuth tokens"""
    try:
        account_id = request.args.get('account_id')
        
        if not account_id:
            return jsonify({
                'ok': False,
                'error': 'Missing account_id'
            }), 400
        
        db = DatabaseManager()
        
        if request.method == 'GET':
            # Refresh token
            logger.info(f"🔄 Refreshing token for account {account_id}")
            
            token_data = db.get_token_by_account_id(account_id)
            if not token_data:
                return jsonify({
                    'ok': False,
                    'error': 'No token found for account'
                }), 404
            
            refresh_token = token_data.get('refresh_token')
            if not refresh_token:
                return jsonify({
                    'ok': False,
                    'error': 'No refresh token available'
                }), 400
            
            try:
                new_token_data = meta_oauth_helper.refresh_access_token(refresh_token, account_id)
                if db.update_token(account_id, new_token_data):
                    logger.info(f"✅ Token refreshed for account {account_id}")
                    return jsonify({
                        'ok': True,
                        'account_id': account_id,
                        'expires_at': new_token_data.get('expires_at')
                    })
                else:
                    return jsonify({
                        'ok': False,
                        'error': 'Failed to update token'
                    }), 500
                    
            except Exception as e:
                logger.error(f"❌ Token refresh failed for account {account_id}: {e}")
                return jsonify({
                    'ok': False,
                    'error': str(e)
                }), 500
        
        elif request.method == 'DELETE':
            # Revoke token
            logger.info(f"🗑️ Revoking token for account {account_id}")
            
            if db.delete_token(account_id):
                # Update account status to disconnected
                db.update_account(account_id, {
                    'status': 'disconnected',
                    'threads_user_id': None,
                    'updated_at': datetime.now().isoformat()
                })
                
                logger.info(f"✅ Token revoked for account {account_id}")
                return jsonify({
                    'ok': True,
                    'account_id': account_id
                })
            else:
                return jsonify({
                    'ok': False,
                    'error': 'Failed to revoke token'
                }), 500
        
    except Exception as e:
        logger.error(f"❌ Error in OAuth refresh: {e}")
        return jsonify({
            'ok': False,
            'error': str(e)
        }), 500

@auth.route('/meta/status/<int:account_id>', methods=['GET'])
def oauth_status(account_id):
    """Check OAuth status for an account"""
    try:
        logger.info(f"🔍 Checking OAuth status for account {account_id}")
        
        db = DatabaseManager()
        token_data = db.get_token_by_account_id(account_id)
        
        if not token_data:
            return jsonify({
                'ok': True,
                'connected': False,
                'account_id': account_id
            })
        
        # Check if token is valid
        access_token = token_data.get('access_token')
        if access_token and meta_client.validate_token(access_token):
            return jsonify({
                'ok': True,
                'connected': True,
                'account_id': account_id,
                'user_id': token_data.get('user_id'),
                'scopes': token_data.get('scopes', []),
                'expires_at': token_data.get('expires_at')
            })
        else:
            return jsonify({
                'ok': True,
                'connected': False,
                'account_id': account_id,
                'reason': 'token_invalid'
            })
        
    except Exception as e:
        logger.error(f"❌ Error checking OAuth status: {e}")
        return jsonify({
            'ok': False,
            'error': str(e)
        }), 500
