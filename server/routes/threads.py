#!/usr/bin/env python3
"""
Threads API Routes
Handles posting and content management via official Threads API
"""

from flask import Blueprint, request, jsonify
import logging
from datetime import datetime
from services.threads_api import threads_api_service
from database import DatabaseManager
from meta_client import meta_client

logger = logging.getLogger(__name__)
threads = Blueprint('threads', __name__)

@threads.route('/post', methods=['POST'])
def create_post():
    """Create a new post via Threads API"""
    try:
        data = request.get_json()
        account_id = data.get('account_id')
        text = data.get('text')
        image_id = data.get('image_id')
        media_urls = data.get('media_urls', [])
        reply_to_id = data.get('reply_to_id')
        quote_post_id = data.get('quote_post_id')
        
        if not account_id or not text:
            return jsonify({
                'ok': False,
                'error': 'Missing account_id or text'
            }), 400
        
        logger.info(f"📝 Creating post for account {account_id}")
        
        # Get database instance
        db = DatabaseManager()
        
        # Get account info
        account = db.get_account_by_id(account_id)
        if not account:
            return jsonify({
                'ok': False,
                'error': 'Account not found'
            }), 404
        
        # Check if account is connected via Meta
        if account.get('provider') != 'meta' or not account.get('threads_user_id'):
            return jsonify({
                'ok': False,
                'error': 'Account not connected to Threads API'
            }), 400
        
        # Get token and refresh if needed
        token_data = db.get_token_by_account_id(account_id)
        if not token_data:
            return jsonify({
                'ok': False,
                'error': 'No access token found for account'
            }), 400
        
        access_token = token_data.get('access_token')
        if not access_token:
            return jsonify({
                'ok': False,
                'error': 'Invalid access token'
            }), 400
        
        # Validate token
        if not meta_client.validate_token(access_token):
            # Try to refresh token
            refresh_token = token_data.get('refresh_token')
            if refresh_token:
                try:
                    from meta_oauth import meta_oauth_helper
                    new_token_data = meta_oauth_helper.refresh_access_token(refresh_token, account_id)
                    db.update_token(account_id, new_token_data)
                    access_token = new_token_data.get('access_token')
                    logger.info(f"✅ Token refreshed for account {account_id}")
                except Exception as e:
                    logger.error(f"❌ Token refresh failed: {e}")
                    return jsonify({
                        'ok': False,
                        'error': 'Token expired and refresh failed'
                    }), 401
            else:
                return jsonify({
                    'ok': False,
                    'error': 'Token expired and no refresh token available'
                }), 401
        
        # Resolve image URL if image_id provided
        image_url = None
        if image_id:
            image = db.get_image_by_id(image_id)
            if image:
                image_url = image.get('url')
                logger.info(f"📸 Using image {image_id}: {image_url}")
            else:
                logger.warning(f"⚠️ Image {image_id} not found")
        
        # Add image URL to media_urls if provided
        if image_url and image_url not in media_urls:
            media_urls.append(image_url)
        
        # Create post via Meta client
        post_result = meta_client.post_thread(
            token=access_token,
            text=text,
            image_url=image_url if image_url else None
        )
        
        if post_result['success']:
            # Record posting history
            history_data = {
                'account_id': account_id,
                'caption_id': None,  # Manual post
                'image_id': image_id,
                'thread_id': post_result.get('thread_id'),
                'api_type': 'threads_api',
                'provider': 'meta',
                'remote_post_id': post_result.get('thread_id'),
                'status': 'posted',
                'error_message': None
            }
            
            db.record_posting_history(
                account_id=account_id,
                caption_id=None,
                image_id=image_id,
                thread_id=post_result.get('thread_id'),
                status='posted'
            )
            
            # Update account last_posted
            db.update_account(account_id, {
                'last_posted': datetime.now().isoformat()
            })
            
            logger.info(f"✅ Post created and published for account {account_id}")
            
            return jsonify({
                'ok': True,
                'thread_id': post_result.get('thread_id'),
                'status': 'published',
                'account_id': account_id
            })
        else:
            # Record failed posting
            db.record_posting_history(
                account_id=account_id,
                caption_id=None,
                image_id=image_id,
                thread_id=None,
                status='failed'
            )
            
            logger.error(f"❌ Post failed for account {account_id}: {post_result.get('error')}")
            return jsonify({
                'ok': False,
                'error': post_result.get('error', 'Unknown error')
            }), 500
        
    except Exception as e:
        logger.error(f"❌ Error creating post: {e}")
        return jsonify({
            'ok': False,
            'error': str(e)
        }), 500

