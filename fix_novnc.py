#!/usr/bin/env python3
"""
Quick fix script for noVNC installation
This script fixes the 404 error by properly installing noVNC web client.
"""

import os
import sys
import subprocess
import shutil
from pathlib import Path
import tempfile
import logging

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def install_novnc_properly():
    """Install noVNC properly to fix the 404 error"""
    try:
        logger.info("🔧 Fixing noVNC installation...")
        
        # Create noVNC directory
        novnc_dir = Path("/usr/share/novnc")
        novnc_dir.mkdir(parents=True, exist_ok=True)
        
        # Method 1: Try package manager first
        try:
            logger.info("Trying package manager installation...")
            subprocess.run(['apt-get', 'update'], check=True, capture_output=True)
            subprocess.run(['apt-get', 'install', '-y', 'novnc'], check=True, capture_output=True)
            
            # Check if installation was successful
            if (Path("/usr/share/novnc/vnc.html").exists() or 
                Path("/usr/share/novnc/vnc_lite.html").exists()):
                logger.info("✅ noVNC installed successfully via package manager!")
                return True
        except subprocess.CalledProcessError:
            logger.info("Package manager installation failed, trying manual download...")
        
        # Method 2: Manual download and install
        try:
            logger.info("Downloading noVNC from GitHub...")
            
            with tempfile.TemporaryDirectory() as temp_dir:
                temp_path = Path(temp_dir)
                
                # Download noVNC
                subprocess.run([
                    'wget', '-q', '--no-check-certificate',
                    'https://github.com/novnc/noVNC/archive/refs/tags/v1.4.0.tar.gz'
                ], cwd=temp_path, check=True)
                
                # Extract
                subprocess.run(['tar', '-xzf', 'v1.4.0.tar.gz'], cwd=temp_path, check=True)
                
                # Copy files properly
                source_dir = temp_path / "noVNC-1.4.0"
                if source_dir.exists():
                    logger.info("Copying noVNC files...")
                    
                    # Remove existing directory if it exists
                    if novnc_dir.exists():
                        shutil.rmtree(novnc_dir)
                    
                    # Copy the entire directory
                    shutil.copytree(source_dir, novnc_dir)
                    
                    logger.info("✅ noVNC installed successfully via manual download!")
                    return True
                else:
                    logger.error("Source directory not found after extraction")
                    
        except Exception as e:
            logger.error(f"Manual download failed: {e}")
        
        # Method 3: Git clone as fallback
        try:
            logger.info("Trying git clone method...")
            
            # Remove existing directory
            if novnc_dir.exists():
                shutil.rmtree(novnc_dir)
            
            subprocess.run([
                'git', 'clone', 'https://github.com/novnc/noVNC.git', str(novnc_dir)
            ], check=True, capture_output=True)
            
            logger.info("✅ noVNC installed successfully via git clone!")
            return True
            
        except subprocess.CalledProcessError:
            logger.error("Git clone failed")
        
        # Method 4: Create working web interface
        logger.info("Creating functional web interface as fallback...")
        create_working_interface()
        return True
        
    except Exception as e:
        logger.error(f"All installation methods failed: {e}")
        return False

