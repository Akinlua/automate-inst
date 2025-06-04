#!/usr/bin/env python3
"""
Test script to verify Instagram login selectors work
This script opens Instagram login page and checks if the selectors can be found
WITHOUT actually logging in.
"""

import os
import sys
import time
import logging
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
import undetected_chromedriver as uc
import ssl
import urllib3

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("selector_test")

def test_instagram_selectors():
    """Test if the Instagram login selectors can be found"""
    
    # Disable SSL warnings
    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
    ssl._create_default_https_context = ssl._create_unverified_context
    
    options = uc.ChromeOptions()
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument('--disable-blink-features=AutomationControlled')
    options.add_argument('--headless')  # Run in headless mode for testing
    
    driver = None
    try:
        driver = uc.Chrome(version_main=136, options=options)
        wait = WebDriverWait(driver, 10)
        
        logger.info("Navigating to Instagram login page...")
        driver.get("https://www.instagram.com/accounts/login/")
        time.sleep(3)
        
        # Test username field selectors
        username_selectors = [
            'input[name="username"]',
            'input._aa4b._add6._ac4d._ap35',
            'input[aria-label="Phone number, username, or email"]'
        ]
        
        username_found = False
        for selector in username_selectors:
            try:
                element = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, selector)))
                logger.info(f"✓ Username field found with selector: {selector}")
                username_found = True
                break
            except TimeoutException:
                logger.warning(f"✗ Username field NOT found with selector: {selector}")
        
        # Test password field selectors
        password_selectors = [
            'input[name="password"]',
            'input._aa4b._add6._ac4d._ap35[type="password"]',
            'input[aria-label="Password"]'
        ]
        
        password_found = False
        for selector in password_selectors:
            try:
                element = driver.find_element(By.CSS_SELECTOR, selector)
                logger.info(f"✓ Password field found with selector: {selector}")
                password_found = True
                break
            except NoSuchElementException:
                logger.warning(f"✗ Password field NOT found with selector: {selector}")
        
        # Test login button selectors
        login_selectors = [
            'button[type="submit"]._aswp._aswr._aswu._asw_._asx2',
            'button[type="submit"]',
            'button._aswp._aswr._aswu._asw_._asx2',
            'div[role="button"]'
        ]
        
        login_found = False
        for selector in login_selectors:
            try:
                element = driver.find_element(By.CSS_SELECTOR, selector)
                logger.info(f"✓ Login button found with selector: {selector}")
                login_found = True
                break
            except NoSuchElementException:
                logger.warning(f"✗ Login button NOT found with selector: {selector}")
        
        # Summary
        logger.info("\n" + "="*50)
        logger.info("SELECTOR TEST RESULTS:")
        logger.info(f"Username field: {'✓ FOUND' if username_found else '✗ NOT FOUND'}")
        logger.info(f"Password field: {'✓ FOUND' if password_found else '✗ NOT FOUND'}")
        logger.info(f"Login button: {'✓ FOUND' if login_found else '✗ NOT FOUND'}")
        
        if username_found and password_found and login_found:
            logger.info("✓ All selectors working - automated login should work!")
        else:
            logger.warning("⚠️  Some selectors failed - automated login may not work")
        
        logger.info("="*50)
        
    except Exception as e:
        logger.error(f"Error during selector test: {e}")
    
    finally:
        if driver:
            driver.quit()

if __name__ == "__main__":
    test_instagram_selectors() 