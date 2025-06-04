#!/usr/bin/env python3
"""
VNC Server Setup for Remote Chrome Browser Access
This module sets up a VNC server to allow remote access to Chrome browser
for manual Instagram login when automated login fails.
"""

import os
import sys
import time
import logging
import subprocess
import signal
import psutil
import threading
import ssl
import urllib3
from pathlib import Path
from typing import Optional, Dict, Any

# Import undetected-chromedriver for better Instagram compatibility
try:
    import undetected_chromedriver as uc
    UC_AVAILABLE = True
except ImportError:
    UC_AVAILABLE = False
    logging.warning("undetected_chromedriver not available, falling back to regular Chrome")

# Import rate limit handler
try:
    from rate_limit_handler import handle_instagram_rate_limit, check_if_rate_limited
    RATE_HANDLER_AVAILABLE = True
except ImportError:
    RATE_HANDLER_AVAILABLE = False
    logging.warning("Rate limit handler not available")

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("vnc_setup.log"),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger("vnc_setup")

class VNCServerManager:
    def __init__(self):
        self.vnc_display = ":1"
        self.vnc_port = 5901
        self.vnc_web_port = 6080
        self.vnc_password = "instagram123"  # Default password
        self.vnc_pid = None
        self.websockify_pid = None
        self.chrome_pid = None
        self.chrome_driver = None  # Store undetected-chromedriver instance
        
        # VNC configuration
        self.vnc_dir = Path.home() / ".vnc"
        self.xstartup_file = self.vnc_dir / "xstartup"
        self.passwd_file = self.vnc_dir / "passwd"
        
    def check_system_compatibility(self) -> bool:
        """Check if the system supports VNC"""
        try:
            # Check if we're on Linux
            if os.name != 'posix' or 'linux' not in sys.platform.lower():
                logger.error("VNC setup is only supported on Linux systems")
                return False
                
            # Check if running as root or in container
            if os.geteuid() == 0:
                logger.info("Running as root - VNC setup should work")
                
            return True
        except Exception as e:
            logger.error(f"System compatibility check failed: {e}")
            return False
            
    def install_vnc_dependencies(self) -> bool:
        """Install VNC server and dependencies"""
        try:
            logger.info("Installing VNC dependencies...")
            
            # Update package list
            subprocess.run(['apt-get', 'update'], check=True, capture_output=True)
            
            # Install VNC server and dependencies
            packages = [
                'tightvncserver',
                'xvfb',
                'fluxbox',
                'x11vnc',
                'websockify',
                'xterm',
                'firefox',  # Backup browser
                'fonts-liberation',
                'fonts-dejavu-core'
            ]
            
            cmd = ['apt-get', 'install', '-y'] + packages
            result = subprocess.run(cmd, check=True, capture_output=True, text=True)
            
            logger.info("VNC dependencies installed successfully")
            return True
            
        except subprocess.CalledProcessError as e:
            logger.error(f"Failed to install VNC dependencies: {e}")
            logger.error(f"Error output: {e.stderr}")
            return False
        except Exception as e:
            logger.error(f"Unexpected error installing dependencies: {e}")
            return False
            
    def setup_vnc_server(self) -> bool:
        """Setup and configure VNC server"""
        try:
            logger.info("Setting up VNC server...")
            
            # Create VNC directory
            self.vnc_dir.mkdir(exist_ok=True, mode=0o700)
            
            # Setup VNC password
            self._setup_vnc_password()
            
            # Create xstartup script
            self._create_xstartup_script()
            
            # Kill any existing VNC servers
            self._kill_existing_vnc_servers()
            
            logger.info("VNC server setup completed")
            return True
            
        except Exception as e:
            logger.error(f"Failed to setup VNC server: {e}")
            return False
            
    def _setup_vnc_password(self):
        """Setup VNC password"""
        try:
            # Use vncpasswd to set password
            process = subprocess.Popen(
                ['vncpasswd', str(self.passwd_file)],
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            
            # Send password twice (password and confirmation)
            stdout, stderr = process.communicate(f"{self.vnc_password}\n{self.vnc_password}\nn\n")
            
            if process.returncode == 0:
                logger.info("VNC password set successfully")
            else:
                logger.warning(f"VNC password setup had issues: {stderr}")
                
        except Exception as e:
            logger.error(f"Failed to setup VNC password: {e}")
            
    def _create_xstartup_script(self):
        """Create xstartup script for VNC"""
        xstartup_content = """#!/bin/bash
xrdb $HOME/.Xresources
xsetroot -solid grey
export XKL_XMODMAP_DISABLE=1
export XDG_CURRENT_DESKTOP="GNOME"
export XDG_SESSION_DESKTOP="GNOME"
export XDG_SESSION_TYPE="x11"

# Start window manager
fluxbox &

# Start terminal
xterm -geometry 80x24+10+10 -ls -title "$VNCDESKTOP Desktop" &

# Keep session alive
while true; do
    sleep 3600
done
"""
        
        try:
            with open(self.xstartup_file, 'w') as f:
                f.write(xstartup_content)
            
            # Make executable
            os.chmod(self.xstartup_file, 0o755)
            logger.info("Created xstartup script")
            
        except Exception as e:
            logger.error(f"Failed to create xstartup script: {e}")
            
    def _kill_existing_vnc_servers(self):
        """Kill any existing VNC servers"""
        try:
            # Kill VNC servers
            subprocess.run(['pkill', '-f', 'Xvnc'], capture_output=True)
            subprocess.run(['pkill', '-f', 'tightvncserver'], capture_output=True)
            subprocess.run(['pkill', '-f', 'websockify'], capture_output=True)
            
            # Wait a moment
            time.sleep(2)
            
            logger.info("Killed existing VNC servers")
            
        except Exception as e:
            logger.warning(f"Error killing existing VNC servers: {e}")
            
    def start_vnc_server(self) -> bool:
        """Start VNC server with fallback options"""
        try:
            logger.info(f"Starting VNC server on display {self.vnc_display}...")
            
            # Try multiple VNC server approaches
            vnc_attempts = [
                self._try_tightvnc_with_fontpath,
                self._try_tightvnc_basic,
                self._try_tigervnc,
                self._try_x11vnc
            ]
            
            for i, attempt_func in enumerate(vnc_attempts):
                logger.info(f"Trying VNC method {i+1}/{len(vnc_attempts)}: {attempt_func.__name__}")
                success = attempt_func()
                logger.info(f"Method {attempt_func.__name__} returned: {success}")
                
                if success:
                    logger.info(f"VNC server started successfully on display {self.vnc_display}")
                    
                    # Get VNC process ID
                    self._find_vnc_pid()
                    
                    # Start websockify for web access
                    self._start_websockify()
                    
                    return True
                    
            logger.error("All VNC server startup attempts failed")
            return False
                
        except Exception as e:
            logger.error(f"Error starting VNC server: {e}")
            return False
    
    def _try_tightvnc_with_fontpath(self) -> bool:
        """Try TightVNC with explicit font paths"""
        try:
            logger.info("Attempting TightVNC with font paths...")
            
            # Common font paths to try
            font_paths = [
                "/usr/share/fonts/X11/misc/",
                "/usr/share/fonts/X11/75dpi/",
                "/usr/share/fonts/X11/100dpi/",
                "/usr/share/fonts/truetype/",
                "/usr/share/fonts/TTF/",
                "/usr/share/fonts/OTF/",
                "/usr/share/fonts/dejavu/",
                "/usr/share/fonts/liberation/"
            ]
            
            # Build font path string
            existing_paths = []
            for path in font_paths:
                if os.path.exists(path):
                    existing_paths.append(path)
            
            if existing_paths:
                fontpath = ",".join(existing_paths)
                
                cmd = [
                    'tightvncserver',
                    self.vnc_display,
                    '-geometry', '1280x720',
                    '-depth', '24',
                    '-passwd', str(self.passwd_file),
                    '-fp', fontpath
                ]
                
                result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
                
                if result.returncode == 0:
                    logger.info("TightVNC started successfully with font paths")
                    return True
                else:
                    logger.warning(f"TightVNC with font paths failed: {result.stderr}")
                    
        except Exception as e:
            logger.warning(f"TightVNC with font paths attempt failed: {e}")
            
        return False
    
    def _try_tightvnc_basic(self) -> bool:
        """Try basic TightVNC without font path"""
        try:
            logger.info("Attempting basic TightVNC...")
            
            cmd = [
                'tightvncserver',
                self.vnc_display,
                '-geometry', '1280x720',
                '-depth', '24',
                '-passwd', str(self.passwd_file),
                '-nolisten', 'tcp'
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
            
            if result.returncode == 0:
                logger.info("Basic TightVNC started successfully")
                return True
            else:
                logger.warning(f"Basic TightVNC failed: {result.stderr}")
                
        except Exception as e:
            logger.warning(f"Basic TightVNC attempt failed: {e}")
            
        return False
    
    def _try_tigervnc(self) -> bool:
        """Try TigerVNC as alternative"""
        try:
            logger.info("Attempting TigerVNC...")
            
            # Check if TigerVNC is available
            if subprocess.run(['which', 'vncserver'], capture_output=True).returncode != 0:
                logger.warning("TigerVNC not found")
                return False
            
            # Kill any existing VNC server on this display first
            try:
                subprocess.run(['vncserver', '-kill', self.vnc_display], capture_output=True)
            except:
                pass
            
            cmd = [
                'vncserver',
                self.vnc_display,
                '-geometry', '1280x720',
                '-depth', '24',
                '-localhost', 'no'
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
            
            if result.returncode == 0:
                # Verify the server is actually running
                time.sleep(2)  # Give it time to start
                
                # Check if VNC process is running
                vnc_running = False
                try:
                    ps_result = subprocess.run(['ps', 'aux'], capture_output=True, text=True)
                    if f'Xvnc {self.vnc_display}' in ps_result.stdout or f'Xtigervnc {self.vnc_display}' in ps_result.stdout:
                        vnc_running = True
                        logger.info("TigerVNC server verified running")
                    else:
                        logger.warning("TigerVNC command succeeded but process not found")
                except Exception as e:
                    logger.warning(f"Could not verify TigerVNC process: {e}")
                
                if vnc_running:
                    logger.info("TigerVNC started successfully")
                    return True
                else:
                    logger.warning("TigerVNC failed to start properly")
                    return False
            else:
                logger.warning(f"TigerVNC failed: {result.stderr}")
                return False
                
        except Exception as e:
            logger.warning(f"TigerVNC attempt failed: {e}")
            
        return False
    
    def _try_x11vnc(self) -> bool:
        """Try x11vnc with Xvfb"""
        try:
            logger.info("Attempting x11vnc with Xvfb...")
            
            # Check if x11vnc is available
            if subprocess.run(['which', 'x11vnc'], capture_output=True).returncode != 0:
                logger.warning("x11vnc not found")
                return False
                
            # Start Xvfb first
            display_num = self.vnc_display.replace(':', '')
            xvfb_cmd = [
                'Xvfb',
                self.vnc_display,
                '-screen', '0', '1280x720x24',
                '-ac',
                '+extension', 'GLX',
                '+render',
                '-noreset'
            ]
            
            xvfb_process = subprocess.Popen(xvfb_cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            time.sleep(2)  # Wait for Xvfb to start
            
            # Check if Xvfb started successfully
            if xvfb_process.poll() is not None:
                logger.warning("Xvfb failed to start")
                return False
            
            # Start window manager
            env = os.environ.copy()
            env['DISPLAY'] = self.vnc_display
            
            fluxbox_process = subprocess.Popen(['fluxbox'], env=env, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            time.sleep(1)
            
            # Start x11vnc
            x11vnc_cmd = [
                'x11vnc',
                '-display', self.vnc_display,
                '-rfbport', str(self.vnc_port),
                '-passwd', self.vnc_password,
                '-shared',
                '-forever',
                '-bg'
            ]
            
            result = subprocess.run(x11vnc_cmd, capture_output=True, text=True, timeout=30)
            
            if result.returncode == 0:
                logger.info("x11vnc started successfully")
                return True
            else:
                logger.warning(f"x11vnc failed: {result.stderr}")
                # Clean up Xvfb if x11vnc failed
                xvfb_process.terminate()
                fluxbox_process.terminate()
                
        except Exception as e:
            logger.warning(f"x11vnc attempt failed: {e}")
            
        return False
            
    def _find_vnc_pid(self):
        """Find VNC server process ID"""
        try:
            for process in psutil.process_iter(['pid', 'name', 'cmdline']):
                if 'Xvnc' in process.info['name'] and self.vnc_display in ' '.join(process.info['cmdline']):
                    self.vnc_pid = process.info['pid']
                    logger.info(f"Found VNC server PID: {self.vnc_pid}")
                    break
        except Exception as e:
            logger.warning(f"Could not find VNC PID: {e}")
            
    def _start_websockify(self) -> bool:
        """Start websockify for web-based VNC access"""
        try:
            logger.info(f"Starting websockify on port {self.vnc_web_port}...")
            
            # Start websockify in background
            cmd = [
                'websockify',
                '--web=/usr/share/novnc/',
                f'{self.vnc_web_port}',
                f'localhost:{self.vnc_port}'
            ]
            
            # Try alternative websockify command if first fails
            try:
                process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            except FileNotFoundError:
                # Try without web directory
                cmd = [
                    'websockify',
                    f'{self.vnc_web_port}',
                    f'localhost:{self.vnc_port}'
                ]
                process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            
            self.websockify_pid = process.pid
            logger.info(f"Websockify started with PID: {self.websockify_pid}")
            
            # Give it a moment to start
            time.sleep(2)
            
            # Check if it's still running
            if process.poll() is None:
                logger.info(f"Websockify running successfully on port {self.vnc_web_port}")
                return True
            else:
                logger.error("Websockify failed to start properly")
                return False
                
        except Exception as e:
            logger.error(f"Failed to start websockify: {e}")
            return False
            
    def _clean_chrome_profile(self, profile_path: str):
        """Clean problematic Chrome profile data"""
        try:
            # Files/folders to clean for fresh Instagram session
            cleanup_items = [
                "Local Storage/leveldb",
                "Session Storage",
                "Network",
                "WebRTC Logs",
                "Pepper Data",
                "Service Worker",
                "IndexedDB",
                "Cache",
                "GPUCache",
                "Application Cache",
                "Cookies",
                "Cookies-journal",
                "Web Data",
                "Web Data-journal"
            ]
            
            for item in cleanup_items:
                item_path = os.path.join(profile_path, item)
                if os.path.exists(item_path):
                    if os.path.isfile(item_path):
                        os.remove(item_path)
                    elif os.path.isdir(item_path):
                        import shutil
                        shutil.rmtree(item_path, ignore_errors=True)
                        
            logger.info("Chrome profile cleaned for fresh Instagram session")
            
        except Exception as e:
            logger.warning(f"Failed to clean Chrome profile: {e}")
    
    def _configure_chrome_profile(self, profile_path: str):
        """Configure Chrome profile for better Instagram compatibility"""
        try:
            # Create profile directory
            os.makedirs(profile_path, exist_ok=True)
            
            # Clean any problematic data first
            self._clean_chrome_profile(profile_path)
            
            # Create preferences file for better stealth
            prefs = {
                "profile": {
                    "default_content_setting_values": {
                        "notifications": 2,  # Block notifications
                        "geolocation": 2,    # Block location
                        "media_stream": 2    # Block camera/mic
                    },
                    "managed_default_content_settings": {
                        "images": 1
                    }
                },
                "security": {
                    "ask_for_password": False
                },
                "credentials_enable_service": False,
                "password_manager_enabled": False,
                "autofill": {
                    "enabled": False
                },
                "dns_prefetching": {
                    "enabled": False
                },
                "safebrowsing": {
                    "enabled": False
                },
                "search": {
                    "suggest_enabled": False
                },
                "alternate_error_pages": {
                    "enabled": False
                },
                "hardware": {
                    "audio_capture_enabled": False,
                    "video_capture_enabled": False
                },
                "default_apps_install_state": 2,
                "hide_web_store_icon": True
            }
            
            # Write preferences
            import json
            prefs_file = os.path.join(profile_path, "Preferences")
            with open(prefs_file, 'w') as f:
                json.dump(prefs, f, indent=2)
                
            logger.info("Chrome profile configured for Instagram compatibility")
            
        except Exception as e:
            logger.warning(f"Failed to configure Chrome profile: {e}")
    
    def start_chrome_in_vnc(self, profile_path: str) -> bool:
        """Start Chrome browser inside VNC session using undetected-chromedriver"""
        try:
            logger.info("Starting Chrome browser in VNC session with undetected-chromedriver...")
            
            # Check if we're currently rate limited
            if RATE_HANDLER_AVAILABLE:
                is_limited, last_blocked = check_if_rate_limited()
                if is_limited:
                    logger.warning(f"Currently rate limited since: {last_blocked}")
                    logger.info("Attempting to handle rate limit...")
                    success = handle_instagram_rate_limit(self, profile_path)
                    if not success:
                        logger.error("Failed to handle rate limit, continuing with caution...")
            
            # Set display for Chrome
            env = os.environ.copy()
            env['DISPLAY'] = self.vnc_display
            
            # Create profile directory if it doesn't exist
            os.makedirs(profile_path, exist_ok=True)
            
            if UC_AVAILABLE:
                # Use undetected-chromedriver (same as setup_chrome.py)
                return self._start_undetected_chrome(profile_path, env)
            else:
                # Fallback to regular Chrome
                return self._start_regular_chrome(profile_path, env)
                
        except Exception as e:
            logger.error(f"Failed to start Chrome in VNC: {e}")
            return False
    
    def _start_undetected_chrome(self, profile_path: str, env: dict) -> bool:
        """Start Chrome using undetected-chromedriver with enhanced stealth (same config as setup_chrome.py)"""
        try:
            logger.info("Using undetected-chromedriver for better Instagram compatibility...")
            
            # Clean profile for fresh session
            self._clean_chrome_profile(profile_path)
            
            # Disable SSL warnings (same as setup_chrome.py)
            urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
            ssl._create_default_https_context = ssl._create_unverified_context
            
            # Use exact same options as setup_chrome.py with additional stealth options
            options = uc.ChromeOptions()
            
            # Core stealth options (from setup_chrome.py)
            options.add_argument('--no-sandbox')
            options.add_argument('--disable-dev-shm-usage')
            options.add_argument('--disable-blink-features=AutomationControlled')
            options.add_argument(f"--user-data-dir={profile_path}")
            options.add_argument('--ignore-ssl-errors')
            options.add_argument('--ignore-certificate-errors')
            options.add_argument('--allow-running-insecure-content')
            
            # Additional stealth options for Instagram
            options.add_argument('--disable-web-security')
            options.add_argument('--disable-features=VizDisplayCompositor')
            options.add_argument('--disable-background-timer-throttling')
            options.add_argument('--disable-backgrounding-occluded-windows')
            options.add_argument('--disable-renderer-backgrounding')
            options.add_argument('--disable-field-trial-config')
            options.add_argument('--disable-back-forward-cache')
            options.add_argument('--disable-ipc-flooding-protection')
            options.add_argument('--disable-hang-monitor')
            options.add_argument('--disable-client-side-phishing-detection')
            options.add_argument('--disable-component-update')
            options.add_argument('--disable-default-apps')
            options.add_argument('--disable-domain-reliability')
            options.add_argument('--disable-features=TranslateUI')
            options.add_argument('--disable-sync')
            options.add_argument('--no-first-run')
            options.add_argument('--no-default-browser-check')
            options.add_argument('--no-pings')
            options.add_argument('--password-store=basic')
            options.add_argument('--use-mock-keychain')
            
            # User agent spoofing
            options.add_argument('--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36')
            
            # VNC-specific options
            options.add_argument(f'--display={self.vnc_display}')
            options.add_argument('--window-size=1280,720')
            options.add_argument('--start-maximized')
            
            # Preferences for better stealth
            prefs = {
                "profile.default_content_setting_values": {
                    "notifications": 2,
                    "geolocation": 2,
                    "media_stream": 2
                },
                "profile.managed_default_content_settings": {
                    "images": 1
                },
                "webrtc.ip_handling_policy": "disable_non_proxied_udp",
                "webrtc.multiple_routes_enabled": False,
                "webrtc.nonproxied_udp_enabled": False
            }
            options.add_experimental_option("prefs", prefs)
            
            # Note: excludeSwitches and useAutomationExtension may not be compatible with all versions
            # options.add_experimental_option("excludeSwitches", ["enable-automation"])
            # options.add_experimental_option('useAutomationExtension', False)
            
            # Set environment for undetected-chromedriver
            original_display = os.environ.get('DISPLAY')
            os.environ['DISPLAY'] = self.vnc_display
            
            try:
                # Start undetected Chrome with version detection
                # Try with minimal options first for compatibility
                try:
                    driver = uc.Chrome(options=options, version_main=None)
                except Exception as e:
                    logger.warning(f"Failed with full options, trying minimal setup: {e}")
                    
                    # Create minimal options for better compatibility
                    minimal_options = uc.ChromeOptions()
                    minimal_options.add_argument('--no-sandbox')
                    minimal_options.add_argument('--disable-dev-shm-usage')
                    minimal_options.add_argument(f"--user-data-dir={profile_path}")
                    minimal_options.add_argument(f'--display={self.vnc_display}')
                    minimal_options.add_argument('--window-size=1280,720')
                    
                    # Try with minimal options
                    driver = uc.Chrome(options=minimal_options, version_main=None)
                
                # Wait before navigating to Instagram
                time.sleep(3)
                
                # Navigate to Instagram with error handling
                max_retries = 3
                for attempt in range(max_retries):
                    try:
                        logger.info(f"Attempting to navigate to Instagram (attempt {attempt + 1}/{max_retries})...")
                        driver.get("https://www.instagram.com/accounts/login/")
                        
                        # Wait and check for rate limiting
                        time.sleep(5)
                        
                        # Check if we got blocked
                        page_title = driver.title.lower()
                        page_source = driver.page_source.lower()
                        
                        if "429" in page_source or "too many requests" in page_source or "rate limit" in page_source:
                            logger.warning(f"Instagram rate limiting detected on attempt {attempt + 1}")
                            
                            # Use rate limit handler if available
                            if RATE_HANDLER_AVAILABLE:
                                logger.info("Using rate limit handler to resolve issue...")
                                success = handle_instagram_rate_limit(self, profile_path, attempt + 1)
                                if success:
                                    logger.info("Rate limit handler resolved the issue")
                                    continue
                            
                            if attempt < max_retries - 1:
                                wait_time = (attempt + 1) * 60  # Progressive backoff (minutes)
                                logger.info(f"Waiting {wait_time} seconds before retry...")
                                time.sleep(wait_time)
                                continue
                            else:
                                logger.error("Max retries reached for Instagram access due to rate limiting")
                                logger.info("Try again later or use manual access through VNC")
                                return False
                        
                        # Check for other blocking indicators
                        blocking_indicators = [
                            "something went wrong",
                            "please wait",
                            "try again later", 
                            "blocked",
                            "suspicious activity",
                            "verify your account"
                        ]
                        
                        if any(indicator in page_source for indicator in blocking_indicators):
                            logger.warning(f"Instagram blocking detected: {[ind for ind in blocking_indicators if ind in page_source]}")
                            if attempt < max_retries - 1:
                                time.sleep(30)
                                continue
                        
                        if "instagram" in page_title:
                            logger.info("Successfully navigated to Instagram")
                            break
                        else:
                            logger.warning(f"Unexpected page: {page_title}")
                            if attempt < max_retries - 1:
                                time.sleep(10)
                                continue
                                
                    except Exception as e:
                        logger.warning(f"Navigation attempt {attempt + 1} failed: {e}")
                        if attempt < max_retries - 1:
                            time.sleep(15)
                            continue
                        else:
                            raise e
                
                logger.info("Chrome started successfully with undetected-chromedriver")
                
                # Store the driver process ID
                self.chrome_pid = driver.service.process.pid
                logger.info(f"Chrome PID: {self.chrome_pid}")
                
                # Store the driver instance to keep it alive
                self.chrome_driver = driver
                
                # Start a background thread to keep the driver alive and monitor for issues
                def keep_chrome_alive():
                    try:
                        while True:
                            time.sleep(30)
                            # Check if Chrome is still running
                            if not psutil.pid_exists(self.chrome_pid):
                                logger.warning("Chrome process died")
                                break
                            
                            # Check for Instagram blocking every few minutes
                            try:
                                current_url = driver.current_url
                                if "instagram.com" not in current_url and "429" not in driver.page_source:
                                    logger.info(f"Chrome still active at: {current_url}")
                            except Exception:
                                pass  # Ignore errors during monitoring
                                
                    except Exception as e:
                        logger.warning(f"Chrome keepalive thread error: {e}")
                
                chrome_thread = threading.Thread(target=keep_chrome_alive, daemon=True)
                chrome_thread.start()
                
                return True
                
            finally:
                # Restore original display
                if original_display:
                    os.environ['DISPLAY'] = original_display
                else:
                    os.environ.pop('DISPLAY', None)
                    
        except Exception as e:
            logger.error(f"Failed to start undetected Chrome: {e}")
            return False
    
    def _start_regular_chrome(self, profile_path: str, env: dict) -> bool:
        """Fallback to regular Chrome if undetected-chromedriver is not available"""
        try:
            logger.info("Using regular Chrome as fallback...")
            
            # Configure Chrome profile for better compatibility
            self._configure_chrome_profile(profile_path)
            
            # Instagram-friendly Chrome command with minimal flags
            chrome_cmd = [
                'google-chrome',
                '--no-sandbox',  # Required for containers
                '--disable-dev-shm-usage',  # Required for limited memory
                '--disable-gpu',  # Better for VNC
                '--no-first-run',
                '--no-default-browser-check',
                '--disable-background-timer-throttling',
                '--disable-backgrounding-occluded-windows',
                '--disable-features=TranslateUI',
                '--disable-extensions-except=',
                '--disable-default-apps',
                '--window-size=1280,720',
                '--start-maximized',
                f'--user-data-dir={profile_path}',
                'https://www.instagram.com/accounts/login/'
            ]
            
            # Try Chrome, fallback to Chromium
            try:
                process = subprocess.Popen(chrome_cmd, env=env, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            except FileNotFoundError:
                # Try chromium-browser
                chrome_cmd[0] = 'chromium-browser'
                try:
                    process = subprocess.Popen(chrome_cmd, env=env, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                except FileNotFoundError:
                    # Try chromium
                    chrome_cmd[0] = 'chromium'
                    process = subprocess.Popen(chrome_cmd, env=env, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            
            self.chrome_pid = process.pid
            logger.info(f"Chrome started with PID: {self.chrome_pid}")
            
            # Give Chrome time to start
            time.sleep(5)  # Increased wait time
            
            # Check if Chrome is still running
            if process.poll() is None:
                logger.info("Chrome started successfully in VNC session")
                return True
            else:
                logger.error("Chrome failed to start properly")
                return False
                
        except Exception as e:
            logger.error(f"Failed to start regular Chrome: {e}")
            return False
            
    def get_access_info(self) -> Dict[str, Any]:
        """Get VNC access information"""
        return {
            'vnc_display': self.vnc_display,
            'vnc_port': self.vnc_port,
            'vnc_web_port': self.vnc_web_port,
            'vnc_password': self.vnc_password,
            'web_url': f'http://localhost:{self.vnc_web_port}/vnc.html',
            'status': self.get_status()
        }
        
    def get_status(self) -> Dict[str, Any]:
        """Get current VNC server status"""
        status = {
            'vnc_running': False,
            'websockify_running': False,
            'chrome_running': False,
            'vnc_pid': self.vnc_pid,
            'websockify_pid': self.websockify_pid,
            'chrome_pid': self.chrome_pid
        }
        
        try:
            # Check VNC server
            if self.vnc_pid and psutil.pid_exists(self.vnc_pid):
                status['vnc_running'] = True
                
            # Check websockify
            if self.websockify_pid and psutil.pid_exists(self.websockify_pid):
                status['websockify_running'] = True
                
            # Check Chrome
            if self.chrome_pid and psutil.pid_exists(self.chrome_pid):
                status['chrome_running'] = True
                
        except Exception as e:
            logger.warning(f"Error checking status: {e}")
            
        return status
        
    def stop_vnc_server(self):
        """Stop VNC server and related processes"""
        try:
            logger.info("Stopping VNC server...")
            
            # Stop Chrome driver first
            if self.chrome_driver:
                try:
                    self.chrome_driver.quit()
                    logger.info("Chrome driver closed")
                except Exception as e:
                    logger.warning(f"Error closing Chrome driver: {e}")
                self.chrome_driver = None
            
            # Stop Chrome process
            if self.chrome_pid:
                try:
                    os.kill(self.chrome_pid, signal.SIGTERM)
                    logger.info("Chrome process terminated")
                except ProcessLookupError:
                    pass
                    
            # Stop websockify
            if self.websockify_pid:
                try:
                    os.kill(self.websockify_pid, signal.SIGTERM)
                    logger.info("Websockify process terminated")
                except ProcessLookupError:
                    pass
                    
            # Stop VNC server
            subprocess.run(['tightvncserver', '-kill', self.vnc_display], capture_output=True)
            subprocess.run(['vncserver', '-kill', self.vnc_display], capture_output=True)
            logger.info("VNC server stopped")
            
            # Reset PIDs
            self.vnc_pid = None
            self.websockify_pid = None
            self.chrome_pid = None
            
        except Exception as e:
            logger.error(f"Error stopping VNC server: {e}")
            
    def setup_and_start(self, profile_path: str) -> Dict[str, Any]:
        """Complete VNC setup and start process"""
        try:
            logger.info("Starting complete VNC setup process...")
            
            # Check system compatibility
            if not self.check_system_compatibility():
                return {
                    'success': False,
                    'error': 'System not compatible with VNC setup'
                }
                
            # Install dependencies
            if not self.install_vnc_dependencies():
                return {
                    'success': False,
                    'error': 'Failed to install VNC dependencies'
                }
                
            # Setup VNC server
            if not self.setup_vnc_server():
                return {
                    'success': False,
                    'error': 'Failed to setup VNC server'
                }
                
            # Start VNC server
            if not self.start_vnc_server():
                return {
                    'success': False,
                    'error': 'Failed to start VNC server'
                }
                
            # Start Chrome in VNC
            if not self.start_chrome_in_vnc(profile_path):
                return {
                    'success': False,
                    'error': 'Failed to start Chrome in VNC session'
                }
                
            return {
                'success': True,
                'access_info': self.get_access_info(),
                'message': 'VNC server started successfully'
            }
            
        except Exception as e:
            logger.error(f"VNC setup failed: {e}")
            return {
                'success': False,
                'error': f'VNC setup failed: {str(e)}'
            }

    def restart_chrome_fresh(self, profile_path: str) -> bool:
        """Restart Chrome with completely fresh session"""
        try:
            logger.info("Restarting Chrome with fresh session...")
            
            # Stop current Chrome driver if running
            if self.chrome_driver:
                try:
                    self.chrome_driver.quit()
                    logger.info("Chrome driver closed")
                except Exception as e:
                    logger.warning(f"Error closing Chrome driver: {e}")
                self.chrome_driver = None
            
            # Stop current Chrome process if running
            if self.chrome_pid:
                try:
                    os.kill(self.chrome_pid, signal.SIGTERM)
                    time.sleep(2)
                except ProcessLookupError:
                    pass
                self.chrome_pid = None
            
            # Force clean the profile
            self._clean_chrome_profile(profile_path)
            
            # Start Chrome again
            return self.start_chrome_in_vnc(profile_path)
            
        except Exception as e:
            logger.error(f"Failed to restart Chrome: {e}")
            return False

# Global VNC manager instance
vnc_manager = VNCServerManager()

def start_vnc_chrome_session(profile_path: str) -> Dict[str, Any]:
    """Start VNC session with Chrome for manual login"""
    return vnc_manager.setup_and_start(profile_path)
    
def get_vnc_status() -> Dict[str, Any]:
    """Get current VNC status"""
    return vnc_manager.get_status()
    
def get_vnc_access_info() -> Dict[str, Any]:
    """Get VNC access information"""
    return vnc_manager.get_access_info()
    
def stop_vnc_session():
    """Stop VNC session"""
    vnc_manager.stop_vnc_server()

def restart_chrome_fresh_session(profile_path: str) -> bool:
    """Restart Chrome with fresh session - callable from web interface"""
    return vnc_manager.restart_chrome_fresh(profile_path)

if __name__ == "__main__":
    # Test VNC setup
    profile_path = os.path.join(os.getcwd(), "chrome_profile_instagram")
    result = start_vnc_chrome_session(profile_path)
    print(f"VNC setup result: {result}") 