#!/usr/bin/env python3
"""
Account Routes
Handles account management with Meta OAuth (legacy login removed)
"""

import os
import logging
from datetime import datetime
from flask import Blueprint, request, jsonify
from database import DatabaseManager

logger = logging.getLogger(__name__)

accounts = Blueprint('accounts', __name__)

@accounts.route('/api/accounts/login', methods=['POST'])
def login_account():
    """Legacy login endpoint - use Meta OAuth instead"""
    return jsonify({
        "ok": False,
        "error": "Legacy login system removed. Please use Meta OAuth flow to connect your Threads account.",
        "oauth_required": True
    }), 400

@accounts.route('/api/accounts/verify', methods=['POST'])
def verify_account():
    """Legacy verification endpoint - use Meta OAuth instead"""
    return jsonify({
        "ok": False,
        "error": "Legacy verification system removed. Please use Meta OAuth flow to connect your Threads account.",
        "oauth_required": True
    }), 400

@accounts.route('/api/accounts/test-login', methods=['GET'])
def test_login():
    """Legacy test login endpoint - use Meta OAuth instead"""
    return jsonify({
        "ok": False,
        "error": "Legacy test login removed. Please use Meta OAuth flow to connect your Threads account.",
        "oauth_required": True
    }), 400
