#!/usr/bin/env python3
"""
Pydantic Compatibility Check
Ensures Pydantic v1.x is installed for instagrapi compatibility
"""

import sys
import subprocess
import os

def check_pydantic_version():
    """Check if Pydantic v1.x is installed"""
    try:
        import pydantic
        version = pydantic.__version__
        print(f"📦 Pydantic version: {version}")
        
        # Check if it's v1.x
        if version.startswith('1.'):
            print("✅ Pydantic v1.x detected - compatible with instagrapi")
            return True
        else:
            print("❌ Pydantic v2.x detected - incompatible with instagrapi")
            print("🔧 This will cause ForwardRef._evaluate() errors")
            return False
            
    except ImportError:
        print("❌ Pydantic not installed")
        return False

def check_instagrapi_import():
    """Test if instagrapi can be imported without errors"""
    try:
        print("🔍 Testing instagrapi import...")
        from instagrapi import Client
        print("✅ Instagrapi imported successfully")
        
        # Test basic client creation
        client = Client()
        print("✅ Instagrapi Client created successfully")
        return True
        
    except Exception as e:
        print(f"❌ Instagrapi import failed: {e}")
        return False

def check_forwardref_error():
    """Test for the specific ForwardRef._evaluate() error"""
    try:
        print("🔍 Testing for ForwardRef._evaluate() error...")
        from instagrapi import Client
        
        # Try to create a client and access some properties that might trigger the error
        client = Client()
        
        # Test some basic operations that might trigger ForwardRef issues
        client.delay_range = [1, 3]
        client.device_settings = {}
        
        print("✅ No ForwardRef._evaluate() error detected")
        return True
        
    except Exception as e:
        error_str = str(e)
        if "ForwardRef._evaluate()" in error_str or "recursive_guard" in error_str:
            print(f"❌ ForwardRef._evaluate() error detected: {error_str}")
            return False
        else:
            print(f"⚠️ Other error during test: {error_str}")
            return True

def install_pydantic_v1():
    """Install Pydantic v1.x"""
    try:
        print("🔧 Installing Pydantic v1.x...")
        subprocess.check_call([
            sys.executable, "-m", "pip", "install", 
            "pydantic==1.10.9", "--force-reinstall"
        ])
        print("✅ Pydantic v1.x installed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to install Pydantic v1.x: {e}")
        return False

def check_environment():
    """Check the deployment environment"""
    print(f"🌍 Environment: {os.getenv('RENDER', 'Local')}")
    print(f"🐍 Python version: {sys.version}")
    print(f"📁 Working directory: {os.getcwd()}")

def main():
    """Main compatibility check"""
    print("🔍 Checking Pydantic compatibility for instagrapi...")
    
    # Check environment
    check_environment()
    
    # Check current Pydantic version
    pydantic_ok = check_pydantic_version()
    
    if not pydantic_ok:
        print("\n🔧 Attempting to fix Pydantic version...")
        if install_pydantic_v1():
            # Re-check after installation
            pydantic_ok = check_pydantic_version()
    
    # Test instagrapi import
    instagrapi_ok = check_instagrapi_import()
    
    # Test for ForwardRef error specifically
    forwardref_ok = check_forwardref_error()
    
    print("\n📊 Compatibility Summary:")
    print(f"   Pydantic v1.x: {'✅' if pydantic_ok else '❌'}")
    print(f"   Instagrapi import: {'✅' if instagrapi_ok else '❌'}")
    print(f"   No ForwardRef error: {'✅' if forwardref_ok else '❌'}")
    
    if pydantic_ok and instagrapi_ok and forwardref_ok:
        print("\n🎉 All compatibility checks passed!")
        print("✅ No more ForwardRef._evaluate() errors expected")
        return True
    else:
        print("\n⚠️ Compatibility issues detected")
        print("🔧 Please check the installation and try again")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
