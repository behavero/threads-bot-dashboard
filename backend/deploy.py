#!/usr/bin/env python3
"""
Enhanced Threads Bot - Deployment Helper Script
Validates and prepares the bot for deployment on Render, Railway, or Replit
"""

import os
import sys
import json
from pathlib import Path
from typing import List, Dict

def check_required_files() -> List[str]:
    """Check if all required files are present"""
    required_files = [
        'core/bot.py',
        'start.py',
        'requirements.txt',
        'config/accounts.json',
        'assets/captions.txt',
        'config/user_agents.txt',
        'assets/images/'
    ]
    
    missing_files = []
    for file in required_files:
        if file.endswith('/'):
            # Directory
            if not Path(file).exists():
                missing_files.append(file)
        else:
            # File
            if not Path(file).exists():
                missing_files.append(file)
    
    return missing_files

def validate_accounts_file() -> bool:
    """Validate config/accounts.json structure"""
    try:
        with open('config/accounts.json', 'r', encoding='utf-8') as f:
            accounts = json.load(f)
        
        if not isinstance(accounts, list):
            print("❌ config/accounts.json should be a list of accounts")
            return False
        
        if len(accounts) == 0:
            print("⚠️  No accounts found in config/accounts.json")
            return False
        
        for i, account in enumerate(accounts):
            required_fields = ['username', 'email', 'password']
            for field in required_fields:
                if field not in account:
                    print(f"❌ Account {i} missing required field: {field}")
                    return False
        
        print(f"✅ Found {len(accounts)} accounts in config/accounts.json")
        return True
        
    except Exception as e:
        print(f"❌ Error reading config/accounts.json: {e}")
        return False

def validate_captions_file() -> bool:
    """Validate assets/captions.txt content"""
    try:
        with open('assets/captions.txt', 'r', encoding='utf-8') as f:
            captions = [line.strip() for line in f if line.strip()]
        
        if len(captions) == 0:
            print("⚠️  No captions found in assets/captions.txt")
            return False
        
        print(f"✅ Found {len(captions)} captions in assets/captions.txt")
        return True
        
    except Exception as e:
        print(f"❌ Error reading assets/captions.txt: {e}")
        return False

def validate_user_agents_file() -> bool:
    """Validate config/user_agents.txt content"""
    try:
        with open('config/user_agents.txt', 'r', encoding='utf-8') as f:
            user_agents = [line.strip() for line in f if line.strip()]
        
        if len(user_agents) == 0:
            print("⚠️  No user agents found in config/user_agents.txt")
            return False
        
        print(f"✅ Found {len(user_agents)} user agents in config/user_agents.txt")
        return True
        
    except Exception as e:
        print(f"❌ Error reading config/user_agents.txt: {e}")
        return False

def check_images_directory() -> bool:
    """Check images directory"""
    images_dir = Path('images/')
    
    if not images_dir.exists():
        print("📁 Creating images directory...")
        images_dir.mkdir(exist_ok=True)
        print("✅ Created images directory")
        return True
    
    # Count image files
    image_extensions = {'.jpg', '.jpeg', '.png', '.gif'}
    image_files = [f for f in images_dir.iterdir() if f.suffix.lower() in image_extensions]
    
    print(f"✅ Images directory exists with {len(image_files)} image files")
    return True

def check_deployment_files() -> bool:
    """Check if deployment configuration files exist"""
    deployment_files = {
        'render.yaml': 'Render.com deployment',
        'railway.json': 'Railway.app deployment',
        'railway.toml': 'Railway.app deployment',
        '.replit': 'Replit.com deployment',
        'replit.nix': 'Replit.com deployment'
    }
    
    found_files = []
    for file, platform in deployment_files.items():
        if Path(file).exists():
            found_files.append(f"{file} ({platform})")
    
    if found_files:
        print(f"✅ Found deployment files: {', '.join(found_files)}")
        return True
    else:
        print("⚠️  No deployment configuration files found")
        print("   Create render.yaml, railway.json, or .replit for deployment")
        return False

def check_requirements() -> bool:
    """Check requirements.txt for essential dependencies"""
    try:
        with open('requirements.txt', 'r') as f:
            requirements = f.read()
        
        essential_deps = [
            'git+https://github.com/Danie1/threads-api.git',
            'python-dotenv',
            'aiohttp',
            'requests',
            'instagrapi',
            'pydantic',
            'python-dateutil',
            'colorlog',
            'Pillow',
            'pyyaml',
            'typing-extensions'
        ]
        
        missing_deps = []
        for dep in essential_deps:
            if dep not in requirements:
                missing_deps.append(dep)
        
        if missing_deps:
            print(f"❌ Missing essential dependencies: {', '.join(missing_deps)}")
            return False
        
        print("✅ All essential dependencies found in requirements.txt")
        return True
        
    except Exception as e:
        print(f"❌ Error reading requirements.txt: {e}")
        return False