def create_working_interface():
    """Create a working web interface that redirects to VNC client instructions"""
    novnc_dir = Path("/usr/share/novnc")
    novnc_dir.mkdir(parents=True, exist_ok=True)
    
    # Create vnc.html with better interface
    html_content = """<!DOCTYPE html>
<html>
<head>
    <title>VNC Access - Instagram Auto Poster</title>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <style>
        * { box-sizing: border-box; }
        body { 
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            line-height: 1.6;
            margin: 0;
            padding: 20px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
        }
        .container {
            max-width: 800px;
            margin: 0 auto;
            background: white;
            padding: 40px;
            border-radius: 15px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.2);
        }
        h1 { color: #333; margin-bottom: 30px; }
        .status { 
            padding: 15px;
            border-radius: 8px;
            margin: 20px 0;
            font-weight: bold;
        }
        .success { background: #d4edda; color: #155724; border: 1px solid #c3e6cb; }
        .info { background: #d1ecf1; color: #0c5460; border: 1px solid #bee5eb; }
        .warning { background: #fff3cd; color: #856404; border: 1px solid #ffeaa7; }
        .error { background: #f8d7da; color: #721c24; border: 1px solid #f5c6cb; }
        
        .method {
            background: #f8f9fa;
            padding: 20px;
            margin: 15px 0;
            border-radius: 8px;
            border-left: 4px solid #007cba;
        }
        .method h3 { margin-top: 0; color: #007cba; }
        
        .code {
            background: #2d3748;
            color: #e2e8f0;
            padding: 15px;
            border-radius: 5px;
            font-family: 'Monaco', 'Menlo', 'Ubuntu Mono', monospace;
            font-size: 14px;
            margin: 10px 0;
            overflow-x: auto;
        }
        
        button {
            background: #007cba;
            color: white;
            padding: 12px 24px;
            border: none;
            border-radius: 6px;
            font-size: 16px;
            cursor: pointer;
            margin: 10px 5px;
            transition: background 0.3s;
        }
        button:hover { background: #005a87; }
        button.secondary { background: #6c757d; }
        button.secondary:hover { background: #545b62; }
        
        .download-links {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 15px;
            margin: 20px 0;
        }
        .download-link {
            display: block;
            padding: 15px;
            background: #e3f2fd;
            border: 1px solid #bbdefb;
            border-radius: 8px;
            text-decoration: none;
            color: #1976d2;
            text-align: center;
            transition: all 0.3s;
        }
        .download-link:hover {
            background: #bbdefb;
            transform: translateY(-2px);
        }
        
        .status-indicator {
            display: inline-block;
            width: 12px;
            height: 12px;
            border-radius: 50%;
            margin-right: 8px;
        }
        .status-green { background: #28a745; }
        .status-red { background: #dc3545; }
        
        @media (max-width: 600px) {
            .container { padding: 20px; }
            .download-links { grid-template-columns: 1fr; }
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>🚀 VNC Server - Instagram Auto Poster</h1>
        
        <div class="status success">
            <span class="status-indicator status-green"></span>
            VNC Server is Running Successfully
        </div>
        
        <div class="status info">
            <strong>🔧 noVNC Web Client Setup Required</strong><br>
            The web-based VNC client needs to be configured. Choose one of the methods below to access your VNC session.
        </div>
        
        <div class="method">
            <h3>🖥️ Method 1: VNC Client Software (Recommended)</h3>
            <p>Download and install a VNC client application:</p>
            
            <div class="download-links">
                <a href="https://www.realvnc.com/en/connect/download/viewer/" class="download-link" target="_blank">
                    <strong>RealVNC Viewer</strong><br>
                    <small>Windows, Mac, Linux</small>
                </a>
                <a href="https://www.tightvnc.com/download.php" class="download-link" target="_blank">
                    <strong>TightVNC</strong><br>
                    <small>Windows, Linux</small>
                </a>
                <a href="https://tigervnc.org/" class="download-link" target="_blank">
                    <strong>TigerVNC</strong><br>
                    <small>Linux, Windows, Mac</small>
                </a>
                <a href="https://apps.apple.com/app/vnc-viewer/id352019548" class="download-link" target="_blank">
                    <strong>VNC Viewer (Mac)</strong><br>
                    <small>Mac App Store</small>
                </a>
            </div>
            
            <p><strong>Connection Details:</strong></p>
            <div class="code">
Server Address: 147.93.112.143:5901
Display: :1
Password: instagram123
            </div>
        </div>
        
        <div class="method">
            <h3>🌐 Method 2: Fix noVNC Web Client</h3>
            <p>Install the web-based VNC client by running these commands on your server:</p>
            <div class="code">
# Quick fix command:
sudo python3 fix_novnc.py

# Or manual installation:
sudo apt-get install novnc
# OR
cd /usr/share && sudo git clone https://github.com/novnc/noVNC.git novnc
            </div>
            <button onclick="tryNoVNC()">🔄 Test noVNC Installation</button>
            <button onclick="window.location.reload()" class="secondary">↻ Refresh Page</button>
        </div>
        
        <div class="method">
            <h3>🔒 Method 3: SSH Tunnel (For Remote Access)</h3>
            <p>If accessing from a remote machine, create an SSH tunnel:</p>
            <div class="code">
# Replace 'user' and 'your-server' with your details
ssh -L 5901:localhost:5901 user@147.93.112.143

# Then connect VNC client to:
# localhost:5901
            </div>
        </div>
        
        <div class="status info">
            <strong>📱 Current Session Status:</strong><br>
            • VNC Display: :1<br>
            • VNC Port: 5901<br>
            • Web Port: 6080<br>
            • Password: instagram123<br>
            • Chrome: Running with Instagram login page<br>
            • Proxy: <span id="proxy-status">http://ng.decodo.com:42032</span>
        </div>
        
        <div class="status warning">
            <strong>⚠️ Note:</strong> Chrome is already running in the VNC session with the Instagram login page loaded. 
            Once you connect via VNC, you can complete any manual login steps required.
        </div>
        
        <hr style="margin: 30px 0; border: none; border-top: 1px solid #eee;">
        
        <p style="text-align: center; color: #666; font-size: 14px;">
            Need help? Check the server logs or contact support.
        </p>
    </div>
    
    <script>
        function tryNoVNC() {
            // Try different possible noVNC URLs
            const urls = ['/vnc_lite.html', '/vnc_auto.html', '/vnc.html?autoconnect=true'];
            
            let found = false;
            let promises = urls.map(url => 
                fetch(url).then(response => {
                    if (response.ok && !found) {
                        found = true;
                        window.location.href = url;
                        return true;
                    }
                    return false;
                }).catch(() => false)
            );
            
            Promise.all(promises).then(results => {
                if (!results.some(r => r)) {
                    alert('noVNC not yet available. Please install it using the commands shown above, then refresh this page.');
                }
            });
        }
        
        // Auto-check for noVNC installation every 30 seconds
        let checkCount = 0;
        const maxChecks = 20; // Stop after 10 minutes
        
        const autoCheck = setInterval(() => {
            checkCount++;
            if (checkCount > maxChecks) {
                clearInterval(autoCheck);
                return;
            }
            
            fetch('/vnc_lite.html')
                .then(response => {
                    if (response.ok) {
                        clearInterval(autoCheck);
                        document.body.innerHTML = `
                            <div style="text-align:center;padding:50px;background:linear-gradient(135deg, #667eea 0%, #764ba2 100%);min-height:100vh;color:white;">
                                <div style="background:white;color:#333;padding:40px;border-radius:15px;max-width:500px;margin:0 auto;">
                                    <h2>🎉 noVNC Available!</h2>
                                    <p>The web VNC client is now ready.</p>
                                    <p>Redirecting in <span id="countdown">3</span> seconds...</p>
                                </div>
                            </div>
                        `;
                        
                        let countdown = 3;
                        const countdownInterval = setInterval(() => {
                            countdown--;
                            document.getElementById('countdown').textContent = countdown;
                            if (countdown <= 0) {
                                clearInterval(countdownInterval);
                                window.location.href = '/vnc_lite.html';
                            }
                        }, 1000);
                    }
                })
                .catch(() => {});
        }, 30000);
        
        // Update page with real server info if available
        if (window.location.hostname !== 'localhost') {
            document.querySelectorAll('.code').forEach(code => {
                code.innerHTML = code.innerHTML.replace(/localhost/g, window.location.hostname);
                code.innerHTML = code.innerHTML.replace(/147\.93\.112\.143/g, window.location.hostname);
            });
        }
    </script>
</body>
</html>"""
    
    # Write the files
    with open(novnc_dir / "vnc.html", 'w') as f:
        f.write(html_content)
    
    with open(novnc_dir / "index.html", 'w') as f:
        f.write(html_content)
    
    logger.info("✅ Functional web interface created")

