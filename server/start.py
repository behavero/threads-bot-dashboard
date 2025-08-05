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
        "environment": "render"
    })

@app.route('/api/health')
def health():
    return jsonify({"health": "ok"})

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

@app.route('/api/captions', methods=['GET'])
def get_captions():
    try:
        db = DatabaseManager()
        # This would need to be implemented in DatabaseManager
        return jsonify({"captions": []})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/captions', methods=['POST'])
def add_caption():
    try:
        data = request.json
        text = data.get('text')
        
        if not text:
            return jsonify({"error": "Caption text required"}), 400
        
        db = DatabaseManager()
        success = db.add_caption(text)
        
        if success:
            return jsonify({"message": "Caption added successfully"}), 201
        else:
            return jsonify({"error": "Failed to add caption"}), 500
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/images', methods=['GET'])
def get_images():
    try:
        db = DatabaseManager()
        # This would need to be implemented in DatabaseManager
        return jsonify({"images": []})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/images', methods=['POST'])
def add_image():
    try:
        data = request.json
        url = data.get('url')
        
        if not url:
            return jsonify({"error": "Image URL required"}), 400
        
        db = DatabaseManager()
        success = db.add_image(url)
        
        if success:
            return jsonify({"message": "Image added successfully"}), 201
        else:
            return jsonify({"error": "Failed to add image"}), 500
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