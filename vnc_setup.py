#!/usr/bin/env python3
"""
VNC Server Setup for Remote Chrome Browser Access
This module sets up a VNC server to allow remote access to Chrome browser
for manual Instagram login with anti-detection measures and proxy support.
"""

import os
import sys
import time
import logging
import subprocess
import signal
import psutil
import threading
import shutil
from pathlib import Path
from typing import Optional, Dict, Any
import json

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

PROXY_SERVER = "http://ng.decodo.com:42032"

class VNCServerManager:
    def __init__(self, proxy_server: Optional[str] = None):
        self.vnc_display = ":1"
        self.vnc_port = 5901
        self.vnc_web_port = 6080
        self.vnc_password = "instagram123"  # Default password
        self.vnc_pid = None
        self.websockify_pid = None
        self.chrome_pid = None
        self.xvfb_pid = None
        
        # Proxy configuration
        self.proxy_server = proxy_server
        
        # VNC configuration
        self.vnc_dir = Path.home() / ".vnc"
        self.xstartup_file = self.vnc_dir / "xstartup"
        self.passwd_file = self.vnc_dir / "passwd"
        
    def set_proxy(self, proxy_server: str):
        """Set proxy server for Chrome"""
        self.proxy_server = proxy_server
        logger.info(f"Proxy server set to: {proxy_server}")
        
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
        """Install VNC server and premium desktop environment"""
        try:
            logger.info("Installing VNC dependencies and desktop environment...")
            
            # Update package list
            subprocess.run(['apt-get', 'update'], check=True, capture_output=True)
            
            # Install comprehensive desktop environment and VNC
            packages = [
                # VNC servers
                'tigervnc-standalone-server',
                'tigervnc-common',
                
                # Desktop environment - XFCE (lightweight but full-featured)
                'xfce4',
                'xfce4-goodies',
                'xfce4-terminal',
                
                # Essential X11 components
                'xserver-xorg-core',
                'xfonts-base',
                'xfonts-75dpi',
                'xfonts-100dpi',
                'fonts-liberation',
                'fonts-dejavu-core',
                'fonts-noto',
                
                # Web access
                'websockify',
                'python3-websockify',
                
                # Audio support
                'pulseaudio',
                'pavucontrol',
                
                # Additional tools
                'dbus-x11',
                'at-spi2-core',
                'firefox',  # Standard Firefox instead of firefox-esr
                'thunar',
                'curl',
                'wget',
                
                # Chrome/Chromium requirements
                'libnss3',
                'libatk-bridge2.0-0',
                'libdrm2',
                'libxcomposite1',
                'libxdamage1',
                'libxrandr2',
                'libgbm1',
                'libxss1',
                'libasound2-dev'  # Development package for audio
            ]
            
            # Install packages in batches to avoid issues
            batch_size = 10
            for i in range(0, len(packages), batch_size):
                batch = packages[i:i + batch_size]
                cmd = ['apt-get', 'install', '-y'] + batch
                try:
                    result = subprocess.run(cmd, check=True, capture_output=True, text=True)
                    logger.info(f"Successfully installed batch: {', '.join(batch)}")
                except subprocess.CalledProcessError as e:
                    logger.warning(f"Some packages in batch failed: {e.stderr}")
                    # Try installing packages one by one
                    for package in batch:
                        try:
                            subprocess.run(['apt-get', 'install', '-y', package], check=True, capture_output=True)
                            logger.info(f"Successfully installed: {package}")
                        except subprocess.CalledProcessError:
                            logger.warning(f"Failed to install: {package} - continuing anyway")
            
            # Install noVNC separately
            self._install_novnc()
            
            logger.info("VNC dependencies and desktop environment installed successfully")
            return True
            
        except subprocess.CalledProcessError as e:
            logger.error(f"Failed to install VNC dependencies: {e}")
            logger.error(f"Error output: {e.stderr}")
            return False
        except Exception as e:
            logger.error(f"Unexpected error installing dependencies: {e}")
            return False
    
    def _install_novnc(self):
        """Install noVNC for web-based VNC access"""
        try:
            logger.info("Installing noVNC...")
            
            # Create noVNC directory
            novnc_dir = Path("/usr/share/novnc")
            novnc_dir.mkdir(parents=True, exist_ok=True)
            
            # Download and install noVNC if not present
            if not (novnc_dir / "vnc.html").exists():
                import tempfile
                with tempfile.TemporaryDirectory() as temp_dir:
                    temp_path = Path(temp_dir)
                    
                    # Download noVNC
                    subprocess.run([
                        'wget', '-q', 
                        'https://github.com/novnc/noVNC/archive/refs/tags/v1.4.0.tar.gz'
                    ], cwd=temp_path, check=True)
                    
                    # Extract
                    subprocess.run([
                        'tar', '-xzf', 'v1.4.0.tar.gz'
                    ], cwd=temp_path, check=True)
                    
                    # Copy to destination
                    subprocess.run([
                        'cp', '-r', str(temp_path / "noVNC-1.4.0" / "*"), str(novnc_dir)
                    ], shell=True, check=True)
                    
                logger.info("noVNC installed successfully")
            else:
                logger.info("noVNC already installed")
                
        except Exception as e:
            logger.warning(f"Failed to install noVNC: {e}")
            
    def setup_vnc_server(self) -> bool:
        """Setup and configure VNC server with proper desktop"""
        try:
            logger.info("Setting up VNC server with XFCE desktop...")
            
            # Create VNC directory
            self.vnc_dir.mkdir(exist_ok=True, mode=0o700)
            
            # Setup VNC password
            self._setup_vnc_password()
            
            # Create xstartup script for XFCE
            self._create_xfce_xstartup_script()
            
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
            
    def _create_xfce_xstartup_script(self):
        """Create xstartup script for XFCE desktop"""
        xstartup_content = """#!/bin/bash

# Set environment variables
export XKL_XMODMAP_DISABLE=1
export XDG_CURRENT_DESKTOP="XFCE"
export XDG_SESSION_DESKTOP="xfce"
export XDG_SESSION_TYPE="x11"
export DESKTOP_SESSION="xfce"

# Load X resources
[ -r $HOME/.Xresources ] && xrdb $HOME/.Xresources

# Set background
xsetroot -solid grey

# Start D-Bus
if [ -z "$DBUS_SESSION_BUS_ADDRESS" ]; then
    eval $(dbus-launch --sh-syntax --exit-with-session)
fi

# Start PulseAudio
pulseaudio --start --exit-idle-time=-1 &

# Start XFCE desktop environment
startxfce4 &

# Keep VNC session alive
while true; do
    sleep 3600
done
"""
        
        try:
            with open(self.xstartup_file, 'w') as f:
                f.write(xstartup_content)
            
            # Make executable
            os.chmod(self.xstartup_file, 0o755)
            logger.info("Created XFCE xstartup script")
            
        except Exception as e:
            logger.error(f"Failed to create xstartup script: {e}")
            
    def _kill_existing_vnc_servers(self):
        """Kill any existing VNC servers"""
        try:
            # Kill VNC servers
            subprocess.run(['pkill', '-f', 'Xvnc'], capture_output=True)
            subprocess.run(['pkill', '-f', 'Xtigervnc'], capture_output=True)
            subprocess.run(['pkill', '-f', 'vncserver'], capture_output=True)
            subprocess.run(['pkill', '-f', 'websockify'], capture_output=True)
            subprocess.run(['pkill', '-f', 'Xvfb'], capture_output=True)
            
            # Wait a moment
            time.sleep(3)
            
            logger.info("Killed existing VNC servers")
            
        except Exception as e:
            logger.warning(f"Error killing existing VNC servers: {e}")
            
    def start_vnc_server(self) -> bool:
        """Start TigerVNC server with XFCE desktop"""
        try:
            logger.info(f"Starting TigerVNC server on display {self.vnc_display}...")
            
            # Kill any existing server on this display
            subprocess.run(['vncserver', '-kill', self.vnc_display], capture_output=True)
            time.sleep(2)
            
            # Start TigerVNC server
            cmd = [
                'vncserver',
                self.vnc_display,
                '-geometry', '1920x1080',
                '-depth', '24',
                '-localhost', 'no',
                '-SecurityTypes', 'VncAuth'
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
            
            if result.returncode == 0:
                logger.info("TigerVNC server started successfully")
                
                # Wait for server to start
                time.sleep(5)
                
                # Verify the server is running
                ps_result = subprocess.run(['ps', 'aux'], capture_output=True, text=True)
                if f'Xtigervnc {self.vnc_display}' in ps_result.stdout or f'Xvnc {self.vnc_display}' in ps_result.stdout:
                    self._find_vnc_pid()
                    self._start_websockify()
                    return True
                else:
                    logger.error("VNC server failed to start properly")
                    return False
            else:
                logger.error(f"Failed to start VNC server: {result.stderr}")
                return False
                
        except Exception as e:
            logger.error(f"Error starting VNC server: {e}")
            return False
            
    def _find_vnc_pid(self):
        """Find VNC server process ID"""
        try:
            for process in psutil.process_iter(['pid', 'name', 'cmdline']):
                if ('Xvnc' in process.info['name'] or 'Xtigervnc' in process.info['name']) and self.vnc_display in ' '.join(process.info['cmdline']):
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
            novnc_path = "/usr/share/novnc/"
            if Path(novnc_path).exists():
                cmd = [
                    'websockify',
                    '--web', novnc_path,
                    f'{self.vnc_web_port}',
                    f'localhost:{self.vnc_port}'
                ]
            else:
                # Fallback without web directory
                cmd = [
                    'websockify',
                    f'{self.vnc_web_port}',
                    f'localhost:{self.vnc_port}'
                ]
            
            process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            self.websockify_pid = process.pid
            logger.info(f"Websockify started with PID: {self.websockify_pid}")
            
            time.sleep(2)
            
            if process.poll() is None:
                logger.info(f"Websockify running successfully on port {self.vnc_web_port}")
                return True
            else:
                logger.error("Websockify failed to start properly")
                return False
                
        except Exception as e:
            logger.error(f"Failed to start websockify: {e}")
            return False

    def _clean_chrome_profile_completely(self, profile_path: str):
        """Completely remove and recreate Chrome profile directory"""
        try:
            # If profile directory exists, remove it completely
            if os.path.exists(profile_path):
                logger.info(f"Removing existing Chrome profile: {profile_path}")
                shutil.rmtree(profile_path, ignore_errors=True)
                time.sleep(1)  # Give filesystem time to complete
            
            # Create fresh profile directory
            os.makedirs(profile_path, exist_ok=True)
            logger.info(f"Created fresh Chrome profile directory: {profile_path}")
            
        except Exception as e:
            logger.error(f"Failed to clean Chrome profile: {e}")

    def _create_anti_detection_chrome_profile(self, profile_path: str):
        """Create Chrome profile with anti-detection measures"""
        try:
            # Ensure profile directory exists
            os.makedirs(profile_path, exist_ok=True)
            
            # Create realistic Chrome preferences for stealth
            prefs = {
                "profile": {
                    "default_content_setting_values": {
                        "notifications": 1,  # Allow notifications (more realistic)
                        "geolocation": 1,    # Allow location (more realistic)
                        "media_stream": 1    # Allow camera/mic (more realistic)
                    },
                    "content_settings": {
                        "exceptions": {
                            "notifications": {
                                "https://www.instagram.com,*": {
                                    "setting": 1
                                }
                            }
                        }
                    }
                },
                "extensions": {
                    "ui": {
                        "developer_mode": False
                    }
                },
                "security": {
                    "ask_for_password": True
                },
                "credentials_enable_service": True,
                "password_manager_enabled": True,
                "autofill": {
                    "enabled": True,
                    "profile_enabled": True
                },
                "dns_prefetching": {
                    "enabled": True
                },
                "safebrowsing": {
                    "enabled": True,
                    "enhanced": False
                },
                "search": {
                    "suggest_enabled": True
                },
                "alternate_error_pages": {
                    "enabled": True
                },
                "hardware": {
                    "audio_capture_enabled": True,
                    "video_capture_enabled": True
                },
                "browser": {
                    "show_home_button": True,
                    "check_default_browser": False
                },
                "bookmark_bar": {
                    "show_on_all_tabs": False
                },
                "sync": {
                    "suppress_start": False
                },
                "first_run_tabs": [
                    "https://www.google.com/"
                ],
                "homepage": "https://www.google.com/",
                "homepage_is_newtabpage": False,
                "session": {
                    "restore_on_startup": 1
                }
            }
            
            # Write preferences
            prefs_file = os.path.join(profile_path, "Preferences")
            with open(prefs_file, 'w') as f:
                json.dump(prefs, f, indent=2)
            
            # Create Local State file to make profile look established
            local_state = {
                "profile": {
                    "info_cache": {
                        "Default": {
                            "active_time": time.time(),
                            "is_using_default_avatar": True,
                            "is_using_default_name": True,
                            "name": "Person 1"
                        }
                    },
                    "last_used": "Default",
                    "last_active_profiles": ["Default"]
                }
            }
            
            local_state_file = os.path.join(profile_path, "Local State")
            with open(local_state_file, 'w') as f:
                json.dump(local_state, f, indent=2)
                
            logger.info("Created anti-detection Chrome profile")
            
        except Exception as e:
            logger.warning(f"Failed to configure Chrome profile: {e}")
            
    def start_chrome_in_vnc(self, profile_path: str) -> bool:
        """Start Chrome browser inside VNC session with anti-detection"""
        try:
            logger.info("Starting Chrome browser in VNC session with anti-detection measures...")
            
            # Set display for Chrome
            env = os.environ.copy()
            env['DISPLAY'] = self.vnc_display
            
            # Clean and recreate profile directory completely
            self._clean_chrome_profile_completely(profile_path)
            
            # Create anti-detection profile
            self._create_anti_detection_chrome_profile(profile_path)
            
            # Wait for desktop to be ready
            time.sleep(5)
            
            # Start Chrome with anti-detection flags
            return self._start_stealth_chrome(profile_path, env)
                
        except Exception as e:
            logger.error(f"Failed to start Chrome in VNC: {e}")
            return False
    
    def _start_stealth_chrome(self, profile_path: str, env: dict) -> bool:
        """Start Chrome with comprehensive anti-detection measures and proxy support"""
        try:
            logger.info("Starting Chrome with stealth configuration and proxy support...")
            
            # Comprehensive anti-detection Chrome flags
            chrome_cmd = [
                'google-chrome',
                
                # Essential flags for VNC/container
                '--no-sandbox',
                '--disable-dev-shm-usage',
                '--disable-gpu',
                
                # Anti-detection flags
                '--disable-blink-features=AutomationControlled',
                '--disable-features=VizDisplayCompositor',
                '--disable-extensions',
                '--disable-plugins',
                '--disable-default-apps',
                '--disable-component-extensions-with-background-pages',
                '--disable-background-timer-throttling',
                '--disable-backgrounding-occluded-windows',
                '--disable-renderer-backgrounding',
                '--disable-field-trial-config',
                '--disable-back-forward-cache',
                '--disable-ipc-flooding-protection',
                
                # Make it look more human
                '--no-first-run',
                '--no-default-browser-check',
                '--disable-translate',
                '--disable-features=TranslateUI',
                '--disable-sync',
                '--disable-background-networking',
                '--disable-features=MediaRouter',
                '--disable-print-preview',
                '--disable-features=VizServiceDisplayCompositor',
                
                # User agent and window management
                '--user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36',
                '--window-size=1920,1080',
                '--start-maximized',
                '--disable-infobars',
                '--disable-notifications',
                
                # Profile and user data
                f'--user-data-dir={profile_path}',
                '--profile-directory=Default'
            ]
            
            # Add proxy configuration if provided
            if self.proxy_server:
                if self.proxy_server.startswith('socks'):
                    chrome_cmd.append(f'--proxy-server={self.proxy_server}')
                    logger.info(f"Using SOCKS proxy: {self.proxy_server}")
                elif self.proxy_server.startswith('http'):
                    chrome_cmd.append(f'--proxy-server={self.proxy_server}')
                    logger.info(f"Using HTTP proxy: {self.proxy_server}")
                else:
                    # Assume HTTP if no protocol specified
                    chrome_cmd.append(f'--proxy-server=http://{self.proxy_server}')
                    logger.info(f"Using HTTP proxy: http://{self.proxy_server}")
            
            # Add target URL
            chrome_cmd.append('https://www.instagram.com/accounts/login/')
            
            # Try different Chrome executables
            chrome_executables = ['google-chrome', 'google-chrome-stable', 'chromium-browser', 'chromium']
            
            process = None
            for executable in chrome_executables:
                try:
                    chrome_cmd[0] = executable
                    logger.info(f"Trying Chrome executable: {executable}")
                    process = subprocess.Popen(chrome_cmd, env=env, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                    break
                except FileNotFoundError:
                    logger.warning(f"Chrome executable not found: {executable}")
                    continue
            
            if process is None:
                logger.error("No Chrome executable found")
                return False
            
            self.chrome_pid = process.pid
            logger.info(f"Chrome started with PID: {self.chrome_pid}")
            
            # Give Chrome time to start and load
            time.sleep(10)
            
            # Check if Chrome is still running
            if process.poll() is None:
                logger.info("Chrome started successfully in VNC session")
                
                # Inject anti-detection JavaScript if possible
                self._inject_anti_detection_scripts(env)
                
                return True
            else:
                logger.error("Chrome failed to start properly")
                return False
                
        except Exception as e:
            logger.error(f"Failed to start stealth Chrome: {e}")
            return False

    def _inject_anti_detection_scripts(self, env: dict):
        """Inject anti-detection JavaScript via developer tools if possible"""
        try:
            # This is a placeholder for potential future enhancement
            # In practice, anti-detection is better handled by the Chrome flags
            # and profile configuration we're already using
            logger.info("Anti-detection measures applied via Chrome configuration")
            
        except Exception as e:
            logger.warning(f"Could not inject anti-detection scripts: {e}")
            
    def get_access_info(self) -> Dict[str, Any]:
        """Get VNC access information"""
        return {
            'vnc_display': self.vnc_display,
            'vnc_port': self.vnc_port,
            'vnc_web_port': self.vnc_web_port,
            'vnc_password': self.vnc_password,
            'web_url': f'http://localhost:{self.vnc_web_port}/vnc.html',
            'direct_vnc': f'localhost:{self.vnc_port}',
            'proxy_server': self.proxy_server,
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
            'chrome_pid': self.chrome_pid,
            'proxy_enabled': bool(self.proxy_server),
            'proxy_server': self.proxy_server
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
                'message': 'VNC server with XFCE desktop started successfully'
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
            logger.info("Restarting Chrome with completely fresh session...")
            
            # Stop current Chrome process if running
            if self.chrome_pid:
                try:
                    os.kill(self.chrome_pid, signal.SIGTERM)
                    time.sleep(3)
                except ProcessLookupError:
                    pass
                self.chrome_pid = None
            
            # Completely clean and recreate the profile
            self._clean_chrome_profile_completely(profile_path)
            
            # Start Chrome again
            return self.start_chrome_in_vnc(profile_path)
            
        except Exception as e:
            logger.error(f"Failed to restart Chrome: {e}")
            return False

# Global VNC manager instance
vnc_manager = VNCServerManager(PROXY_SERVER)

def start_vnc_chrome_session(profile_path: str, proxy_server: Optional[str] = None) -> Dict[str, Any]:
    """Start VNC session with Chrome for manual login"""
    global vnc_manager
    if proxy_server:
        vnc_manager.set_proxy(proxy_server)
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

def set_vnc_proxy(proxy_server: str):
    """Set proxy server for VNC Chrome sessions"""
    vnc_manager.set_proxy(proxy_server)

if __name__ == "__main__":
    # Test VNC setup
    profile_path = os.path.join(os.getcwd(), "chrome_profile_instagram")
    result = start_vnc_chrome_session(profile_path)
    print(f"VNC setup result: {result}") 