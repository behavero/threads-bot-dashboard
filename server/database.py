import os
import requests
from typing import List, Dict, Optional
from datetime import datetime
from supabase import create_client, Client

class DatabaseManager:
    def __init__(self):
        # Use the new Supabase-Vercel integration variables
        self.supabase_url = os.getenv("SUPABASE_URL")
        self.supabase_key = os.getenv("SUPABASE_SERVICE_ROLE_KEY") or os.getenv("SUPABASE_KEY")
        
        if not self.supabase_url or not self.supabase_key:
            raise ValueError("Supabase credentials not configured")
        
        # Initialize headers for HTTP requests
        self.headers = {
            "apikey": self.supabase_key,
            "Authorization": f"Bearer {self.supabase_key}",
            "Content-Type": "application/json"
        }
        
        # Try to initialize Supabase client (optional)
        try:
            # Use minimal client initialization to avoid proxy issues
            self.supabase: Client = create_client(
                self.supabase_url, 
                self.supabase_key
            )
            self.use_supabase_client = True
            print("✅ Supabase client initialized successfully")
        except Exception as e:
            print(f"⚠️ Supabase client initialization failed, using HTTP requests: {e}")
            self.use_supabase_client = False
    
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
            # Always use HTTP requests for backend operations (more reliable)
            response = requests.get(
                f"{self.supabase_url}/rest/v1/accounts",
                params={"status": "eq.enabled"},
                headers=self.headers
            )
            if response.status_code == 200:
                return response.json()
            else:
                print(f"❌ HTTP {response.status_code}: {response.text}")
                return []
        except Exception as e:
            print(f"❌ Error fetching accounts: {e}")
            return []
    
    def get_unused_caption(self) -> Optional[Dict]:
        """Get a random unused caption"""
        try:
            response = self.supabase.table("captions").select("*").eq("used", False).limit(1).execute()
            return response.data[0] if response.data else None
        except Exception as e:
            print(f"❌ Error fetching caption: {e}")
            return None
    
    def get_unused_image(self) -> Optional[Dict]:
        """Get a random unused image"""
        try:
            response = self.supabase.table("images").select("*").eq("used", False).limit(1).execute()
            return response.data[0] if response.data else None
        except Exception as e:
            print(f"❌ Error fetching image: {e}")
            return None
    
    def mark_caption_used(self, caption_id: str):
        """Mark a caption as used"""
        try:
            self.supabase.table("captions").update({"used": True}).eq("id", caption_id).execute()
        except Exception as e:
            print(f"❌ Error marking caption used: {e}")
    
    def mark_image_used(self, image_id: str):
        """Mark an image as used"""
        try:
            self.supabase.table("images").update({"used": True}).eq("id", image_id).execute()
        except Exception as e:
            print(f"❌ Error marking image used: {e}")
    
    def update_account_last_posted(self, account_id: str):
        """Update account's last posted timestamp"""
        try:
            self.supabase.table("accounts").update({"last_posted": datetime.now().isoformat()}).eq("id", account_id).execute()
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
            
            self.supabase.table("posting_history").insert(data).execute()
        except Exception as e:
            print(f"❌ Error recording posting history: {e}")
    
    def add_account(self, username: str, password: str, user_id: str = None) -> bool:
        """Add a new account"""
        try:
            account_data = {"username": username, "password": password}
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
    
    def add_caption(self, text: str, user_id: str = None) -> bool:
        """Add a new caption"""
        try:
            caption_data = {"text": text}
            if user_id:
                caption_data["user_id"] = user_id
                
            response = requests.post(
                f"{self.supabase_url}/rest/v1/captions",
                json=caption_data,
                headers=self.headers
            )
            return response.status_code == 201
        except Exception as e:
            print(f"❌ Error adding caption: {e}")
            return False
    
    def add_image(self, url: str, user_id: str = None) -> bool:
        """Add a new image"""
        try:
            image_data = {"url": url}
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
    
    def get_posting_history(self) -> List[Dict]:
        """Get posting history"""
        try:
            response = requests.get(
                f"{self.supabase_url}/rest/v1/posting_history",
                params={"order": "posted_at.desc"},
                headers=self.headers
            )
            if response.status_code == 200:
                return response.json()
            else:
                print(f"❌ HTTP {response.status_code}: {response.text}")
                return []
        except Exception as e:
            print(f"❌ Error fetching posting history: {e}")
            return []
    
    def get_statistics(self) -> Dict:
        """Get comprehensive statistics"""
        try:
            accounts = self.get_active_accounts()
            captions = self.get_all_captions()
            images = self.get_all_images()
            history = self.get_posting_history()
            
            return {
                "total_accounts": len(accounts),
                "active_accounts": len([a for a in accounts if a.get('status') == 'enabled']),
                "total_captions": len(captions),
                "total_images": len(images),
                "total_posts": len(history),
                "successful_posts": len([h for h in history if h.get('status') == 'success']),
                "failed_posts": len([h for h in history if h.get('status') == 'failed']),
                "last_posted": history[0].get('posted_at') if history else None
            }
        except Exception as e:
            print(f"❌ Error getting statistics: {e}")
            return {} 