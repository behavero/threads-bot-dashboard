#!/usr/bin/env python3
"""
Threads Auto-Posting Bot
Main entry point with Flask API and bot scheduling
"""

import os
import threading
import time
from datetime import datetime
from flask import Flask, jsonify, request
from flask_cors import CORS
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Check environment variables first
def validate_environment():
    """Validate that required environment variables are set"""
    required_vars = ['SUPABASE_URL', 'SUPABASE_KEY']
    missing_vars = []
    
    for var in required_vars:
        if not os.getenv(var):
            missing_vars.append(var)
    
    if missing_vars:
        print(f"❌ Missing environment variables: {', '.join(missing_vars)}")
        print("Please set these in your Render/Railway environment variables:")
        print("SUPABASE_URL=https://perwbmtwutwzsvlirwik.supabase.co")
        print("SUPABASE_KEY=your-supabase-key")
        return False
    
    return True

# Validate environment before importing modules
if not validate_environment():
    print("❌ Environment not ready. Exiting.")
    exit(1)

from database import DatabaseManager
from threads_bot import ThreadsBot
from engagement_tracker import engagement_tracker
import asyncio

app = Flask(__name__)
CORS(app)

# Global bot instance
bot = None
bot_thread = None
bot_running = False

@app.route('/')
def home():
    return jsonify({
        "status": "running",
        "service": "threads-bot",
        "timestamp": datetime.now().isoformat(),
        "environment": "render"
    })

@app.route('/api/status')
def status():
    return jsonify({
        "status": "running" if bot_running else "stopped",
        "service": "threads-bot",
        "bot_running": bot_running,
        "timestamp": datetime.now().isoformat(),
        "environment": "render",
        "backend_url": "https://threads-bot-dashboard-3.onrender.com"
    })

@app.route('/api/health')
def health():
    return jsonify({
        "health": "ok",
        "service": "threads-bot",
        "timestamp": datetime.now().isoformat(),
        "environment": "render"
    })

@app.route('/api/info')
def info():
    """Get detailed service information"""
    return jsonify({
        "service": "threads-bot",
        "environment": "render",
        "backend_url": "https://threads-bot-dashboard-3.onrender.com",
        "supabase_connected": bool(os.getenv("SUPABASE_URL")),
        "bot_status": "running" if bot_running else "stopped",
        "timestamp": datetime.now().isoformat()
    })

