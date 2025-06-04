#!/usr/bin/env python3
"""
Undetected ChromeDriver Compatibility Checker
Tests different Chrome options to find compatible configuration
"""

import logging
import sys
import os

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_undetected_chromedriver():
    """Test if undetected-chromedriver works with different option sets"""
    
    try:
        import undetected_chromedriver as uc
        logger.info("✅ undetected_chromedriver imported successfully")
        logger.info(f"Version: {uc.__version__}")
    except ImportError:
        logger.error("❌ undetected_chromedriver not installed")
        logger.info("Install with: pip install undetected-chromedriver")
        return False
    
    # Test profile path
    test_profile = "test_chrome_profile"
    os.makedirs(test_profile, exist_ok=True)
    
    # Test configurations from most compatible to most advanced
    test_configs = [
        {
            "name": "Minimal Options",
            "options": [
                '--no-sandbox',
                '--disable-dev-shm-usage',
                f'--user-data-dir={test_profile}',
                '--window-size=1280,720'
            ],
            "experimental": {}
        },
        {
            "name": "Basic Stealth",
            "options": [
                '--no-sandbox',
                '--disable-dev-shm-usage',
                '--disable-blink-features=AutomationControlled',
                f'--user-data-dir={test_profile}',
                '--window-size=1280,720'
            ],
            "experimental": {}
        },
        {
            "name": "Advanced Stealth",
            "options": [
                '--no-sandbox',
                '--disable-dev-shm-usage',
                '--disable-blink-features=AutomationControlled',
                '--disable-web-security',
                '--disable-features=VizDisplayCompositor',
                f'--user-data-dir={test_profile}',
                '--window-size=1280,720'
            ],
            "experimental": {
                "prefs": {
                    "profile.default_content_setting_values": {
                        "notifications": 2
                    }
                }
            }
        },
        {
            "name": "Full Stealth (Legacy)",
            "options": [
                '--no-sandbox',
                '--disable-dev-shm-usage',
                '--disable-blink-features=AutomationControlled',
                '--disable-web-security',
                '--disable-features=VizDisplayCompositor',
                f'--user-data-dir={test_profile}',
                '--window-size=1280,720'
            ],
            "experimental": {
                "prefs": {
                    "profile.default_content_setting_values": {
                        "notifications": 2
                    }
                },
                "excludeSwitches": ["enable-automation"],
                "useAutomationExtension": False
            }
        }
    ]
    
    successful_config = None
    
    for config in test_configs:
        logger.info(f"\n🔬 Testing: {config['name']}")
        
        try:
            # Create Chrome options
            options = uc.ChromeOptions()
            
            # Add arguments
            for arg in config['options']:
                options.add_argument(arg)
                logger.debug(f"  Added argument: {arg}")
            
            # Add experimental options
            for key, value in config['experimental'].items():
                options.add_experimental_option(key, value)
                logger.debug(f"  Added experimental option: {key}")
            
            # Try to create driver
            logger.info("  Attempting to create Chrome driver...")
            driver = uc.Chrome(options=options, version_main=None)
            
            # Test basic functionality
            logger.info("  Testing navigation...")
            driver.get("https://www.google.com")
            
            title = driver.title
            logger.info(f"  Page title: {title}")
            
            # Close driver
            driver.quit()
            
            logger.info(f"✅ {config['name']} - SUCCESS!")
            successful_config = config
            break
            
        except Exception as e:
            logger.warning(f"❌ {config['name']} - FAILED: {e}")
            continue
    
    # Cleanup
    try:
        import shutil
        shutil.rmtree(test_profile, ignore_errors=True)
    except:
        pass
    
    if successful_config:
        logger.info(f"\n🎯 Recommended configuration: {successful_config['name']}")
        logger.info("Chrome arguments:")
        for arg in successful_config['options']:
            logger.info(f"  {arg}")
        if successful_config['experimental']:
            logger.info("Experimental options:")
            for key, value in successful_config['experimental'].items():
                logger.info(f"  {key}: {value}")
        return True
    else:
        logger.error("\n❌ No compatible configuration found!")
        logger.info("Try updating undetected-chromedriver: pip install --upgrade undetected-chromedriver")
        return False

def main():
    print("🔬 Undetected ChromeDriver Compatibility Checker")
    print("=" * 50)
    
    success = test_undetected_chromedriver()
    
    if success:
        print("\n✅ Compatible configuration found!")
        print("You can now run vnc_setup.py")
    else:
        print("\n❌ No compatible configuration found")
        print("Recommendations:")
        print("1. Update undetected-chromedriver: pip install --upgrade undetected-chromedriver")
        print("2. Try installing a different version: pip install undetected-chromedriver==3.4.0")
        print("3. Check Chrome/Chromium installation")

if __name__ == "__main__":
    main() 