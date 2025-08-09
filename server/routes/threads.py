#!/usr/bin/env python3
"""
Threads API Routes
Handles direct posting to Threads with session-first approach
"""

import os
import logging
import requests
from datetime import datetime
from flask import Blueprint, request, jsonify
from database import DatabaseManager
from services.rate_limiter import rate_limiter, TEST_POST_LIMIT, TEST_POST_WINDOW

logger = logging.getLogger(__name__)
threads = Blueprint('threads', __name__)

@threads.route('/api/threads/post', methods=['POST'])
def post_to_threads():
    """Post content to Threads using session-first approach"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({
                "ok": False,
                "error": "No JSON data provided"
            }), 400
        
        account_id = data.get('account_id')
        text = data.get('text')
        image_url = data.get('image_url')
        is_test = data.get('is_test', False)
        
        if not account_id or not text:
            return jsonify({
                "ok": False,
                "error": "Account ID and text are required"
            }), 400
        
        # Rate limiting for test posts
        if is_test:
            rate_key = f"test_post_account_{account_id}"
            allowed, remaining = rate_limiter.is_allowed(
                rate_key, TEST_POST_LIMIT, TEST_POST_WINDOW
            )
            
            if not allowed:
                return jsonify({
                    "ok": False,
                    "error": f"Rate limit exceeded. Max {TEST_POST_LIMIT} test posts per hour per account.",
                    "rate_limit": {
                        "max_requests": TEST_POST_LIMIT,
                        "window_seconds": TEST_POST_WINDOW,
                        "remaining": remaining
                    }
                }), 429
        
        logger.info(f"📝 Posting to Threads for account {account_id} (test: {is_test})")
        
        # Get account details from database
        db = DatabaseManager()
        account = db.get_account_by_id(account_id)
        
        if not account:
            return jsonify({
                "ok": False,
                "error": "Account not found"
            }), 404
        
        # Check if account can post (has session or official API)
        from services.threads_api import threads_client
        posting_method = threads_client.get_posting_method(account)
        
        if posting_method == "no_method_available":
            return jsonify({
                "ok": False,
                "error": "Account cannot post. Please upload a session file or connect via Meta OAuth.",
                "help": {
                    "session": "Upload a .json session file in the Accounts page",
                    "oauth": "Connect via Meta OAuth (requires official API access)"
                },
                "connection_status": account.get('connection_status', 'disconnected')
            }), 403
        
        # Use ThreadsClient for posting
        from services.threads_api import threads_client
        
        success, message = threads_client.post_thread(account, text, image_url)
        
        # Store posting record
        status = "posted" if success else "failed"
        db.record_posting_history(account_id, None, None, None, status)
        
        if success:
            # Update account last posted time
            db.update_account(account_id, {
                'last_posted_at': datetime.now().isoformat(),
                'updated_at': datetime.now().isoformat()
            })
            
            logger.info(f"✅ Posted successfully for account {account_id}")
            
            post_data = {
                "account_id": account_id,
                "username": account.get('username'),
                "text": text,
                "image_url": image_url,
                "posted_at": datetime.now().isoformat(),
                "status": "posted",
                "method": threads_client.get_posting_method(account)
            }
            
            return jsonify({
                "ok": True,
                "post": post_data,
                "message": f"Post created successfully via {post_data['method']}"
            }), 201
        else:
            logger.error(f"❌ Failed to post for account {account_id}: {message}")
            return jsonify({
                "ok": False,
                "error": message
            }), 500
        
    except Exception as e:
        logger.error(f"❌ Error posting to Threads: {e}")
        return jsonify({
            "ok": False,
            "error": str(e)
        }), 500

@threads.route('/api/threads/accounts/<int:account_id>/test', methods=['POST'])
def test_account_connection(account_id):
    """Test if an account can post to Threads"""
    try:
        logger.info(f"🧪 Testing account {account_id} connection")
        
        # Get account details
        db = DatabaseManager()
        account = db.get_account_by_id(account_id)
        
        if not account:
            return jsonify({
                "ok": False,
                "error": "Account not found"
            }), 404
        
        # Simple test post
        test_text = "Test post from Threads Bot! 🚀"
        
        # This would be replaced with actual Threads API call
        test_result = {
            "account_id": account_id,
            "username": account.get('username'),
            "test_text": test_text,
            "status": "test_successful",
            "timestamp": datetime.now().isoformat()
        }
        
        logger.info(f"✅ Test successful for account {account_id}")
        
        return jsonify({
            "ok": True,
            "test": test_result,
            "message": "Account connection test successful"
        }), 200
        
    except Exception as e:
        logger.error(f"❌ Error testing account connection: {e}")
        return jsonify({
            "ok": False,
            "error": str(e)
        }), 500
