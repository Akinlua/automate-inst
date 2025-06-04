#!/usr/bin/env python3
"""
Setup Integration Module
Provides web interface integration for Instagram Chrome profile setup
"""

import os
import time
import logging
import threading
from pathlib import Path
from dotenv import load_dotenv, set_key
from setup_chrome import ChromeProfileSetup

# Setup logging
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

class WebSetupIntegration:
    def __init__(self):
        self.setup_instance = None
        self.setup_thread = None
        self.setup_status = {
            'running': False,
            'step': '',
            'message': '',
            'success': False,
            'error': None,
            'requires_verification': False,
            'chrome_profile_path': None
        }
        
    def start_setup(self, username, password):
        """Start the Chrome setup process with given credentials"""
        if self.setup_status['running']:
            return {'success': False, 'error': 'Setup already in progress'}
        
        # Temporarily set credentials (not saved to file)
        self.username = username
        self.password = password
        # os.environ['INSTAGRAM_USERNAME'] = username
        # os.environ['INSTAGRAM_PASSWORD'] = password
        
        # Reset status
        self.setup_status = {
            'running': True,
            'step': 'starting',
            'message': 'Initializing Chrome setup...',
            'success': False,
            'error': None,
            'requires_verification': False,
            'chrome_profile_path': None
        }
        
        # Start setup in background thread
        self.setup_thread = threading.Thread(target=self._run_setup_thread)
        self.setup_thread.daemon = True
        self.setup_thread.start()
        
        return {'success': True, 'message': 'Setup started'}
    
    def _run_setup_thread(self):
        """Run the setup process in a background thread"""
        try:
            self.setup_instance = ChromeProfileSetup()
            
            # Step 1: Setup Chrome driver
            self.setup_status.update({
                'step': 'chrome_setup',
                'message': 'Setting up Chrome driver...'
            })
            
            if not self.setup_instance.setup_chrome_with_custom_profile():
                self.setup_status.update({
                    'running': False,
                    'error': 'Failed to setup Chrome driver',
                    'step': 'failed'
                })
                return
            
            # Step 2: Check if already logged in
            self.setup_status.update({
                'step': 'login_check',
                'message': 'Checking if already logged in...'
            })
            
            if self.setup_instance.check_if_already_logged_in():
                self.setup_status.update({
                    'step': 'completed',
                    'message': 'Already logged in to Instagram!',
                    'success': True,
                    'running': False,
                    'chrome_profile_path': self.setup_instance.CUSTOM_PROFILE_PATH
                })
                self._save_profile_path()
                return
            
            # Step 3: Navigate to Instagram
            self.setup_status.update({
                'step': 'navigation',
                'message': 'Navigating to Instagram...'
            })
            
            if not self.setup_instance.navigate_to_instagram():
                self.setup_status.update({
                    'running': False,
                    'error': 'Failed to navigate to Instagram',
                    'step': 'failed'
                })
                return
            
            # Step 4: Perform login
            self.setup_status.update({
                'step': 'login',
                'message': 'Attempting to log in...'
            })
            
            if not self.setup_instance.perform_login(self.username, self.password):
                self.setup_status.update({
                    'running': False,
                    'error': 'Failed to log in. Please check your credentials.',
                    'step': 'failed'
                })
                return
            
            # Step 5: Check for email verification
            self.setup_status.update({
                'step': 'verification_check',
                'message': 'Checking for email verification...'
            })
            
            # Check if verification is required
            if self._check_email_verification_required():
                self.setup_status.update({
                    'step': 'verification_required',
                    'message': 'Email verification required. Please check your email.',
                    'requires_verification': True
                })
                return
            
            # Step 6: Complete setup
            self._complete_setup()
            
        except Exception as e:
            logger.error(f"Setup error: {e}")
            self.setup_status.update({
                'running': False,
                'error': f'Setup failed: {str(e)}',
                'step': 'failed'
            })
        finally:
            # Clear credentials from environment
            # clean up driver quite
            self.setup_instance.cleanup()
            if 'INSTAGRAM_USERNAME' in os.environ:
                del os.environ['INSTAGRAM_USERNAME']
            if 'INSTAGRAM_PASSWORD' in os.environ:
                del os.environ['INSTAGRAM_PASSWORD']
    
    def _check_email_verification_required(self):
        """Check if email verification is required"""
        try:
            # Check for verification input fields
            verification_indicators = [
                'input.x1i10hfl.xggy1nq.xtpw4lu.x1tutvks.x1s3xk63.x1s07b3s.x1a2a7pz.xjbqb8w.x1v8p93f.xogb00i.x16stqrj.x1ftr3km.x1ejq31n.xd10rxx.x1sy0etr.x17r0tee.x972fbf.xcfux6l.x1qhh985.xm0m39n.x9f619.xzsf02u.x1lliihq.x15h3p50.x10emqs4.x1vr9vpq.x1iyjqo2.x1y44fgy.x10d0gm4.x1fhayk4.x16wdlz0.x3cjxhe.x8182xy.xwrv7xz.xeuugli.xlyipyv.x1hcrkkg.xfvqz1d.x12vv892.x163jz68.xpp3fsf.xvr60a6.x1sfh74k.x53uk0m.x185fvkj.x1p97g3g.xmtqnhx.x11ig0mb.x1quw8ve.xx0ingd.xp5op4.xs8nzd4.x1fzehxr.xha3pab',
                'input[placeholder*="Code"]',
                'input[aria-label*="Code"]',
                'input[name="verificationCode"]'
            ]
            
            from selenium.webdriver.common.by import By
            from selenium.webdriver.support.ui import WebDriverWait
            from selenium.webdriver.support import expected_conditions as EC
            from selenium.common.exceptions import TimeoutException
            
            for selector in verification_indicators:
                try:
                    WebDriverWait(self.setup_instance.driver, 3).until(
                        EC.presence_of_element_located((By.CSS_SELECTOR, selector))
                    )
                    return True
                except TimeoutException:
                    continue
            
            return False
            
        except Exception as e:
            logger.warning(f"Error checking verification: {e}")
            return False
    
    def submit_verification_code(self, code):
        """Submit email verification code"""
        if not self.setup_status['requires_verification']:
            return {'success': False, 'error': 'Verification not required'}
        
        try:
            self.setup_status.update({
                'step': 'verification_submit',
                'message': 'Submitting verification code...'
            })
            
            from selenium.webdriver.common.by import By
            from selenium.webdriver.support.ui import WebDriverWait
            from selenium.webdriver.support import expected_conditions as EC
            from selenium.common.exceptions import TimeoutException, NoSuchElementException
            
            # Find verification input
            verification_selectors = [
                'input.x1i10hfl.xggy1nq.xtpw4lu.x1tutvks.x1s3xk63.x1s07b3s.x1a2a7pz.xjbqb8w.x1v8p93f.xogb00i.x16stqrj.x1ftr3km.x1ejq31n.xd10rxx.x1sy0etr.x17r0tee.x972fbf.xcfux6l.x1qhh985.xm0m39n.x9f619.xzsf02u.x1lliihq.x15h3p50.x10emqs4.x1vr9vpq.x1iyjqo2.x1y44fgy.x10d0gm4.x1fhayk4.x16wdlz0.x3cjxhe.x8182xy.xwrv7xz.xeuugli.xlyipyv.x1hcrkkg.xfvqz1d.x12vv892.x163jz68.xpp3fsf.xvr60a6.x1sfh74k.x53uk0m.x185fvkj.x1p97g3g.xmtqnhx.x11ig0mb.x1quw8ve.xx0ingd.xp5op4.xs8nzd4.x1fzehxr.xha3pab',
                'input[placeholder*="Code"]',
                'input[aria-label*="Code"]',
                'input[name="verificationCode"]'
            ]
            
            verification_input = None
            for selector in verification_selectors:
                try:
                    verification_input = WebDriverWait(self.setup_instance.driver, 5).until(
                        EC.presence_of_element_located((By.CSS_SELECTOR, selector))
                    )
                    break
                except TimeoutException:
                    continue
            
            if not verification_input:
                return {'success': False, 'error': 'Could not find verification input field'}
            
            # Clear and enter code
            verification_input.clear()
            verification_input.send_keys(code)
            
            # Find and click continue button
            continue_selectors = [
                'div.x1ja2u2z.x78zum5.x2lah0s.x1n2onr6.xl56j7k.x6s0dn4.xozqiw3.x1q0g3np.x972fbf.xcfux6l.x1qhh985.xm0m39n.x9f619.xtvsq51.xqdzp0n.x15p4eik.x1ismhnl.x16ie3sq.x1xila8y.x1xarc30.xrwyoh0',
                'div[type="submit"]',
                'div[role="button"]'
            ]
            
            continue_button = None
            for selector in continue_selectors:
                try:
                    continue_button = self.setup_instance.driver.find_element(By.CSS_SELECTOR, selector)
                    if continue_button.is_enabled():
                        break
                except NoSuchElementException:
                    continue
            
            if not continue_button:
                return {'success': False, 'error': 'Could not find Continue button'}
            
            continue_button.click()
            
            # Wait and check if verification was successful
            time.sleep(5)
            
            current_url = self.setup_instance.driver.current_url
            if "challenge" in current_url or "verify" in current_url:
                # Check for error messages
                error_selectors = [
                    '[role="alert"]',
                    '.error',
                    '[aria-live="polite"]'
                ]
                
                for error_selector in error_selectors:
                    try:
                        error_element = self.setup_instance.driver.find_element(By.CSS_SELECTOR, error_selector)
                        if error_element.is_displayed() and error_element.text.strip():
                            return {'success': False, 'error': f'Verification failed: {error_element.text}'}
                    except NoSuchElementException:
                        continue
                
                return {'success': False, 'error': 'Verification code appears to be incorrect'}
            
            # Verification successful, complete setup
            self._complete_setup()
            return {'success': True, 'message': 'Verification successful'}
            
        except Exception as e:
            logger.error(f"Verification error: {e}")
            self.setup_status.update({
                'running': False,
                'error': f'Verification failed: {str(e)}',
                'step': 'failed'
            })
            return {'success': False, 'error': str(e)}
    
    def _complete_setup(self):
        """Complete the setup process"""
        try:
            # Handle save info prompt
            self.setup_status.update({
                'step': 'save_info',
                'message': 'Handling save info prompt...'
            })
            
            self.setup_instance.handle_save_info_prompt()
            
            # Verify login success
            self.setup_status.update({
                'step': 'verification',
                'message': 'Verifying login success...'
            })
            
            if self.setup_instance.verify_login_success():
                self.setup_status.update({
                    'step': 'completed',
                    'message': 'Setup completed successfully!',
                    'success': True,
                    'running': False,
                    'requires_verification': False,
                    'chrome_profile_path': os.path.join(os.getcwd(), "chrome_profile_instagram")
                })
                self._save_profile_path()
            else:
                self.setup_status.update({
                    'running': False,
                    'error': 'Could not verify login success',
                    'step': 'failed'
                })
            
        except Exception as e:
            logger.error(f"Setup completion error: {e}")
            self.setup_status.update({
                'running': False,
                'error': f'Setup completion failed: {str(e)}',
                'step': 'failed'
            })
    
    def _save_profile_path(self):
        """Save the Chrome profile path to .env file"""
        try:
            profile_path = os.path.join(os.getcwd(), "chrome_profile_instagram")
            set_key('.env', 'CHROME_PROFILE_PATH', profile_path)
            logger.info(f"Saved Chrome profile path to .env: {profile_path}")
        except Exception as e:
            logger.error(f"Failed to save profile path: {e}")
    
    def get_status(self):
        """Get current setup status"""
        return self.setup_status.copy()
    
    def logout(self):
        """Logout by deleting Chrome profile"""
        try:
            profile_path = os.getenv('CHROME_PROFILE_PATH')
            if profile_path and os.path.exists(profile_path):
                import shutil
                shutil.rmtree(profile_path)
                logger.info(f"Deleted Chrome profile: {profile_path}")
            
            # Remove from .env file
            env_file = '.env'
            if os.path.exists(env_file):
                with open(env_file, 'r') as f:
                    lines = f.readlines()
                
                with open(env_file, 'w') as f:
                    for line in lines:
                        if not line.startswith('CHROME_PROFILE_PATH='):
                            f.write(line)
            
            return {'success': True, 'message': 'Logged out successfully'}
            
        except Exception as e:
            logger.error(f"Logout error: {e}")
            return {'success': False, 'error': str(e)}
    
    def is_logged_in(self):
        """Check if user is logged in (Chrome profile exists)"""
        profile_path = os.getenv('CHROME_PROFILE_PATH')
        return profile_path and os.path.exists(profile_path)

# Global instance
web_setup = WebSetupIntegration() 