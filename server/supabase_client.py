#!/usr/bin/env python3
"""
Simple Supabase Client for Session Management
Matches the provided approach for session handling
"""

import os
from supabase import create_client

# Supabase configuration
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY")
SESSION_BUCKET = "sessions"

# Create Supabase client
if SUPABASE_URL and SUPABASE_KEY:
    supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
else:
    supabase = None
    print("⚠️ Supabase credentials not found")

def get_session_path(username):
    """Get session filename for username"""
    safe_username = username.replace('/', '_').replace('\\', '_').replace(' ', '_')
    return f"{safe_username}.json"

def load_session_from_supabase(username: str, client):
    """Load session from Supabase Storage"""
    if not supabase:
        print("❌ Supabase client not available")
        return None
    
    session_file = get_session_path(username)
    
    try:
        # Download session file from Supabase
        result = supabase.storage.from_(SESSION_BUCKET).download(session_file)
        
        if not result:
            print(f"📁 No session found for {username}")
            return None
        
        # Create temp file and load settings
        import tempfile
        with tempfile.NamedTemporaryFile(delete=False) as temp_file:
            temp_file.write(result)
            client.load_settings(temp_file.name)
        
        print(f"✅ Session loaded from Supabase for {username}")
        return client
        
    except Exception as e:
        print(f"❌ Failed to load session for {username}: {e}")
        return None

def save_session_to_supabase(username: str, client):
    """Save session to Supabase Storage"""
    if not supabase:
        print("❌ Supabase client not available")
        return False
    
    session_file = get_session_path(username)
    
    try:
        import tempfile
        import os
        
        # Create temp file and dump settings
        with tempfile.NamedTemporaryFile(delete=False) as temp_file:
            client.dump_settings(temp_file.name)
            
            # Upload to Supabase with upsert
            with open(temp_file.name, "rb") as f:
                supabase.storage.from_(SESSION_BUCKET).upload(
                    session_file, 
                    f, 
                    {"upsert": True}
                )
            
            # Clean up temp file
            os.remove(temp_file.name)
        
        print(f"✅ Session saved to Supabase for {username}")
        return True
        
    except Exception as e:
        print(f"❌ Failed to save session for {username}: {e}")
        return False

def session_exists_in_supabase(username: str) -> bool:
    """Check if session exists in Supabase Storage"""
    if not supabase:
        return False
    
    try:
        session_file = get_session_path(username)
        files = supabase.storage.from_(SESSION_BUCKET).list()
        return any(file.name == session_file for file in files)
    except Exception as e:
        print(f"❌ Error checking session existence: {e}")
        return False

def delete_session_from_supabase(username: str) -> bool:
    """Delete session from Supabase Storage"""
    if not supabase:
        return False
    
    try:
        session_file = get_session_path(username)
        supabase.storage.from_(SESSION_BUCKET).remove([session_file])
        print(f"✅ Session deleted from Supabase for {username}")
        return True
    except Exception as e:
        print(f"❌ Failed to delete session for {username}: {e}")
        return False