def create_sample_files():
    """Create sample files if they don't exist"""
    
    # Create sample config/accounts.json if it doesn't exist
    if not Path('config/accounts.json').exists():
        sample_accounts = [
            {
                "username": "your_username_1",
                "email": "your_email_1@example.com",
                "password": "your_password_1",
                "enabled": True,
                "description": "Sample account 1",
                "posting_schedule": {
                    "frequency": "every_5_minutes",
                    "interval_minutes": 5,
                    "timezone": "UTC",
                    "start_time": "00:00",
                    "end_time": "23:59"
                },
                "posting_config": {
                    "use_random_caption": True,
                    "use_random_image": True,
                    "max_posts_per_day": 288,
                    "delay_between_posts_seconds": 300,
                    "user_agent_rotation": True,
                    "random_delays": True,
                    "media_variation": True,
                    "anti_detection_level": "high",
                    "session_timeout": 3600,
                    "max_retries": 3
                },
                "fingerprint_config": {
                    "device_type": "iPhone",
                    "os_version": "17.0",
                    "browser_version": "Safari/604.1",
                    "screen_resolution": "1170x2532",
                    "timezone": "UTC"
                }
            }
        ]
        
        with open('config/accounts.json', 'w', encoding='utf-8') as f:
            json.dump(sample_accounts, f, indent=2, ensure_ascii=False)
        
        print("📝 Created sample config/accounts.json")
        print("⚠️  Please update with your actual account credentials!")
    
    # Create sample assets/captions.txt if it doesn't exist
    if not Path('assets/captions.txt').exists():
        sample_captions = [
            "Just posted this amazing content! 🔥",
            "Check out this incredible post! ✨",
            "Another great day, another great post! 🌟",
            "Sharing some awesome content with you all! 💯",
            "This is absolutely amazing! 🚀"
        ]
        
        with open('assets/captions.txt', 'w', encoding='utf-8') as f:
            f.write('\n'.join(sample_captions))
        
        print("📝 Created sample assets/captions.txt")
        print("⚠️  Please update with your actual captions!")

def main():
    """Main deployment validation function"""
    print("🚀 Enhanced Threads Bot - Deployment Validator")
    print("=" * 50)
    
    # Check required files
    print("\n📋 Checking required files...")
    missing_files = check_required_files()
    
    if missing_files:
        print(f"❌ Missing required files: {', '.join(missing_files)}")
        print("\n📝 Creating sample files...")
        create_sample_files()
        print("\n📋 Re-checking required files...")
        missing_files = check_required_files()
    
    if missing_files:
        print(f"❌ Still missing files: {', '.join(missing_files)}")
        return False
    
    print("✅ All required files present")
    
    # Validate file contents
    print("\n🔍 Validating file contents...")
    
    accounts_valid = validate_accounts_file()
    captions_valid = validate_captions_file()
    user_agents_valid = validate_user_agents_file()
    images_valid = check_images_directory()
    requirements_valid = check_requirements()
    
    # Check deployment files
    print("\n🚀 Checking deployment configuration...")
    deployment_valid = check_deployment_files()
    
    # Summary
    print("\n" + "=" * 50)
    print("📊 DEPLOYMENT VALIDATION SUMMARY")
    print("=" * 50)
    
    all_valid = (
        accounts_valid and 
        captions_valid and 
        user_agents_valid and 
        images_valid and 
        requirements_valid
    )
    
    if all_valid:
        print("✅ All validations passed!")
        print("\n🚀 Your bot is ready for deployment!")
        print("\n📋 Next steps:")
        print("1. Update enhanced_accounts.json with your credentials")
        print("2. Update captions.txt with your content")
        print("3. Add images to the images/ directory")
        print("4. Push to GitHub")
        print("5. Deploy on your chosen platform:")
        print("   - Render.com: Connect repository, auto-deploy")
        print("   - Railway.app: Connect repository, auto-deploy")
        print("   - Replit.com: Import repository, click Run")
        
        if deployment_valid:
            print("\n✅ Deployment configuration files found!")
        else:
            print("\n⚠️  No deployment files found - create render.yaml, railway.json, or .replit")
        
        return True
    else:
        print("❌ Some validations failed. Please fix the issues above.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 