#!/usr/bin/env python3
"""
Stats Routes
Handles statistics and analytics endpoints
"""

import logging
from datetime import datetime, timedelta
from flask import Blueprint, request, jsonify
from database import DatabaseManager

logger = logging.getLogger(__name__)

stats = Blueprint('stats', __name__)

@stats.route('/api/stats/engagement', methods=['GET'])
def get_engagement_stats():
    """Get engagement statistics for the specified number of days"""
    try:
        days = request.args.get('days', 7, type=int)
        if days <= 0 or days > 365:
            return jsonify({
                "ok": False,
                "error": "Days parameter must be between 1 and 365"
            }), 400
        
        logger.info(f"📊 Getting engagement stats for {days} days")
        
        db = DatabaseManager()
        
        # Calculate date range
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)
        
        # Get posting history for the date range
        posting_history = db.get_posting_history()
        
        # Filter by date range and aggregate
        engagement_data = []
        daily_totals = {}
        
        for post in posting_history:
            try:
                post_date = datetime.fromisoformat(post.get('created_at', '').replace('Z', '+00:00'))
                if start_date <= post_date <= end_date:
                    date_key = post_date.strftime('%Y-%m-%d')
                    
                    if date_key not in daily_totals:
                        daily_totals[date_key] = {
                            'total_posts': 0,
                            'successful_posts': 0,
                            'failed_posts': 0
                        }
                    
                    daily_totals[date_key]['total_posts'] += 1
                    
                    if post.get('status') == 'success':
                        daily_totals[date_key]['successful_posts'] += 1
                    elif post.get('status') == 'failed':
                        daily_totals[date_key]['failed_posts'] += 1
                        
            except (ValueError, TypeError) as e:
                logger.warning(f"⚠️ Invalid date format in posting history: {e}")
                continue
        
        # Convert to series format
        for date_key in sorted(daily_totals.keys()):
            engagement_data.append({
                'date': date_key,
                'total_posts': daily_totals[date_key]['total_posts'],
                'successful_posts': daily_totals[date_key]['successful_posts'],
                'failed_posts': daily_totals[date_key]['failed_posts']
            })
        
        # Calculate overall totals
        total_posts = sum(day['total_posts'] for day in engagement_data)
        total_successful = sum(day['successful_posts'] for day in engagement_data)
        total_failed = sum(day['failed_posts'] for day in engagement_data)
        
        success_rate = (total_successful / total_posts * 100) if total_posts > 0 else 0
        
        return jsonify({
            "ok": True,
            "series": engagement_data,
            "totals": {
                "total_posts": total_posts,
                "successful_posts": total_successful,
                "failed_posts": total_failed,
                "success_rate": round(success_rate, 2)
            },
            "period": {
                "days": days,
                "start_date": start_date.isoformat(),
                "end_date": end_date.isoformat()
            }
        }), 200
        
    except Exception as e:
        logger.error(f"❌ Error getting engagement stats: {e}")
        return jsonify({
            "ok": False,
            "error": "Failed to get engagement statistics"
        }), 500

@stats.route('/api/stats/overview', methods=['GET'])
def get_stats_overview():
    """Get comprehensive statistics overview"""
    try:
        logger.info("📊 Getting stats overview")
        
        db = DatabaseManager()
        stats_data = db.get_statistics()
        
        return jsonify({
            "ok": True,
            "stats": stats_data,
            "timestamp": datetime.now().isoformat()
        }), 200
        
    except Exception as e:
        logger.error(f"❌ Error getting stats overview: {e}")
        return jsonify({
            "ok": False,
            "error": "Failed to get statistics overview"
        }), 500

@stats.route('/api/stats/accounts', methods=['GET'])
def get_account_stats():
    """Get account-specific statistics"""
    try:
        logger.info("📊 Getting account stats")
        
        db = DatabaseManager()
        accounts = db.get_active_accounts()
        
        account_stats = {
            "total_accounts": len(accounts),
            "enabled_accounts": len([a for a in accounts if a.get('status') == 'enabled']),
            "disabled_accounts": len([a for a in accounts if a.get('status') == 'disabled']),
            "accounts_with_recent_login": len([a for a in accounts if a.get('last_login')]),
            "accounts_with_recent_post": len([a for a in accounts if a.get('last_posted')])
        }
        
        return jsonify({
            "ok": True,
            "stats": account_stats,
            "timestamp": datetime.now().isoformat()
        }), 200
        
    except Exception as e:
        logger.error(f"❌ Error getting account stats: {e}")
        return jsonify({
            "ok": False,
            "error": "Failed to get account statistics"
        }), 500
