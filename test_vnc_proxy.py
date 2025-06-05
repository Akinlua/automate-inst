#!/usr/bin/env python3
"""
Test script for VNC setup with proxy support
This script demonstrates how to use the VNC server with different proxy configurations.
"""

import os
import sys
from vnc_setup import start_vnc_chrome_session, get_vnc_status, set_vnc_proxy, stop_vnc_session

def test_vnc_with_proxy():
    """Test VNC setup with proxy configuration"""
    
    # Example proxy configurations
    proxy_configs = {
        'http_proxy': 'http://proxy.example.com:8080',
        'socks5_proxy': 'socks5://127.0.0.1:1080',
        'https_proxy': 'https://proxy.example.com:8080',
        'no_proxy': None
    }
    
    print("🚀 VNC Proxy Setup Test")
    print("=" * 50)
    
    # Set profile path
    profile_path = os.path.join(os.getcwd(), "chrome_profile_vnc_test")
    
    print("\nAvailable proxy configurations:")
    for i, (name, proxy) in enumerate(proxy_configs.items(), 1):
        print(f"{i}. {name}: {proxy or 'No proxy'}")
    
    # Get user choice
    try:
        choice = input("\nSelect proxy configuration (1-4) or press Enter for no proxy: ").strip()
        if not choice:
            choice = "4"  # Default to no proxy
        
        choice_idx = int(choice) - 1
        proxy_name = list(proxy_configs.keys())[choice_idx]
        proxy_server = proxy_configs[proxy_name]
        
        print(f"\nSelected: {proxy_name}")
        if proxy_server:
            print(f"Proxy server: {proxy_server}")
        else:
            print("No proxy will be used")
            
    except (ValueError, IndexError):
        print("Invalid choice, using no proxy")
        proxy_server = None
    
    print("\n" + "=" * 50)
    print("Starting VNC setup...")
    
    try:
        # Start VNC session with proxy
        result = start_vnc_chrome_session(profile_path, proxy_server)
        
        if result['success']:
            print("\n✅ VNC setup successful!")
            access_info = result['access_info']
            
            print("\n📋 Access Information:")
            print("-" * 30)
            print(f"VNC Display: {access_info['vnc_display']}")
            print(f"VNC Port: {access_info['vnc_port']}")
            print(f"Web VNC Port: {access_info['vnc_web_port']}")
            print(f"Password: {access_info['vnc_password']}")
            print(f"Web Access: {access_info['web_url']}")
            print(f"Direct VNC: {access_info['direct_vnc']}")
            if access_info.get('proxy_server'):
                print(f"Proxy Server: {access_info['proxy_server']}")
            
            print("\n🔗 How to connect:")
            print("1. Web Browser: Open the Web Access URL above")
            print("2. VNC Client: Connect to the Direct VNC address")
            print("3. Use the password shown above when prompted")
            
            print("\n⚠️  Note: Chrome should open automatically with Instagram login page")
            print("   If proxy is configured, all traffic will go through the proxy")
            
            # Show status
            status = get_vnc_status()
            print(f"\n📊 Current Status:")
            print(f"VNC Running: {'✅' if status['vnc_running'] else '❌'}")
            print(f"Web VNC Running: {'✅' if status['websockify_running'] else '❌'}")
            print(f"Chrome Running: {'✅' if status['chrome_running'] else '❌'}")
            print(f"Proxy Enabled: {'✅' if status['proxy_enabled'] else '❌'}")
            
            print("\n🛑 To stop VNC server later, run:")
            print("python3 -c \"from vnc_setup import stop_vnc_session; stop_vnc_session()\"")
            
        else:
            print(f"\n❌ VNC setup failed: {result['error']}")
            print("\nTroubleshooting:")
            print("1. Make sure you're running as root/sudo")
            print("2. Check if all dependencies are installed")
            print("3. Verify network connectivity if using proxy")
            
    except KeyboardInterrupt:
        print("\n\n⚠️  Setup interrupted by user")
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        print("\nPlease check the vnc_setup.log file for detailed error information")

def test_proxy_change():
    """Test changing proxy configuration on running VNC session"""
    print("\n🔄 Testing proxy change on running session...")
    
    status = get_vnc_status()
    if not status['vnc_running']:
        print("❌ No VNC session running. Start a session first.")
        return
    
    new_proxy = input("Enter new proxy server (or press Enter to disable): ").strip()
    
    if new_proxy:
        set_vnc_proxy(new_proxy)
        print(f"✅ Proxy changed to: {new_proxy}")
        print("⚠️  Note: You'll need to restart Chrome for proxy changes to take effect")
    else:
        set_vnc_proxy("")
        print("✅ Proxy disabled")

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "change-proxy":
        test_proxy_change()
    else:
        test_vnc_with_proxy() 