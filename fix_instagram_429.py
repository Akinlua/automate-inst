#!/usr/bin/env python3
"""
Instagram 429 Error Fix Script
Provides immediate solutions for Instagram rate limiting issues
"""

import os
import sys
import time
import logging
import shutil
from pathlib import Path

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def clear_all_chrome_data():
    """Clear all Chrome data to start fresh"""
    profile_paths = [
        "chrome_profile_instagram",
        os.path.expanduser("~/.config/google-chrome"),
        os.path.expanduser("~/.cache/google-chrome"),
    ]
    
    for profile_path in profile_paths:
        if os.path.exists(profile_path):
            try:
                logger.info(f"Clearing Chrome data: {profile_path}")
                if os.path.isdir(profile_path):
                    shutil.rmtree(profile_path)
                else:
                    os.remove(profile_path)
                logger.info(f"✅ Cleared: {profile_path}")
            except Exception as e:
                logger.warning(f"❌ Failed to clear {profile_path}: {e}")

def wait_for_rate_limit_reset():
    """Wait for Instagram rate limit to reset"""
    wait_time = 3600  # 1 hour
    logger.info(f"Waiting {wait_time/60:.0f} minutes for Instagram rate limit to reset...")
    
    start_time = time.time()
    while time.time() - start_time < wait_time:
        remaining = wait_time - (time.time() - start_time)
        mins = int(remaining // 60)
        secs = int(remaining % 60)
        print(f"\rRate limit cooldown: {mins:02d}:{secs:02d} remaining", end="", flush=True)
        time.sleep(1)
    
    print("\n✅ Rate limit cooldown complete!")

def create_fresh_profile():
    """Create a completely fresh Chrome profile"""
    timestamp = int(time.time())
    new_profile = f"chrome_profile_instagram_fresh_{timestamp}"
    
    try:
        os.makedirs(new_profile, exist_ok=True)
        logger.info(f"✅ Created fresh profile: {new_profile}")
        return new_profile
    except Exception as e:
        logger.error(f"❌ Failed to create fresh profile: {e}")
        return None

def main():
    print("🔧 Instagram 429 Error Fix Script")
    print("=" * 40)
    
    print("\n📋 Available options:")
    print("1. Clear all Chrome data and start fresh")
    print("2. Wait for rate limit reset (1 hour)")
    print("3. Create new Chrome profile")
    print("4. All of the above")
    print("5. Exit")
    
    try:
        choice = input("\nSelect option (1-5): ").strip()
        
        if choice == "1":
            print("\n🧹 Clearing Chrome data...")
            clear_all_chrome_data()
            print("✅ Chrome data cleared. Restart VNC setup.")
            
        elif choice == "2":
            print("\n⏰ Starting rate limit cooldown...")
            wait_for_rate_limit_reset()
            
        elif choice == "3":
            print("\n📁 Creating fresh profile...")
            new_profile = create_fresh_profile()
            if new_profile:
                print(f"✅ Use this profile path: {new_profile}")
            
        elif choice == "4":
            print("\n🔄 Running complete fix process...")
            
            # Step 1: Clear data
            print("Step 1: Clearing Chrome data...")
            clear_all_chrome_data()
            
            # Step 2: Create fresh profile
            print("Step 2: Creating fresh profile...")
            new_profile = create_fresh_profile()
            
            # Step 3: Wait
            print("Step 3: Waiting for rate limit reset...")
            wait_for_rate_limit_reset()
            
            print("\n✅ Complete fix process finished!")
            if new_profile:
                print(f"Use profile path: {new_profile}")
            
        elif choice == "5":
            print("👋 Exiting...")
            sys.exit(0)
            
        else:
            print("❌ Invalid choice. Please select 1-5.")
            
    except KeyboardInterrupt:
        print("\n\n👋 Interrupted by user. Exiting...")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main() 