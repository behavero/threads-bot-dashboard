#!/usr/bin/env python3
"""
Database manager for Threads Bot
Handles all database operations with Supabase
"""

import os
import requests
from typing import List, Dict, Optional
from datetime import datetime

class DatabaseManager:
    def __init__(self):
        self.supabase_url = os.getenv('SUPABASE_URL')
        self.supabase_key = os.getenv('SUPABASE_KEY') or os.getenv('SUPABASE_SERVICE_ROLE_KEY')
        
        if not self.supabase_url or not self.supabase_key:
            print("❌ Supabase credentials not configured")
            print(f"SUPABASE_URL: {self.supabase_url}")
            print(f"SUPABASE_KEY exists: {bool(self.supabase_key)}")
            raise ValueError("Missing Supabase credentials")
        
        self.headers = {
            'apikey': self.supabase_key,
            'Authorization': f'Bearer {self.supabase_key}',
            'Content-Type': 'application/json',
            'Prefer': 'return=representation'
        }
        
        print("✅ Database manager initialized")
        print(f"✅ Supabase URL: {self.supabase_url}")
        print(f"✅ Using service role key: {bool(self.supabase_key)}")
    
    def get_active_accounts(self) -> List[Dict]:
        """Get all active accounts"""
        try:
            response = requests.get(
                f"{self.supabase_url}/rest/v1/accounts",
                headers=self.headers,
                params={'status': 'eq.enabled'}
            )
            if response.status_code == 200:
                return response.json()
            else:
                print(f"❌ HTTP {response.status_code}: {response.text}")
                return []
        except Exception as e:
            print(f"❌ Error fetching accounts: {e}")
            return []
    
    def add_account(self, username: str, password: str, user_id: str = None) -> bool:
        """Add a new account"""
        try:
            account_data = {
                "username": username,
                "password": password,
                "status": "enabled"
            }
            if user_id:
                account_data["user_id"] = user_id
                
            response = requests.post(
                f"{self.supabase_url}/rest/v1/accounts",
                json=account_data,
                headers=self.headers
            )
            return response.status_code == 201
        except Exception as e:
            print(f"❌ Error adding account: {e}")
            return False
    
    def get_all_captions(self) -> List[Dict]:
        """Get all captions"""
        try:
            response = requests.get(
                f"{self.supabase_url}/rest/v1/captions",
                headers=self.headers
            )
            if response.status_code == 200:
                return response.json()
            else:
                print(f"❌ HTTP {response.status_code}: {response.text}")
                return []
        except Exception as e:
            print(f"❌ Error fetching captions: {e}")
            return []
    
    def add_caption(self, text: str, category: str = 'general', tags: List[str] = None, user_id: str = None) -> bool:
        """Add a new caption"""
        try:
            caption_data = {
                "text": text,
                "category": category,
                "tags": tags or [],
                "used": False
            }
            if user_id:
                caption_data["user_id"] = user_id
                
            print(f"📝 Adding caption: {caption_data}")
            print(f"📝 Supabase URL: {self.supabase_url}")
            print(f"📝 Headers: {self.headers}")
                
            response = requests.post(
                f"{self.supabase_url}/rest/v1/captions",
                json=caption_data,
                headers=self.headers
            )
            
            print(f"📝 Response status: {response.status_code}")
            print(f"📝 Response text: {response.text}")
            
            if response.status_code != 201:
                print(f"❌ HTTP Error: {response.status_code}")
                print(f"❌ Response: {response.text}")
                return False
            
            return True
        except Exception as e:
            print(f"❌ Error adding caption: {e}")
            print(f"❌ Exception type: {type(e)}")
            import traceback
            print(f"❌ Traceback: {traceback.format_exc()}")
            return False
    
    def add_image(self, url: str, filename: str = None, size: int = None, type: str = None, user_id: str = None) -> bool:
        """Add a new image"""
        try:
            image_data = {
                "url": url,
                "used": False
            }
            if filename:
                image_data["filename"] = filename
            if size:
                image_data["size"] = size
            if type:
                image_data["type"] = type
            if user_id:
                image_data["user_id"] = user_id
                
            response = requests.post(
                f"{self.supabase_url}/rest/v1/images",
                json=image_data,
                headers=self.headers
            )
            return response.status_code == 201
        except Exception as e:
            print(f"❌ Error adding image: {e}")
            return False
    
    def get_all_images(self) -> List[Dict]:
        """Get all images"""
        try:
            response = requests.get(
                f"{self.supabase_url}/rest/v1/images",
                headers=self.headers
            )
            if response.status_code == 200:
                return response.json()
            else:
                print(f"❌ HTTP {response.status_code}: {response.text}")
                return []
        except Exception as e:
            print(f"❌ Error fetching images: {e}")
            return []
    
    def get_posting_history(self, account_id: Optional[int] = None) -> List[Dict]:
        """Get posting history"""
        try:
            params = {}
            if account_id:
                params['account_id'] = f'eq.{account_id}'
                
            response = requests.get(
                f"{self.supabase_url}/rest/v1/posting_history",
                headers=self.headers,
                params=params
            )
            if response.status_code == 200:
                return response.json()
            else:
                print(f"❌ HTTP {response.status_code}: {response.text}")
                return []
        except Exception as e:
            print(f"❌ Error fetching posting history: {e}")
            return []
    
    def add_posting_record(self, account_id: int, caption_id: Optional[int] = None, 
                          image_id: Optional[int] = None, status: str = 'pending') -> bool:
        """Add a posting record"""
        try:
            record_data = {
                "account_id": account_id,
                "status": status
            }
            if caption_id:
                record_data["caption_id"] = caption_id
            if image_id:
                record_data["image_id"] = image_id
                
            response = requests.post(
                f"{self.supabase_url}/rest/v1/posting_history",
                json=record_data,
                headers=self.headers
            )
            return response.status_code == 201
        except Exception as e:
            print(f"❌ Error adding posting record: {e}")
            return False
    
    def update_posting_record(self, record_id: int, status: str, error_message: str = None) -> bool:
        """Update a posting record"""
        try:
            update_data = {
                "status": status
            }
            if error_message:
                update_data["error_message"] = error_message
                
            response = requests.patch(
                f"{self.supabase_url}/rest/v1/posting_history?id=eq.{record_id}",
                json=update_data,
                headers=self.headers
            )
            return response.status_code == 204
        except Exception as e:
            print(f"❌ Error updating posting record: {e}")
            return False
    
    def get_statistics(self) -> Dict:
        """Get comprehensive statistics"""
        try:
            accounts = self.get_active_accounts()
            captions = self.get_all_captions()
            images = self.get_all_images()
            posting_history = self.get_posting_history()
            
            return {
                "total_accounts": len(accounts),
                "active_accounts": len([a for a in accounts if a.get('status') == 'enabled']),
                "total_captions": len(captions),
                "unused_captions": len([c for c in captions if not c.get('used')]),
                "total_images": len(images),
                "unused_images": len([i for i in images if not i.get('used')]),
                "total_posts": len(posting_history),
                "successful_posts": len([p for p in posting_history if p.get('status') == 'success']),
                "failed_posts": len([p for p in posting_history if p.get('status') == 'failed']),
                "last_updated": datetime.now().isoformat()
            }
        except Exception as e:
            print(f"❌ Error getting statistics: {e}")
            return {} 