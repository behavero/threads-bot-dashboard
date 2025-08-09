#!/usr/bin/env python3
"""
Autopilot Routes
Handles automated posting with idempotent tick endpoint
"""

import os
import logging
from datetime import datetime, timedelta
from flask import Blueprint, request, jsonify
from services.autopilot import autopilot_service
from database import DatabaseManager

logger = logging.getLogger(__name__)
autopilot = Blueprint('autopilot', __name__)

def acquire_lock(lock_id: str, timeout_seconds: int = 30) -> bool:
    """Poor-man's lock using database"""
    try:
        db = DatabaseManager()
        now = datetime.now()
        expires_at = now + timedelta(seconds=timeout_seconds)
        
        # Try to insert lock
        lock_data = {
            'id': lock_id,
            'locked_at': now.isoformat(),
            'expires_at': expires_at.isoformat()
        }
        
        response = db._make_request(
            'POST',
            f"{db.supabase_url}/rest/v1/autopilot_locks",
            json=lock_data
        )
        
        if response.status_code == 201:
            logger.info(f"🔒 Acquired lock: {lock_id}")
            return True
        else:
            # Check if lock exists and is expired
            response = db._make_request(
                'GET',
                f"{db.supabase_url}/rest/v1/autopilot_locks",
                params={'id': f'eq.{lock_id}'}
            )
            
            if response.status_code == 200:
                locks = response.json()
                if locks:
                    lock = locks[0]
                    lock_expires = datetime.fromisoformat(lock['expires_at'])
                    
                    if now > lock_expires:
                        # Lock expired, delete and try again
                        logger.info(f"🔓 Lock expired, deleting: {lock_id}")
                        db._make_request(
                            'DELETE',
                            f"{db.supabase_url}/rest/v1/autopilot_locks?id=eq.{lock_id}"
                        )
                        
                        # Try to acquire again
                        response = db._make_request(
                            'POST',
                            f"{db.supabase_url}/rest/v1/autopilot_locks",
                            json=lock_data
                        )
                        
                        if response.status_code == 201:
                            logger.info(f"🔒 Acquired lock after cleanup: {lock_id}")
                            return True
            
            logger.warning(f"⚠️ Could not acquire lock: {lock_id}")
            return False
            
    except Exception as e:
        logger.error(f"❌ Error acquiring lock: {e}")
        return False

def release_lock(lock_id: str) -> bool:
    """Release the lock"""
    try:
        db = DatabaseManager()
        response = db._make_request(
            'DELETE',
            f"{db.supabase_url}/rest/v1/autopilot_locks?id=eq.{lock_id}"
        )
        
        if response.status_code == 204:
            logger.info(f"🔓 Released lock: {lock_id}")
            return True
        else:
            logger.warning(f"⚠️ Could not release lock: {lock_id}")
            return False
            
    except Exception as e:
        logger.error(f"❌ Error releasing lock: {e}")
        return False

@autopilot.route('/tick', methods=['POST'])
def tick():
    """Idempotent tick endpoint for autopilot posting"""
    lock_id = "autopilot:tick"
    
    # Try to acquire lock
    if not acquire_lock(lock_id):
        return jsonify({
            'ok': False,
            'error': 'Another autopilot tick is already running',
            'processed': 0,
            'timestamp': datetime.now().isoformat()
        }), 409
    
    try:
        logger.info("🚀 Starting autopilot tick")
        now = datetime.now()
        
        # Get due accounts
        due_accounts = autopilot_service.due_accounts(now)
        
        if not due_accounts:
            logger.info("📭 No due accounts found")
            return jsonify({
                'ok': True,
                'processed': 0,
                'message': 'No due accounts found',
                'timestamp': now.isoformat()
            })
        
        logger.info(f"📝 Processing {len(due_accounts)} due accounts")
        
        results = []
        successes = 0
        failures = 0
        
        for account in due_accounts:
            try:
                account_id = account['id']
                username = account['username']
                
                logger.info(f"📝 Processing account {account_id} ({username})")
                
                # Pick content
                caption = autopilot_service.pick_caption()
                if not caption:
                    logger.warning(f"⚠️ No caption available for account {account_id}")
                    results.append({
                        'account_id': account_id,
                        'username': username,
                        'status': 'failed',
                        'error': 'No caption available'
                    })
                    failures += 1
                    continue
                
                image = autopilot_service.pick_image()
                if image:
                    logger.info(f"🖼️ Using image: {image['id']}")
                
                # Post content
                success, message = autopilot_service.post_once(account, caption, image)
                
                # Record history
                autopilot_service.record_posting_history(
                    account_id=account_id,
                    caption_id=caption['id'],
                    image_id=image['id'] if image else None,
                    success=success,
                    message=message
                )
                
                # Mark caption as used if successful
                if success:
                    autopilot_service.mark_caption_used(caption['id'])
                
                # Update account stats
                autopilot_service.update_account_posting_stats(account_id, success)
                
                # Schedule next run
                autopilot_service.schedule_next(account)
                
                # Record result
                result = {
                    'account_id': account_id,
                    'username': username,
                    'status': 'success' if success else 'failed',
                    'caption_id': caption['id'],
                    'image_id': image['id'] if image else None,
                    'message': message
                }
                
                results.append(result)
                
                if success:
                    successes += 1
                    logger.info(f"✅ Posted successfully for account {account_id}")
                else:
                    failures += 1
                    logger.error(f"❌ Failed to post for account {account_id}: {message}")
                
            except Exception as e:
                logger.error(f"❌ Error processing account {account.get('id')}: {e}")
                results.append({
                    'account_id': account.get('id'),
                    'username': account.get('username'),
                    'status': 'failed',
                    'error': str(e)
                })
                failures += 1
        
        # Clean up expired locks
        cleanup_expired_locks()
        
        logger.info(f"✅ Autopilot tick completed: {successes} successes, {failures} failures")
        
        return jsonify({
            'ok': True,
            'processed': len(due_accounts),
            'successes': successes,
            'failures': failures,
            'results': results,
            'timestamp': now.isoformat()
        })
        
    except Exception as e:
        logger.error(f"❌ Error in autopilot tick: {e}")
        return jsonify({
            'ok': False,
            'error': str(e),
            'processed': 0,
            'timestamp': datetime.now().isoformat()
        }), 500
        
    finally:
        # Always release lock
        release_lock(lock_id)

