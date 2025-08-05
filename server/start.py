#!/usr/bin/env python3
"""
Minimal Threads Bot Server
Simple Flask server for Railway deployment
"""

import requests
import os
from flask import Flask, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

def initialize_supabase_schema():
    url = os.getenv("SUPABASE_URL")
    key = os.getenv("SUPABASE_KEY")
    if not url or not key:
        print("Supabase credentials not set.")
        return

    headers = {
        "apikey": key,
        "Authorization": f"Bearer {key}",
        "Content-Type": "application/json"
    }

    sql_path = os.path.join("config", "init_schema.sql")
    if not os.path.exists(sql_path):
        print("SQL schema file not found.")
        return

    with open(sql_path, "r") as file:
        sql = file.read()

    response = requests.post(
        f"{url}/rest/v1/rpc/execute_sql",
        json={"sql": sql},
        headers=headers
    )

    if response.status_code == 200:
        print("✅ Supabase schema initialized successfully.")
    else:
        print("❌ Failed to initialize schema:", response.text)

@app.route('/')
def home():
    return jsonify({"status": "Threads Bot is running!"})

@app.route('/api/status')
def status():
    return jsonify({
        "status": "running",
        "service": "threads-bot",
        "platform": "railway"
    })

@app.route('/api/health')
def health():
    return jsonify({"health": "ok"})

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)

# Call schema initialization before starting the Flask app
initialize_supabase_schema() 