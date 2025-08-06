#!/bin/bash

# Threads Bot Deployment Script
# This script handles deployment on Render and other platforms

echo "🚀 Starting Threads Bot deployment..."

# Update pip to latest version
echo "📦 Updating pip..."
python -m pip install --upgrade pip

# Install Python dependencies
echo "📦 Installing Python dependencies..."
pip install -r requirements.txt

# Verify installation
echo "✅ Verifying installation..."
python -c "import flask, supabase, aiohttp; print('All dependencies installed successfully')"

# Start the application
echo "🚀 Starting Threads Bot server..."
python start.py 