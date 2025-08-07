#!/usr/bin/env python3
"""
WSGI entry point for production deployment
"""

import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Import the Flask app
from start import app

if __name__ == "__main__":
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port) 