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
                print(f"verification found")
                self.setup_status.update({
                    'step': 'verification_required',
                    'message': 'Email verification required. Please check your email and enter the code in the frontend. Waiting 120 seconds for input...',
                    'requires_verification': True,
                    'countdown_seconds': 120  # Add countdown field for frontend
                })
                
                # Wait 120 seconds for user to input verification code on frontend
                wait_time = 120
                for i in range(wait_time):
                    time.sleep(1)
                    # Update countdown message
                    print(f"waiting {i} seconds")
                    remaining = wait_time - i
                    self.setup_status.update({
                        'message': f'Email verification required. Please enter the code in the frontend. Waiting {remaining} seconds...',
                        'countdown_seconds': remaining  # Update countdown for frontend
                    })
                    print(f"after update")  
                    # Check if verification was submitted (status would change)
                    if not self.setup_status.get('requires_verification', False):
                        print(f"breaked")
                        break
                
                # If still requires verification after wait, the user didn't submit code
                print("after break")
                if self.setup_status.get('requires_verification', False):
                    print("timeout")
                    self.setup_status.update({
                        'running': False,
                        'error': 'Verification timeout. Please try again and enter the code within 120 seconds.',
                        'step': 'failed',
                        'requires_verification': False,
                        'countdown_seconds': 0  # Reset countdown
                    })
                    # Only cleanup on timeout
                    print("Cleaning up browser on timeout")
                    self.setup_instance.cleanup()
                    return
                
                # If we reach here, verification was submitted via submit_verification_code
                # The _complete_setup() will be called from submit_verification_code method
                # return
            
            # Step 6: Complete setup
            self._complete_setup()
            
        except Exception as e:
            logger.error(f"Setup error: {e}")
            self.setup_status.update({
                'running': False,
                'error': f'Setup failed: {str(e)}',
                'step': 'failed'
            })
            # Cleanup on exception
            if self.setup_instance:
                print("Cleaning up browser on exception")
                self.setup_instance.cleanup()
        finally:
            # Clear credentials from environment (but don't cleanup browser if verification pending)
            if 'INSTAGRAM_USERNAME' in os.environ:
                del os.environ['INSTAGRAM_USERNAME']
            if 'INSTAGRAM_PASSWORD' in os.environ:
                del os.environ['INSTAGRAM_PASSWORD']
            
            # Only cleanup if not waiting for verification and not already completed and not currently processing verification
            if (not self.setup_status.get('requires_verification', False) and 
                not self.setup_status.get('success', False) and 
                self.setup_status.get('step') != 'verification_submit' and
                self.setup_instance):
                print("Cleaning up browser on cleanup")
                self.setup_instance.cleanup()
    
    def _check_email_verification_required(self):
        """Check if email verification is required"""
        try:
            time.sleep(30)
            print(f"Checking for verification input fields")
            # Check for verification input fields
            verification_indicators = [
                'input.x1i10hfl.xggy1nq.xtpw4lu.x1tutvks.x1s3xk63.x1s07b3s.x1a2a7pz.xjbqb8w.x1v8p93f.x1o3jo1z.x16stqrj.xv5lvn5.x1ejq31n.x18oe1m7.x1sy0etr.xstzfhl.x972fbf.x10w94by.x1qhh985.x14e42zd.x9f619.xzsf02u.x1lliihq.x15h3p50.x10emqs4.x1vr9vpq.x1iyjqo2.x1y44fgy.x10d0gm4.x1fhayk4.x16wdlz0.x3cjxhe.xe9ewy2.x11lt19s.xeuugli.xlyipyv.x1hcrkkg.xfvqz1d.x12vv892.x1hu168l.xttzon8.xvr60a6.x1sfh74k.x53uk0m.x185fvkj.x1p97g3g.xmtqnhx.x11ig0mb.x1quw8ve.xx0ingd.xp5op4.xs8nzd4.x1fzehxr.xha3pab',
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
                    WebDriverWait(self.setup_instance.driver, 10).until(
                        EC.presence_of_element_located((By.CSS_SELECTOR, selector))
                    )
                    print(f"Verification input field found: {selector}")
                    return True
                except TimeoutException:
                    continue
            
            return False
            
        except Exception as e:
            logger.warning(f"Error checking verification: {e}")
            return False
    
    def submit_verification_code(self, code):
        """Submit email verification code"""
        print(f"submit verification code")
        print(f"requires verification: {self.setup_status['requires_verification']}")
        if not self.setup_status['requires_verification']:
            print(f"verification not required")
            return {'success': False, 'error': 'Verification not required'}
        
        try:
            self.setup_status.update({
                'step': 'verification_submit',
                'message': 'Submitting verification code...',
            })
            
            from selenium.webdriver.common.by import By
            from selenium.webdriver.support.ui import WebDriverWait
            from selenium.webdriver.support import expected_conditions as EC
            from selenium.common.exceptions import TimeoutException, NoSuchElementException
            
            # Check if driver is still available
            if not self.setup_instance or not hasattr(self.setup_instance, 'driver') or not self.setup_instance.driver:
                print(f"browser session expired")
                self.setup_status.update({
                    'running': False,
                    'error': 'Browser session expired. Please restart the login process.',
                    'step': 'failed'
                })
                return {'success': False, 'error': 'Browser session expired. Please restart the login process.'}
            
            # Find verification input using the two-step approach
            # First find the parent div, then the input inside it
            try:
                # Execute JavaScript to find and fill the verification input
                verification_script = f"""
                // Find the parent div
                const parentDiv = document.querySelector('div.x6s0dn4.x78zum5.x1qughib.xh8yej3');

                if (parentDiv) {{
                    // Then find the input inside it
                    const input = parentDiv.querySelector('input.x1i10hfl.xggy1nq.xtpw4lu.x1tutvks.x1s3xk63.x1s07b3s.x1a2a7pz.xjbqb8w.x1v8p93f.x1o3jo1z.x16stqrj.xv5lvn5.x1ejq31n.x18oe1m7.x1sy0etr.xstzfhl.x972fbf.x10w94by.x1qhh985.x14e42zd.x9f619.xzsf02u.x1lliihq.x15h3p50.x10emqs4.x1vr9vpq.x1iyjqo2.x1y44fgy.x10d0gm4.x1fhayk4.x16wdlz0.x3cjxhe.xe9ewy2.x11lt19s.xeuugli.xlyipyv.x1hcrkkg.xfvqz1d.x12vv892.x1hu168l.xttzon8.xvr60a6.x1sfh74k.x53uk0m.x185fvkj.x1p97g3g.xmtqnhx.x11ig0mb.x1quw8ve.xx0ingd.xp5op4.xs8nzd4.x1fzehxr.xha3pab');

                    if (input) {{
                        // Set the value using native setter to update property properly
                        const nativeInputValueSetter = Object.getOwnPropertyDescriptor(
                            window.HTMLInputElement.prototype,
                            "value"
                        ).set;

                        nativeInputValueSetter.call(input, "{code}");

                        // Trigger events (very important for React/Vue apps)
                        input.dispatchEvent(new Event('input', {{ bubbles: true }}));
                        input.dispatchEvent(new Event('change', {{ bubbles: true }}));
                        
                        return 'success';
                    }} else {{
                        return 'input_not_found';
                    }}
                }} else {{
                    return 'parent_not_found';
                }}
                """
                
                result = self.setup_instance.driver.execute_script(verification_script)
                print(f"Verification script result: {result}")
                
                if result == 'parent_not_found':
                    print(f"could not find verification parent div")
                    self.setup_status.update({
                        'running': False,
                        'error': 'Could not find verification form. Page may have changed.',
                        'step': 'failed'
                    })
                    if self.setup_instance:
                        print(f"clean up here 7")
                        self.setup_instance.cleanup()
                    return {'success': False, 'error': 'Could not find verification form'}
                    
                elif result == 'input_not_found':
                    print(f"could not find verification input field inside parent")
                    self.setup_status.update({
                        'running': False,
                        'error': 'Could not find verification input field. Page may have changed.',
                        'step': 'failed'
                    })
                    if self.setup_instance:
                        print(f"clean up here 8")
                        self.setup_instance.cleanup()
                    return {'success': False, 'error': 'Could not find verification input field'}
                    
                elif result == 'success':
                    print(f"code sent successfully")
                else:
                    print(f"unexpected result: {result}")
                    
            except Exception as js_error:
                print(f"JavaScript execution error: {js_error}")
                self.setup_status.update({
                    'running': False,
                    'error': f'Failed to execute verification script: {str(js_error)}',
                    'step': 'failed'
                })
                if self.setup_instance:
                    print(f"clean up here js_error")
                    self.setup_instance.cleanup()
                return {'success': False, 'error': f'Script execution failed: {str(js_error)}'}
            
            time.sleep(5)
            
            # Find and click continue button using JavaScript
            continue_script = """
                const classSelector = 'div.x1ja2u2z.x78zum5.x2lah0s.x1n2onr6.xl56j7k.x6s0dn4.xozqiw3.x1q0g3np.x972fbf.x10w94by.x1qhh985.x14e42zd.x9f619.xtvsq51.xqdzp0n.x15p4eik.x1ismhnl.x16ie3sq.x1xila8y.x1bumbmr.xc8cyl1';

                const button = document.querySelector(classSelector);
                if (button) {
                    button.click();
                    console.log("✅ Clicked the continue button.");
                    'success'; // Final expression is returned
                } else {
                    console.log("❌ Button not found.");
                    'button_not_found';
                }
            """

            
            try:
                result = self.setup_instance.driver.execute_script(continue_script)
                print(f"Continue button script result: {result}")

                
                # if result != 'success':
                #     print(f"could not find continue button")
                #     self.setup_status.update({
                #         'running': False,
                #         'error': 'Could not find Continue button. Page may have changed.',
                #         'step': 'failed'
                #     })
                #     if self.setup_instance:
                #         print(f"clean up here 6")
                #         self.setup_instance.cleanup()
                #     return {'success': False, 'error': 'Could not find Continue button'}
                
                print(f"continue button clicked")
                
            except Exception as js_error:
                print(f"Continue button JavaScript execution error: {js_error}")
                self.setup_status.update({
                    'running': False,
                    'error': f'Failed to execute continue button script: {str(js_error)}',
                    'step': 'failed'
                })
                if self.setup_instance:
                    print(f"clean up here js_error")
                    self.setup_instance.cleanup()
                return {'success': False, 'error': f'Continue button script execution failed: {str(js_error)}'}
            
            # Wait and check if verification was successful
            time.sleep(15)
            print(f"waiting 15 seconds come on")
            # current_url = self.setup_instance.driver.current_url
            # print(f"current url: {current_url}")
            # if "challenge" in current_url or "verify" or "codeentry" in current_url:
            #     print(f"verification failed")
            #     # Check for error messages
            #     error_selectors = [
            #         '[role="alert"]',
            #         '.error',
            #         '[aria-live="polite"]'
            #     ]
                
            #     for error_selector in error_selectors:
            #         try:
            #             error_element = self.setup_instance.driver.find_element(By.CSS_SELECTOR, error_selector)
            #             if error_element.is_displayed() and error_element.text.strip():
            #                 error_msg = f'Verification failed: {error_element.text}'
            #                 self.setup_status.update({
            #                     'running': False,
            #                     'error': error_msg,
            #                     'step': 'failed'
            #                 })
            #                 if self.setup_instance:
            #                     print(f"clean up here 5")
            #                     self.setup_instance.cleanup()
            #                 return {'success': False, 'error': error_msg}
            #         except NoSuchElementException:
            #             continue
                
            #     # Generic error if no specific error found
            #     error_msg = 'Verification code appears to be incorrect'
            #     self.setup_status.update({
            #         'running': False,
            #         'error': error_msg,
            #         'step': 'failed'
            #     })
            #     if self.setup_instance:
            #         print(f"clean up here 9")
                    
            #         self.setup_instance.cleanup()
            #     return {'success': False, 'error': error_msg}
            
            # Verification successful, complete setup
            print(f"verification successful")
            self.setup_status.update({
                'step': 'verification_submit',
                'message': 'Submitting verification code...',
                'requires_verification': False,  # Clear the flag to stop the waiting loop
                'countdown_seconds': 0  # Reset countdown when verification is submitted
            })
            # self._complete_setup()
            return {'success': True, 'message': 'Verification successful'}
            
        except Exception as e:
            logger.error(f"Verification error: {e}")
            error_msg = f'Verification failed: {str(e)}'
            self.setup_status.update({
                'running': False,
                'error': error_msg,
                'step': 'failed'
            })
            # Cleanup browser on exception
            if self.setup_instance:
                print(f"clean up here 10")
                
                self.setup_instance.cleanup()
            return {'success': False, 'error': str(e)}
    
    def _complete_setup(self):
        """Complete the setup process"""
        try:
            print(f"complete setup")
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
                
                # Cleanup browser after successful setup
                if self.setup_instance:
                    print("Cleaning up browser after successful setup")
                    self.setup_instance.cleanup()
            else:
                self.setup_status.update({
                    'running': False,
                    'error': 'Could not verify login success',
                    'step': 'failed'
                })
                # Cleanup browser on failure
                if self.setup_instance:
                    print("Cleaning up browser on failure")
                    self.setup_instance.cleanup()
            
        except Exception as e:
            logger.error(f"Setup completion error: {e}")
            self.setup_status.update({
                'running': False,
                'error': f'Setup completion failed: {str(e)}',
                'step': 'failed'
            })
            # Cleanup browser on exception
            if self.setup_instance:
                print("Cleaning up browser on exception in complete setup")
                self.setup_instance.cleanup()
    
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