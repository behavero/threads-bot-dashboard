import os
import requests
from typing import List, Dict, Optional
from datetime import datetime

class DatabaseManager:
    def __init__(self):
        self.supabase_url = os.getenv("SUPABASE_URL")
        self.supabase_key = os.getenv("SUPABASE_KEY")
        
        if not self.supabase_url or not self.supabase_key:
            raise ValueError("Supabase credentials not configured")
        
        self.headers = {
            "apikey": self.supabase_key,
            "Authorization": f"Bearer {self.supabase_key}",
            "Content-Type": "application/json"
        }
    
    def initialize_schema(self):
        """Initialize database schema"""
        # Try multiple possible paths for the SQL file
        possible_paths = [
            "init_schema.sql",  # In current directory (server/)
            os.path.join("config", "init_schema.sql"),
            os.path.join("..", "config", "init_schema.sql"),
            os.path.join(os.path.dirname(__file__), "..", "config", "init_schema.sql"),
            os.path.join(os.getcwd(), "config", "init_schema.sql"),
            os.path.join(os.getcwd(), "..", "config", "init_schema.sql")
        ]
        
        sql_path = None
        for path in possible_paths:
            if os.path.exists(path):
                sql_path = path
                break
        
        if not sql_path:
            print(f"❌ SQL schema file not found. Tried paths: {possible_paths}")
            return False
        
        print(f"✅ Found SQL schema at: {sql_path}")
        
        with open(sql_path, "r") as file:
            sql = file.read()
        
        try:
            response = requests.post(
                f"{self.supabase_url}/rest/v1/rpc/execute_sql",
                json={"sql": sql},
                headers=self.headers
            )
            
            if response.status_code == 200:
                print("✅ Database schema initialized successfully")
                return True
            else:
                print(f"❌ Failed to initialize schema: {response.text}")
                return False
        except Exception as e:
            print(f"❌ Database initialization error: {e}")
            return False
    
    def get_active_accounts(self) -> List[Dict]:
        """Get all active accounts"""
        try:
            response = requests.get(
                f"{self.supabase_url}/rest/v1/accounts",
                params={"active": "eq.true"},
                headers=self.headers
            )
            return response.json() if response.status_code == 200 else []
        except Exception as e:
            print(f"❌ Error fetching accounts: {e}")
            return []
    
    def get_unused_caption(self) -> Optional[Dict]:
        """Get a random unused caption"""
        try:
            response = requests.get(
                f"{self.supabase_url}/rest/v1/captions",
                params={"used": "eq.false"},
                headers=self.headers
            )
            captions = response.json() if response.status_code == 200 else []
            return captions[0] if captions else None
        except Exception as e:
            print(f"❌ Error fetching caption: {e}")
            return None
    
    def get_unused_image(self) -> Optional[Dict]:
        """Get a random unused image"""
        try:
            response = requests.get(
                f"{self.supabase_url}/rest/v1/images",
                params={"used": "eq.false"},
                headers=self.headers
            )
            images = response.json() if response.status_code == 200 else []
            return images[0] if images else None
        except Exception as e:
            print(f"❌ Error fetching image: {e}")
            return None
    
    def mark_caption_used(self, caption_id: str):
        """Mark a caption as used"""
        try:
            requests.patch(
                f"{self.supabase_url}/rest/v1/captions",
                json={"used": True},
                params={"id": f"eq.{caption_id}"},
                headers=self.headers
            )
        except Exception as e:
            print(f"❌ Error marking caption used: {e}")
    
    def mark_image_used(self, image_id: str):
        """Mark an image as used"""
        try:
            requests.patch(
                f"{self.supabase_url}/rest/v1/images",
                json={"used": True},
                params={"id": f"eq.{image_id}"},
                headers=self.headers
            )
        except Exception as e:
            print(f"❌ Error marking image used: {e}")
    
    def update_account_last_posted(self, account_id: str):
        """Update account's last posted timestamp"""
        try:
            requests.patch(
                f"{self.supabase_url}/rest/v1/accounts",
                json={"last_posted": datetime.now().isoformat()},
                params={"id": f"eq.{account_id}"},
                headers=self.headers
            )
        except Exception as e:
            print(f"❌ Error updating account: {e}")
    
    def record_posting_history(self, account_id: str, caption_id: str, 
                              image_id: str, status: str, error_message: str = None):
        """Record a posting attempt"""
        try:
            data = {
                "account_id": account_id,
                "caption_id": caption_id,
                "image_id": image_id,
                "status": status,
                "error_message": error_message,
                "posted_at": datetime.now().isoformat() if status == "success" else None
            }
            
            requests.post(
                f"{self.supabase_url}/rest/v1/posting_history",
                json=data,
                headers=self.headers
            )
        except Exception as e:
            print(f"❌ Error recording posting history: {e}")
    
    def add_account(self, username: str, password: str) -> bool:
        """Add a new account"""
        try:
            response = requests.post(
                f"{self.supabase_url}/rest/v1/accounts",
                json={"username": username, "password": password},
                headers=self.headers
            )
            return response.status_code == 201
        except Exception as e:
            print(f"❌ Error adding account: {e}")
            return False
    
    def add_caption(self, text: str) -> bool:
        """Add a new caption"""
        try:
            response = requests.post(
                f"{self.supabase_url}/rest/v1/captions",
                json={"text": text},
                headers=self.headers
            )
            return response.status_code == 201
        except Exception as e:
            print(f"❌ Error adding caption: {e}")
            return False
    
    def add_image(self, url: str) -> bool:
        """Add a new image"""
        try:
            response = requests.post(
                f"{self.supabase_url}/rest/v1/images",
                json={"url": url},
                headers=self.headers
            )
            return response.status_code == 201
        except Exception as e:
            print(f"❌ Error adding image: {e}")
            return False 