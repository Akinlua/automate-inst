#!/usr/bin/env python3
"""
Scheduler runner for Instagram Auto Poster
Run this script to start the background scheduler service
"""

import sys
import signal
import logging
from instagram_poster import InstagramPoster

def signal_handler(sig, frame):
    """Handle interrupt signals"""
    print('\n🛑 Scheduler stopped by user')
    sys.exit(0)

def main():
    """Main function to run the scheduler"""
    print("🚀 Starting Instagram Auto Poster Scheduler...")
    print("📱 This will post content automatically based on your settings")
    print("⚡ Press Ctrl+C to stop the scheduler")
    print("=" * 60)
    
    # Set up signal handler for graceful shutdown
    signal.signal(signal.SIGINT, signal_handler)
    
    try:
        # Initialize the poster
        poster = InstagramPoster()
        
        # Display current settings
        settings = poster.settings
        print(f"📊 Current Settings:")
        print(f"   • Enabled: {settings.get('enabled', True)}")
        print(f"   • Images per post: {settings.get('num_images', 1)}")
        print(f"   • Posting interval: {settings.get('post_interval_hours', 4)} hours")
        print("=" * 60)
        
        # Check if scheduler is enabled
        if not settings.get('enabled', True):
            print("⚠️  Scheduler is disabled. Enable it in the web interface settings.")
            print("💡 Visit http://localhost:5000/settings to configure")
            return
        
        # Start the scheduler
        poster.run_scheduler()
        
    except KeyboardInterrupt:
        print('\n🛑 Scheduler stopped by user')
    except Exception as e:
        print(f'❌ Error running scheduler: {e}')
        logging.error(f"Scheduler error: {e}")

if __name__ == "__main__":
    main() 