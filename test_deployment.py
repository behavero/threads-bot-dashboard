#!/usr/bin/env python3
"""
Simple deployment test script
Tests if the basic structure works without external dependencies
"""

import os
import sys
from pathlib import Path

def test_basic_structure():
    """Test if the basic project structure is correct"""
    print("🧪 Testing basic project structure...")
    
    # Check required directories
    required_dirs = ['core', 'config', 'assets', 'server', 'docs']
    for dir_name in required_dirs:
        if Path(dir_name).exists():
            print(f"✅ {dir_name}/ directory exists")
        else:
            print(f"❌ {dir_name}/ directory missing")
            return False
    
    # Check required files
    required_files = [
        'start.py',
        'requirements.txt',
        'core/bot.py',
        'config/user_agents.txt',
        'assets/captions.txt'
    ]
    
    for file_name in required_files:
        if Path(file_name).exists():
            print(f"✅ {file_name} exists")
        else:
            print(f"❌ {file_name} missing")
            return False
    
    return True

def test_imports():
    """Test if basic imports work"""
    print("\n🧪 Testing basic imports...")
    
    try:
        import aiohttp
        print("✅ aiohttp imported successfully")
    except ImportError:
        print("❌ aiohttp import failed")
        return False
    
    try:
        import requests
        print("✅ requests imported successfully")
    except ImportError:
        print("❌ requests import failed")
        return False
    
    try:
        import flask
        print("✅ flask imported successfully")
    except ImportError:
        print("❌ flask import failed")
        return False
    
    return True

def test_config_loading():
    """Test if configuration files can be loaded"""
    print("\n🧪 Testing configuration loading...")
    
    try:
        with open('config/user_agents.txt', 'r') as f:
            user_agents = [line.strip() for line in f if line.strip()]
        print(f"✅ Loaded {len(user_agents)} user agents")
    except Exception as e:
        print(f"❌ Failed to load user agents: {e}")
        return False
    
    try:
        with open('assets/captions.txt', 'r') as f:
            captions = [line.strip() for line in f if line.strip()]
        print(f"✅ Loaded {len(captions)} captions")
    except Exception as e:
        print(f"❌ Failed to load captions: {e}")
        return False
    
    return True

def main():
    """Main test function"""
    print("🚀 Enhanced Threads Bot - Deployment Test")
    print("=" * 50)
    
    # Test basic structure
    if not test_basic_structure():
        print("\n❌ Basic structure test failed")
        return False
    
    # Test imports
    if not test_imports():
        print("\n❌ Import test failed")
        return False
    
    # Test config loading
    if not test_config_loading():
        print("\n❌ Configuration test failed")
        return False
    
    print("\n✅ All tests passed! Deployment should work.")
    print("\n📋 Next steps:")
    print("1. Deploy to Render/Railway")
    print("2. Add threads-api dependency: pip install git+https://github.com/Danie1/threads-api.git")
    print("3. Configure accounts in config/accounts.json")
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 