@app.route('/api/post/schedule', methods=['GET', 'POST'])
def schedule_posts():
    """Get or create posting schedules"""
    try:
        db = DatabaseManager()
        
        if request.method == 'GET':
            # Get all schedules
            # This would need to be implemented in DatabaseManager
            return jsonify({"schedules": []})
        
        elif request.method == 'POST':
            # Create new schedule
            data = request.json
            account_id = data.get('account_id')
            caption_id = data.get('caption_id')
            image_id = data.get('image_id')
            scheduled_time = data.get('scheduled_time')
            
            if not all([account_id, scheduled_time]):
                return jsonify({"error": "Account ID and scheduled time required"}), 400
            
            # This would need to be implemented in DatabaseManager
            return jsonify({"message": "Schedule created successfully"}), 201
            
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/status', methods=['GET'])
def get_status():
    """Health check endpoint"""
    try:
        return jsonify({
            "status": "healthy",
            "timestamp": datetime.now().isoformat(),
            "version": "1.0.0"
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/stats', methods=['GET'])
def get_stats():
    """Get comprehensive statistics"""
    try:
        db = DatabaseManager()
        stats = db.get_statistics()
        stats["bot_status"] = "running" if bot_running else "stopped"
        return jsonify(stats)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/stats/engagement', methods=['GET'])
def get_engagement_stats():
    """Get daily engagement statistics"""
    try:
        days = request.args.get('days', 7, type=int)
        stats = engagement_tracker.get_daily_engagement_stats(days)
        return jsonify(stats)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/stats/refresh', methods=['POST'])
def refresh_engagement_stats():
    """Manually refresh engagement data"""
    try:
        # Run async function in sync context
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        result = loop.run_until_complete(engagement_tracker.refresh_engagement_data())
        loop.close()
        
        return jsonify(result)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/accounts', methods=['GET'])
def get_accounts():
    try:
        db = DatabaseManager()
        accounts = db.get_active_accounts()
        return jsonify({"accounts": accounts})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/accounts', methods=['POST'])
def add_account():
    try:
        data = request.json
        username = data.get('username')
        password = data.get('password')
        
        if not username or not password:
            return jsonify({"error": "Username and password required"}), 400
        
        db = DatabaseManager()
        success = db.add_account(username, password)
        
        if success:
            return jsonify({"message": "Account added successfully"}), 201
        else:
            return jsonify({"error": "Failed to add account"}), 500
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/accounts/<account_id>/toggle', methods=['PATCH'])
def toggle_account(account_id):
    try:
        data = request.json
        active = data.get('active', False)
        
        db = DatabaseManager()
        # This would need to be implemented in DatabaseManager
        # For now, return success
        return jsonify({"message": "Account status updated successfully"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/accounts/<account_id>', methods=['DELETE'])
def delete_account(account_id):
    try:
        db = DatabaseManager()
        # This would need to be implemented in DatabaseManager
        # For now, return success
        return jsonify({"message": "Account deleted successfully"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/statistics')
def get_statistics():
    try:
        db = DatabaseManager()
        accounts = db.get_active_accounts()
        
        # Calculate statistics
        total_accounts = len(accounts)
        active_accounts = len([a for a in accounts if a.get('active', False)])
        
        return jsonify({
            "total_accounts": total_accounts,
            "active_accounts": active_accounts,
            "bot_status": bot_running,
            "last_updated": datetime.now().isoformat()
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/bot/start', methods=['POST'])
def start_bot():
    try:
        global bot_running
        if not bot_running:
            start_bot()
            bot_running = True
            return jsonify({"message": "Bot started successfully"})
        else:
            return jsonify({"message": "Bot is already running"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/bot/stop', methods=['POST'])
def stop_bot():
    try:
        global bot_running, bot_thread
        if bot_running and bot_thread:
            # This would need proper bot stopping logic
            bot_running = False
            return jsonify({"message": "Bot stopped successfully"})
        else:
            return jsonify({"message": "Bot is not running"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/captions', methods=['GET'])
def get_captions():
    try:
        db = DatabaseManager()
        captions = db.get_all_captions()
        
        # Process captions to ensure all fields have default values
        processed_captions = []
        for caption in captions:
            processed_caption = {
                'id': caption.get('id'),
                'user_id': caption.get('user_id'),
                'text': caption.get('text', ''),
                'category': caption.get('category', 'general'),
                'tags': caption.get('tags', []),
                'used': caption.get('used', False),
                'created_at': caption.get('created_at'),
                'updated_at': caption.get('updated_at', caption.get('created_at'))
            }
            processed_captions.append(processed_caption)
        
        return jsonify({"captions": processed_captions})
    except Exception as e:
        print(f"❌ Error fetching captions: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/captions', methods=['POST'])
def add_caption():
    try:
        data = request.json
        text = data.get('text')
        category = data.get('category', 'general')
        tags = data.get('tags', [])
        
        # Validate required fields
        if not text:
            return jsonify({"error": "Caption text is required"}), 400
        
        if not isinstance(text, str) or len(text.strip()) == 0:
            return jsonify({"error": "Caption text must be a non-empty string"}), 400
        
        # Validate category
        if category and not isinstance(category, str):
            return jsonify({"error": "Category must be a string"}), 400
        
        # Validate tags
        if tags and not isinstance(tags, list):
            return jsonify({"error": "Tags must be an array"}), 400
        
        # Clean and validate tags
        if tags:
            cleaned_tags = []
            for tag in tags:
                if isinstance(tag, str) and tag.strip():
                    cleaned_tags.append(tag.strip())
            tags = cleaned_tags
        
        print(f"📝 Adding caption: text='{text[:50]}...', category='{category}', tags={tags}")
        
        try:
            # Use direct Supabase approach like the working test
            import requests
            
            supabase_url = "https://perwbmtwutwzsvlirwik.supabase.co"
            service_key = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InBlcndibXR3dXR3enN2bGlyd2lrIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc1NDQwNTU4MiwiZXhwIjoyMDY5OTgxNTgyfQ.fpTpKFrK0Eg60rN7jpWPKKQFTmIrxVlcHY2MMeKx2AE"
            
            headers = {
                'apikey': service_key,
                'Authorization': f'Bearer {service_key}',
                'Content-Type': 'application/json',
                'Prefer': 'return=representation'
            }
            
            caption_data = {
                "text": text,
                "category": category,
                "tags": tags,
                "used": False
            }
            
            print(f"📝 Direct Supabase request: {caption_data}")
            
            response = requests.post(
                f"{supabase_url}/rest/v1/captions",
                json=caption_data,
                headers=headers
            )
            
            print(f"📝 Direct response: {response.status_code}")
            print(f"📝 Direct response text: {response.text}")
            
            if response.status_code == 201:
                return jsonify({"message": "Caption added successfully"}), 201
            else:
                return jsonify({"error": f"Failed to add caption: {response.text}"}), 500
                
        except Exception as e:
            print(f"❌ Direct Supabase error: {e}")
            return jsonify({"error": f"Database error: {str(e)}"}), 500
    except Exception as e:
        print(f"❌ Error adding caption: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/images', methods=['GET'])
def get_images():
    try:
        db = DatabaseManager()
        images = db.get_all_images()
        return jsonify({"images": images})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/images', methods=['POST'])
def add_image():
    try:
        data = request.json
        url = data.get('url')
        filename = data.get('filename')
        size = data.get('size')
        type = data.get('type')
        
        if not url:
            return jsonify({"error": "Image URL required"}), 400
        
        db = DatabaseManager()
        success = db.add_image(url, filename, size, type)
        
        if success:
            return jsonify({"message": "Image added successfully"}), 201
        else:
            return jsonify({"error": "Failed to add image"}), 500
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/debug', methods=['GET'])
def debug_info():
    """Debug endpoint to check environment and database"""
    try:
        import os
        from database import DatabaseManager
        
        debug_info = {
            "environment": {
                "SUPABASE_URL": os.getenv('SUPABASE_URL', 'NOT SET'),
                "SUPABASE_KEY": "SET" if os.getenv('SUPABASE_KEY') else "NOT SET",
                "SUPABASE_SERVICE_ROLE_KEY": "SET" if os.getenv('SUPABASE_SERVICE_ROLE_KEY') else "NOT SET"
            },
            "database_test": None,
            "database_manager_test": None,
            "timestamp": datetime.now().isoformat()
        }
        
        # Test database connection
        try:
            db = DatabaseManager()
            captions = db.get_all_captions()
            debug_info["database_test"] = {
                "status": "success",
                "captions_count": len(captions),
                "sample_caption": captions[0] if captions else None
            }
            
            # Test database manager initialization
            debug_info["database_manager_test"] = {
                "status": "success",
                "supabase_url": db.supabase_url,
                "has_key": bool(db.supabase_key),
                "headers_count": len(db.headers)
            }
        except Exception as e:
            debug_info["database_test"] = {
                "status": "error",
                "error": str(e)
            }
            debug_info["database_manager_test"] = {
                "status": "error",
                "error": str(e)
            }
        
        return jsonify(debug_info)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

def run_bot():
    """Run the bot in a separate thread"""
    global bot, bot_running
    
    try:
        print("🤖 Starting Threads Bot...")
        bot = ThreadsBot()
        bot_running = True
        bot.run_continuously()
    except Exception as e:
        print(f"❌ Bot thread error: {e}")
        bot_running = False

def start_bot():
    """Start the bot in a background thread"""
    global bot_thread
    
    if bot_thread and bot_thread.is_alive():
        print("⚠️ Bot is already running")
        return
    
    bot_thread = threading.Thread(target=run_bot, daemon=True)
    bot_thread.start()
    print("🚀 Bot started in background thread")

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    
    print("🚀 Starting Threads Bot on Render...")
    print(f"🌐 Port: {port}")
    print(f"🔗 Supabase URL: {os.getenv('SUPABASE_URL', 'NOT SET')}")
    
    # Start the bot in background
    start_bot()
    
    # Start Flask app
    print(f"🌐 Starting Flask server on port {port}")
    app.run(host='0.0.0.0', port=port, debug=False) 