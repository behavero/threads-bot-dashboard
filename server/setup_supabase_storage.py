#!/usr/bin/env python3
"""
Supabase Storage Setup Script
Creates the sessions bucket and sets up proper permissions
"""

import os
from supabase import create_client

def setup_supabase_storage():
    """Set up Supabase Storage for session management"""
    try:
        # Get Supabase credentials
        supabase_url = os.getenv("SUPABASE_URL")
        supabase_key = os.getenv("SUPABASE_SERVICE_ROLE_KEY")
        
        if not supabase_url or not supabase_key:
            print("❌ SUPABASE_URL and SUPABASE_SERVICE_ROLE_KEY must be set")
            return False
        
        # Create Supabase client
        supabase = create_client(supabase_url, supabase_key)
        
        # Check if sessions bucket exists
        try:
            buckets = supabase.storage.list_buckets()
            bucket_names = [bucket.name for bucket in buckets]
            
            if "sessions" not in bucket_names:
                print("📦 Creating sessions bucket...")
                
                # Create bucket with appropriate settings
                supabase.storage.create_bucket(
                    "sessions",
                    public=True,
                    file_size_limit=5242880,  # 5MB limit
                    allowed_mime_types=['application/json']
                )
                print("✅ Sessions bucket created successfully")
            else:
                print("✅ Sessions bucket already exists")
            
            # List buckets to confirm
            buckets = supabase.storage.list_buckets()
            print(f"📋 Available buckets: {[b.name for b in buckets]}")
            
            return True
            
        except Exception as e:
            print(f"❌ Error creating bucket: {e}")
            print("📝 Please create the 'sessions' bucket manually in Supabase Dashboard:")
            print("   1. Go to Storage in Supabase Dashboard")
            print("   2. Click 'Create a new bucket'")
            print("   3. Name it 'sessions'")
            print("   4. Set it as public")
            print("   5. Set file size limit to 5MB")
            print("   6. Allow JSON files")
            return False
            
    except Exception as e:
        print(f"❌ Error setting up Supabase Storage: {e}")
        return False

def test_supabase_connection():
    """Test Supabase connection and storage access"""
    try:
        from supabase_storage import supabase_storage_manager
        
        print("✅ Supabase Storage connection successful")
        print(f"🌐 Using bucket: {supabase_storage_manager.session_bucket}")
        
        # Test listing files
        files = supabase_storage_manager.supabase.storage.from_("sessions").list()
        print(f"📁 Found {len(files)} files in sessions bucket")
        
        return True
        
    except Exception as e:
        print(f"❌ Supabase Storage connection failed: {e}")
        return False

if __name__ == "__main__":
    print("🚀 Setting up Supabase Storage for session management...")
    
    # Setup bucket
    if setup_supabase_storage():
        print("✅ Supabase Storage setup completed")
        
        # Test connection
        if test_supabase_connection():
            print("✅ All tests passed!")
        else:
            print("⚠️ Connection test failed")
    else:
        print("❌ Supabase Storage setup failed")
