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
        print(f"✅ Headers configured: {list(self.headers.keys())}")
    
    def get_active_accounts(self) -> List[Dict]:
        """Get all active accounts"""
        try:
            print("🔍 get_active_accounts: Starting request...")
            print(f"🔍 get_active_accounts: Supabase URL: {self.supabase_url}")
            print(f"🔍 get_active_accounts: Headers: {self.headers}")
            
            # First try without filter to see all accounts
            print("🔍 get_active_accounts: Fetching all accounts (no filter)...")
            response = requests.get(
                f"{self.supabase_url}/rest/v1/accounts",
                headers=self.headers
            )
            
            print(f"🔍 get_active_accounts: Response status: {response.status_code}")
            print(f"🔍 get_active_accounts: Response headers: {dict(response.headers)}")
            print(f"🔍 get_active_accounts: Response text: {response.text[:500]}...")
            
            if response.status_code == 200:
                accounts = response.json()
                print(f"🔍 get_active_accounts: Retrieved {len(accounts)} total accounts")
                
                if accounts:
                    print(f"🔍 get_active_accounts: Sample account: {accounts[0]}")
                    # Check if accounts have status field
                    if 'status' in accounts[0]:
                        print(f"🔍 get_active_accounts: Accounts have status field")
                        # Filter for enabled accounts
                        enabled_accounts = [a for a in accounts if a.get('status') == 'enabled']
                        print(f"🔍 get_active_accounts: Found {len(enabled_accounts)} enabled accounts")
                        return enabled_accounts
                    else:
                        print(f"🔍 get_active_accounts: Accounts don't have status field, returning all")
                        return accounts
                else:
                    print(f"🔍 get_active_accounts: No accounts found")
                    return []
            else:
                print(f"❌ get_active_accounts: HTTP {response.status_code}: {response.text}")
                return []
        except Exception as e:
            print(f"❌ get_active_accounts: Error fetching accounts: {e}")
            import traceback
            print(f"❌ get_active_accounts: Traceback: {traceback.format_exc()}")
            return []
    
    def get_account_by_username(self, username: str) -> Optional[Dict]:
        """Get account by username"""
        try:
            print(f"🔍 get_account_by_username: Looking for username '{username}'")
            
            response = requests.get(
                f"{self.supabase_url}/rest/v1/accounts",
                headers=self.headers,
                params={'username': f'eq.{username}'}
            )
            
            print(f"🔍 get_account_by_username: Response status: {response.status_code}")
            
            if response.status_code == 200:
                accounts = response.json()
                if accounts:
                    print(f"🔍 get_account_by_username: Found account: {accounts[0]}")
                    return accounts[0]
                else:
                    print(f"🔍 get_account_by_username: No account found for username '{username}'")
                    return None
            else:
                print(f"❌ get_account_by_username: HTTP {response.status_code}: {response.text}")
                return None
        except Exception as e:
            print(f"❌ get_account_by_username: Error: {e}")
            return None
    
    def add_account(self, account_data: dict) -> Optional[int]:
        """Add a new account with dictionary data"""
        try:
            print(f"🔍 add_account: Creating account with data: {account_data}")
            
            # Ensure required fields
            if 'username' not in account_data:
                print("❌ add_account: Missing username in account data")
                return None
                
            # Set default values
            if 'status' not in account_data:
                account_data['status'] = 'enabled'
            if 'created_at' not in account_data:
                account_data['created_at'] = datetime.now().isoformat()
                
            response = requests.post(
                f"{self.supabase_url}/rest/v1/accounts",
                json=account_data,
                headers=self.headers
            )
            
            print(f"🔍 add_account: Response status: {response.status_code}")
            print(f"🔍 add_account: Response text: {response.text}")
            
            if response.status_code == 201:
                # Try to get the created account ID from response
                try:
                    created_account = response.json()
                    if isinstance(created_account, list) and len(created_account) > 0:
                        account_id = created_account[0].get('id')
                        print(f"🔍 add_account: Created account with ID: {account_id}")
                        return account_id
                    elif isinstance(created_account, dict):
                        account_id = created_account.get('id')
                        print(f"🔍 add_account: Created account with ID: {account_id}")
                        return account_id
                except Exception as e:
                    print(f"🔍 add_account: Could not parse response for account ID: {e}")
                    return True  # Success but no ID returned
            else:
                print(f"❌ add_account: HTTP {response.status_code}: {response.text}")
                return None
        except Exception as e:
            print(f"❌ Error adding account: {e}")
            return None
    
    def save_session_data(self, account_id: int, session_data: dict) -> bool:
        """Save session data for an account"""
        try:
            print(f"🔍 save_session_data: Saving session for account {account_id}")
            
            response = requests.patch(
                f"{self.supabase_url}/rest/v1/accounts?id=eq.{account_id}",
                json={"session_data": session_data},
                headers=self.headers
            )
            
            print(f"🔍 save_session_data: Response status: {response.status_code}")
            return response.status_code == 204
        except Exception as e:
            print(f"❌ Error saving session data: {e}")
            return False
    
    def get_session_data(self, account_id: int) -> Optional[dict]:
        """Get session data for an account"""
        try:
            print(f"🔍 get_session_data: Getting session for account {account_id}")
            
            response = requests.get(
                f"{self.supabase_url}/rest/v1/accounts",
                headers=self.headers,
                params={'id': f'eq.{account_id}'}
            )
            
            if response.status_code == 200:
                accounts = response.json()
                if accounts and accounts[0].get('session_data'):
                    print(f"🔍 get_session_data: Found session data for account {account_id}")
                    return accounts[0]['session_data']
                else:
                    print(f"🔍 get_session_data: No session data found for account {account_id}")
                    return None
            else:
                print(f"❌ get_session_data: HTTP {response.status_code}: {response.text}")
                return None
        except Exception as e:
            print(f"❌ Error getting session data: {e}")
            return None
    
    def get_unused_caption(self) -> Optional[Dict]:
        """Get a random unused caption"""
        try:
            print("🔍 get_unused_caption: Fetching unused caption...")
            
            response = requests.get(
                f"{self.supabase_url}/rest/v1/captions",
                headers=self.headers,
                params={'used': 'eq.false'}
            )
            
            if response.status_code == 200:
                captions = response.json()
                if captions:
                    # Pick a random caption
                    import random
                    caption = random.choice(captions)
                    print(f"🔍 get_unused_caption: Selected caption: {caption['id']}")
                    return caption
                else:
                    print("🔍 get_unused_caption: No unused captions found")
                    return None
            else:
                print(f"❌ get_unused_caption: HTTP {response.status_code}: {response.text}")
                return None
        except Exception as e:
            print(f"❌ Error getting unused caption: {e}")
            return None
    
    def get_unused_image(self) -> Optional[Dict]:
        """Get a random unused image"""
        try:
            print("🔍 get_unused_image: Fetching unused image...")
            
            response = requests.get(
                f"{self.supabase_url}/rest/v1/images",
                headers=self.headers,
                params={'used': 'eq.false'}
            )
            
            if response.status_code == 200:
                images = response.json()
                if images:
                    # Pick a random image
                    import random
                    image = random.choice(images)
                    print(f"🔍 get_unused_image: Selected image: {image['id']}")
                    return image
                else:
                    print("🔍 get_unused_image: No unused images found")
                    return None
            else:
                print(f"❌ get_unused_image: HTTP {response.status_code}: {response.text}")
                return None
        except Exception as e:
            print(f"❌ Error getting unused image: {e}")
            return None
    
    def mark_caption_used(self, caption_id: int) -> bool:
        """Mark a caption as used"""
        try:
            print(f"🔍 mark_caption_used: Marking caption {caption_id} as used")
            
            response = requests.patch(
                f"{self.supabase_url}/rest/v1/captions?id=eq.{caption_id}",
                json={"used": True},
                headers=self.headers
            )
            
            print(f"🔍 mark_caption_used: Response status: {response.status_code}")
            return response.status_code == 204
        except Exception as e:
            print(f"❌ Error marking caption as used: {e}")
            return False
    
    def mark_image_used(self, image_id: int) -> bool:
        """Mark an image as used"""
        try:
            print(f"🔍 mark_image_used: Marking image {image_id} as used")
            
            response = requests.patch(
                f"{self.supabase_url}/rest/v1/images?id=eq.{image_id}",
                json={"used": True},
                headers=self.headers
            )
            
            print(f"🔍 mark_image_used: Response status: {response.status_code}")
            return response.status_code == 204
        except Exception as e:
            print(f"❌ Error marking image as used: {e}")
            return False
    
    def update_account_last_posted(self, account_id: int) -> bool:
        """Update account's last_posted timestamp"""
        try:
            print(f"🔍 update_account_last_posted: Updating account {account_id}")
            
            from datetime import datetime
            response = requests.patch(
                f"{self.supabase_url}/rest/v1/accounts?id=eq.{account_id}",
                json={"last_posted": datetime.now().isoformat()},
                headers=self.headers
            )
            
            print(f"🔍 update_account_last_posted: Response status: {response.status_code}")
            return response.status_code == 204
        except Exception as e:
            print(f"❌ Error updating account last_posted: {e}")
            return False
    
    def update_account_last_login(self, account_id: int) -> bool:
        """Update account's last_login timestamp"""
        try:
            print(f"🔍 update_account_last_login: Updating account {account_id}")
            
            from datetime import datetime
            response = requests.patch(
                f"{self.supabase_url}/rest/v1/accounts?id=eq.{account_id}",
                json={"last_login": datetime.now().isoformat()},
                headers=self.headers
            )
            
            print(f"🔍 update_account_last_login: Response status: {response.status_code}")
            return response.status_code == 204
        except Exception as e:
            print(f"❌ Error updating account last_login: {e}")
            return False
    
    def update_account(self, account_id: int, data: dict) -> bool:
        """Update an existing account"""
        try:
            print(f"🔍 update_account: Updating account {account_id} with data: {data}")
            
            response = requests.patch(
                f"{self.supabase_url}/rest/v1/accounts?id=eq.{account_id}",
                json=data,
                headers=self.headers
            )
            
            print(f"🔍 update_account: Response status: {response.status_code}")
            print(f"🔍 update_account: Response text: {response.text}")
            
            return response.status_code == 204
        except Exception as e:
            print(f"❌ Error updating account: {e}")
            return False
    
    def delete_account(self, account_id: int) -> bool:
        """Delete an account"""
        try:
            print(f"🔍 delete_account: Deleting account {account_id}")
            
            response = requests.delete(
                f"{self.supabase_url}/rest/v1/accounts?id=eq.{account_id}",
                headers=self.headers
            )
            
            print(f"🔍 delete_account: Response status: {response.status_code}")
            print(f"🔍 delete_account: Response text: {response.text}")
            
            return response.status_code == 204
        except Exception as e:
            print(f"❌ Error deleting account: {e}")
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
            print(f"📝 Request URL: {self.supabase_url}/rest/v1/captions")
                
            response = requests.post(
                f"{self.supabase_url}/rest/v1/captions",
                json=caption_data,
                headers=self.headers
            )
            
            print(f"📝 Response status: {response.status_code}")
            print(f"📝 Response text: {response.text}")
            print(f"📝 Response headers: {dict(response.headers)}")
            
            if response.status_code != 201:
                print(f"❌ HTTP Error: {response.status_code}")
                print(f"❌ Response: {response.text}")
                return False
            
            print("✅ Caption added successfully")
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
    
    def delete_image(self, image_id: int) -> bool:
        """Delete an image"""
        try:
            response = requests.delete(
                f"{self.supabase_url}/rest/v1/images?id=eq.{image_id}",
                headers=self.headers
            )
            return response.status_code == 204
        except Exception as e:
            print(f"❌ Error deleting image: {e}")
            return False
    
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

    # Data Deletion Methods for Meta Compliance
    def delete_accounts_by_user_id(self, user_id: str) -> int:
        """Delete all accounts associated with a user_id"""
        try:
            print(f"🗑️ delete_accounts_by_user_id: Deleting accounts for user_id: {user_id}")
            
            # In a real implementation, you'd have a user_id field in accounts table
            # For now, we'll delete based on some identifier or pattern
            # This is a placeholder implementation
            
            response = requests.delete(
                f"{self.supabase_url}/rest/v1/accounts",
                headers=self.headers,
                params={'user_id': f'eq.{user_id}'}
            )
            
            print(f"🗑️ delete_accounts_by_user_id: Response status: {response.status_code}")
            
            if response.status_code == 200:
                deleted_count = len(response.json()) if response.json() else 0
                print(f"🗑️ delete_accounts_by_user_id: Deleted {deleted_count} accounts")
                return deleted_count
            else:
                print(f"❌ delete_accounts_by_user_id: HTTP {response.status_code}: {response.text}")
                return 0
        except Exception as e:
            print(f"❌ delete_accounts_by_user_id: Error: {e}")
            return 0

    def delete_posting_history_by_user_id(self, user_id: str) -> int:
        """Delete all posting history associated with a user_id"""
        try:
            print(f"🗑️ delete_posting_history_by_user_id: Deleting posting history for user_id: {user_id}")
            
            response = requests.delete(
                f"{self.supabase_url}/rest/v1/posting_history",
                headers=self.headers,
                params={'user_id': f'eq.{user_id}'}
            )
            
            print(f"🗑️ delete_posting_history_by_user_id: Response status: {response.status_code}")
            
            if response.status_code == 200:
                deleted_count = len(response.json()) if response.json() else 0
                print(f"🗑️ delete_posting_history_by_user_id: Deleted {deleted_count} posting records")
                return deleted_count
            else:
                print(f"❌ delete_posting_history_by_user_id: HTTP {response.status_code}: {response.text}")
                return 0
        except Exception as e:
            print(f"❌ delete_posting_history_by_user_id: Error: {e}")
            return 0

    def delete_captions_by_user_id(self, user_id: str) -> int:
        """Delete all captions associated with a user_id"""
        try:
            print(f"🗑️ delete_captions_by_user_id: Deleting captions for user_id: {user_id}")
            
            response = requests.delete(
                f"{self.supabase_url}/rest/v1/captions",
                headers=self.headers,
                params={'user_id': f'eq.{user_id}'}
            )
            
            print(f"🗑️ delete_captions_by_user_id: Response status: {response.status_code}")
            
            if response.status_code == 200:
                deleted_count = len(response.json()) if response.json() else 0
                print(f"🗑️ delete_captions_by_user_id: Deleted {deleted_count} captions")
                return deleted_count
            else:
                print(f"❌ delete_captions_by_user_id: HTTP {response.status_code}: {response.text}")
                return 0
        except Exception as e:
            print(f"❌ delete_captions_by_user_id: Error: {e}")
            return 0

    def delete_images_by_user_id(self, user_id: str) -> int:
        """Delete all images associated with a user_id"""
        try:
            print(f"🗑️ delete_images_by_user_id: Deleting images for user_id: {user_id}")
            
            response = requests.delete(
                f"{self.supabase_url}/rest/v1/images",
                headers=self.headers,
                params={'user_id': f'eq.{user_id}'}
            )
            
            print(f"🗑️ delete_images_by_user_id: Response status: {response.status_code}")
            
            if response.status_code == 200:
                deleted_count = len(response.json()) if response.json() else 0
                print(f"🗑️ delete_images_by_user_id: Deleted {deleted_count} images")
                return deleted_count
            else:
                print(f"❌ delete_images_by_user_id: HTTP {response.status_code}: {response.text}")
                return 0
        except Exception as e:
            print(f"❌ delete_images_by_user_id: Error: {e}")
            return 0

    def delete_sessions_by_user_id(self, user_id: str) -> int:
        """Delete all sessions associated with a user_id from Supabase Storage"""
        try:
            print(f"🗑️ delete_sessions_by_user_id: Deleting sessions for user_id: {user_id}")
            
            # Delete from Supabase Storage
            # This would require the Supabase Storage Admin SDK
            # For now, we'll return a placeholder count
            
            print(f"🗑️ delete_sessions_by_user_id: Sessions deletion placeholder - would delete sessions for user_id: {user_id}")
            return 0  # Placeholder - implement with actual storage deletion
        except Exception as e:
            print(f"❌ delete_sessions_by_user_id: Error: {e}")
            return 0

    # Token Management Methods for Threads API
    def save_token(self, account_id: int, token_data: dict) -> bool:
        """Save or update token for an account"""
        try:
            print(f"💾 save_token: Saving token for account {account_id}")
            
            # Check if token already exists
            existing_token = self.get_token_by_account_id(account_id)
            
            if existing_token:
                # Update existing token
                response = requests.patch(
                    f"{self.supabase_url}/rest/v1/tokens",
                    headers=self.headers,
                    params={'account_id': f'eq.{account_id}'},
                    json=token_data
                )
            else:
                # Create new token
                token_data['account_id'] = account_id
                response = requests.post(
                    f"{self.supabase_url}/rest/v1/tokens",
                    headers=self.headers,
                    json=token_data
                )
            
            if response.status_code in [200, 201, 204]:
                print(f"✅ save_token: Token saved for account {account_id}")
                return True
            else:
                print(f"❌ save_token: Failed to save token for account {account_id}: {response.status_code} - {response.text}")
                return False
                
        except Exception as e:
            print(f"❌ save_token: Error: {e}")
            return False

    def get_token_by_account_id(self, account_id: int) -> Optional[dict]:
        """Get token data for an account"""
        try:
            print(f"🔍 get_token_by_account_id: Getting token for account {account_id}")
            
            response = requests.get(
                f"{self.supabase_url}/rest/v1/tokens",
                headers=self.headers,
                params={'account_id': f'eq.{account_id}'}
            )
            
            if response.status_code == 200:
                tokens = response.json()
                if tokens:
                    print(f"✅ get_token_by_account_id: Token found for account {account_id}")
                    return tokens[0]
                else:
                    print(f"📂 get_token_by_account_id: No token found for account {account_id}")
                    return None
            else:
                print(f"❌ get_token_by_account_id: HTTP {response.status_code}: {response.text}")
                return None
                
        except Exception as e:
            print(f"❌ get_token_by_account_id: Error: {e}")
            return None

    def update_token(self, account_id: int, token_data: dict) -> bool:
        """Update token data for an account"""
        try:
            print(f"🔄 update_token: Updating token for account {account_id}")
            
            response = requests.patch(
                f"{self.supabase_url}/rest/v1/tokens",
                headers=self.headers,
                params={'account_id': f'eq.{account_id}'},
                json=token_data
            )
            
            if response.status_code in [200, 204]:
                print(f"✅ update_token: Token updated for account {account_id}")
                return True
            else:
                print(f"❌ update_token: Failed to update token for account {account_id}: {response.status_code} - {response.text}")
                return False
                
        except Exception as e:
            print(f"❌ update_token: Error: {e}")
            return False

    def delete_token(self, account_id: int) -> bool:
        """Delete token for an account"""
        try:
            print(f"🗑️ delete_token: Deleting token for account {account_id}")
            
            response = requests.delete(
                f"{self.supabase_url}/rest/v1/tokens",
                headers=self.headers,
                params={'account_id': f'eq.{account_id}'}
            )
            
            if response.status_code in [200, 204]:
                print(f"✅ delete_token: Token deleted for account {account_id}")
                return True
            else:
                print(f"❌ delete_token: Failed to delete token for account {account_id}: {response.status_code} - {response.text}")
                return False
                
        except Exception as e:
            print(f"❌ delete_token: Error: {e}")
            return False

    def get_all_tokens(self) -> List[dict]:
        """Get all tokens"""
        try:
            print("🔍 get_all_tokens: Getting all tokens")
            
            response = requests.get(
                f"{self.supabase_url}/rest/v1/tokens",
                headers=self.headers
            )
            
            if response.status_code == 200:
                tokens = response.json()
                print(f"✅ get_all_tokens: Retrieved {len(tokens)} tokens")
                return tokens
            else:
                print(f"❌ get_all_tokens: HTTP {response.status_code}: {response.text}")
                return []
                
        except Exception as e:
            print(f"❌ get_all_tokens: Error: {e}")
            return []

    # Scheduled Posts Methods
    def add_scheduled_post(self, account_id: int, scheduled_for: str, caption_id: Optional[int] = None, 
                          image_id: Optional[int] = None) -> bool:
        """Add a scheduled post"""
        try:
            print(f"📅 add_scheduled_post: Adding scheduled post for account {account_id}")
            
            post_data = {
                "account_id": account_id,
                "scheduled_for": scheduled_for,
                "status": "pending"
            }
            
            if caption_id:
                post_data["caption_id"] = caption_id
            if image_id:
                post_data["image_id"] = image_id
                
            response = requests.post(
                f"{self.supabase_url}/rest/v1/scheduled_posts",
                headers=self.headers,
                json=post_data
            )
            
            if response.status_code == 201:
                print(f"✅ add_scheduled_post: Scheduled post added for account {account_id}")
                return True
            else:
                print(f"❌ add_scheduled_post: Failed to add scheduled post: {response.status_code} - {response.text}")
                return False
                
        except Exception as e:
            print(f"❌ add_scheduled_post: Error: {e}")
            return False

    def get_scheduled_posts(self, account_id: Optional[int] = None, status: Optional[str] = None) -> List[dict]:
        """Get scheduled posts"""
        try:
            print(f"🔍 get_scheduled_posts: Getting scheduled posts")
            
            params = {}
            if account_id:
                params['account_id'] = f'eq.{account_id}'
            if status:
                params['status'] = f'eq.{status}'
                
            response = requests.get(
                f"{self.supabase_url}/rest/v1/scheduled_posts",
                headers=self.headers,
                params=params
            )
            
            if response.status_code == 200:
                posts = response.json()
                print(f"✅ get_scheduled_posts: Retrieved {len(posts)} scheduled posts")
                return posts
            else:
                print(f"❌ get_scheduled_posts: HTTP {response.status_code}: {response.text}")
                return []
                
        except Exception as e:
            print(f"❌ get_scheduled_posts: Error: {e}")
            return []

    def update_scheduled_post_status(self, post_id: int, status: str) -> bool:
        """Update scheduled post status"""
        try:
            print(f"🔄 update_scheduled_post_status: Updating post {post_id} to status {status}")
            
            response = requests.patch(
                f"{self.supabase_url}/rest/v1/scheduled_posts",
                headers=self.headers,
                params={'id': f'eq.{post_id}'},
                json={"status": status}
            )
            
            if response.status_code in [200, 204]:
                print(f"✅ update_scheduled_post_status: Post {post_id} status updated to {status}")
                return True
            else:
                print(f"❌ update_scheduled_post_status: Failed to update post {post_id}: {response.status_code} - {response.text}")
                return False
                
        except Exception as e:
            print(f"❌ update_scheduled_post_status: Error: {e}")
            return False

    # OAuth State Management Methods
    def store_oauth_state(self, account_id: int, state: str) -> bool:
        """Store OAuth state for CSRF protection"""
        try:
            print(f"💾 store_oauth_state: Storing state for account {account_id}")
            
            state_data = {
                "account_id": account_id,
                "state": state,
                "created_at": datetime.now().isoformat()
            }
            
            response = requests.post(
                f"{self.supabase_url}/rest/v1/oauth_states",
                headers=self.headers,
                json=state_data
            )
            
            if response.status_code == 201:
                print(f"✅ store_oauth_state: State stored for account {account_id}")
                return True
            else:
                print(f"❌ store_oauth_state: Failed to store state: {response.status_code} - {response.text}")
                return False
                
        except Exception as e:
            print(f"❌ store_oauth_state: Error: {e}")
            return False

    def get_oauth_state_account_id(self, state: str) -> Optional[int]:
        """Get account_id from OAuth state"""
        try:
            print(f"🔍 get_oauth_state_account_id: Looking up state")
            
            response = requests.get(
                f"{self.supabase_url}/rest/v1/oauth_states",
                headers=self.headers,
                params={'state': f'eq.{state}'}
            )
            
            if response.status_code == 200:
                states = response.json()
                if states:
                    account_id = states[0].get('account_id')
                    print(f"✅ get_oauth_state_account_id: Found account {account_id}")
                    return account_id
                else:
                    print(f"📂 get_oauth_state_account_id: No state found")
                    return None
            else:
                print(f"❌ get_oauth_state_account_id: HTTP {response.status_code}: {response.text}")
                return None
                
        except Exception as e:
            print(f"❌ get_oauth_state_account_id: Error: {e}")
            return None

    def delete_oauth_state(self, state: str) -> bool:
        """Delete OAuth state after use"""
        try:
            print(f"🗑️ delete_oauth_state: Deleting state")
            
            response = requests.delete(
                f"{self.supabase_url}/rest/v1/oauth_states",
                headers=self.headers,
                params={'state': f'eq.{state}'}
            )
            
            if response.status_code in [200, 204]:
                print(f"✅ delete_oauth_state: State deleted")
                return True
            else:
                print(f"❌ delete_oauth_state: Failed to delete state: {response.status_code} - {response.text}")
                return False
                
        except Exception as e:
            print(f"❌ delete_oauth_state: Error: {e}")
            return False

    def cleanup_expired_oauth_states(self) -> int:
        """Clean up expired OAuth states (older than 1 hour)"""
        try:
            print(f"🧹 cleanup_expired_oauth_states: Cleaning up expired states")
            
            # Calculate cutoff time (1 hour ago)
            cutoff_time = (datetime.now() - timedelta(hours=1)).isoformat()
            
            response = requests.delete(
                f"{self.supabase_url}/rest/v1/oauth_states",
                headers=self.headers,
                params={'created_at': f'lt.{cutoff_time}'}
            )
            
            if response.status_code in [200, 204]:
                print(f"✅ cleanup_expired_oauth_states: Expired states cleaned up")
                return 0  # Placeholder - actual count would need separate query
            else:
                print(f"❌ cleanup_expired_oauth_states: Failed to cleanup: {response.status_code} - {response.text}")
                return 0
                
        except Exception as e:
            print(f"❌ cleanup_expired_oauth_states: Error: {e}")
            return 0

    def get_account_by_id(self, account_id: int) -> Optional[dict]:
        """Get account by ID"""
        try:
            print(f"🔍 get_account_by_id: Getting account {account_id}")
            
            response = requests.get(
                f"{self.supabase_url}/rest/v1/accounts",
                headers=self.headers,
                params={'id': f'eq.{account_id}'}
            )
            
            if response.status_code == 200:
                accounts = response.json()
                if accounts:
                    print(f"✅ get_account_by_id: Found account {account_id}")
                    return accounts[0]
                else:
                    print(f"📂 get_account_by_id: No account found with ID {account_id}")
                    return None
            else:
                print(f"❌ get_account_by_id: HTTP {response.status_code}: {response.text}")
                return None
                
        except Exception as e:
            print(f"❌ get_account_by_id: Error: {e}")
            return None

    def get_image_by_id(self, image_id: int) -> Optional[dict]:
        """Get image by ID"""
        try:
            print(f"🔍 get_image_by_id: Getting image {image_id}")
            
            response = requests.get(
                f"{self.supabase_url}/rest/v1/images",
                headers=self.headers,
                params={'id': f'eq.{image_id}'}
            )
            
            if response.status_code == 200:
                images = response.json()
                if images:
                    print(f"✅ get_image_by_id: Found image {image_id}")
                    return images[0]
                else:
                    print(f"📂 get_image_by_id: No image found with ID {image_id}")
                    return None
            else:
                print(f"❌ get_image_by_id: HTTP {response.status_code}: {response.text}")
                return None
                
        except Exception as e:
            print(f"❌ get_image_by_id: Error: {e}")
            return None

    def get_caption_by_id(self, caption_id: int) -> Optional[dict]:
        """Get caption by ID"""
        try:
            print(f"🔍 get_caption_by_id: Getting caption {caption_id}")
            
            response = requests.get(
                f"{self.supabase_url}/rest/v1/captions",
                headers=self.headers,
                params={'id': f'eq.{caption_id}'}
            )
            
            if response.status_code == 200:
                captions = response.json()
                if captions:
                    print(f"✅ get_caption_by_id: Found caption {caption_id}")
                    return captions[0]
                else:
                    print(f"📂 get_caption_by_id: No caption found with ID {caption_id}")
                    return None
            else:
                print(f"❌ get_caption_by_id: HTTP {response.status_code}: {response.text}")
                return None
                
        except Exception as e:
            print(f"❌ get_caption_by_id: Error: {e}")
            return None

    def record_posting_history(self, account_id: int, caption_id: Optional[int] = None,
                              image_id: Optional[int] = None, thread_id: Optional[str] = None,
                              status: str = 'posted') -> bool:
        """Record posting history"""
        try:
            print(f"📝 record_posting_history: Recording post for account {account_id}")
            
            data = {
                'account_id': account_id,
                'caption_id': caption_id,
                'image_id': image_id,
                'thread_id': thread_id,
                'status': status,
                'posted_at': datetime.now().isoformat()
            }
            
            response = requests.post(
                f"{self.supabase_url}/rest/v1/posting_history",
                headers=self.headers,
                json=data
            )
            
            if response.status_code == 201:
                print(f"✅ record_posting_history: Posting history recorded for account {account_id}")
                return True
            else:
                print(f"❌ record_posting_history: Failed to record: {response.status_code} - {response.text}")
                return False
                
        except Exception as e:
            print(f"❌ record_posting_history: Error: {e}")
            return False 