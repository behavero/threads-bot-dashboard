#!/bin/bash
echo "🚀 Building Enhanced Threads Bot Backend..."

# Check if we're in the right directory
if [ ! -f "main.py" ]; then
    echo "❌ Error: main.py not found. Make sure we're in the backend directory."
    exit 1
fi

# Install Python dependencies
echo "📦 Installing Python dependencies..."
pip install -r requirements.txt

# Check if installation was successful
if [ $? -ne 0 ]; then
    echo "❌ Error: Failed to install Python dependencies"
    exit 1
fi

echo "✅ Build completed successfully!"
echo "🎯 Ready to start with: python main.py" 