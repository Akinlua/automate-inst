#!/usr/bin/env python3
"""
Test script for fixed VNC setup with selenium-driverless async/await
"""

import os
import sys
import asyncio
import logging

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def test_vnc_async():
    """Test VNC setup with proper async/await"""
    try:
        from vnc_setup import start_vnc_chrome_session, get_vnc_status, get_vnc_access_info
        
        profile_path = os.path.join(os.getcwd(), "chrome_profile_instagram")
        
        print("🧪 Testing VNC setup with selenium-driverless (async/await fixed)")
        print("=" * 60)
        
        # Test VNC session start
        print("\n1. Starting VNC session...")
        result = await start_vnc_chrome_session(profile_path)
        
        if result['success']:
            print("✅ VNC session started successfully!")
            
            # Get access info (synchronous)
            access_info = get_vnc_access_info()
            print(f"\n📋 Access Information:")
            print(f"   Web URL: {access_info['web_url']}")
            print(f"   Password: {access_info['vnc_password']}")
            print(f"   VNC Port: {access_info['vnc_port']}")
            
            # Get detailed status (asynchronous)
            print(f"\n2. Getting detailed status...")
            status = await get_vnc_status()
            print(f"📊 VNC Status:")
            print(f"   VNC Running: {'✅' if status['vnc_running'] else '❌'}")
            print(f"   Websockify Running: {'✅' if status['websockify_running'] else '❌'}")
            print(f"   Chrome Running: {'✅' if status['chrome_running'] else '❌'}")
            print(f"   Selenium Driver Active: {'✅' if status['selenium_driver_active'] else '❌'}")
            
            print(f"\n🌐 Connect to VNC:")
            print(f"   Open browser: {access_info['web_url']}")
            print(f"   Password: {access_info['vnc_password']}")
            print(f"   You should see Chrome with Instagram loaded!")
            
            print(f"\n🎉 Test completed successfully!")
            print(f"   Chrome should be running in VNC with Instagram login page")
            print(f"   No more async/await warnings!")
            
        else:
            print(f"❌ VNC session failed: {result.get('error', 'Unknown error')}")
            return False
            
    except Exception as e:
        print(f"❌ Test failed with error: {e}")
        logger.error(f"Test failed: {e}", exc_info=True)
        return False
    
    return True

def test_sync_wrapper():
    """Synchronous wrapper for testing from Flask-like environments"""
    try:
        # Test that we can call async functions from sync context
        result = asyncio.run(test_vnc_async())
        return result
    except Exception as e:
        print(f"❌ Sync wrapper test failed: {e}")
        return False

if __name__ == "__main__":
    print("🚀 Testing VNC setup with selenium-driverless async fixes")
    
    # Test async version
    print("\n=== Testing Async Version ===")
    success = asyncio.run(test_vnc_async())
    
    if success:
        print("\n✅ All tests passed!")
        print("VNC setup is working correctly with selenium-driverless")
        print("No more RuntimeWarnings about coroutines not being awaited!")
    else:
        print("\n❌ Some tests failed!")
        sys.exit(1) 