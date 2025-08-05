#!/usr/bin/env python3
"""
Minimal Threads Bot Server
Simple Flask server for Railway deployment
"""

import os
from flask import Flask, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

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