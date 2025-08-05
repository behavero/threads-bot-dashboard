#!/usr/bin/env python3
"""
Health check endpoint for Enhanced Threads Bot
Provides status information for deployment platforms
"""

import os
import json
import time
from datetime import datetime
from pathlib import Path

def get_bot_status():
    """Get current bot status"""
    status = {
        "status": "running",
        "timestamp": datetime.now().isoformat(),
        "environment": os.getenv('ENVIRONMENT', 'development'),
        "platform": os.getenv('PLATFORM', 'unknown'),
        "version": "2.0.0",
        "features": {
            "anti_detection": True,
            "user_agent_rotation": True,
            "session_management": True,
            "rate_limit_handling": True,
            "human_behavior_simulation": True
        }
    }
    
    # Check if required files exist
    required_files = [
        'enhanced_accounts.json',
        'captions.txt',
        'user_agents.txt'
    ]
    
    file_status = {}
    for file in required_files:
        file_status[file] = Path(file).exists()
    
    status['files'] = file_status
    
    # Check if images directory exists
    status['images_directory'] = Path('images/').exists()
    
    return status

def health_check():
    """Simple health check function"""
    try:
        status = get_bot_status()
        return {
            "status": "healthy",
            "data": status
        }
    except Exception as e:
        return {
            "status": "unhealthy",
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }

if __name__ == "__main__":
    # Print status as JSON for deployment platforms
    import json
    result = health_check()
    print(json.dumps(result, indent=2)) 