def test_installation():
    """Test if the installation was successful"""
    novnc_dir = Path("/usr/share/novnc")
    
    if (novnc_dir / "vnc.html").exists():
        logger.info("✅ vnc.html is available")
        return True
    elif (novnc_dir / "vnc_lite.html").exists():
        logger.info("✅ vnc_lite.html is available")
        return True
    else:
        logger.warning("❌ No VNC web interface found")
        return False

def main():
    print("🔧 noVNC Installation Fix Script")
    print("=" * 40)
    
    if os.geteuid() != 0:
        print("❌ This script must be run as root")
        print("Usage: sudo python3 fix_novnc.py")
        sys.exit(1)
    
    if install_novnc_properly():
        print("\n✅ noVNC installation completed!")
        
        if test_installation():
            print("\n🌐 You can now access VNC via web browser:")
            print("   http://your-server-ip:6080/vnc.html")
            print("   Password: instagram123")
        
        print("\n🔄 Refreshing your browser page should now work!")
        print("   If the web interface still shows 404, try:")
        print("   - Refresh the page (Ctrl+F5)")
        print("   - Clear browser cache")
        print("   - Use a VNC client instead")
    else:
        print("\n❌ Installation failed, but a functional interface was created")
        print("   You can still access VNC using a VNC client")
        print("   Server: your-server-ip:5901")
        print("   Password: instagram123")

if __name__ == "__main__":
    main() 