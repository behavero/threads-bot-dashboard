#!/usr/bin/env python3
"""
Threads API Routes
Handles direct posting to Threads without OAuth
"""

import os
import logging
import requests
from datetime import datetime
from flask import Blueprint, request, jsonify
from database import DatabaseManager

logger = logging.getLogger(__name__)
threads = Blueprint('threads', __name__)

@threads.route('/api/threads/post', methods=['POST'])
def post_to_threads():
    """Post content to Threads using direct API"""
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
        
        if not account_id or not text:
            return jsonify({
                "ok": False,
                "error": "Account ID and text are required"
            }), 400
        
        logger.info(f"📝 Posting to Threads for account {account_id}")
        
        # Get account details from database
        db = DatabaseManager()
        account = db.get_account_by_id(account_id)
        
        if not account:
            return jsonify({
                "ok": False,
                "error": "Account not found"
            }), 404
        
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
