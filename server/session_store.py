#!/usr/bin/env python3
"""
Supabase Session Store for Threads Login
Simplified session management using Supabase Storage
"""

from supabase import create_client
import os
import json
from instagrapi import Client
from typing import Optional

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY")

if not SUPABASE_URL or not SUPABASE_KEY:
    raise ValueError("SUPABASE_URL and SUPABASE_SERVICE_ROLE_KEY must be set")

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

def load_session_from_supabase(username: str) -> Optional[Client]:
    """Load session from Supabase Storage"""
    try:
        file_path = f"{username}/session.json"
        res = supabase.storage.from_("sessions").download(file_path)
        session_settings = json.loads(res.decode())
        
        client = Client()
        client.set_settings(session_settings)
        print(f"[Supabase] Session loaded for {username}")
        return client
        
    except Exception as e:
        print(f"[Supabase] No session for {username} — {e}")
        return None

def save_session_to_supabase(username: str, client: Client) -> bool:
    """Save session to Supabase Storage"""
    try:
        session_settings = client.get_settings()
        file_path = f"{username}/session.json"
        
        supabase.storage.from_("sessions").upload(
            file_path, 
            json.dumps(session_settings), 
            {"content-type": "application/json"}, 
            upsert=True
        )
        print(f"[Supabase] Session saved for {username}")
        return True
        
    except Exception as e:
        print(f"[Supabase] Failed to save session for {username} — {e}")
        return False

def delete_session_from_supabase(username: str) -> bool:
    """Delete session from Supabase Storage"""
    try:
        file_path = f"{username}/session.json"
        supabase.storage.from_("sessions").remove([file_path])
        print(f"[Supabase] Session deleted for {username}")
        return True
        
    except Exception as e:
        print(f"[Supabase] Failed to delete session for {username} — {e}")
        return False

def session_exists_in_supabase(username: str) -> bool:
    """Check if session exists in Supabase Storage"""
    try:
        file_path = f"{username}/session.json"
        files = supabase.storage.from_("sessions").list()
        return any(file.name == file_path for file in files)
        
    except Exception as e:
        print(f"[Supabase] Error checking session existence for {username} — {e}")
        return False

def list_sessions_from_supabase() -> list:
    """List all sessions in Supabase Storage"""
    try:
        files = supabase.storage.from_("sessions").list()
        sessions = []
        
        for file in files:
            if file.name.endswith('/session.json'):
                username = file.name.split('/')[0]
                sessions.append({
                    "username": username,
                    "created_at": file.created_at,
                    "updated_at": file.updated_at,
                    "size": file.metadata.get('size', 0) if file.metadata else 0
                })
        
        return sessions
        
    except Exception as e:
        print(f"[Supabase] Error listing sessions — {e}")
        return []