@threads.route('/schedule', methods=['POST'])
def schedule_post():
    """Schedule a post for later"""
    try:
        data = request.get_json()
        account_id = data.get('account_id')
        caption_id = data.get('caption_id')
        image_id = data.get('image_id')
        scheduled_for = data.get('scheduled_for')
        
        if not account_id or not scheduled_for:
            return jsonify({
                'ok': False,
                'error': 'Missing account_id or scheduled_for'
            }), 400
        
        logger.info(f"📅 Scheduling post for account {account_id}")
        
        # Add to scheduled posts
        db = DatabaseManager()
        if db.add_scheduled_post(account_id, scheduled_for, caption_id, image_id):
            logger.info(f"✅ Post scheduled for account {account_id}")
            
            return jsonify({
                'ok': True,
                'account_id': account_id,
                'scheduled_for': scheduled_for
            })
        else:
            return jsonify({
                'ok': False,
                'error': 'Failed to schedule post'
            }), 500
        
    except Exception as e:
        logger.error(f"❌ Error scheduling post: {e}")
        return jsonify({
            'ok': False,
            'error': str(e)
        }), 500

@threads.route('/accounts/<int:account_id>/posts', methods=['GET'])
def get_account_posts(account_id):
    """Get posts for an account"""
    try:
        logger.info(f"📊 Getting posts for account {account_id}")
        
        # Get account info first
        account_info = threads_api_service.get_account_info(account_id)
        
        if not account_info['success']:
            return jsonify({
                'ok': False,
                'error': account_info['error']
            }), 500
        
        # Get posting history from database
        db = DatabaseManager()
        posting_history = db.get_posting_history_by_account(account_id)
        
        return jsonify({
            'ok': True,
            'account_info': account_info['data'],
            'posts': posting_history
        })
        
    except Exception as e:
        logger.error(f"❌ Error getting account posts: {e}")
        return jsonify({
            'ok': False,
            'error': str(e)
        }), 500

@threads.route('/accounts/<int:account_id>/insights', methods=['GET'])
def get_account_insights(account_id):
    """Get insights for an account"""
    try:
        logger.info(f"📈 Getting insights for account {account_id}")
        
        # Get posting history
        db = DatabaseManager()
        posting_history = db.get_posting_history_by_account(account_id)
        
        # Get insights for recent posts
        insights = []
        for post in posting_history[-10:]:  # Last 10 posts
            if post.get('thread_id'):
                insight_result = threads_api_service.get_post_insights(account_id, post['thread_id'])
                if insight_result['success']:
                    insights.append({
                        'thread_id': post['thread_id'],
                        'insights': insight_result['data']
                    })
        
        return jsonify({
            'ok': True,
            'account_id': account_id,
            'insights': insights
        })
        
    except Exception as e:
        logger.error(f"❌ Error getting account insights: {e}")
        return jsonify({
            'ok': False,
            'error': str(e)
        }), 500

@threads.route('/posts/<thread_id>/insights', methods=['GET'])
def get_post_insights(thread_id):
    """Get insights for a specific post"""
    try:
        account_id = request.args.get('account_id')
        
        if not account_id:
            return jsonify({
                'ok': False,
                'error': 'Missing account_id'
            }), 400
        
        logger.info(f"📈 Getting insights for thread {thread_id}")
        
        result = threads_api_service.get_post_insights(account_id, thread_id)
        
        if result['success']:
            return jsonify({
                'ok': True,
                'thread_id': thread_id,
                'insights': result['data']
            })
        else:
            return jsonify({
                'ok': False,
                'error': result['error']
            }), 500
        
    except Exception as e:
        logger.error(f"❌ Error getting post insights: {e}")
        return jsonify({
            'ok': False,
            'error': str(e)
        }), 500

@threads.route('/test/<int:account_id>', methods=['POST'])
def test_account_connection(account_id):
    """Test if an account can post via Threads API"""
    try:
        logger.info(f"🧪 Testing account {account_id} connection")
        
        # Try to get account info
        account_info = threads_api_service.get_account_info(account_id)
        
        if account_info['success']:
            return jsonify({
                'ok': True,
                'account_id': account_id,
                'connected': True,
                'account_info': account_info['data']
            })
        else:
            return jsonify({
                'ok': True,
                'account_id': account_id,
                'connected': False,
                'error': account_info['error']
            })
        
    except Exception as e:
        logger.error(f"❌ Error testing account connection: {e}")
        return jsonify({
            'ok': False,
            'error': str(e)
        }), 500
