#!/usr/bin/env python3
"""
Test script for improved VNC Chrome configuration
"""

import os
import sys
import time
from vnc_setup import start_vnc_chrome_session, restart_chrome_fresh_session, get_vnc_access_info

def test_improved_chrome():
    """Test the improved Chrome configuration"""
    profile_path = os.path.join(os.getcwd(), "chrome_profile_instagram")
    
    print("🧪 Testing improved Chrome configuration for Instagram...")
    print("=" * 60)
    
    # Test VNC session start
    print("\n1. Starting VNC session with improved Chrome...")
    result = start_vnc_chrome_session(profile_path)
    
    if result['success']:
        print("✅ VNC session started successfully!")
        
        # Get access info
        access_info = get_vnc_access_info()
        print(f"\n📋 Access Information:")
        print(f"   Web URL: {access_info['web_url']}")
        print(f"   Password: {access_info['vnc_password']}")
        print(f"   VNC Port: {access_info['vnc_port']}")
        
        print(f"\n🌐 Connect to VNC:")
        print(f"   1. Open browser and go to: {access_info['web_url']}")
        print(f"   2. Enter password: {access_info['vnc_password']}")
        print(f"   3. You should see Chrome with Instagram login page")
        
        print(f"\n🔧 If you see 'Something went wrong' on Instagram:")
        print(f"   1. Try refreshing the page")
        print(f"   2. Clear browser data manually")
        print(f"   3. Or run: python3 -c \"from vnc_setup import restart_chrome_fresh_session; restart_chrome_fresh_session('{profile_path}')\"")
        
        print(f"\n💡 Tips for successful login:")
        print(f"   - Use the same IP/location you normally use")
        print(f"   - Don't use incognito/private mode")
        print(f"   - Be patient with loading times")
        print(f"   - Try typing slowly and naturally")
        
    else:
        print(f"❌ VNC session failed: {result.get('error', 'Unknown error')}")
        return False
    
    return True

def test_chrome_restart():
    """Test Chrome restart functionality"""
    profile_path = os.path.join(os.getcwd(), "chrome_profile_instagram")
    
    print("\n🔄 Testing Chrome restart functionality...")
    print("-" * 40)
    
    result = restart_chrome_fresh_session(profile_path)
    if result:
        print("✅ Chrome restarted successfully with fresh session")
    else:
        print("❌ Chrome restart failed")
    
    return result

if __name__ == "__main__":
    print("🚀 VNC Chrome Configuration Tester")
    print("=" * 40)
    
    # Test improved Chrome
    if test_improved_chrome():
        print("\n" + "=" * 60)
        print("✅ VNC Chrome test completed successfully!")
        print("\nNext steps:")
        print("1. Access the VNC web interface")
        print("2. Try logging into Instagram")
        print("3. If issues persist, try the Chrome restart function")
    else:
        print("\n❌ VNC Chrome test failed")
        sys.exit(1) 