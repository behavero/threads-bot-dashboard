#!/usr/bin/env python3
"""
Engagement Tracker for Threads Bot
Fetches and stores engagement data from Threads API
"""

import os
import asyncio
import aiohttp
from datetime import datetime, timedelta
from typing import List, Dict, Optional
from database import DatabaseManager
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class EngagementTracker:
    def __init__(self):
        self.db = DatabaseManager()
        self.threads_api_base = "https://www.threads.net/api/v1"
        
    async def fetch_account_posts(self, account: Dict) -> List[Dict]:
        """Fetch posts for a specific account"""
        try:
            # This is a mock implementation - replace with actual Threads API
            # For now, we'll simulate engagement data
            username = account.get('username')
            logger.info(f"Fetching posts for account: {username}")
            
            # Simulate API call delay
            await asyncio.sleep(0.1)
            
            # Mock data - replace with actual Threads API integration
            mock_posts = [
                {
                    'id': f'post_{username}_1',
                    'date': (datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d'),
                    'likes': 150,
                    'replies': 25,
                    'reposts': 10,
                    'quotes': 5
                },
                {
                    'id': f'post_{username}_2',
                    'date': (datetime.now() - timedelta(days=2)).strftime('%Y-%m-%d'),
                    'likes': 200,
                    'replies': 30,
                    'reposts': 15,
                    'quotes': 8
                },
                {
                    'id': f'post_{username}_3',
                    'date': (datetime.now() - timedelta(days=3)).strftime('%Y-%m-%d'),
                    'likes': 180,
                    'replies': 20,
                    'reposts': 12,
                    'quotes': 6
                }
            ]
            
            return mock_posts
            
        except Exception as e:
            logger.error(f"Error fetching posts for account {account.get('username')}: {e}")
            return []
    
    def calculate_engagement(self, post: Dict) -> Dict:
        """Calculate total engagement for a post"""
        likes = post.get('likes', 0)
        replies = post.get('replies', 0)
        reposts = post.get('reposts', 0)
        quotes = post.get('quotes', 0)
        
        total_engagement = likes + replies + reposts + quotes
        
        return {
            'date': post.get('date'),
            'likes': likes,
            'replies': replies,
            'reposts': reposts,
            'quotes': quotes,
            'total_engagement': total_engagement
        }
    
    async def aggregate_daily_engagement(self, account_id: int, posts: List[Dict]) -> Dict:
        """Aggregate engagement data by date"""
        daily_data = {}
        
        for post in posts:
            engagement = self.calculate_engagement(post)
            date = engagement['date']
            
            if date not in daily_data:
                daily_data[date] = {
                    'likes': 0,
                    'replies': 0,
                    'reposts': 0,
                    'quotes': 0,
                    'total_engagement': 0,
                    'post_count': 0
                }
            
            daily_data[date]['likes'] += engagement['likes']
            daily_data[date]['replies'] += engagement['replies']
            daily_data[date]['reposts'] += engagement['reposts']
            daily_data[date]['quotes'] += engagement['quotes']
            daily_data[date]['total_engagement'] += engagement['total_engagement']
            daily_data[date]['post_count'] += 1
        
        return daily_data
    
    async def store_daily_engagement(self, account_id: int, daily_data: Dict):
        """Store daily engagement data in database"""
        try:
            for date, data in daily_data.items():
                engagement_record = {
                    'account_id': account_id,
                    'date': date,
                    'total_engagement': data['total_engagement'],
                    'likes': data['likes'],
                    'replies': data['replies'],
                    'reposts': data['reposts'],
                    'quotes': data['quotes'],
                    'post_count': data['post_count'],
                    'updated_at': datetime.now().isoformat()
                }
                
                # Use upsert to handle existing records
                if hasattr(self.db, 'use_supabase_client') and self.db.use_supabase_client:
                    # Use Supabase client
                    self.db.supabase.table("daily_engagement").upsert(
                        engagement_record,
                        on_conflict="account_id,date"
                    ).execute()
                else:
                    # Use HTTP requests
                    import requests
                    response = requests.post(
                        f"{self.db.supabase_url}/rest/v1/daily_engagement",
                        json=engagement_record,
                        headers=self.db.headers
                    )
                    
                    if response.status_code == 409:  # Conflict, update existing
                        requests.patch(
                            f"{self.db.supabase_url}/rest/v1/daily_engagement",
                            json=engagement_record,
                            params={"account_id": f"eq.{account_id}", "date": f"eq.{date}"},
                            headers=self.db.headers
                        )
                
            logger.info(f"Stored engagement data for account {account_id}")
            
        except Exception as e:
            logger.error(f"Error storing engagement data for account {account_id}: {e}")
    
    async def refresh_engagement_data(self, days_back: int = 7) -> Dict:
        """Refresh engagement data for all accounts"""
        try:
            logger.info("Starting engagement data refresh...")
            
            # Get all active accounts
            accounts = self.db.get_active_accounts()
            logger.info(f"Found {len(accounts)} active accounts")
            
            total_processed = 0
            total_errors = 0
            
            for account in accounts:
                try:
                    account_id = account.get('id')
                    username = account.get('username')
                    
                    logger.info(f"Processing account: {username}")
                    
                    # Fetch posts for this account
                    posts = await self.fetch_account_posts(account)
                    
                    if posts:
                        # Aggregate daily engagement
                        daily_data = await self.aggregate_daily_engagement(account_id, posts)
                        
                        # Store in database
                        await self.store_daily_engagement(account_id, daily_data)
                        
                        total_processed += 1
                        logger.info(f"Successfully processed {username}")
                    else:
                        logger.warning(f"No posts found for {username}")
                        
                except Exception as e:
                    total_errors += 1
                    logger.error(f"Error processing account {account.get('username')}: {e}")
            
            result = {
                'success': True,
                'total_accounts': len(accounts),
                'processed': total_processed,
                'errors': total_errors,
                'timestamp': datetime.now().isoformat()
            }
            
            logger.info(f"Engagement refresh completed: {result}")
            return result
            
        except Exception as e:
            logger.error(f"Error in engagement refresh: {e}")
            return {
                'success': False,
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            }
    
    def get_daily_engagement_stats(self, days: int = 7) -> Dict:
        """Get aggregated daily engagement statistics"""
        try:
            if hasattr(self.db, 'use_supabase_client') and self.db.use_supabase_client:
                # Use Supabase client
                response = self.db.supabase.table("daily_engagement").select("*").execute()
                data = response.data if response.data else []
            else:
                # Use HTTP requests
                import requests
                response = requests.get(
                    f"{self.db.supabase_url}/rest/v1/daily_engagement",
                    headers=self.db.headers
                )
                data = response.json() if response.status_code == 200 else []
            
            # Aggregate by date
            daily_stats = {}
            for record in data:
                date = record.get('date')
                if date not in daily_stats:
                    daily_stats[date] = {
                        'total_engagement': 0,
                        'likes': 0,
                        'replies': 0,
                        'reposts': 0,
                        'quotes': 0,
                        'post_count': 0,
                        'account_count': 0
                    }
                
                daily_stats[date]['total_engagement'] += record.get('total_engagement', 0)
                daily_stats[date]['likes'] += record.get('likes', 0)
                daily_stats[date]['replies'] += record.get('replies', 0)
                daily_stats[date]['reposts'] += record.get('reposts', 0)
                daily_stats[date]['quotes'] += record.get('quotes', 0)
                daily_stats[date]['post_count'] += record.get('post_count', 0)
                daily_stats[date]['account_count'] += 1
            
            # Convert to sorted list
            sorted_stats = []
            for date, stats in sorted(daily_stats.items(), reverse=True):
                sorted_stats.append({
                    'date': date,
                    **stats
                })
            
            return {
                'success': True,
                'data': sorted_stats[:days],
                'total_days': len(sorted_stats)
            }
            
        except Exception as e:
            logger.error(f"Error getting engagement stats: {e}")
            return {
                'success': False,
                'error': str(e),
                'data': []
            }

# Global tracker instance
engagement_tracker = EngagementTracker() 