def cleanup_expired_locks():
    """Clean up expired locks"""
    try:
        db = DatabaseManager()
        now = datetime.now()
        
        response = db._make_request(
            'DELETE',
            f"{db.supabase_url}/rest/v1/autopilot_locks",
            params={'expires_at': f'lt.{now.isoformat()}'}
        )
        
        if response.status_code == 204:
            logger.info("🧹 Cleaned up expired locks")
            
    except Exception as e:
        logger.error(f"❌ Error cleaning up locks: {e}")

@autopilot.route('/status', methods=['GET'])
def status():
    """Get autopilot status"""
    try:
        db = DatabaseManager()
        now = datetime.now()
        
        # Get autopilot-enabled accounts
        response = db._make_request(
            'GET',
            f"{db.supabase_url}/rest/v1/accounts",
            params={
                'autopilot_enabled': 'eq.true',
                'select': 'id,username,next_run_at,last_posted_at,cadence_minutes,jitter_seconds'
            }
        )
        
        if response.status_code == 200:
            accounts = response.json()
            
            # Calculate stats
            total_accounts = len(accounts)
            due_accounts = len([a for a in accounts if a.get('next_run_at') and 
                              datetime.fromisoformat(a['next_run_at']) <= now])
            
            return jsonify({
                'ok': True,
                'total_accounts': total_accounts,
                'due_accounts': due_accounts,
                'timestamp': now.isoformat()
            })
        else:
            return jsonify({
                'ok': False,
                'error': 'Failed to fetch accounts'
            }), 500
            
    except Exception as e:
        logger.error(f"❌ Error getting autopilot status: {e}")
        return jsonify({
            'ok': False,
            'error': str(e)
        }), 500

@autopilot.route('/accounts/<int:account_id>/enable', methods=['POST'])
def enable_autopilot(account_id):
    """Enable autopilot for an account"""
    try:
        data = request.get_json() or {}
        cadence_minutes = data.get('cadence_minutes', 10)
        jitter_seconds = data.get('jitter_seconds', 60)
        
        db = DatabaseManager()
        now = datetime.now()
        
        # Calculate initial next_run_at
        next_run = now + timedelta(minutes=cadence_minutes)
        
        update_data = {
            'autopilot_enabled': True,
            'cadence_minutes': cadence_minutes,
            'jitter_seconds': jitter_seconds,
            'next_run_at': next_run.isoformat(),
            'updated_at': now.isoformat()
        }
        
        if db.update_account(account_id, update_data):
            logger.info(f"✅ Enabled autopilot for account {account_id}")
            return jsonify({
                'ok': True,
                'account_id': account_id,
                'next_run_at': next_run.isoformat(),
                'message': 'Autopilot enabled'
            })
        else:
            return jsonify({
                'ok': False,
                'error': 'Failed to enable autopilot'
            }), 500
            
    except Exception as e:
        logger.error(f"❌ Error enabling autopilot: {e}")
        return jsonify({
            'ok': False,
            'error': str(e)
        }), 500

@autopilot.route('/accounts/<int:account_id>/disable', methods=['POST'])
def disable_autopilot(account_id):
    """Disable autopilot for an account"""
    try:
        db = DatabaseManager()
        now = datetime.now()
        
        update_data = {
            'autopilot_enabled': False,
            'next_run_at': None,
            'updated_at': now.isoformat()
        }
        
        if db.update_account(account_id, update_data):
            logger.info(f"✅ Disabled autopilot for account {account_id}")
            return jsonify({
                'ok': True,
                'account_id': account_id,
                'message': 'Autopilot disabled'
            })
        else:
            return jsonify({
                'ok': False,
                'error': 'Failed to disable autopilot'
            }), 500
            
    except Exception as e:
        logger.error(f"❌ Error disabling autopilot: {e}")
        return jsonify({
            'ok': False,
            'error': str(e)
        }), 500
