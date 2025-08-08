#!/usr/bin/env python3
"""
Scheduler Routes
Handles automated posting and scheduling via Threads API
"""

from flask import Blueprint, request, jsonify
import logging
from datetime import datetime, timedelta
from services.threads_api import threads_api_service
from database import DatabaseManager
from meta_client import meta_client
import requests

logger = logging.getLogger(__name__)
scheduler = Blueprint('scheduler', __name__)

@scheduler.route('/run', methods=['POST'])
def run_scheduler():
    """Run the scheduler to post due content - cron-safe"""
    try:
        logger.info("🚀 Running scheduler (cron-safe)")
        
        db = DatabaseManager()
        
        # Get due scheduled posts
        now = datetime.now()
        due_posts = db.get_scheduled_posts(status='pending')
        
        # Filter posts that are actually due
        due_posts = [post for post in due_posts if 
                    datetime.fromisoformat(post['scheduled_for']) <= now]
        
        logger.info(f"📅 Found {len(due_posts)} due scheduled posts to process")
        
        if not due_posts:
            return jsonify({
                'ok': True,
                'processed': 0,
                'message': 'No due posts found',
                'timestamp': now.isoformat()
            })
        
        results = []
        import time
        
        for i, post in enumerate(due_posts):
            try:
                post_id = post['id']
                account_id = post['account_id']
                scheduled_for = datetime.fromisoformat(post['scheduled_for'])
                
                logger.info(f"📝 Processing due post {post_id} for account {account_id}")
                
                # Get account info
                account = db.get_account_by_id(account_id)
                if not account:
                    logger.error(f"❌ Account {account_id} not found for post {post_id}")
                    db.update_scheduled_post_status(post_id, 'failed')
                    results.append({
                        'post_id': post_id,
                        'status': 'failed',
                        'error': 'Account not found'
                    })
                    continue
                
                # Check if account is connected
                if account.get('provider') != 'meta' or not account.get('threads_user_id'):
                    logger.error(f"❌ Account {account_id} not connected to Threads API")
                    db.update_scheduled_post_status(post_id, 'failed')
                    results.append({
                        'post_id': post_id,
                        'status': 'failed',
                        'error': 'Account not connected to Threads API'
                    })
                    continue
                
                # Get content
                caption_text = None
                image_url = None
                
                if post.get('caption_id'):
                    caption = db.get_caption_by_id(post['caption_id'])
                    if caption:
                        caption_text = caption['text']
                
                if post.get('image_id'):
                    image = db.get_image_by_id(post['image_id'])
                    if image:
                        image_url = image['url']
                
                if not caption_text:
                    logger.warning(f"⚠️ No caption for post {post_id}")
                    db.update_scheduled_post_status(post_id, 'failed')
                    results.append({
                        'post_id': post_id,
                        'status': 'failed',
                        'error': 'No caption available'
                    })
                    continue
                
                # Get token and validate
                token_data = db.get_token_by_account_id(account_id)
                if not token_data:
                    logger.error(f"❌ No token for account {account_id}")
                    db.update_scheduled_post_status(post_id, 'failed')
                    results.append({
                        'post_id': post_id,
                        'status': 'failed',
                        'error': 'No access token found'
                    })
                    continue
                
                access_token = token_data.get('access_token')
                if not access_token:
                    logger.error(f"❌ Invalid token for account {account_id}")
                    db.update_scheduled_post_status(post_id, 'failed')
                    results.append({
                        'post_id': post_id,
                        'status': 'failed',
                        'error': 'Invalid access token'
                    })
                    continue
                
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
                            logger.error(f"❌ Token refresh failed for account {account_id}: {e}")
                            db.update_scheduled_post_status(post_id, 'failed')
                            results.append({
                                'post_id': post_id,
                                'status': 'failed',
                                'error': 'Token expired and refresh failed'
                            })
                            continue
                    else:
                        logger.error(f"❌ Token expired for account {account_id}")
                        db.update_scheduled_post_status(post_id, 'failed')
                        results.append({
                            'post_id': post_id,
                            'status': 'failed',
                            'error': 'Token expired'
                        })
                        continue
                
                # Create and publish post
                post_result = meta_client.post_thread(
                    token=access_token,
                    text=caption_text,
                    image_url=image_url
                )
                
                if post_result['success']:
                    # Record posting history
                    db.record_posting_history(
                        account_id=account_id,
                        caption_id=post.get('caption_id'),
                        image_id=post.get('image_id'),
                        thread_id=post_result.get('thread_id'),
                        status='posted'
                    )
                    
                    # Mark scheduled post as completed
                    db.update_scheduled_post_status(post_id, 'completed')
                    
                    # Update account last_posted
                    db.update_account(account_id, {
                        'last_posted': datetime.now().isoformat()
                    })
                    
                    logger.info(f"✅ Post {post_id} published successfully")
                    results.append({
                        'post_id': post_id,
                        'status': 'completed',
                        'thread_id': post_result.get('thread_id')
                    })
                else:
                    # Mark as failed
                    db.update_scheduled_post_status(post_id, 'failed')
                    logger.error(f"❌ Post {post_id} failed: {post_result.get('error')}")
                    results.append({
                        'post_id': post_id,
                        'status': 'failed',
                        'error': post_result.get('error', 'Unknown error')
                    })
                
                # Add delay between posts to avoid rate limiting
                if i < len(due_posts) - 1:  # Don't delay after the last post
                    delay = min(2 + (i * 0.5), 10)  # Progressive backoff: 2s, 2.5s, 3s, etc., max 10s
                    logger.info(f"⏳ Waiting {delay}s before next post...")
                    time.sleep(delay)
                    
            except Exception as e:
                logger.error(f"❌ Error processing post {post.get('id', 'unknown')}: {e}")
                if post.get('id'):
                    db.update_scheduled_post_status(post['id'], 'failed')
                results.append({
                    'post_id': post.get('id', 'unknown'),
                    'status': 'failed',
                    'error': str(e)
                })
        
        logger.info(f"✅ Scheduler completed. Processed {len(results)} posts")
        
        return jsonify({
            'ok': True,
            'processed': len(results),
            'results': results,
            'timestamp': now.isoformat()
        })
        
    except Exception as e:
        logger.error(f"❌ Error running scheduler: {e}")
        return jsonify({
            'ok': False,
            'error': str(e)
        }), 500

