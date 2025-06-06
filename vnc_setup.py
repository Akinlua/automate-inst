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
import asyncio
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
        self.driver = None  # Selenium driver instance
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
                'libasound2-dev',  # Development package for audio
                
                # Python selenium requirements
                'python3-pip'
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
            
            # Install selenium-driverless
            self._install_selenium_driverless()
            
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
    
    def _install_selenium_driverless(self):
        """Install selenium-driverless"""
        try:
            logger.info("Installing selenium-driverless...")
            subprocess.run(['pip3', 'install', 'selenium-driverless'], check=True, capture_output=True)
            logger.info("selenium-driverless installed successfully")
        except subprocess.CalledProcessError as e:
            logger.error(f"Failed to install selenium-driverless: {e}")
            # Try alternative installation
            try:
                subprocess.run(['pip', 'install', 'selenium-driverless'], check=True, capture_output=True)
                logger.info("selenium-driverless installed with pip")
            except subprocess.CalledProcessError as e2:
                logger.error(f"Failed to install selenium-driverless with pip: {e2}")
    
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
                    
                    # Copy to destination using Python instead of shell command
                    source_dir = temp_path / "noVNC-1.4.0"
                    if source_dir.exists():
                        import shutil
                        for item in source_dir.iterdir():
                            dest_item = novnc_dir / item.name
                            if item.is_file():
                                shutil.copy2(item, dest_item)
                            elif item.is_dir():
                                shutil.copytree(item, dest_item, dirs_exist_ok=True)
                        logger.info("noVNC files copied successfully")
                    else:
                        logger.error(f"Source directory not found: {source_dir}")
                        
                logger.info("noVNC installed successfully")
            else:
                logger.info("noVNC already installed")
                
        except Exception as e:
            logger.warning(f"Failed to install noVNC: {e}")
            # Try alternative installation method
            self._install_novnc_fallback()
            
    def _install_novnc_fallback(self):
        """Fallback method to install noVNC using git or package manager"""
        try:
            logger.info("Trying fallback noVNC installation...")
            
            # Try installing noVNC via apt first
            try:
                subprocess.run(['apt-get', 'install', '-y', 'novnc'], check=True, capture_output=True)
                logger.info("noVNC installed via package manager")
                return
            except subprocess.CalledProcessError:
                logger.info("Package manager installation failed, trying git...")
            
            # Try git clone as fallback
            novnc_dir = Path("/usr/share/novnc")
            novnc_dir.mkdir(parents=True, exist_ok=True)
            
            try:
                subprocess.run([
                    'git', 'clone', 'https://github.com/novnc/noVNC.git', str(novnc_dir)
                ], check=True, capture_output=True)
                logger.info("noVNC installed via git clone")
                return
            except subprocess.CalledProcessError:
                logger.info("Git installation failed, creating minimal web interface...")
            
            # Create a minimal web interface as last resort
            self._create_minimal_vnc_interface()
            
        except Exception as e:
            logger.warning(f"All noVNC installation methods failed: {e}")
            self._create_minimal_vnc_interface()
            
    def _create_minimal_vnc_interface(self):
        """Create a minimal VNC web interface"""
        try:
            logger.info("Creating minimal VNC web interface...")
            
            novnc_dir = Path("/usr/share/novnc")
            novnc_dir.mkdir(parents=True, exist_ok=True)
            
            # Create a simple HTML redirect page
            html_content = """<!DOCTYPE html>
<html>
<head>
    <title>VNC Access - Instagram Auto Poster</title>
    <meta charset="utf-8">
    <style>
        body { 
            font-family: Arial, sans-serif; 
            text-align: center; 
            padding: 50px;
            background: #f5f5f5;
        }
        .container {
            max-width: 600px;
            margin: 0 auto;
            background: white;
            padding: 30px;
            border-radius: 10px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }
        .status { margin: 20px 0; }
        .success { color: green; }
        .info { color: blue; }
        .warning { color: orange; }
        button {
            background: #007cba;
            color: white;
            padding: 12px 24px;
            border: none;
            border-radius: 5px;
            font-size: 16px;
            cursor: pointer;
            margin: 10px;
        }
        button:hover { background: #005a87; }
        .code {
            background: #f0f0f0;
            padding: 10px;
            border-radius: 5px;
            font-family: monospace;
            margin: 10px 0;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>🚀 VNC Access - Instagram Auto Poster</h1>
        
        <div class="status success">
            ✅ VNC Server is Running
        </div>
        
        <p>Your VNC server is active and ready for use. Since the full noVNC web client isn't available, you can connect using:</p>
        
        <h3>🔗 Connection Methods:</h3>
        
        <div class="info">
            <strong>Option 1: VNC Client (Recommended)</strong><br>
            Download a VNC client like RealVNC, TightVNC, or TigerVNC Viewer<br>
            <div class="code">
                Server: localhost:5901<br>
                Password: instagram123
            </div>
        </div>
        
        <div class="info">
            <strong>Option 2: SSH Tunnel + VNC</strong><br>
            For remote access, create an SSH tunnel:<br>
            <div class="code">
                ssh -L 5901:localhost:5901 user@your-server<br>
                Then connect VNC client to localhost:5901
            </div>
        </div>
        
        <div class="warning">
            <strong>Option 3: Install noVNC manually</strong><br>
            <div class="code">
                sudo apt-get install novnc<br>
                # or<br>
                cd /usr/share && sudo git clone https://github.com/novnc/noVNC.git novnc
            </div>
            Then refresh this page.
        </div>
        
        <h3>📋 Connection Details:</h3>
        <div class="code">
            VNC Display: :1<br>
            VNC Port: 5901<br>
            Web Port: 6080<br>
            Password: instagram123
        </div>
        
        <p>Chrome should be running automatically in the VNC session with Instagram login page loaded.</p>
        
        <button onclick="checkNoVNC()">🔄 Check for noVNC</button>
        <button onclick="window.location.reload()">↻ Refresh Page</button>
    </div>
    
    <script>
        function checkNoVNC() {
            fetch('/vnc_lite.html')
                .then(response => {
                    if (response.ok) {
                        window.location.href = '/vnc_lite.html';
                    } else {
                        alert('noVNC not found. Please install manually or use a VNC client.');
                    }
                })
                .catch(() => {
                    alert('noVNC not available. Please use a VNC client to connect.');
                });
        }
        
        // Auto-check for noVNC every 30 seconds
        setInterval(() => {
            fetch('/vnc_lite.html')
                .then(response => {
                    if (response.ok) {
                        document.body.innerHTML = '<div style="text-align:center;padding:50px;"><h2>noVNC Available!</h2><p>Redirecting...</p></div>';
                        setTimeout(() => window.location.href = '/vnc_lite.html', 2000);
                    }
                })
                .catch(() => {});
        }, 30000);
    </script>
</body>
</html>"""
            
            # Write the HTML file
            with open(novnc_dir / "vnc.html", 'w') as f:
                f.write(html_content)
                
            # Also create index.html as fallback
            with open(novnc_dir / "index.html", 'w') as f:
                f.write(html_content)
                
            logger.info("Minimal VNC web interface created")
            
        except Exception as e:
            logger.error(f"Failed to create minimal web interface: {e}")
            
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

    def _setup_chrome_profile(self, profile_path: str):
        """Setup Chrome profile directory and downloads folder"""
        try:
            # Create profile directory
            os.makedirs(profile_path, exist_ok=True)
            
            # Create downloads directory
            download_dir = os.path.abspath(os.path.join(os.path.dirname(profile_path), "downloads"))
            os.makedirs(download_dir, exist_ok=True)
            logger.info(f"Downloads will be saved to: {download_dir}")
            logger.info(f"Using Chrome profile at: {profile_path}")
            
            return download_dir
        except Exception as e:
            logger.error(f"Failed to setup Chrome profile: {e}")
            return None

    async def start_chrome_in_vnc(self, profile_path: str) -> bool:
        """Start Chrome browser inside VNC session using selenium-driverless"""
        try:
            logger.info("Starting Chrome browser in VNC session with selenium-driverless...")
            
            # Setup profile and downloads
            download_dir = self._setup_chrome_profile(profile_path)
            if not download_dir:
                return False
            
            # Set display for Chrome
            os.environ['DISPLAY'] = self.vnc_display
            
            # Wait for desktop to be ready
            await asyncio.sleep(5)
            
            # Start Chrome with selenium-driverless
            return await self._start_selenium_driverless_chrome(profile_path, download_dir)
                
        except Exception as e:
            logger.error(f"Failed to start Chrome in VNC: {e}")
            return False
    
    async def _start_selenium_driverless_chrome(self, profile_path: str, download_dir: str) -> bool:
        """Start Chrome with selenium-driverless and minimal options"""
        try:
            logger.info("Starting Chrome with selenium-driverless...")
            
            # Import selenium-driverless
            try:
                from selenium_driverless import webdriver
                from selenium_driverless.types.by import By
            except ImportError as e:
                logger.error(f"selenium-driverless not available: {e}")
                logger.info("Attempting to install selenium-driverless...")
                self._install_selenium_driverless()
                try:
                    from selenium_driverless import webdriver
                    from selenium_driverless.types.by import By
                except ImportError as e2:
                    logger.error(f"Failed to import selenium-driverless after installation: {e2}")
                    return False
            
            # Configure Chrome options with minimal flags
            options = webdriver.ChromeOptions()
            
            # Essential flags for VNC/container environment
            # options.add_argument("--no-sandbox")
            options.add_argument("--disable-gpu")
            options.add_argument("--disable-dev-shm-usage")
            options.add_argument("--window-size=1920,1080")
            # options.add_argument("--disable-blink-features=AutomationControlled")
            
            # Minimal logging
            options.add_argument("--log-level=3")
            
            # Set download preferences
            prefs = {
                "download.default_directory": download_dir.replace("\\", "/"),
                "download.prompt_for_download": False,
                "download.directory_upgrade": True,
                "safebrowsing.enabled": False,
                "plugins.always_open_pdf_externally": True,
                "browser.download.folderList": 2,
                "browser.helperApps.neverAsk.saveToDisk": "application/pdf,application/x-pdf,application/octet-stream,text/plain,text/html",
                "browser.download.manager.showWhenStarting": False
            }
            options.add_experimental_option("prefs", prefs)
            
            # Add proxy if configured
            if self.proxy_server:
                options.add_argument(f"--proxy-server={self.proxy_server}")
                logger.info(f"Using proxy: {self.proxy_server}")
            
            # Start Chrome with selenium-driverless
            logger.info("Initializing selenium-driverless Chrome driver...")
            self.driver = await webdriver.Chrome(options=options)
            
            # Navigate to Instagram
            logger.info("Navigating to Instagram...")
            await self.driver.get("https://www.instagram.com")
            
            logger.info("Chrome started successfully with selenium-driverless in VNC session")
            return True
                
        except Exception as e:
            logger.error(f"Failed to start selenium-driverless Chrome: {e}")
            if self.driver:
                try:
                    await self.driver.quit()
                except:
                    pass
                self.driver = None
            return False
            
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
            'status': self._get_basic_status()
        }
        
    def _get_basic_status(self) -> Dict[str, Any]:
        """Get basic VNC server status without async operations"""
        status = {
            'vnc_running': False,
            'websockify_running': False,
            'chrome_running': False,
            'vnc_pid': self.vnc_pid,
            'websockify_pid': self.websockify_pid,
            'selenium_driver_active': bool(self.driver),
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
                
            # Check Chrome via selenium driver (basic check without async)
            if self.driver:
                status['chrome_running'] = True
                
        except Exception as e:
            logger.warning(f"Error checking basic status: {e}")
            
        return status
        
    async def get_status(self) -> Dict[str, Any]:
        """Get current VNC server status"""
        status = {
            'vnc_running': False,
            'websockify_running': False,
            'chrome_running': False,
            'vnc_pid': self.vnc_pid,
            'websockify_pid': self.websockify_pid,
            'selenium_driver_active': bool(self.driver),
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
                
            # Check Chrome via selenium driver
            if self.driver:
                try:
                    # Try to get current URL to check if driver is alive
                    current_url = await self.driver.current_url
                    status['chrome_running'] = True
                except:
                    status['chrome_running'] = False
                    status['selenium_driver_active'] = False
                    self.driver = None
                
        except Exception as e:
            logger.warning(f"Error checking status: {e}")
            
        return status
        
    async def stop_vnc_server(self):
        """Stop VNC server and related processes"""
        try:
            logger.info("Stopping VNC server...")
            
            # Stop selenium driver
            if self.driver:
                try:
                    await self.driver.quit()
                    logger.info("Selenium driver stopped")
                except Exception as e:
                    logger.warning(f"Error stopping selenium driver: {e}")
                self.driver = None
                    
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
            
        except Exception as e:
            logger.error(f"Error stopping VNC server: {e}")
            
    async def setup_and_start(self, profile_path: str) -> Dict[str, Any]:
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
                
            # Start Chrome in VNC with selenium-driverless
            if not await self.start_chrome_in_vnc(profile_path):
                return {
                    'success': False,
                    'error': 'Failed to start Chrome with selenium-driverless in VNC session'
                }
                
            return {
                'success': True,
                'access_info': self.get_access_info(),
                'message': 'VNC server with XFCE desktop and selenium-driverless Chrome started successfully'
            }
            
        except Exception as e:
            logger.error(f"VNC setup failed: {e}")
            return {
                'success': False,
                'error': f'VNC setup failed: {str(e)}'
            }

    async def restart_chrome_fresh(self, profile_path: str) -> bool:
        """Restart Chrome with completely fresh session using selenium-driverless"""
        try:
            logger.info("Restarting Chrome with completely fresh session...")
            
            # Stop current selenium driver if running
            if self.driver:
                try:
                    await self.driver.quit()
                    await asyncio.sleep(3)
                except Exception as e:
                    logger.warning(f"Error stopping current driver: {e}")
                self.driver = None
            
            # Completely clean and recreate the profile
            if os.path.exists(profile_path):
                logger.info(f"Removing existing Chrome profile: {profile_path}")
                shutil.rmtree(profile_path, ignore_errors=True)
                await asyncio.sleep(1)
            
            # Start Chrome again
            return await self.start_chrome_in_vnc(profile_path)
            
        except Exception as e:
            logger.error(f"Failed to restart Chrome: {e}")
            return False

# Global VNC manager instance
vnc_manager = VNCServerManager()

async def start_vnc_chrome_session(profile_path: str, proxy_server: Optional[str] = None) -> Dict[str, Any]:
    """Start VNC session with Chrome for manual login"""
    global vnc_manager
    if proxy_server:
        vnc_manager.set_proxy(proxy_server)
    return await vnc_manager.setup_and_start(profile_path)
    
async def get_vnc_status() -> Dict[str, Any]:
    """Get current VNC status"""
    return await vnc_manager.get_status()
    
def get_vnc_access_info() -> Dict[str, Any]:
    """Get VNC access information"""
    return vnc_manager.get_access_info()
    
async def stop_vnc_session():
    """Stop VNC session"""
    await vnc_manager.stop_vnc_server()

async def restart_chrome_fresh_session(profile_path: str) -> bool:
    """Restart Chrome with fresh session - callable from web interface"""
    return await vnc_manager.restart_chrome_fresh(profile_path)

def set_vnc_proxy(proxy_server: str):
    """Set proxy server for VNC Chrome sessions"""
    vnc_manager.set_proxy(proxy_server)

def get_driver():
    """Get the current selenium-driverless driver instance"""
    return vnc_manager.driver if vnc_manager else None

async def main():
    """Main async function for testing VNC setup"""
    profile_path = os.path.join(os.getcwd(), "chrome_profile_instagram")
    result = await start_vnc_chrome_session(profile_path)
    print(f"VNC setup result: {result}")

if __name__ == "__main__":
    # Test VNC setup
    asyncio.run(main()) 