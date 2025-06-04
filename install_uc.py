#!/usr/bin/env python3
"""
Install undetected-chromedriver for VNC Instagram automation
"""

import subprocess
import sys
import logging

logger = logging.getLogger(__name__)

def install_undetected_chromedriver():
    """Install undetected-chromedriver package"""
    try:
        print("Installing undetected-chromedriver...")
        
        # Install using pip
        result = subprocess.run([
            sys.executable, "-m", "pip", "install", "undetected-chromedriver"
        ], capture_output=True, text=True)
        
        if result.returncode == 0:
            print("✅ undetected-chromedriver installed successfully!")
            print(result.stdout)
            return True
        else:
            print("❌ Failed to install undetected-chromedriver")
            print(result.stderr)
            return False
            
    except Exception as e:
        print(f"Error installing undetected-chromedriver: {e}")
        return False

def verify_installation():
    """Verify that undetected-chromedriver can be imported"""
    try:
        import undetected_chromedriver
        print(f"✅ undetected-chromedriver version: {undetected_chromedriver.__version__}")
        return True
    except ImportError:
        print("❌ undetected-chromedriver not available")
        return False

if __name__ == "__main__":
    print("Installing undetected-chromedriver for Instagram VNC automation...")
    
    if install_undetected_chromedriver():
        if verify_installation():
            print("✅ Installation complete! You can now run vnc_setup.py with enhanced Chrome support.")
        else:
            print("❌ Installation verification failed")
    else:
        print("❌ Installation failed") 