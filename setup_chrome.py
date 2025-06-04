#!/usr/bin/env python3
import os
import sys
import time
import logging
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from dotenv import load_dotenv
import ssl
import urllib3
import undetected_chromedriver as uc
# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("chrome_setup.log"),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger("chrome_setup")

# Load environment variables
load_dotenv()

# Configuration
CHROMEDRIVER_PATH = os.getenv("CHROMEDRIVER_PATH", "chromedriver")
CUSTOM_PROFILE_PATH = os.path.join(os.getcwd(), "chrome_profile_instagram")
INSTAGRAM_USERNAME = os.getenv("INSTAGRAM_USERNAME")
INSTAGRAM_PASSWORD = os.getenv("INSTAGRAM_PASSWORD")

class ChromeProfileSetup:
    def __init__(self):
        self.driver = None
        self.wait = None
        
    def cleanup(self):
        """Clean up resources and close the browser"""
        try:
            if self.driver:
                logger.info("Closing browser...")
                self.driver.quit()
                self.driver = None
                logger.info("Browser closed successfully")
        except Exception as e:
            logger.error(f"Error closing browser: {e}")
        
    def setup_chrome_with_custom_profile(self):
        """Setup Chrome driver with a custom profile directory"""
        chrome_options = Options()
        
        # Create custom profile directory if it doesn't exist
        if not os.path.exists(CUSTOM_PROFILE_PATH):
            os.makedirs(CUSTOM_PROFILE_PATH)
            logger.info(f"Created custom profile directory: {CUSTOM_PROFILE_PATH}")
        
        # Use custom profile directory
        chrome_options.add_argument(f"--user-data-dir={CUSTOM_PROFILE_PATH}")
        
        # Additional options for better stability
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--disable-blink-features=AutomationControlled")
        chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
        chrome_options.add_experimental_option('useAutomationExtension', False)
        
        # Remove the detach option so browser closes when script ends
        # chrome_options.add_experimental_option("detach", True)

        prefs = {
            "download.prompt_for_download": False,
            "download.directory_upgrade": True,
            "safebrowsing.enabled": False,  # Disable safe browsing which can block downloads
            "plugins.always_open_pdf_externally": True,  # Auto-download PDFs
            "browser.download.folderList": 2,  # 2 means custom location
            "browser.helperApps.neverAsk.saveToDisk": "application/pdf,application/x-pdf,application/octet-stream,text/plain,text/html",
            "browser.download.manager.showWhenStarting": False
        }
        chrome_options.add_experimental_option("prefs", prefs)
        
        try:
            # Disable SSL warnings
            urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
            ssl._create_default_https_context = ssl._create_unverified_context

            options = uc.ChromeOptions()
            options.add_argument('--no-sandbox')
            options.add_argument('--disable-dev-shm-usage')
            options.add_argument('--disable-blink-features=AutomationControlled')
            options.add_argument(f"--user-data-dir={CUSTOM_PROFILE_PATH}")
            options.add_argument('--ignore-ssl-errors')
            options.add_argument('--ignore-certificate-errors')
            options.add_argument('--allow-running-insecure-content')

            # options.add_argument("--headless")

            self.driver = uc.Chrome(version_main=136, options=options)
            self.wait = WebDriverWait(self.driver, 10)
            
            logger.info("Chrome driver setup successful with custom profile")
            return True
        except Exception as e:
            logger.error(f"Failed to setup Chrome driver: {e}")
            self.cleanup()
            return False
    
    def navigate_to_instagram(self):
        """Navigate to Instagram login page"""
        try:
            self.driver.get("https://www.instagram.com/accounts/login/")
            logger.info("Navigated to Instagram login page")
            time.sleep(3)  # Wait for page to load
            return True
        except Exception as e:
            logger.error(f"Failed to navigate to Instagram: {e}")
            self.cleanup()
            return False
    
    def perform_login(self, username, password):
        """Automatically fill in login credentials and submit"""
        if not username or not password:
            logger.error("Instagram username or password not found in environment variables")
            logger.info("Please add INSTAGRAM_USERNAME and INSTAGRAM_PASSWORD to your .env file")
            self.cleanup()
            return False
        
        try:
            logger.info("Attempting automatic login...")
            
            # Wait for username field and fill it
            username_selectors = [
                'input[name="username"]',
                'input._aa4b._add6._ac4d._ap35',
                'input[aria-label="Phone number, username, or email"]'
            ]
            
            username_field = None
            for selector in username_selectors:
                try:
                    username_field = self.wait.until(
                        EC.presence_of_element_located((By.CSS_SELECTOR, selector))
                    )
                    break
                except TimeoutException:
                    continue
            
            if not username_field:
                logger.error("Could not find username field")
                return False
            
            username_field.clear()
            username_field.send_keys(username)
            logger.info("Username entered successfully")
            
            # Wait for password field and fill it
            password_selectors = [
                'input[name="password"]',
                'input._aa4b._add6._ac4d._ap35[type="password"]',
                'input[aria-label="Password"]'
            ]
            
            password_field = None
            for selector in password_selectors:
                try:
                    password_field = self.driver.find_element(By.CSS_SELECTOR, selector)
                    break
                except NoSuchElementException:
                    continue
            
            if not password_field:
                logger.error("Could not find password field")
                return False
            
            password_field.clear()
            password_field.send_keys(password)
            logger.info("Password entered successfully")
            
            # Find and click login button
            login_selectors = [
                'button[type="submit"]._aswp._aswr._aswu._asw_._asx2',
                'button[type="submit"]',
                'button._aswp._aswr._aswu._asw_._asx2',
                'div[role="button"]'
            ]
            
            login_button = None
            for selector in login_selectors:
                try:
                    login_button = self.driver.find_element(By.CSS_SELECTOR, selector)
                    if login_button.is_enabled():
                        break
                except NoSuchElementException:
                    continue
            
            if not login_button:
                logger.error("Could not find login button")
                return False
            
            login_button.click()
            logger.info("Login button clicked")
            
            # Wait a bit for login to process
            time.sleep(5)
            
            return True
            
        except Exception as e:
            logger.error(f"Error during login: {e}")
            return False
    
    def handle_email_verification(self):
        """Handle email verification if it appears after login"""
        try:
            logger.info("Checking for email verification prompt...")
            
            # Check if we're on the email verification page
            verification_indicators = [
                'input.x1i10hfl.xggy1nq.xtpw4lu.x1tutvks.x1s3xk63.x1s07b3s.x1a2a7pz.xjbqb8w.x1v8p93f.xogb00i.x16stqrj.x1ftr3km.x1ejq31n.xd10rxx.x1sy0etr.x17r0tee.x972fbf.xcfux6l.x1qhh985.xm0m39n.x9f619.xzsf02u.x1lliihq.x15h3p50.x10emqs4.x1vr9vpq.x1iyjqo2.x1y44fgy.x10d0gm4.x1fhayk4.x16wdlz0.x3cjxhe.x8182xy.xwrv7xz.xeuugli.xlyipyv.x1hcrkkg.xfvqz1d.x12vv892.x163jz68.xpp3fsf.xvr60a6.x1sfh74k.x53uk0m.x185fvkj.x1p97g3g.xmtqnhx.x11ig0mb.x1quw8ve.xx0ingd.xp5op4.xs8nzd4.x1fzehxr.xha3pab',
                'input[placeholder*="Code"]',
                'input[aria-label*="Code"]',
                'input[name="verificationCode"]'
            ]
            
            verification_input = None
            for selector in verification_indicators:
                try:
                    verification_input = WebDriverWait(self.driver, 5).until(
                        EC.presence_of_element_located((By.CSS_SELECTOR, selector))
                    )
                    logger.info(f"Email verification page detected with selector: {selector}")
                    break
                except TimeoutException:
                    continue
            
            if not verification_input:
                logger.info("No email verification prompt found - proceeding")
                return True
            
            # Email verification page detected
            logger.info("="*50)
            logger.info("📧 EMAIL VERIFICATION REQUIRED")
            logger.info("Instagram has sent a verification code to your email.")
            logger.info("Please check your email and enter the code below.")
            logger.info("="*50)
            
            # Wait for user to enter the code
            max_attempts = 3
            for attempt in range(max_attempts):
                try:
                    verification_code = input(f"Enter the verification code (Attempt {attempt + 1}/{max_attempts}): ").strip()
                    
                    if not verification_code:
                        logger.warning("No code entered. Please try again.")
                        continue
                    
                    if not verification_code.isdigit() or len(verification_code) < 4:
                        logger.warning("Invalid code format. Please enter a valid verification code.")
                        continue
                    
                    # Clear the input field and enter the code
                    verification_input.clear()
                    verification_input.send_keys(verification_code)
                    logger.info(f"Verification code entered: {verification_code}")
                    
                    # Find and click the continue button
                    continue_selectors = [
                        'div.x1ja2u2z.x78zum5.x2lah0s.x1n2onr6.xl56j7k.x6s0dn4.xozqiw3.x1q0g3np.x972fbf.xcfux6l.x1qhh985.xm0m39n.x9f619.xtvsq51.xqdzp0n.x15p4eik.x1ismhnl.x16ie3sq.x1xila8y.x1xarc30.xrwyoh0',
                        'div[type="submit"]',
                        'div[role="button"]'
                    ]
                    
                    continue_button = None
                    for selector in continue_selectors:
                        try:
                            continue_button = self.driver.find_element(By.CSS_SELECTOR, selector)
                            if continue_button.is_enabled():
                                break
                        except NoSuchElementException:
                            continue
                    
                    if not continue_button:
                        logger.error("Could not find Continue button")
                        continue
                    
                    continue_button.click()
                    logger.info("Continue button clicked")
                    
                    # Wait to see if verification was successful
                    time.sleep(5)
                    
                    # Check if we're still on verification page or if there's an error
                    current_url = self.driver.current_url
                    if "challenge" in current_url or "verify" in current_url:
                        # Check for error messages
                        error_selectors = [
                            '[role="alert"]',
                            '.error',
                            '[aria-live="polite"]'
                        ]
                        
                        error_found = False
                        for error_selector in error_selectors:
                            try:
                                error_element = self.driver.find_element(By.CSS_SELECTOR, error_selector)
                                if error_element.is_displayed() and error_element.text.strip():
                                    logger.warning(f"Verification failed: {error_element.text}")
                                    error_found = True
                                    break
                            except NoSuchElementException:
                                continue
                        
                        if not error_found:
                            logger.warning("Verification code may be incorrect. Please try again.")
                        continue
                    else:
                        logger.info("✓ Email verification successful!")
                        return True
                        
                except KeyboardInterrupt:
                    logger.info("Verification interrupted by user")
                    return False
                except Exception as e:
                    logger.error(f"Error during verification attempt {attempt + 1}: {e}")
                    continue
            
            logger.error("Failed to verify email after maximum attempts")
            logger.info("You can continue manually in the browser if needed")
            return False
            
        except Exception as e:
            logger.warning(f"Error handling email verification: {e}")
            return True  # Don't fail the whole process
    
    def handle_save_info_prompt(self):
        """Handle the 'Save Info' prompt that appears after login"""
        try:
            logger.info("Checking for 'Save Info' prompt...")
            
            # Wait for potential save info button
            save_info_selectors = [
                'button._aswp._aswr._aswu._asw_._asx2[type="button"]',
                'button[type="button"]._aswp._aswr._aswu._asw_._asx2',
                'button:contains("Save Info")',
                'button:contains("Save")',
                'div[role="button"]:contains("Save")'
            ]
            
            save_button = None
            for selector in save_info_selectors:
                try:
                    # Wait up to 10 seconds for save info button
                    save_button = WebDriverWait(self.driver, 10).until(
                        EC.element_to_be_clickable((By.CSS_SELECTOR, selector))
                    )
                    break
                except TimeoutException:
                    continue
            
            if save_button:
                save_button.click()
                logger.info("'Save Info' button clicked successfully")
                time.sleep(2)
                return True
            else:
                logger.info("No 'Save Info' prompt found - proceeding")
                return True
                
        except Exception as e:
            logger.warning(f"Error handling save info prompt: {e}")
            # Don't fail the whole process for this
            return True
    
    def check_if_already_logged_in(self):
        """Check if user is already logged in to Instagram"""
        try:
            logger.info("Checking if already logged in...")
            
            # Navigate to Instagram home page first
            self.driver.get("https://www.instagram.com/")
            time.sleep(3)
            
            # Check for login indicators
            logged_in_indicators = [
                'svg[aria-label="Home"]',  # Home icon
                'div[role="main"]',  # Main content area
                '[data-testid="mobile-nav-home"]',
                'input[placeholder="Search"]',  # Search box
                'a[href*="/direct/"]',  # Messages link
                'svg[aria-label="New post"]'  # New post button
            ]
            
            for indicator in logged_in_indicators:
                try:
                    WebDriverWait(self.driver, 5).until(
                        EC.presence_of_element_located((By.CSS_SELECTOR, indicator))
                    )
                    logger.info("✓ Already logged in to Instagram!")
                    return True
                except TimeoutException:
                    continue
            
            # Check if we're on login page (means not logged in)
            login_indicators = [
                'input[name="username"]',
                'input[name="password"]',
                'button[type="submit"]'
            ]
            
            login_elements_found = 0
            for indicator in login_indicators:
                try:
                    self.driver.find_element(By.CSS_SELECTOR, indicator)
                    login_elements_found += 1
                except NoSuchElementException:
                    continue
            
            if login_elements_found >= 2:
                logger.info("Not logged in - login form detected")
                return False
            
            logger.info("Login status unclear - proceeding with login")
            return False
            
        except Exception as e:
            logger.warning(f"Error checking login status: {e}")
            return False
    
    def verify_login_success(self):
        """Verify that login was successful with comprehensive checks"""
        try:
            logger.info("Verifying login success...")
            
            # Wait a bit for page to load after login actions
            time.sleep(3)
            
            # First check: Look for success indicators on current page
            success_indicators = [
                # 'a[href="/"]',  # Home link
                'svg[aria-label="Home"]',  # Home icon
                'div[role="main"]',  # Main content area
                '[data-testid="mobile-nav-home"]',
                'input[placeholder="Search"]',  # Search box
                'a[href*="/direct/"]',  # Messages link
                'svg[aria-label="New post"]'  # New post button
            ]
            
            for indicator in success_indicators:
                try:
                    WebDriverWait(self.driver, 5).until(
                        EC.presence_of_element_located((By.CSS_SELECTOR, indicator))
                    )
                    logger.info(f"Login successful - found success indicator: {indicator}")
                    return True
                except TimeoutException:
                    continue
            
            # Second check: Navigate to home page and verify
            try:
                logger.info("Navigating to home page to verify login...")
                self.driver.get("https://www.instagram.com/")
                time.sleep(3)
                
                for indicator in success_indicators:
                    try:
                        WebDriverWait(self.driver, 10).until(
                            EC.presence_of_element_located((By.CSS_SELECTOR, indicator))
                        )
                        logger.info("Login successful - verified on home page")
                        return True
                    except TimeoutException:
                        continue
            except Exception as e:
                logger.warning(f"Error navigating to home page: {e}")
            
            # Third check: Check URL patterns
            current_url = self.driver.current_url
            if "instagram.com" in current_url:
                # If we're not on login, challenge, or error pages, assume success
                if not any(keyword in current_url for keyword in ["login", "challenge", "verify", "error", "suspended"]):
                    logger.info("Login appears successful based on URL pattern")
                    return True
            
            # Fourth check: Look for login form (means we're NOT logged in)
            login_form_indicators = [
                'input[name="username"]',
                'input[name="password"]',
                'form[method="post"]'
            ]
            
            login_form_found = False
            for indicator in login_form_indicators:
                try:
                    element = self.driver.find_element(By.CSS_SELECTOR, indicator)
                    if element.is_displayed():
                        login_form_found = True
                        break
                except NoSuchElementException:
                    continue
            
            if login_form_found:
                logger.error("Login verification failed - still on login page")
                return False
            
            # If we get here, we're not sure but probably logged in
            logger.warning("Login verification inconclusive - may need manual verification")
            logger.info("Please check the browser to confirm you're logged in")
            return True
            
        except Exception as e:
            logger.error(f"Error verifying login: {e}")
            return False
    
    def run_setup(self):
        """Run the automated Chrome profile setup"""
        logger.info("Starting Automated Chrome Profile Setup for Instagram")
        logger.info("="*50)
        
        try:
            if not self.setup_chrome_with_custom_profile():
                logger.error("Failed to setup Chrome driver. Exiting...")
                return
            
            # First check if already logged in
            if self.check_if_already_logged_in():
                logger.info("✓ Already logged in to Instagram!")
                logger.info("Profile is ready to use. No login needed.")
                self.update_env_file()
                logger.info("Setup completed successfully!")
                self.cleanup()
                return
                
            if not self.navigate_to_instagram():
                logger.error("Failed to navigate to Instagram. Exiting...")
                return
            
            login_successful = False
            if not self.perform_login(INSTAGRAM_USERNAME, INSTAGRAM_PASSWORD):
                logger.error("Failed to login automatically. Please check your credentials.")
                logger.info("You can still log in manually if needed.")
                logger.info("Please complete the login process manually in the browser...")
                
                # Wait for manual login
                input("Press Enter after you have completed the login process manually...")
                
                # Check if manual login was successful
                if self.verify_login_success():
                    logger.info("✓ Manual login verification successful!")
                    login_successful = True
                else:
                    logger.warning("Could not verify manual login. Please check the browser.")
                    
            else:
                logger.info("✓ Automatic login completed")
                login_successful = True
                
                # Handle email verification if it appears
                if not self.handle_email_verification():
                    logger.warning("Email verification failed or was skipped")
                    # Don't fail the whole process, user might complete manually
                
                # Handle save info prompt
                self.handle_save_info_prompt()
                
                # Final verification
                if self.verify_login_success():
                    logger.info("✓ Login verification successful!")
                else:
                    logger.warning("Could not verify login success automatically")
                    logger.info("Please check the browser to confirm you're logged in")
                    
                    # Ask user to confirm
                    user_confirm = input("Are you successfully logged in to Instagram? (y/n): ").lower().strip()
                    if user_confirm in ['y', 'yes']:
                        logger.info("✓ User confirmed successful login!")
                        login_successful = True
                    else:
                        logger.warning("User indicated login was not successful")
                        login_successful = False
            
            if login_successful:
                logger.info("🎉 Chrome browser setup completed successfully!")
                logger.info("Profile will be saved to: " + CUSTOM_PROFILE_PATH)
                logger.info("")
                logger.info("✓ You can now:")
                logger.info("  1. Run the main application: python3 app.py")
                logger.info("  2. The app will use your saved Instagram session")
                
                # Update .env file with profile path
                self.update_env_file()
                
                # Wait a few seconds to ensure session is saved
                logger.info("Saving session data...")
                time.sleep(5)
                
                logger.info("✓ Setup completed successfully!")
            else:
                logger.error("❌ Setup was not completed successfully")
                logger.info("Please try running the setup again or complete login manually")
            
            logger.info("="*50)
            
        except KeyboardInterrupt:
            logger.info("Setup interrupted by user. Cleaning up...")
        except Exception as e:
            logger.error(f"Unexpected error during setup: {e}")
        finally:
            # Always cleanup at the end
            self.cleanup()
        
    def update_env_file(self):
        """Update the .env file with the custom profile path"""
        try:
            # Read existing .env file
            env_lines = []
            if os.path.exists('.env'):
                with open('.env', 'r') as f:
                    env_lines = f.readlines()
            
            # Check if CHROME_PROFILE_PATH already exists
            profile_path_exists = False
            for i, line in enumerate(env_lines):
                if line.startswith('CHROME_PROFILE_PATH='):
                    env_lines[i] = f'CHROME_PROFILE_PATH={CUSTOM_PROFILE_PATH}\n'
                    profile_path_exists = True
                    break
            
            # Add CHROME_PROFILE_PATH if it doesn't exist
            if not profile_path_exists:
                env_lines.append(f'CHROME_PROFILE_PATH={CUSTOM_PROFILE_PATH}\n')
            
            # Write back to .env file
            with open('.env', 'w') as f:
                f.writelines(env_lines)
            
            logger.info(f"Updated .env file with CHROME_PROFILE_PATH={CUSTOM_PROFILE_PATH}")
            
        except Exception as e:
            logger.error(f"Failed to update .env file: {e}")
            logger.info(f"Please manually add this line to your .env file:")
            logger.info(f"CHROME_PROFILE_PATH={CUSTOM_PROFILE_PATH}")

if __name__ == "__main__":
    setup = ChromeProfileSetup()
    setup.run_setup() 