@scheduler.route('/status', methods=['GET'])
def scheduler_status():
    """Get scheduler status and upcoming posts"""
    try:
        db = DatabaseManager()
        
        # Get pending scheduled posts
        pending_posts = db.get_scheduled_posts(status='pending')
        
        # Get recent completed posts
        completed_posts = db.get_scheduled_posts(status='completed')
        recent_completed = [p for p in completed_posts if 
                          datetime.fromisoformat(p['updated_at']) > datetime.now() - timedelta(hours=24)]
        
        # Get failed posts
        failed_posts = db.get_scheduled_posts(status='failed')
        recent_failed = [p for p in failed_posts if 
                        datetime.fromisoformat(p['updated_at']) > datetime.now() - timedelta(hours=24)]
        
        return jsonify({
            'ok': True,
            'pending_count': len(pending_posts),
            'recent_completed_count': len(recent_completed),
            'recent_failed_count': len(recent_failed),
            'next_run': (datetime.now() + timedelta(minutes=5)).isoformat(),
            'pending_posts': pending_posts[:5],  # Show next 5
            'recent_completed': recent_completed[:5],
            'recent_failed': recent_failed[:5]
        })
        
    except Exception as e:
        logger.error(f"❌ Error getting scheduler status: {e}")
        return jsonify({
            'ok': False,
            'error': str(e)
        }), 500

@scheduler.route('/accounts/<int:account_id>/enable', methods=['POST'])
def enable_account_scheduling(account_id):
    """Enable scheduling for an account"""
    try:
        logger.info(f"✅ Enabling scheduling for account {account_id}")
        
        db = DatabaseManager()
        db.update_account(account_id, {
            'status': 'scheduling_enabled',
            'updated_at': datetime.now().isoformat()
        })
        
        return jsonify({
            'ok': True,
            'account_id': account_id,
            'status': 'scheduling_enabled'
        })
        
    except Exception as e:
        logger.error(f"❌ Error enabling scheduling: {e}")
        return jsonify({
            'ok': False,
            'error': str(e)
        }), 500

@scheduler.route('/accounts/<int:account_id>/disable', methods=['POST'])
def disable_account_scheduling(account_id):
    """Disable scheduling for an account"""
    try:
        logger.info(f"❌ Disabling scheduling for account {account_id}")
        
        db = DatabaseManager()
        db.update_account(account_id, {
            'status': 'connected',  # Back to connected but not scheduling
            'updated_at': datetime.now().isoformat()
        })
        
        return jsonify({
            'ok': True,
            'account_id': account_id,
            'status': 'connected'
        })
        
    except Exception as e:
        logger.error(f"❌ Error disabling scheduling: {e}")
        return jsonify({
            'ok': False,
            'error': str(e)
        }), 500

@scheduler.route('/posts/<int:post_id>/cancel', methods=['POST'])
def cancel_scheduled_post(post_id):
    """Cancel a scheduled post"""
    try:
        logger.info(f"❌ Cancelling scheduled post {post_id}")
        
        db = DatabaseManager()
        if db.update_scheduled_post_status(post_id, 'cancelled'):
            return jsonify({
                'ok': True,
                'post_id': post_id,
                'status': 'cancelled'
            })
        else:
            return jsonify({
                'ok': False,
                'error': 'Failed to cancel post'
            }), 500
        
    except Exception as e:
        logger.error(f"❌ Error cancelling scheduled post: {e}")
        return jsonify({
            'ok': False,
            'error': str(e)
        }), 500

@scheduler.route('/posts/<int:post_id>/reschedule', methods=['POST'])
def reschedule_post(post_id):
    """Reschedule a post"""
    try:
        data = request.get_json()
        new_scheduled_for = data.get('scheduled_for')
        
        if not new_scheduled_for:
            return jsonify({
                'ok': False,
                'error': 'Missing scheduled_for'
            }), 400
        
        logger.info(f"📅 Rescheduling post {post_id} to {new_scheduled_for}")
        
        db = DatabaseManager()
        response = requests.patch(
            f"{db.supabase_url}/rest/v1/scheduled_posts",
            headers=db.headers,
            params={'id': f'eq.{post_id}'},
            json={
                'scheduled_for': new_scheduled_for,
                'status': 'pending',
                'updated_at': datetime.now().isoformat()
            }
        )
        
        if response.status_code in [200, 204]:
            return jsonify({
                'ok': True,
                'post_id': post_id,
                'scheduled_for': new_scheduled_for
            })
        else:
            return jsonify({
                'ok': False,
                'error': 'Failed to reschedule post'
            }), 500
        
    except Exception as e:
        logger.error(f"❌ Error rescheduling post: {e}")
        return jsonify({
            'ok': False,
            'error': str(e)
        }), 500
