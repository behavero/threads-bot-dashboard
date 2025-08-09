#!/usr/bin/env python3
"""
Scheduler Routes
Server-side autopost runner for connected accounts (internal cron only)
"""

import logging
from datetime import datetime, timedelta
from flask import Blueprint, request, jsonify
from database import DatabaseManager
from services.autopilot import autopilot_service

logger = logging.getLogger(__name__)

scheduler = Blueprint('scheduler', __name__)

@scheduler.route('/api/scheduler/run', methods=['POST'])
def run_scheduler():
    """
    Server-side autopost runner for connected accounts (internal cron only)
    
    Process:
    1. Select accounts.autopilot_enabled = true AND next_run <= NOW()
    2. For each, pick a random caption+image from Supabase
    3. Attempt to post (log/record with posting_history until publish scope is granted)
    4. On success: set last_posted_at = NOW() and next_run = NOW() + cadence_minutes
    5. On failure: set next_run = NOW() + 5 minutes and record error
    """
    try:
        logger.info("🚀 Starting scheduler run")
        start_time = datetime.now()
        
        # Get due accounts
        due_accounts = autopilot_service.due_accounts(start_time)
        
        if not due_accounts:
            logger.info("📭 No due accounts found")
            return jsonify({
                'ok': True,
                'processed': 0,
                'message': 'No due accounts found',
                'timestamp': start_time.isoformat()
            })
        
        logger.info(f"📝 Processing {len(due_accounts)} due accounts")
        
        results = []
        successes = 0
        failures = 0
        
        for account in due_accounts:
            account_id = account['id']
            username = account['username']
            
            try:
                logger.info(f"🎯 Processing account {account_id} ({username})")
                
                # Pick random caption
                caption = autopilot_service.pick_caption(account)
                if not caption:
                    error_msg = f"No caption available for account {account_id}"
                    logger.warning(f"⚠️ {error_msg}")
                    
                    # Record failure and apply 5-minute backoff
                    autopilot_service.handle_posting_failure(account_id, error_msg)
                    results.append({
                        'account_id': account_id,
                        'username': username,
                        'success': False,
                        'error': error_msg
                    })
                    failures += 1
                    continue
                
                # Pick random image
                image = autopilot_service.pick_image()
                if not image:
                    logger.warning(f"⚠️ No image available for account {account_id}, posting text only")
                
                # Attempt to post
                post_success, post_message = autopilot_service.post_once(account, caption, image)
                
                # Record posting history
                autopilot_service.record_posting_history(
                    account_id=account_id,
                    caption_id=caption['id'],
                    image_id=image['id'] if image else None,
                    success=post_success,
                    message=post_message
                )
                
                if post_success:
                    # Handle success: update last_posted_at, schedule next run
                    autopilot_service.handle_posting_success(
                        account_id=account_id,
                        caption_id=caption['id'],
                        image_id=image['id'] if image else None
                    )
                    
                    logger.info(f"✅ Successfully posted for account {account_id}")
                    results.append({
                        'account_id': account_id,
                        'username': username,
                        'success': True,
                        'caption_id': caption['id'],
                        'image_id': image['id'] if image else None,
                        'message': post_message
                    })
                    successes += 1
                    
                else:
                    # Handle failure: apply 5-minute backoff, record error
                    autopilot_service.handle_posting_failure(account_id, post_message)
                    
                    logger.error(f"❌ Failed to post for account {account_id}: {post_message}")
                    results.append({
                        'account_id': account_id,
                        'username': username,
                        'success': False,
                        'error': post_message
                    })
                    failures += 1
                    
            except Exception as e:
                error_msg = f"Exception processing account {account_id}: {str(e)}"
                logger.error(f"❌ {error_msg}")
                
                # Record failure and apply backoff
                autopilot_service.handle_posting_failure(account_id, error_msg)
                results.append({
                    'account_id': account_id,
                    'username': username,
                    'success': False,
                    'error': error_msg
                })
                failures += 1
        
        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()
        
        logger.info(f"🏁 Scheduler run completed in {duration:.2f}s: {successes} successes, {failures} failures")
        
        return jsonify({
            'ok': True,
            'processed': len(due_accounts),
            'successes': successes,
            'failures': failures,
            'duration_seconds': duration,
            'results': results,
            'timestamp': end_time.isoformat()
        })
        
    except Exception as e:
        logger.error(f"❌ Critical error in scheduler run: {e}")
        return jsonify({
            'ok': False,
            'error': str(e),
            'processed': 0,
            'timestamp': datetime.now().isoformat()
        }), 500

@scheduler.route('/api/scheduler/status', methods=['GET'])
def scheduler_status():
    """Get scheduler status and next due accounts"""
    try:
        db = DatabaseManager()
        now = datetime.now()
        
        # Get accounts due in next 60 minutes
        next_hour = now + timedelta(hours=1)
        
        response = db._make_request(
            'GET',
            f"{db.supabase_url}/rest/v1/accounts",
            params={
                'autopilot_enabled': 'eq.true',
                'next_run_at': f'lte.{next_hour.isoformat()}',
                'select': 'id,username,next_run_at,last_posted_at,cadence_minutes,connection_status',
                'order': 'next_run_at.asc'
            }
        )
        
        upcoming_accounts = []
        if response.status_code == 200:
            upcoming_accounts = response.json()
        
        # Count due now
        due_now = [acc for acc in upcoming_accounts if acc.get('next_run_at') and acc['next_run_at'] <= now.isoformat()]
        
        return jsonify({
            'ok': True,
            'current_time': now.isoformat(),
            'due_now': len(due_now),
            'due_next_hour': len(upcoming_accounts),
            'upcoming_accounts': upcoming_accounts[:10]  # Limit to first 10
        })
        
    except Exception as e:
        logger.error(f"❌ Error getting scheduler status: {e}")
        return jsonify({
            'ok': False,
            'error': str(e)
        }), 500
