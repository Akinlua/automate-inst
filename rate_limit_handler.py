#!/usr/bin/env python3
"""
Instagram Rate Limit Handler
Provides strategies to handle Instagram rate limiting (HTTP 429 errors)
"""

import time
import random
import logging
import subprocess
import os
from datetime import datetime, timedelta
from pathlib import Path

logger = logging.getLogger(__name__)

class InstagramRateLimitHandler:
    def __init__(self):
        self.rate_limit_file = Path("rate_limit_tracker.txt")
        self.last_access_time = None
        self.access_count = 0
        self.daily_limit = 50  # Conservative daily access limit
        
    def check_rate_limit_status(self):
        """Check if we're currently rate limited"""
        try:
            if self.rate_limit_file.exists():
                with open(self.rate_limit_file, 'r') as f:
                    content = f.read().strip()
                    if content:
                        last_blocked = datetime.fromisoformat(content)
                        # Wait at least 1 hour after being blocked
                        if datetime.now() - last_blocked < timedelta(hours=1):
                            return True, last_blocked
            return False, None
        except Exception as e:
            logger.warning(f"Error checking rate limit status: {e}")
            return False, None
    
    def record_rate_limit(self):
        """Record that we hit a rate limit"""
        try:
            with open(self.rate_limit_file, 'w') as f:
                f.write(datetime.now().isoformat())
            logger.info("Rate limit recorded")
        except Exception as e:
            logger.error(f"Failed to record rate limit: {e}")
    
    def get_wait_time(self, attempt_number=1):
        """Calculate wait time based on attempt number"""
        base_wait = 30  # Base wait time in seconds
        exponential_backoff = base_wait * (2 ** (attempt_number - 1))
        jitter = random.uniform(0.5, 1.5)  # Add randomness
        return min(exponential_backoff * jitter, 300)  # Cap at 5 minutes
    
    def clear_browser_data(self, profile_path):
        """Clear browser data to appear as a new user"""
        try:
            logger.info("Clearing browser data for fresh session...")
            
            # Items to clear
            clear_items = [
                "Cookies",
                "Cookies-journal", 
                "Local Storage",
                "Session Storage",
                "Network",
                "Service Worker",
                "Cache",
                "GPUCache",
                "Application Cache",
                "Web Data",
                "Web Data-journal",
                "History",
                "History-journal",
                "Login Data",
                "Login Data-journal"
            ]
            
            for item in clear_items:
                item_path = os.path.join(profile_path, item)
                if os.path.exists(item_path):
                    if os.path.isfile(item_path):
                        os.remove(item_path)
                        logger.debug(f"Removed file: {item}")
                    elif os.path.isdir(item_path):
                        import shutil
                        shutil.rmtree(item_path, ignore_errors=True)
                        logger.debug(f"Removed directory: {item}")
            
            logger.info("Browser data cleared successfully")
            return True
            
        except Exception as e:
            logger.error(f"Failed to clear browser data: {e}")
            return False
    
    def restart_network_services(self):
        """Restart network services to potentially get a new IP"""
        try:
            logger.info("Attempting to restart network services...")
            
            # This is for Linux systems - adjust for your environment
            commands = [
                ["sudo", "systemctl", "restart", "NetworkManager"],
                ["sudo", "service", "networking", "restart"],
                ["sudo", "dhclient", "-r"],  # Release IP
                ["sudo", "dhclient"]         # Renew IP
            ]
            
            for cmd in commands:
                try:
                    result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
                    if result.returncode == 0:
                        logger.info(f"Successfully ran: {' '.join(cmd)}")
                    else:
                        logger.warning(f"Command failed: {' '.join(cmd)} - {result.stderr}")
                except subprocess.TimeoutExpired:
                    logger.warning(f"Command timed out: {' '.join(cmd)}")
                except FileNotFoundError:
                    logger.debug(f"Command not found: {' '.join(cmd)}")
                except Exception as e:
                    logger.warning(f"Error running command {' '.join(cmd)}: {e}")
            
            # Wait for network to stabilize
            time.sleep(10)
            return True
            
        except Exception as e:
            logger.error(f"Failed to restart network services: {e}")
            return False
    
    def use_different_access_method(self, vnc_manager, profile_path):
        """Try different access methods when rate limited"""
        strategies = [
            self._strategy_fresh_profile,
            self._strategy_mobile_user_agent,
            self._strategy_different_endpoint,
            self._strategy_proxy_rotation
        ]
        
        for i, strategy in enumerate(strategies):
            logger.info(f"Trying strategy {i+1}: {strategy.__name__}")
            if strategy(vnc_manager, profile_path):
                return True
            time.sleep(30)  # Wait between strategies
        
        return False
    
    def _strategy_fresh_profile(self, vnc_manager, profile_path):
        """Strategy 1: Use completely fresh profile"""
        try:
            # Create a new profile path with timestamp
            timestamp = int(time.time())
            new_profile = f"{profile_path}_fresh_{timestamp}"
            
            logger.info(f"Creating fresh profile: {new_profile}")
            os.makedirs(new_profile, exist_ok=True)
            
            # Stop current Chrome and restart with new profile
            if vnc_manager.chrome_driver:
                vnc_manager.chrome_driver.quit()
                vnc_manager.chrome_driver = None
            
            return vnc_manager.start_chrome_in_vnc(new_profile)
            
        except Exception as e:
            logger.error(f"Fresh profile strategy failed: {e}")
            return False
    
    def _strategy_mobile_user_agent(self, vnc_manager, profile_path):
        """Strategy 2: Use mobile user agent"""
        try:
            logger.info("Switching to mobile user agent...")
            
            # This would require modifying the Chrome options
            # For now, we'll clear data and restart
            self.clear_browser_data(profile_path)
            time.sleep(5)
            
            return vnc_manager.restart_chrome_fresh(profile_path)
            
        except Exception as e:
            logger.error(f"Mobile user agent strategy failed: {e}")
            return False
    
    def _strategy_different_endpoint(self, vnc_manager, profile_path):
        """Strategy 3: Try accessing Instagram through different endpoints"""
        try:
            logger.info("Trying different Instagram endpoints...")
            
            endpoints = [
                "https://www.instagram.com/",
                "https://instagram.com/",
                "https://m.instagram.com/",
                "https://www.instagram.com/explore/",
                "https://help.instagram.com/"
            ]
            
            if vnc_manager.chrome_driver:
                for endpoint in endpoints:
                    try:
                        logger.info(f"Trying endpoint: {endpoint}")
                        vnc_manager.chrome_driver.get(endpoint)
                        time.sleep(10)
                        
                        # Check if we can access without being blocked
                        if "429" not in vnc_manager.chrome_driver.page_source:
                            logger.info(f"Success with endpoint: {endpoint}")
                            # Navigate to login page
                            vnc_manager.chrome_driver.get("https://www.instagram.com/accounts/login/")
                            return True
                            
                    except Exception as e:
                        logger.warning(f"Endpoint {endpoint} failed: {e}")
                        continue
            
            return False
            
        except Exception as e:
            logger.error(f"Different endpoint strategy failed: {e}")
            return False
    
    def _strategy_proxy_rotation(self, vnc_manager, profile_path):
        """Strategy 4: Simulate proxy rotation by changing network settings"""
        try:
            logger.info("Attempting network refresh...")
            
            # Clear browser data
            self.clear_browser_data(profile_path)
            
            # Try to restart network (may require sudo)
            self.restart_network_services()
            
            # Restart Chrome
            return vnc_manager.restart_chrome_fresh(profile_path)
            
        except Exception as e:
            logger.error(f"Proxy rotation strategy failed: {e}")
            return False
    
    def handle_rate_limit(self, vnc_manager, profile_path, attempt_number=1):
        """Main handler for rate limiting"""
        try:
            logger.warning(f"Handling Instagram rate limit (attempt {attempt_number})")
            
            # Record the rate limit
            self.record_rate_limit()
            
            # Calculate wait time
            wait_time = self.get_wait_time(attempt_number)
            logger.info(f"Waiting {wait_time:.1f} seconds before retry...")
            
            # Wait with periodic updates
            start_time = time.time()
            while time.time() - start_time < wait_time:
                remaining = wait_time - (time.time() - start_time)
                if remaining > 30:
                    logger.info(f"Rate limit cooldown: {remaining:.0f} seconds remaining...")
                    time.sleep(30)
                else:
                    time.sleep(remaining)
                    break
            
            # Try different access strategies
            logger.info("Attempting to bypass rate limit...")
            success = self.use_different_access_method(vnc_manager, profile_path)
            
            if success:
                logger.info("Successfully bypassed rate limit!")
                return True
            else:
                logger.warning("All bypass strategies failed")
                return False
                
        except Exception as e:
            logger.error(f"Error handling rate limit: {e}")
            return False

# Global rate limit handler
rate_handler = InstagramRateLimitHandler()

def handle_instagram_rate_limit(vnc_manager, profile_path, attempt_number=1):
    """Public function to handle rate limiting"""
    return rate_handler.handle_rate_limit(vnc_manager, profile_path, attempt_number)

def check_if_rate_limited():
    """Check if we're currently rate limited"""
    return rate_handler.check_rate_limit_status()

def clear_rate_limit_record():
    """Clear rate limit record"""
    try:
        if rate_handler.rate_limit_file.exists():
            rate_handler.rate_limit_file.unlink()
            logger.info("Rate limit record cleared")
    except Exception as e:
        logger.error(f"Failed to clear rate limit record: {e}")

if __name__ == "__main__":
    # Test the rate limit handler
    print("Instagram Rate Limit Handler")
    
    is_limited, last_blocked = check_if_rate_limited()
    if is_limited:
        print(f"Currently rate limited since: {last_blocked}")
    else:
        print("No active rate limit detected") 