#!/bin/bash

# Instagram Auto Poster - Distribution Package Creator
# This script creates complete packages with modern GUI installers

set -e

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

echo ""
echo "=============================================="
echo "   Instagram Auto Poster - Package Creator"
echo "=============================================="
echo ""

# Get current directory and create package directory
CURRENT_DIR="$(pwd)"
PACKAGE_DIR="Instagram_Auto_Poster_Package"
APP_DIR="$PACKAGE_DIR/InstagramAutoPoster"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)

print_status "Creating distribution package with modern GUI installers..."

# Clean and create package directory
if [[ -d "$PACKAGE_DIR" ]]; then
    rm -rf "$PACKAGE_DIR"
fi
mkdir -p "$PACKAGE_DIR"
mkdir -p "$APP_DIR"

# Create core application files to include (go in subfolder)
CORE_FILES=(
    "app.py"
    "instagram_poster.py"
    "requirements.txt"
    "setup_integration.py"
    "setup_chrome.py"
    "vnc_setup.py"
    "run_scheduler.py"
    "test_setup.py"
    "troubleshoot_chrome.py"
    ".env.example"
)

# Setup scripts (go in subfolder)
SETUP_SCRIPTS=(
    "setup.sh"
    "setup.bat"
    "start.sh" 
    "start.bat"
    "setup_noninteractive.sh"
    "setup_noninteractive.bat"
    "start_noninteractive.sh"
    "start_noninteractive.bat"
    "create_launchers.sh"
    "create_simple_mac_launchers.sh"
)

# Documentation files (go in subfolder)
DOC_FILES=(
    "README.md"
    "SETUP_README.md"
)

# Directories to include (go in subfolder)
DIRECTORIES=(
    "templates"
    "static"
    "content"
)

print_status "Copying core application files to InstagramAutoPoster/..."
for file in "${CORE_FILES[@]}"; do
    if [[ -f "$file" ]]; then
        # Special handling for app.py to fix Windows Unicode issues
        if [[ "$file" == "app.py" ]]; then
            # Create a Windows-compatible version of app.py
            cp "$file" "$APP_DIR/"
            
            # Fix Unicode encoding issues in app.py for Windows
            cd "$PACKAGE_DIR"
            python3 << 'PYTHON_SCRIPT'
import re

# Read the original app.py
with open("InstagramAutoPoster/app.py", "r", encoding="utf-8") as f:
    content = f.read()

# Add encoding configuration at the top
new_content = '''#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sys

# Fix Windows Unicode encoding issues
if sys.platform == "win32":
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')
    # Set console codepage to UTF-8 if possible
    try:
        import ctypes
        ctypes.windll.kernel32.SetConsoleOutputCP(65001)
    except:
        pass

''' + content

# Replace emoji characters with safe ASCII alternatives for Windows compatibility
emoji_replacements = {
    "🚀": "[LAUNCH]",
    "📱": "[MOBILE]", 
    "⚙️": "[SETTINGS]",
    "🛑": "[STOP]",
    "✅": "[OK]",
    "❌": "[ERROR]",
    "⚠️": "[WARNING]",
    "📊": "[STATS]",
    "🎯": "[TARGET]",
    "🔍": "[SEARCH]",
    "📝": "[EDIT]",
    "💾": "[SAVE]",
    "🗑️": "[DELETE]",
    "📤": "[UPLOAD]",
    "🔄": "[REFRESH]",
    "⏰": "[TIME]",
    "🎉": "[SUCCESS]",
    "🔧": "[TOOLS]",
    "📂": "[FOLDER]",
    "🌐": "[WEB]",
    "💻": "[COMPUTER]",
    "📋": "[CLIPBOARD]",
    "🖼️": "[IMAGE]",
    "📺": "[SCREEN]",
    "🔑": "[KEY]",
    "🎨": "[DESIGN]",
    "📈": "[CHART]",
    "🔒": "[LOCKED]",
    "🔓": "[UNLOCKED]",
    "⭐": "[STAR]",
    "🎪": "[EVENT]",
    "🏆": "[TROPHY]",
    "📸": "[CAMERA]",
    "💡": "[IDEA]",
    "🚫": "[BLOCKED]",
    "✨": "[SPARKLE]"
}

# Apply replacements only to print statements and comments, not to code logic
lines = new_content.split('\n')
for i, line in enumerate(lines):
    # Only replace emojis in print statements, comments, or string literals
    if 'print(' in line or line.strip().startswith('#') or line.strip().startswith('"""') or line.strip().startswith("'''"):
        for emoji, replacement in emoji_replacements.items():
            line = line.replace(emoji, replacement)
        lines[i] = line

new_content = '\n'.join(lines)

# Write the modified content back
with open("InstagramAutoPoster/app.py", "w", encoding="utf-8") as f:
    f.write(new_content)

print("✓ Fixed Unicode encoding issues in app.py")
PYTHON_SCRIPT
            cd "$CURRENT_DIR"
        else
            cp "$file" "$APP_DIR/"
        fi
        print_status "  ✓ $file"
    else
        print_warning "  ⚠ $file not found - skipping"
    fi
done

print_status "Copying setup scripts to InstagramAutoPoster/..."
for file in "${SETUP_SCRIPTS[@]}"; do
    if [[ -f "$file" ]]; then
        cp "$file" "$APP_DIR/"
        chmod +x "$APP_DIR/$file" 2>/dev/null || true
        print_status "  ✓ $file"
    else
        print_warning "  ⚠ $file not found - skipping"
    fi
done

print_status "Copying documentation to InstagramAutoPoster/..."
for file in "${DOC_FILES[@]}"; do
    if [[ -f "$file" ]]; then
        cp "$file" "$APP_DIR/"
        print_status "  ✓ $file"
    else
        print_warning "  ⚠ $file not found - skipping"
    fi
done

print_status "Copying directories to InstagramAutoPoster/..."
for dir in "${DIRECTORIES[@]}"; do
    if [[ -d "$dir" ]]; then
        cp -r "$dir" "$APP_DIR/"
        print_status "  ✓ $dir/"
    else
        print_warning "  ⚠ $dir/ not found - creating empty directory"
        mkdir -p "$APP_DIR/$dir"
    fi
done

# Create GUI installers in main package folder
print_status "Creating modern GUI installers in main folder..."

cd "$PACKAGE_DIR"

# Create cross-platform GUI installer
print_status "Creating GUI installer script..."

cat > "gui_installer.py" << 'EOF'
#!/usr/bin/env python3

import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import os
import sys
import subprocess
import threading
import platform
import time
import signal
from pathlib import Path

# Try to import psutil, but don't fail if it's not available yet
try:
    import psutil
    PSUTIL_AVAILABLE = True
except ImportError:
    PSUTIL_AVAILABLE = False
    print("Warning: psutil not available yet - some features will be limited until setup completes")

class InstagramAutoPoserInstaller:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Instagram Auto Poster - Setup")
        self.root.geometry("600x550")
        self.root.resizable(False, False)
        
        # Check for auto-launch mode
        self.auto_launch_mode = "--auto-launch" in sys.argv
        
        # Center the window
        self.center_window()
        
        # Set app icon (if available)
        try:
            self.root.iconbitmap('InstagramAutoPoster/static/favicon.ico')
        except:
            pass
        
        # Variables
        self.is_setup_mode = True
        self.app_dir = Path(__file__).parent / "InstagramAutoPoster"
        self.setup_complete = False
        self.server_process = None
        self.server_running = False
        
        # Create GUI
        self.create_widgets()
        
        # Auto-detect mode
        self.detect_mode()
        
        # Update auto-startup button status
        self.update_startup_button()
        
        # Handle auto-launch mode
        if self.auto_launch_mode:
            self.handle_auto_launch()
        
        # Handle window close
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
    
    def center_window(self):
        self.root.update_idletasks()
        x = (self.root.winfo_screenwidth() // 2) - (600 // 2)
        y = (self.root.winfo_screenheight() // 2) - (550 // 2)
        self.root.geometry(f"600x550+{x}+{y}")
    
    def create_widgets(self):
        # Header frame
        header_frame = tk.Frame(self.root, bg="#1a237e", height=80)
        header_frame.pack(fill="x")
        header_frame.pack_propagate(False)
        
        # Title
        title_label = tk.Label(
            header_frame, 
            text="Instagram Auto Poster",
            font=("Arial", 18, "bold"),
            fg="white",
            bg="#1a237e"
        )
        title_label.pack(pady=20)
        
        # Main content frame
        self.content_frame = tk.Frame(self.root, padx=20, pady=20)
        self.content_frame.pack(fill="both", expand=True)
        
        # Welcome message
        self.welcome_label = tk.Label(
            self.content_frame,
            text="Welcome! Click 'Start Setup' to install all requirements and launch the application.",
            font=("Arial", 11),
            wraplength=550,
            justify="center"
        )
        self.welcome_label.pack(pady=10)
        
        # Status frame
        status_frame = tk.Frame(self.content_frame)
        status_frame.pack(fill="x", pady=10)
        
        # Progress bar
        self.progress = ttk.Progressbar(
            status_frame, 
            mode='indeterminate',
            length=550
        )
        self.progress.pack(pady=5)
        
        # Status label
        self.status_label = tk.Label(
            status_frame,
            text="Ready to start...",
            font=("Arial", 10),
            fg="#666"
        )
        self.status_label.pack()
        
        # Server status frame
        server_status_frame = tk.Frame(self.content_frame)
        server_status_frame.pack(fill="x", pady=5)
        
        self.server_status_label = tk.Label(
            server_status_frame,
            text="Server Status: Stopped",
            font=("Arial", 10, "bold"),
            fg="#d32f2f"
        )
        self.server_status_label.pack()
        
        # Log area
        log_frame = tk.Frame(self.content_frame)
        log_frame.pack(fill="both", expand=True, pady=10)
        
        tk.Label(log_frame, text="Installation Progress:", font=("Arial", 10, "bold")).pack(anchor="w")
        
        self.log_text = scrolledtext.ScrolledText(
            log_frame,
            height=10,
            font=("Consolas", 9),
            wrap=tk.WORD,
            state=tk.DISABLED
        )
        self.log_text.pack(fill="both", expand=True)
        
        # Button frame
        button_frame = tk.Frame(self.content_frame)
        button_frame.pack(fill="x", pady=10)
        
        # Main action button
        self.action_button = tk.Button(
            button_frame,
            text="Start Setup",
            font=("Arial", 12, "bold"),
            bg="#4caf50",
            fg="white",
            padx=20,
            pady=10,
            command=self.start_setup
        )
        self.action_button.pack(side="left")
        
        # Stop server button
        self.stop_button = tk.Button(
            button_frame,
            text="Stop Server",
            font=("Arial", 10),
            bg="#f44336",
            fg="white",
            padx=15,
            pady=8,
            command=self.stop_server,
            state="disabled"
        )
        self.stop_button.pack(side="left", padx=10)
        
        # Open app folder button
        self.folder_button = tk.Button(
            button_frame,
            text="Open App Folder",
            font=("Arial", 10),
            padx=15,
            pady=8,
            command=self.open_app_folder
        )
        self.folder_button.pack(side="left")
        
        # Auto-startup button
        self.startup_button = tk.Button(
            button_frame,
            text="Enable Auto-Startup",
            font=("Arial", 10),
            bg="#9c27b0",
            fg="white",
            padx=15,
            pady=8,
            command=self.toggle_auto_startup
        )
        self.startup_button.pack(side="left", padx=5)
        
        # Close button
        self.close_button = tk.Button(
            button_frame,
            text="Close",
            font=("Arial", 10),
            padx=15,
            pady=8,
            command=self.on_closing
        )
        self.close_button.pack(side="right")
    
    def detect_mode(self):
        """Detect if this is first setup or subsequent launch"""
        venv_path = self.app_dir / "venv"
        
        # Check if server is already running AND belongs to our app
        server_actually_running = self.is_our_server_running()
        
        if venv_path.exists():
            self.is_setup_mode = False
            if server_actually_running:
                # Server is already running
                self.welcome_label.config(text="Instagram Auto Poster is already running! Server is active on port 5003.")
                self.action_button.config(
                    text="Open in Browser",
                    bg="#ff9800",
                    command=self.open_browser
                )
                self.status_label.config(text="Server is running - ready to use!")
                self.update_server_status(True)
                self.log_message("✅ Detected running server on port 5003")
                self.log_message("🌐 Server is available at: http://localhost:5003")
            else:
                # Setup complete but server not running
                self.welcome_label.config(text="Instagram Auto Poster is ready! Click 'Launch App' to start.")
                self.action_button.config(
                    text="Launch App",
                    bg="#2196f3",
                    command=self.launch_app
                )
                self.status_label.config(text="Application ready to launch...")
                self.update_server_status(False)
                # Clear any stale state file
                self.clear_server_state()
    
    def is_our_server_running(self):
        """Check if our specific Instagram Auto Poster server is running"""
        self.log_message("🔍 Checking if server is already running...")
        
        # Method 1: Simple port check first
        port_in_use = False
        try:
            import socket
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(2)  # 2 second timeout
            result = sock.connect_ex(('localhost', 5003))
            sock.close()
            port_in_use = (result == 0)
            self.log_message(f"🔍 Port 5003 check: {'IN USE' if port_in_use else 'FREE'}")
        except Exception as e:
            self.log_message(f"⚠️ Port check failed: {str(e)}")
            return False
        
        if not port_in_use:
            self.log_message("✅ Port 5003 is free - no server running")
            return False
        
        # Method 2: Try to make HTTP request to verify it's our app
        self.log_message("🔍 Port is in use - checking if it's our Instagram server...")
        try:
            import urllib.request
            import urllib.error
            
            # Try to access the main page with a short timeout
            request = urllib.request.Request('http://localhost:5003/')
            request.add_header('User-Agent', 'InstagramAutoPoster-Checker')
            
            with urllib.request.urlopen(request, timeout=3) as response:
                if response.code == 200:
                    content = response.read().decode('utf-8', errors='ignore')
                    # Look for Instagram Auto Poster specific content
                    if ('Instagram Auto Poster' in content or 
                        'instagram' in content.lower() or 
                        'content' in content.lower() and 'upload' in content.lower()):
                        self.log_message("✅ Confirmed: Instagram Auto Poster server is running")
                        return True
                    else:
                        self.log_message("⚠️ Port 5003 in use by different application")
                        return False
                else:
                    self.log_message(f"⚠️ Unexpected response code: {response.code}")
                    return False
                    
        except urllib.error.URLError as e:
            self.log_message(f"⚠️ HTTP request failed: {str(e)}")
            # If HTTP request fails but port is in use, it might still be starting up
            # Check if it's a connection refused (server not ready) vs other error
            if "Connection refused" in str(e) or "Connection reset" in str(e):
                self.log_message("ℹ️ Server might be starting up - treating as not ready")
                return False
            else:
                # Other HTTP error - might be our server but having issues
                self.log_message("⚠️ Server responding but with errors - treating as running")
                return True
                
        except Exception as e:
            self.log_message(f"⚠️ Error checking server: {str(e)}")
            return False
        
        # Method 3: Check process list if psutil is available
        if PSUTIL_AVAILABLE:
            self.log_message("🔍 Using psutil to check for our app process...")
            try:
                for proc in psutil.process_iter(['pid', 'name', 'cmdline', 'cwd']):
                    try:
                        if proc.info['cmdline']:
                            cmdline = ' '.join(proc.info['cmdline'])
                            if ('app.py' in cmdline and 
                                'python' in proc.info['name'].lower()):
                                # Found a Python process running app.py
                                if (proc.info['cwd'] and 
                                    'InstagramAutoPoster' in proc.info['cwd']):
                                    self.log_message(f"✅ Found our app process: PID {proc.info['pid']}")
                                    return True
                    except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                        continue
                        
                self.log_message("⚠️ No matching app.py process found")
            except Exception as e:
                self.log_message(f"⚠️ Process check failed: {str(e)}")
        
        # Method 4: Check server state file
        state_file = self.app_dir / '.server_state'
        if state_file.exists():
            try:
                with open(state_file, 'r') as f:
                    state_data = f.read().strip()
                    if state_data == 'running':
                        self.log_message("✅ Server state file indicates running")
                        return True
                    else:
                        self.log_message("ℹ️ Server state file indicates stopped")
            except Exception as e:
                self.log_message(f"⚠️ Could not read server state: {str(e)}")
        
        # If we get here, port is in use but we can't confirm it's our server
        self.log_message("⚠️ Port 5003 in use but cannot confirm it's our server")
        return True  # Assume it's running to be safe
    
    def save_server_state(self, running=True):
        """Save server state to file for persistence"""
        try:
            state_file = self.app_dir / '.server_state'
            with open(state_file, 'w') as f:
                if running:
                    f.write('running')
                else:
                    f.write('stopped')
        except Exception as e:
            self.log_message(f"⚠️ Could not save server state: {str(e)}")
    
    def clear_server_state(self):
        """Clear server state file"""
        try:
            state_file = self.app_dir / '.server_state'
            if state_file.exists():
                state_file.unlink()
        except Exception as e:
            self.log_message(f"⚠️ Could not clear server state: {str(e)}")
    
    def log_message(self, message):
        """Add message to log area"""
        self.log_text.config(state=tk.NORMAL)
        self.log_text.insert(tk.END, f"{message}\n")
        self.log_text.see(tk.END)
        self.log_text.config(state=tk.DISABLED)
        self.root.update()
    
    def update_status(self, status):
        """Update status label"""
        self.status_label.config(text=status)
        self.root.update()
    
    def update_server_status(self, running):
        """Update server status indicator"""
        self.server_running = running
        if running:
            self.server_status_label.config(
                text="Server Status: Running ✓",
                fg="#388e3c"
            )
            self.stop_button.config(state="normal")
        else:
            self.server_status_label.config(
                text="Server Status: Stopped",
                fg="#d32f2f"
            )
            self.stop_button.config(state="disabled")
    
    def find_and_kill_processes(self, process_name="python"):
        """Find and kill processes related to the app"""
        if not PSUTIL_AVAILABLE:
            self.log_message("⚠️ psutil not available - using basic process cleanup")
            # Use basic OS commands for process cleanup
            try:
                if platform.system() == "Windows":
                    # Use taskkill to find and kill python processes running app.py
                    subprocess.run(["taskkill", "/f", "/im", "python.exe", "/fi", "WINDOWTITLE eq *app.py*"], 
                                 capture_output=True)
                    subprocess.run(["taskkill", "/f", "/im", "python3.exe", "/fi", "WINDOWTITLE eq *app.py*"], 
                                 capture_output=True)
                else:
                    # Use pkill on Unix systems
                    subprocess.run(["pkill", "-f", "app.py"], capture_output=True)
                
                self.log_message("✅ Basic process cleanup completed")
                self.clear_server_state()
            except Exception as e:
                self.log_message(f"⚠️ Basic cleanup error: {str(e)}")
            return
        
        try:
            killed_any = False
            # Find processes by name containing app.py
            for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
                try:
                    if proc.info['cmdline']:
                        cmdline = ' '.join(proc.info['cmdline'])
                        if 'app.py' in cmdline and 'python' in proc.info['name'].lower():
                            self.log_message(f"🛑 Terminating Flask app process (PID: {proc.info['pid']})")
                            proc.terminate()
                            try:
                                proc.wait(timeout=3)
                                killed_any = True
                            except psutil.TimeoutExpired:
                                proc.kill()
                                killed_any = True
                except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                    # Process already gone or no access - this is fine
                    continue
            
            # Also try to find by port
            for conn in psutil.net_connections():
                try:
                    if hasattr(conn, 'laddr') and conn.laddr and conn.laddr.port == 5003:
                        proc = psutil.Process(conn.pid)
                        self.log_message(f"🛑 Terminating process using port 5003: {proc.name()} (PID: {conn.pid})")
                        proc.terminate()
                        try:
                            proc.wait(timeout=3)
                            killed_any = True
                        except psutil.TimeoutExpired:
                            proc.kill()
                            killed_any = True
                except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess, AttributeError):
                    # Process already gone, no access, or connection info unavailable - this is fine
                    continue
            
            if killed_any:
                self.log_message("✅ Process cleanup completed")
                # If we killed processes, clear the server state
                self.clear_server_state()
            
        except Exception as e:
            # Only log if it's a significant error, not just cleanup issues
            if "No such process" not in str(e) and "Access denied" not in str(e):
                self.log_message(f"⚠️ Note: Some processes may still be running: {str(e)}")
    
    def start_setup(self):
        """Start the setup process"""
        self.action_button.config(state="disabled")
        self.progress.start()
        
        # Run setup in separate thread
        thread = threading.Thread(target=self.run_setup)
        thread.daemon = True
        thread.start()
    
    def run_setup(self):
        """Run the actual setup process"""
        # Declare global variables at the top of the function
        global psutil, PSUTIL_AVAILABLE
        
        try:
            self.update_status("Starting installation...")
            self.log_message("🚀 Starting Instagram Auto Poster setup...")
            self.log_message(f"📁 App directory: {self.app_dir}")
            
            # First, install psutil if not available (needed for the installer itself)
            if not PSUTIL_AVAILABLE:
                self.log_message("📦 Installing psutil for installer functionality...")
                self.update_status("Installing psutil...")
                try:
                    subprocess.run([sys.executable, "-m", "pip", "install", "psutil"], 
                                 check=True, capture_output=True, text=True, timeout=60)
                    self.log_message("✅ psutil installed successfully!")
                    # Try to import it now
                    import psutil
                    PSUTIL_AVAILABLE = True
                    self.log_message("✅ psutil is now available for use")
                except Exception as e:
                    self.log_message(f"⚠️ Could not install psutil: {str(e)}")
                    self.log_message("⚠️ Continuing with limited functionality...")
            
            # Change to app directory
            os.chdir(self.app_dir)
            
            # Determine setup script
            if platform.system() == "Windows":
                setup_script_path = self.app_dir / "setup_noninteractive.bat"
                setup_script = str(setup_script_path.resolve())  # Get absolute path
                
                # Verify the batch file exists before trying to run it
                if not setup_script_path.exists():
                    raise FileNotFoundError(f"Setup script not found: {setup_script}")
                
                self.log_message(f"🔍 Batch file found: {setup_script}")
                self.log_message(f"🔍 Working directory: {self.app_dir}")
                
                # For Windows paths with spaces, ensure proper quoting
                if ' ' in setup_script:
                    setup_script = f'"{setup_script}"'
                    self.log_message("🔧 Added quotes for spaces in path")
            else:
                setup_script = "./setup_noninteractive.sh"
            
            self.log_message(f"🔧 Running setup script: {setup_script}")
            self.update_status("Installing Python and dependencies...")
            
            # Run setup process
            if platform.system() == "Windows":
                # On Windows, explicitly call batch file with cmd.exe
                self.log_message(f"🔧 Executing: cmd.exe /c {setup_script}")
                self.log_message(f"🔧 Current working directory: {os.getcwd()}")
                self.log_message(f"🔧 Target working directory: {self.app_dir}")
                
                try:
                    process = subprocess.Popen(
                        ["cmd.exe", "/c", setup_script],
                        stdout=subprocess.PIPE,
                        stderr=subprocess.STDOUT,
                        text=True,
                        cwd=str(self.app_dir),  # Ensure string path
                        shell=False  # Explicitly no shell since we're using cmd.exe
                    )
                except Exception as e:
                    self.log_message(f"❌ Failed to start process: {str(e)}")
                    self.log_message("🔧 Attempting alternative Windows execution method...")
                    
                    # Fallback: try with shell=True
                    try:
                        process = subprocess.Popen(
                            setup_script,
                            stdout=subprocess.PIPE,
                            stderr=subprocess.STDOUT,
                            text=True,
                            cwd=str(self.app_dir),
                            shell=True
                        )
                        self.log_message("✅ Fallback method started successfully")
                    except Exception as e2:
                        raise Exception(f"Both execution methods failed: {str(e)} and {str(e2)}")
            else:
                process = subprocess.Popen(
                    ["bash", setup_script],
                    stdout=subprocess.PIPE,
                    stderr=subprocess.STDOUT,
                    text=True,
                    cwd=self.app_dir
                )
            
            # Read output line by line
            for line in process.stdout:
                line = line.strip()
                if line:
                    # Filter and format output
                    if "INFO" in line or "SUCCESS" in line:
                        self.log_message(f"✅ {line}")
                    elif "WARNING" in line:
                        self.log_message(f"⚠️ {line}")
                    elif "ERROR" in line:
                        self.log_message(f"❌ {line}")
                    elif "Failed" in line or "failed" in line:
                        self.log_message(f"❌ {line}")
                    elif "Installing" in line or "installing" in line:
                        self.log_message(f"📦 {line}")
                    else:
                        self.log_message(line)
                    
                    # Update status based on content
                    if "python" in line.lower():
                        self.update_status("Setting up Python...")
                    elif "pip" in line.lower() or "install" in line.lower():
                        self.update_status("Installing dependencies...")
                    elif "chrome" in line.lower():
                        self.update_status("Checking Chrome installation...")
                    elif "virtual" in line.lower():
                        self.update_status("Creating virtual environment...")
            
            process.wait()
            
            if process.returncode == 0:
                # Verify installation by testing imports
                self.log_message("🧪 Verifying installation by testing imports...")
                self.update_status("Verifying installation...")
                
                # Try to import critical modules
                venv_python = self.app_dir / "venv" / "Scripts" / "python.exe"
                
                if venv_python.exists():
                    python_cmd = str(venv_python)
                    self.log_message(f"✅ Testing with: {python_cmd}")
                    
                    # Test critical imports
                    critical_modules = ["flask", "selenium", "PIL", "requests", "dotenv"]
                    all_imports_ok = True
                    
                    for module in critical_modules:
                        try:
                            result = subprocess.run(
                                [python_cmd, "-c", f"import {module}; print('{module} OK')"],
                                cwd=self.app_dir,
                                capture_output=True,
                                text=True,
                                timeout=10
                            )
                            
                            if result.returncode == 0:
                                self.log_message(f"✅ {module} import successful")
                            else:
                                self.log_message(f"❌ {module} import failed: {result.stderr}")
                                all_imports_ok = False
                        except Exception as e:
                            self.log_message(f"❌ Could not test {module}: {str(e)}")
                            all_imports_ok = False
                    
                    if not all_imports_ok:
                        self.log_message("⚠️ Some imports failed - setup may be incomplete")
                        messagebox.showwarning(
                            "Setup Warning",
                            "Setup completed but some dependencies may not have installed correctly.\n\n" +
                            "The application might not work properly. Check the log for details."
                        )
                    else:
                        self.log_message("✅ All critical modules imported successfully!")
                
                self.setup_complete = True
                self.update_status("✅ Setup completed successfully!")
                self.log_message("🎉 Setup completed successfully!")
                self.log_message("🌐 You can now access the app at: http://localhost:5003")
                
                # Update UI for launch mode
                self.action_button.config(
                    text="Launch App",
                    bg="#2196f3",
                    command=self.launch_app,
                    state="normal"
                )
                
                # Auto-launch the app after setup
                self.log_message("🚀 Auto-launching application...")
                time.sleep(1)
                self.launch_app()
                
            else:
                self.update_status("❌ Setup failed!")
                self.log_message("❌ Setup failed! Please check the errors above.")
                self.log_message(f"❌ Setup process exited with code: {process.returncode}")
                self.action_button.config(state="normal")
                messagebox.showerror(
                    "Setup Failed",
                    "Setup encountered errors. Please check the log for details.\n\n" +
                    "Common issues:\n" +
                    "• Internet connection problems during download\n" +
                    "• Antivirus blocking installation\n" +
                    "• Insufficient disk space\n" +
                    "• Python/pip configuration issues"
                )
        
        except Exception as e:
            self.update_status(f"❌ Error: {str(e)}")
            self.log_message(f"❌ Error: {str(e)}")
            self.action_button.config(state="normal")
            messagebox.showerror("Error", f"Setup failed with error:\n{str(e)}")
        
        finally:
            self.progress.stop()
    
    def launch_app(self):
        """Launch the application"""
        self.action_button.config(state="disabled")
        self.progress.start()
        
        # Run launch in separate thread
        thread = threading.Thread(target=self.run_launch)
        thread.daemon = True
        thread.start()
    
    def run_launch(self):
        """Run the actual launch process"""
        try:
            self.update_status("Launching application...")
            self.log_message("🚀 Launching Instagram Auto Poster...")
            
            # Stop existing server if running
            self.find_and_kill_processes()
            time.sleep(2)
            
            # Change to app directory
            os.chdir(self.app_dir)
            
            # For Windows, we need special handling due to start /B behavior
            if platform.system() == "Windows":
                self.launch_windows_server()
            else:
                self.launch_unix_server()
                
        except Exception as e:
            self.update_status(f"❌ Error: {str(e)}")
            self.log_message(f"❌ Error: {str(e)}")
            messagebox.showerror("Error", f"Failed to launch app:\n{str(e)}")
        
        finally:
            self.progress.stop()
            self.action_button.config(state="normal")
    
    def launch_windows_server(self):
        """Launch server on Windows with special handling"""
        self.log_message("🪟 Launching on Windows...")
        self.update_status("Starting Windows server...")
        
        # Method 1: Try direct Python execution first
        try:
            self.log_message("📝 Attempting direct Python execution...")
            
            # Use system-wide Python instead of virtual environment
            python_cmd = sys.executable
            self.log_message(f"✅ Using system-wide Python: {python_cmd}")
            
            # First, test if app.py can even import without running it
            self.log_message("🔍 Testing app.py imports...")
            test_process = subprocess.Popen(
                [python_cmd, "-c", "import app; print('✅ All imports successful')"],
                cwd=self.app_dir,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            
            test_stdout, test_stderr = test_process.communicate(timeout=10)
            
            if test_process.returncode != 0:
                self.log_message("❌ Import test failed!")
                if test_stderr:
                    self.log_message(f"🔍 Import errors: {test_stderr}")
                if test_stdout:
                    self.log_message(f"🔍 Import output: {test_stdout}")
                
                # Try to reinstall dependencies
                self.log_message("🔄 Attempting to fix missing dependencies...")
                self.attempt_dependency_fix(python_cmd)
                return
            else:
                self.log_message("✅ Import test passed - all modules available")
            
            # Create a completely detached process that won't be affected by the GUI
            # This is the key fix - we create a separate Python process that runs independently
            self.log_message("🚀 Starting completely detached Flask server...")
            
            # Set environment variables to prevent Python from freezing
            env = os.environ.copy()
            env['PYTHONUNBUFFERED'] = '1'  # Force unbuffered output
            env['PYTHONDONTWRITEBYTECODE'] = '1'  # Don't write .pyc files
            env['PYTHONIOENCODING'] = 'utf-8'  # Force UTF-8 encoding
            env['FLASK_ENV'] = 'production'  # Set Flask to production mode
            env['PYTHONUTF8'] = '1'  # Force UTF-8 mode
            
            # Create startup info for hidden window
            startup_info = subprocess.STARTUPINFO()
            startup_info.dwFlags |= subprocess.STARTF_USESHOWWINDOW
            startup_info.wShowWindow = subprocess.SW_HIDE
            
            # Use simpler process creation that's more compatible
            # Just use DETACHED_PROCESS to separate from GUI without complex flags
            self.server_process = subprocess.Popen(
                [python_cmd, "-u", "app.py"],
                cwd=self.app_dir,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                stdin=subprocess.DEVNULL,  # Prevent waiting for input
                text=True,
                env=env,  # Use our custom environment
                creationflags=subprocess.DETACHED_PROCESS,  # Simple detached process
                startupinfo=startup_info
            )
            
            # Don't monitor the process output in real-time as this can cause blocking
            # Instead, just check if the port becomes available
            self.log_message("⏱️ Waiting for server to start (detached mode)...")
            startup_success = False
            
            # Give the server time to start without blocking on output
            for attempt in range(15):  # Wait up to 30 seconds
                time.sleep(2)
                
                # Just check if port is listening, don't read process output
                port_listening = False
                try:
                    import socket
                    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    sock.settimeout(1)  # 1 second timeout
                    result = sock.connect_ex(('localhost', 5003))
                    sock.close()
                    if result == 0:
                        port_listening = True
                except:
                    pass
                
                if port_listening:
                    startup_success = True
                    self.log_message(f"✅ Server ready after {(attempt + 1) * 2} seconds!")
                    break
                
                # Check if process died early (but don't read output as it can block)
                if self.server_process.poll() is not None:
                    self.log_message("💀 Process terminated early!")
                    break
                
                self.log_message(f"⏳ Waiting for server... ({attempt + 1}/15)")
            
            if startup_success:
                self.handle_successful_launch()
            else:
                # Only try to read output if the process has actually terminated
                if self.server_process.poll() is not None:
                    try:
                        stdout, stderr = self.server_process.communicate(timeout=2)
                        error_output = stderr if stderr else "Unknown error"
                        if "ModuleNotFoundError" in error_output or "ImportError" in error_output:
                            self.log_message("🔄 Detected missing dependencies - attempting fix...")
                            self.attempt_dependency_fix(python_cmd)
                        else:
                            self.handle_failed_launch(f"Server failed to start. Error: {error_output}")
                    except subprocess.TimeoutExpired:
                        self.handle_failed_launch("Server process not responding")
                else:
                    # Process is still running but port not available
                    self.handle_failed_launch("Server started but port 5003 is not accessible")
                
        except subprocess.TimeoutExpired:
            self.log_message("⏰ Import test timed out - possible dependency issues")
            self.attempt_dependency_fix(python_cmd)
        except Exception as e:
            self.log_message(f"❌ Direct launch failed: {str(e)}")
            # Try fallback method for Windows
            if "parameter is incorrect" in str(e).lower() or "winerror 87" in str(e).lower():
                self.log_message("🔄 Trying fallback Windows launch method...")
                self.launch_windows_fallback(python_cmd)
            else:
                self.handle_failed_launch(str(e))
    
    def attempt_dependency_fix(self, python_cmd):
        """Attempt to fix missing dependencies"""
        self.log_message("🔧 Attempting to fix missing dependencies...")
        self.update_status("Fixing missing dependencies...")
        
        try:
            # Try to reinstall all dependencies
            self.log_message("📦 Reinstalling dependencies...")
            
            dependencies = [
                "selenium", "Pillow", "python-dotenv", "schedule", 
                "jiter", "distro", "requests", "flask", "werkzeug", "pytz", 
                "psutil", "undetected-chromedriver", "setuptools", 
                "selenium-driverless"
            ]
            
            for dep in dependencies:
                self.log_message(f"🔄 Installing {dep}...")
                result = subprocess.run(
                    [python_cmd, "-m", "pip", "install", dep, "--upgrade"],
                    cwd=self.app_dir,
                    capture_output=True,
                    text=True,
                    timeout=120
                )
                
                if result.returncode == 0:
                    self.log_message(f"✅ {dep} installed successfully")
                else:
                    self.log_message(f"❌ Failed to install {dep}: {result.stderr}")
            
            # Test imports again
            self.log_message("🧪 Testing imports after reinstallation...")
            test_result = subprocess.run(
                [python_cmd, "-c", "import app; print('All imports successful after fix')"],
                cwd=self.app_dir,
                capture_output=True,
                text=True,
                timeout=10
            )
            
            if test_result.returncode == 0:
                self.log_message("✅ Dependencies fixed! Retrying server start...")
                # Retry launching the server
                self.launch_windows_server_retry(python_cmd)
            else:
                self.log_message("❌ Dependencies still missing after reinstall")
                self.log_message(f"🔍 Import errors: {test_result.stderr}")
                self.handle_failed_launch(f"Missing dependencies could not be fixed: {test_result.stderr}")
                
        except Exception as e:
            self.log_message(f"❌ Dependency fix failed: {str(e)}")
            self.handle_failed_launch(f"Could not fix dependencies: {str(e)}")
    
    def launch_windows_server_retry(self, python_cmd):
        """Retry launching Windows server after dependency fix"""
        try:
            self.log_message("🔄 Retrying server launch...")
            
            self.server_process = subprocess.Popen(
                [python_cmd, "app.py"],
                cwd=self.app_dir,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                creationflags=subprocess.CREATE_NEW_PROCESS_GROUP
            )
            
            # Wait for startup
            for attempt in range(10):
                time.sleep(2)
                
                if self.server_process.poll() is not None:
                    stdout, stderr = self.server_process.communicate()
                    self.log_message(f"💀 Process failed again: {stderr}")
                    self.handle_failed_launch(f"Server still fails after dependency fix: {stderr}")
                    return
                
                # Check if port is listening
                try:
                    for conn in psutil.net_connections():
                        if hasattr(conn, 'laddr') and conn.laddr and conn.laddr.port == 5003:
                            self.log_message(f"✅ Server started successfully after fix!")
                            self.handle_successful_launch()
                            return
                except:
                    pass
                
                self.log_message(f"⏳ Retry attempt {attempt + 1}/10...")
            
            self.handle_failed_launch("Server failed to start even after dependency fix")
            
        except Exception as e:
            self.handle_failed_launch(f"Retry failed: {str(e)}")
    
    def launch_unix_server(self):
        """Launch server on Unix systems"""
        self.log_message("🐧 Launching on Unix system...")
        start_script = "./start_noninteractive.sh"
        
        self.log_message(f"▶️ Running: {start_script}")
        self.update_status("Starting web server...")
        
        # Start the application process in completely detached mode
        # This prevents the GUI from blocking the Flask server
        self.server_process = subprocess.Popen(
            ["bash", start_script],
            cwd=self.app_dir,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            stdin=subprocess.DEVNULL,  # Prevent waiting for input
            text=True,
            preexec_fn=os.setsid  # Create new session - completely detached
        )
        
        # Don't monitor output in real-time - just check if port becomes available
        self.log_message("⏱️ Waiting for server to start (detached mode)...")
        startup_success = False
        
        # Give server time to start without blocking on output reading
        for attempt in range(15):  # Wait up to 30 seconds
            time.sleep(2)
            
            # Check if port is listening
            port_listening = False
            try:
                import socket
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.settimeout(1)  # 1 second timeout
                result = sock.connect_ex(('localhost', 5003))
                sock.close()
                if result == 0:
                    port_listening = True
            except:
                pass
            
            if port_listening:
                startup_success = True
                self.log_message(f"✅ Server ready after {(attempt + 1) * 2} seconds!")
                break
            
            # Check if process died early (but don't read output as it can block)
            if self.server_process.poll() is not None:
                self.log_message("💀 Process terminated early!")
                break
            
            self.log_message(f"⏳ Waiting for server... ({attempt + 1}/15)")
        
        if startup_success:
            self.handle_successful_launch()
        else:
            # Only try to read output if process has terminated
            error_output = "Unknown error"
            if self.server_process.poll() is not None:
                try:
                    stdout, stderr = self.server_process.communicate(timeout=2)
                    error_output = stderr if stderr else stdout if stdout else "Unknown error"
                except subprocess.TimeoutExpired:
                    error_output = "Process not responding"
            
            self.handle_failed_launch(f"Unix server failed to start. Output: {error_output}")
    
    def handle_successful_launch(self):
        """Handle successful server launch"""
        self.update_status("✅ Application launched!")
        self.update_server_status(True)
        # Save server state for future detection
        self.save_server_state(True)
        self.log_message("✅ Application launched successfully!")
        self.log_message("🌐 Opening browser to: http://localhost:5003")
        
        # Try to open browser
        try:
            import webbrowser
            webbrowser.open("http://localhost:5003")
        except Exception as e:
            self.log_message(f"⚠️ Could not auto-open browser: {str(e)}")
        
        # Show success message and then auto-close the GUI
        messagebox.showinfo(
            "App Launched!",
            "Instagram Auto Poster is now running!\n\n" +
            "The web interface should open automatically.\n" +
            "If not, go to: http://localhost:5003\n\n" +
            "This window will close automatically.\n" +
            "The server will continue running in the background.\n\n" +
            "To stop the server later, reopen this application\n" +
            "and click 'Stop Server'."
        )
        
        # Auto-close the GUI after showing the message
        self.log_message("✅ Server is running - closing GUI window...")
        self.log_message("ℹ️ To stop server, reopen this application and click 'Stop Server'")
        
        # Close the window immediately after user clicks OK
        self.root.after(100, self.auto_close_after_launch)
    
    def auto_close_after_launch(self):
        """Auto-close the GUI after successful launch"""
        # Save the running state before closing
        self.save_server_state(True)
        self.root.quit()
        self.root.destroy()
    
    def handle_failed_launch(self, error_msg):
        """Handle failed server launch"""
        self.update_status("❌ Application failed to start!")
        self.log_message("❌ Application failed to start!")
        self.log_message(f"🔍 Error details: {error_msg}")
        
        # Additional debugging for Windows
        if platform.system() == "Windows":
            self.log_message("🔧 Windows debugging info:")
            
            # Check system Python instead
            try:
                python_version = subprocess.run([sys.executable, "--version"], capture_output=True, text=True)
                self.log_message(f"✅ System Python: {python_version.stdout.strip()}")
            except:
                self.log_message("❌ System Python check failed")
            
            # Check if app.py exists
            app_py = self.app_dir / "app.py"
            if app_py.exists():
                self.log_message("✅ app.py found")
            else:
                self.log_message("❌ app.py not found")
            
            # Check what's using port 5003
            try:
                import socket
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                result = sock.connect_ex(('localhost', 5003))
                sock.close()
                if result == 0:
                    self.log_message("⚠️ Port 5003 is already in use")
                else:
                    self.log_message("ℹ️ Port 5003 is free")
            except Exception as e:
                self.log_message(f"⚠️ Could not check port status: {str(e)}")
        
        messagebox.showerror(
            "Launch Failed", 
            f"Failed to start the server.\n\n" +
            f"Error: {error_msg}\n\n" +
            "Please check the log for more details."
        )
    
    def stop_server(self):
        """Stop the server process"""
        try:
            self.log_message("🛑 Stopping server...")
            
            # Kill all processes related to our app
            self.find_and_kill_processes()
            
            # Also terminate our tracked process if it exists
            if self.server_process and self.server_process.poll() is None:
                if platform.system() == "Windows":
                    # On Windows, send CTRL_BREAK_EVENT to the process group
                    try:
                        self.server_process.send_signal(signal.CTRL_BREAK_EVENT)
                        self.server_process.wait(timeout=3)
                    except:
                        # Force kill the process tree
                        subprocess.run(["taskkill", "/f", "/t", "/pid", str(self.server_process.pid)], 
                                     capture_output=True)
                else:
                    # On Unix-like systems, kill the process group
                    try:
                        os.killpg(os.getpgid(self.server_process.pid), signal.SIGTERM)
                        self.server_process.wait(timeout=3)
                    except:
                        # Force kill if it doesn't respond
                        try:
                            os.killpg(os.getpgid(self.server_process.pid), signal.SIGKILL)
                        except:
                            pass
                
                self.server_process = None
            
            self.update_server_status(False)
            # Clear server state when stopped
            self.save_server_state(False)
            self.clear_server_state()
            self.log_message("✅ Server stopped successfully!")
            self.update_status("Server stopped")
            
        except Exception as e:
            self.log_message(f"⚠️ Error stopping server: {str(e)}")
    
    def open_app_folder(self):
        """Open the application folder"""
        try:
            if platform.system() == "Windows":
                os.startfile(self.app_dir)
            elif platform.system() == "Darwin":  # macOS
                subprocess.run(["open", self.app_dir])
            else:  # Linux
                subprocess.run(["xdg-open", self.app_dir])
        except Exception as e:
            messagebox.showerror("Error", f"Could not open folder:\n{str(e)}")
    
    def on_closing(self):
        """Handle window close event"""
        should_stop_server = False
        
        if self.server_running:
            result = messagebox.askyesno(
                "Server Running", 
                "The Instagram Auto Poster server is still running.\n\n" +
                "Do you want to stop the server before closing?"
            )
            if result:  # User clicked Yes - stop server
                should_stop_server = True
                self.stop_server()
                time.sleep(2)
                # Final cleanup - kill any remaining processes
                self.find_and_kill_processes()
                # Ensure state is cleared since server was stopped
                self.clear_server_state()
            else:  # User clicked No - keep server running
                self.log_message("✅ Server will continue running in background")
                # Save state to indicate server should still be running
                self.save_server_state(True)
        else:
            # No server running, safe to do cleanup
            self.find_and_kill_processes()
            # Ensure state reflects server is stopped
            self.clear_server_state()
        
        self.root.quit()
        self.root.destroy()
    
    def run(self):
        """Start the GUI"""
        self.root.mainloop()
    
    def open_browser(self):
        """Open browser to running app"""
        try:
            import webbrowser
            webbrowser.open("http://localhost:5003")
            self.log_message("✅ Opened browser to: http://localhost:5003")
        except Exception as e:
            self.log_message(f"❌ Failed to open browser: {str(e)}")
            messagebox.showerror("Error", f"Could not open browser:\n{str(e)}")

    def toggle_auto_startup(self):
        """Toggle auto-startup functionality"""
        if self.is_auto_startup_enabled():
            self.disable_auto_startup()
        else:
            self.enable_auto_startup()
    
    def is_auto_startup_enabled(self):
        """Check if auto-startup is currently enabled"""
        try:
            if platform.system() == "Windows":
                import winreg
                key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, 
                                   r"Software\Microsoft\Windows\CurrentVersion\Run", 
                                   0, winreg.KEY_READ)
                try:
                    winreg.QueryValueEx(key, "InstagramAutoPoster")
                    winreg.CloseKey(key)
                    return True
                except FileNotFoundError:
                    winreg.CloseKey(key)
                    return False
            
            elif platform.system() == "Darwin":  # macOS
                plist_path = Path.home() / "Library/LaunchAgents/com.instagramautoposter.startup.plist"
                return plist_path.exists()
            
            else:  # Linux
                desktop_path = Path.home() / ".config/autostart/InstagramAutoPoster.desktop"
                return desktop_path.exists()
        except:
            return False
    
    def enable_auto_startup(self):
        """Enable auto-startup on system boot"""
        try:
            app_path = str(self.app_dir.parent.absolute())
            
            if platform.system() == "Windows":
                self.enable_windows_startup(app_path)
            elif platform.system() == "Darwin":
                self.enable_macos_startup(app_path)
            else:
                self.enable_linux_startup(app_path)
            
            self.startup_button.config(
                text="Disable Auto-Startup",
                bg="#f44336"
            )
            self.log_message("✅ Auto-startup enabled! App will start on system boot.")
            messagebox.showinfo(
                "Auto-Startup Enabled",
                "Instagram Auto Poster will now start automatically when your computer boots!\n\n" +
                "The app will launch minimized in the background.\n" +
                "Access it at: http://localhost:5003"
            )
            
        except Exception as e:
            self.log_message(f"❌ Failed to enable auto-startup: {str(e)}")
            messagebox.showerror("Error", f"Failed to enable auto-startup:\n{str(e)}")
    
    def disable_auto_startup(self):
        """Disable auto-startup on system boot"""
        try:
            if platform.system() == "Windows":
                self.disable_windows_startup()
            elif platform.system() == "Darwin":
                self.disable_macos_startup()
            else:
                self.disable_linux_startup()
            
            self.startup_button.config(
                text="Enable Auto-Startup",
                bg="#9c27b0"
            )
            self.log_message("✅ Auto-startup disabled.")
            messagebox.showinfo("Auto-Startup Disabled", "Auto-startup has been disabled.")
            
        except Exception as e:
            self.log_message(f"❌ Failed to disable auto-startup: {str(e)}")
            messagebox.showerror("Error", f"Failed to disable auto-startup:\n{str(e)}")
    
    def enable_windows_startup(self, app_path):
        """Enable Windows startup via registry"""
        import winreg
        
        # Create startup script
        startup_script = Path(app_path) / "startup_silent.bat"
        startup_script.write_text(f'''@echo off
cd /d "{app_path}"
start /min python gui_installer.py --auto-launch
''', encoding='utf-8')
        
        # Add to Windows startup registry
        key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, 
                           r"Software\Microsoft\Windows\CurrentVersion\Run", 
                           0, winreg.KEY_SET_VALUE)
        winreg.SetValueEx(key, "InstagramAutoPoster", 0, winreg.REG_SZ, str(startup_script))
        winreg.CloseKey(key)
    
    def disable_windows_startup(self):
        """Disable Windows startup"""
        import winreg
        key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, 
                           r"Software\Microsoft\Windows\CurrentVersion\Run", 
                           0, winreg.KEY_SET_VALUE)
        try:
            winreg.DeleteValue(key, "InstagramAutoPoster")
        except FileNotFoundError:
            pass
        winreg.CloseKey(key)
    
    def enable_macos_startup(self, app_path):
        """Enable macOS startup via LaunchAgent"""
        plist_dir = Path.home() / "Library/LaunchAgents"
        plist_dir.mkdir(exist_ok=True)
        
        plist_content = f'''<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.instagramautoposter.startup</string>
    <key>ProgramArguments</key>
    <array>
        <string>python3</string>
        <string>{app_path}/gui_installer.py</string>
        <string>--auto-launch</string>
    </array>
    <key>WorkingDirectory</key>
    <string>{app_path}</string>
    <key>RunAtLoad</key>
    <true/>
    <key>KeepAlive</key>
    <false/>
    <key>StandardOutPath</key>
    <string>/tmp/instagram_auto_poster.log</string>
    <key>StandardErrorPath</key>
    <string>/tmp/instagram_auto_poster_error.log</string>
</dict>
</plist>'''
        
        plist_path = plist_dir / "com.instagramautoposter.startup.plist"
        plist_path.write_text(plist_content, encoding='utf-8')
        
        # Load the launch agent
        subprocess.run(["launchctl", "load", str(plist_path)], capture_output=True)
    
    def disable_macos_startup(self):
        """Disable macOS startup"""
        plist_path = Path.home() / "Library/LaunchAgents/com.instagramautoposter.startup.plist"
        if plist_path.exists():
            # Unload the launch agent
            subprocess.run(["launchctl", "unload", str(plist_path)], capture_output=True)
            plist_path.unlink()
    
    def enable_linux_startup(self, app_path):
        """Enable Linux startup via autostart desktop file"""
        autostart_dir = Path.home() / ".config/autostart"
        autostart_dir.mkdir(parents=True, exist_ok=True)
        
        desktop_content = f'''[Desktop Entry]
Name=Instagram Auto Poster
Comment=Auto-start Instagram Auto Poster
Type=Application
Exec=python3 "{app_path}/gui_installer.py" --auto-launch
Hidden=false
NoDisplay=false
X-GNOME-Autostart-enabled=true
'''
        
        desktop_path = autostart_dir / "InstagramAutoPoster.desktop"
        desktop_path.write_text(desktop_content, encoding='utf-8')
        desktop_path.chmod(0o755)
    
    def disable_linux_startup(self):
        """Disable Linux startup"""
        desktop_path = Path.home() / ".config/autostart/InstagramAutoPoster.desktop"
        if desktop_path.exists():
            desktop_path.unlink()

    def update_startup_button(self):
        """Update auto-startup button status"""
        if self.is_auto_startup_enabled():
            self.startup_button.config(
                text="Disable Auto-Startup",
                bg="#f44336"
            )
        else:
            self.startup_button.config(
                text="Enable Auto-Startup",
                bg="#9c27b0"
            )

    def handle_auto_launch(self):
        """Handle auto-launch mode"""
        self.action_button.config(state="disabled")
        self.progress.start()
        
        # Run auto-launch in separate thread
        thread = threading.Thread(target=self.run_auto_launch)
        thread.daemon = True
        thread.start()
    
    def run_auto_launch(self):
        """Run the actual auto-launch process"""
        try:
            self.update_status("Launching application...")
            self.log_message("🚀 Launching Instagram Auto Poster...")
            
            # Stop existing server if running
            self.find_and_kill_processes()
            time.sleep(2)
            
            # Change to app directory
            os.chdir(self.app_dir)
            
            # Use the same launch methods as regular launch
            if platform.system() == "Windows":
                self.launch_windows_server()
            else:
                self.launch_unix_server()
                
        except Exception as e:
            self.update_status(f"❌ Error: {str(e)}")
            self.log_message(f"❌ Error: {str(e)}")
            messagebox.showerror("Error", f"Failed to launch app:\n{str(e)}")
        
        finally:
            self.progress.stop()
            self.action_button.config(state="normal")

    def launch_windows_fallback(self, python_cmd):
        """Fallback Windows launch method without detached process"""
        try:
            self.log_message("🔧 Using simple Windows launch method...")
            
            # Use the simplest possible process creation
            self.server_process = subprocess.Popen(
                [python_cmd, "app.py"],
                cwd=self.app_dir,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            
            # Wait for startup with simple method
            self.log_message("⏱️ Waiting for server startup...")
            startup_success = False
            
            for attempt in range(15):  # Wait up to 30 seconds
                time.sleep(2)
                
                # Check if process died early
                if self.server_process.poll() is not None:
                    stdout, stderr = self.server_process.communicate()
                    error_output = stderr if stderr else stdout if stdout else "Unknown error"
                    self.log_message(f"💀 Process failed: {error_output}")
                    
                    if "ModuleNotFoundError" in error_output or "ImportError" in error_output:
                        self.log_message("🔄 Detected missing dependencies - attempting fix...")
                        self.attempt_dependency_fix(python_cmd)
                        return
                    else:
                        self.handle_failed_launch(f"Fallback method failed: {error_output}")
                        return
                
                # Check if port is listening
                port_listening = False
                try:
                    import socket
                    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    sock.settimeout(1)
                    result = sock.connect_ex(('localhost', 5003))
                    sock.close()
                    if result == 0:
                        port_listening = True
                except:
                    pass
                
                if port_listening:
                    startup_success = True
                    self.log_message(f"✅ Fallback method succeeded after {(attempt + 1) * 2} seconds!")
                    break
                
                self.log_message(f"⏳ Fallback waiting... ({attempt + 1}/15)")
            
            if startup_success:
                self.handle_successful_launch()
            else:
                self.handle_failed_launch("Fallback method: Server started but port not accessible")
                
        except Exception as e:
            self.log_message(f"❌ Fallback method also failed: {str(e)}")
            self.handle_failed_launch(f"All Windows launch methods failed: {str(e)}")

if __name__ == "__main__":
    app = InstagramAutoPoserInstaller()
    app.run()
EOF

print_success "  ✓ GUI installer script created"

# Create Python launcher executables
print_status "Creating platform-specific GUI launchers..."

# Windows launcher
cat > "Instagram Auto Poster.bat" << 'EOF'
@echo off
title Instagram Auto Poster
cd /d "%~dp0"

REM Enable delayed expansion for the loop
setlocal EnableDelayedExpansion

REM Try to find Python
set PYTHON_CMD=

echo Checking for Python installation...
for %%i in (python3.13 python3.12 python3.11 python3.10 python3.9 python3.8 python3 python) do (
    %%i --version >nul 2>&1
    if !errorlevel! == 0 (
        set PYTHON_CMD=%%i
        goto :found_python
    )
)

REM If Python not found, automatically download and install it
echo Python not found. Downloading and installing Python automatically (ensure after successful download to close and start the application...
echo This may take a few minutes...
echo.

REM Create temp directory for download
if not exist "%TEMP%\InstagramAutoPoster" mkdir "%TEMP%\InstagramAutoPoster"
cd /d "%TEMP%\InstagramAutoPoster"

REM Download Python installer
echo Downloading Python installer...
powershell -Command "& {[Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12; Invoke-WebRequest -Uri 'https://www.python.org/ftp/python/3.11.9/python-3.11.9-amd64.exe' -OutFile 'python_installer.exe'}"

if not exist "python_installer.exe" (
    echo Failed to download Python installer.
    echo Please manually install Python from https://python.org/downloads
    echo Press any key to open Python download page...
    pause >nul
    start https://python.org/downloads
    exit /b 1
)

REM Install Python silently with pip and add to PATH
echo Installing Python...
echo This will take a few minutes, please wait...
python_installer.exe /quiet InstallAllUsers=0 PrependPath=1 Include_pip=1 Include_tcltk=1

REM Wait for installation to complete
timeout /t 10 >nul

REM Clean up installer
del python_installer.exe

REM Return to original directory
cd /d "%~dp0"

REM Refresh PATH by restarting command processor
echo Refreshing system PATH...
call refreshenv.cmd >nul 2>&1 || (
    echo Please restart this script after Python installation completes.
    echo Press any key to restart...
    pause >nul
    "%~f0"
    exit /b
)

REM Try to find Python again after installation
echo Checking for Python after installation...
for %%i in (python3.13 python3.12 python3.11 python3.10 python3.9 python3.8 python3 python) do (
    %%i --version >nul 2>&1
    if !errorlevel! == 0 (
        set PYTHON_CMD=%%i
        goto :found_python
    )
)

REM If still not found, try refreshing PATH manually
echo Refreshing PATH variables...
for /f "tokens=2*" %%a in ('reg query "HKCU\Environment" /v PATH 2^>nul') do set "UserPath=%%b"
for /f "tokens=2*" %%a in ('reg query "HKLM\SYSTEM\CurrentControlSet\Control\Session Manager\Environment" /v PATH 2^>nul') do set "SystemPath=%%b"
set "PATH=%UserPath%;%SystemPath%"

REM Try Python one more time
for %%i in (python3.13 python3.12 python3.11 python3.10 python3.9 python3.8 python3 python) do (
    %%i --version >nul 2>&1
    if !errorlevel! == 0 (
        set PYTHON_CMD=%%i
        goto :found_python
    )
)

echo Python installation may have succeeded but is not in PATH.
echo Please restart your computer and try again, or install Python manually.
echo Press any key to open Python download page...
pause >nul
start https://python.org/downloads
exit /b 1

:found_python
echo Found Python: !PYTHON_CMD!
echo Starting Instagram Auto Poster...
"!PYTHON_CMD!" gui_installer.py
if !errorlevel! neq 0 (
    echo.
    echo Failed to start the installer.
    pause
)
EOF

print_success "  ✓ Windows GUI launcher created"

# macOS launcher
cat > "Instagram Auto Poster.command" << 'EOF'
#!/bin/bash

# Get the directory where this .command file is located
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$SCRIPT_DIR"

# Function to find Python
find_python() {
    for cmd in python3.13 python3.12 python3.11 python3.10 python3.9 python3.8 python3 python; do
        if command -v "$cmd" >/dev/null 2>&1; then
            echo "$cmd"
            return 0
        fi
    done
    return 1
}

# Try to find Python
PYTHON_CMD=$(find_python)

if [[ -z "$PYTHON_CMD" ]]; then
    echo "Python not found. Please install Python from https://python.org"
    echo "Press Enter to open Python download page..."
    read
    open "https://python.org/downloads"
    exit 1
fi

echo "Starting Instagram Auto Poster..."
"$PYTHON_CMD" gui_installer.py

# Keep terminal open if there was an error
if [[ $? -ne 0 ]]; then
    echo ""
    echo "Failed to start the installer."
    read -p "Press Enter to close..."
fi
EOF

chmod +x "Instagram Auto Poster.command"
print_success "  ✓ macOS GUI launcher created"

# Linux launcher
cat > "Instagram Auto Poster.desktop" << 'EOF'
[Desktop Entry]
Name=Instagram Auto Poster
Comment=Instagram Auto Poster - Modern Setup & Launch
Exec=bash -c "cd '%k' && python3 gui_installer.py || (echo 'Failed to start installer'; read -p 'Press Enter to close...')"
Icon=applications-internet
Type=Application
Terminal=false
Categories=Network;WebDevelopment;
EOF

chmod +x "Instagram Auto Poster.desktop"
print_success "  ✓ Linux GUI launcher created"

# Create comprehensive README for main folder
cat > "USER_GUIDE.md" << 'EOF'
# Instagram Auto Poster - User Guide

Welcome! This package provides a modern, user-friendly way to install and run the Instagram Auto Poster.

## 🚀 Quick Start - One Click Setup!

### 🪟 Windows Users
**Double-click:** `Instagram Auto Poster.bat`

### 🍎 macOS Users  
**Double-click:** `Instagram Auto Poster.command`
- *Note: Right-click → Open on first use for security*

### 🐧 Linux Users
**Double-click:** `Instagram Auto Poster.desktop`

## ⚡ Auto-Startup Feature (NEW!)

Want the Instagram Auto Poster to start automatically when your computer boots? 

1. **Launch the installer** (double-click the launcher for your OS)
2. **Click "Enable Auto-Startup"** button in the installer window
3. **Done!** The app will now start automatically every time you boot your computer

### How Auto-Startup Works
- 🔄 **Windows**: Adds entry to Windows startup registry
- 🍎 **macOS**: Creates a LaunchAgent that starts with your user session
- 🐧 **Linux**: Adds desktop file to autostart directory

### Managing Auto-Startup
- **Enable**: Click "Enable Auto-Startup" (purple button)
- **Disable**: Click "Disable Auto-Startup" (red button)
- **Status**: Button color shows current state

## ✨ What You'll See

When you double-click the launcher, you'll see a beautiful, modern installer window that:

- 🎯 **No Scary Terminal**: Clean, graphical interface
- 📊 **Progress Tracking**: Real-time installation progress
- 🔄 **Auto-Detection**: Knows if it's first-time setup or app launch
- ⚡ **One-Click Setup**: Installs everything automatically
- 🌐 **Auto-Launch**: Opens your browser to the app when ready
- 🚀 **Auto-Startup**: Can start with your computer (optional)

## 📁 Folder Structure

```
Instagram_Auto_Poster_Package/
├── Instagram Auto Poster.bat      (Windows GUI launcher)
├── Instagram Auto Poster.command  (macOS GUI launcher)  
├── Instagram Auto Poster.desktop  (Linux launcher)
├── gui_installer.py               (Modern GUI installer)
├── USER_GUIDE.md                  (this file)
└── InstagramAutoPoster/           (application files)
    ├── app.py                     (main application)
    ├── setup.sh                   (setup script)
    ├── start.sh                   (start script)
    └── [all other files...]
```

## 🎯 Installation Process

The modern installer automatically:

1. **🔍 Detects Your System**: Windows, macOS, or Linux
2. **🐍 Installs Python**: If not already installed (3.8+)
3. **📦 Creates Environment**: Isolated virtual environment
4. **⬇️ Downloads Dependencies**: All required packages
5. **🏗️ Sets Up Folders**: Creates necessary directories
6. **🌐 Checks Chrome**: Verifies browser installation
7. **🚀 Launches App**: Opens web interface automatically

## 📱 After Installation

1. **Web Interface**: Automatically opens at `http://localhost:5003`
2. **Setup Chrome**: Click the setup button in the web interface
3. **Upload Content**: Add your images and captions to the `content` folder
4. **Configure Schedule**: Set your posting preferences
5. **Start Posting**: Enable scheduler or post manually
6. **Auto-Startup** (Optional): Click "Enable Auto-Startup" for boot-time launching

## 🔧 Requirements

- **Google Chrome** (install from https://google.com/chrome)
- **Internet Connection** (for downloading dependencies)
- **Python 3.8+** (installed automatically if missing)

## 🆘 Troubleshooting

### Common Solutions
- **Permission Issues**: Right-click → "Open" or "Run as Administrator"
- **Chrome Not Found**: Install from https://google.com/chrome
- **Port 5003 Busy**: The installer will show instructions to change the port
- **Auto-Startup Not Working**: Make sure you have user permissions for startup entries

### First-Time Setup
1. The installer window will show "Start Setup" - click it
2. Wait for the automated installation (3-5 minutes)
3. Click "Launch App" when setup completes
4. Your browser opens to the app automatically
5. Optionally click "Enable Auto-Startup" for automatic boot-time launching

### Subsequent Uses
1. The installer window will show "Launch App" directly
2. Click it to start the application
3. Your browser opens to the app automatically

### Auto-Startup Management
- **Enable**: Purple "Enable Auto-Startup" button
- **Disable**: Red "Disable Auto-Startup" button
- **Check Status**: Button color indicates current state
- **Troubleshoot**: Auto-startup runs silently in background

## ⚠️ Important Notes

- **Educational Use Only**: Follow Instagram's Terms of Service
- **Responsible Usage**: Don't spam or violate platform rules
- **Chrome Required**: Must be installed separately
- **Internet Required**: For initial dependency downloads
- **Auto-Startup**: Runs in background - access via http://localhost:5003

## 🎉 Modern Features

- **🖥️ Native Look**: Matches your operating system's style
- **📈 Progress Bars**: See installation progress in real-time
- **💬 Clear Messages**: No confusing technical jargon
- **🎯 Smart Detection**: Knows what to do automatically
- **🌐 Auto-Browser**: Opens the app in your browser automatically
- **🚀 Auto-Startup**: Start with computer boot (optional)
- **⚡ Background Mode**: Runs silently when auto-started

## 🔄 Auto-Startup Behavior

When auto-startup is enabled:
- **Silent Launch**: Starts automatically without showing installer window
- **Background Running**: Runs in system background
- **Immediate Access**: Available at http://localhost:5003 right after boot
- **No Interruption**: Doesn't interfere with your normal startup routine
- **Easy Disable**: Use the installer to disable anytime

---

**Ready to start? Just double-click the launcher for your operating system! 🚀**

*No terminals, no command lines, no confusion - just click and go!* ✨

**Want auto-startup? Click "Enable Auto-Startup" in the installer!** 🔄
EOF

cd "$CURRENT_DIR"

# Create archive
print_status "Creating distribution archive..."

if command -v zip >/dev/null 2>&1; then
    ARCHIVE_NAME="Instagram_Auto_Poster_${TIMESTAMP}.zip"
    zip -r "$ARCHIVE_NAME" "$PACKAGE_DIR" > /dev/null
    print_success "Created ZIP archive: $ARCHIVE_NAME"
elif command -v tar >/dev/null 2>&1; then
    ARCHIVE_NAME="Instagram_Auto_Poster_${TIMESTAMP}.tar.gz"
    tar -czf "$ARCHIVE_NAME" "$PACKAGE_DIR"
    print_success "Created TAR.GZ archive: $ARCHIVE_NAME"
else
    print_warning "No archive tool found - distribution folder ready: $PACKAGE_DIR"
    ARCHIVE_NAME="$PACKAGE_DIR"
fi

# Create Windows MSI Installer using NSIS
print_status "Creating professional Windows MSI installer..."

# Create NSIS installer script
cat > "installer.nsi" << 'EOF'
; Instagram Auto Poster - Professional Windows Installer
; Created with NSIS (Nullsoft Scriptable Install System)

!define APP_NAME "Instagram Auto Poster"
!define APP_VERSION "1.0.0"
!define APP_PUBLISHER "Instagram Auto Poster Team"
!define APP_URL "https://github.com/your-repo/instagram-auto-poster"
!define APP_DESCRIPTION "Professional Instagram automation tool with modern GUI"

; Installer name and output file
Name "${APP_NAME}"
OutFile "Instagram_Auto_Poster_Installer_${TIMESTAMP}.exe"
InstallDir "$PROGRAMFILES\InstagramAutoPoster"
RequestExecutionLevel admin

; Modern UI includes
!include "MUI2.nsh"
!include "FileFunc.nsh"
!include "LogicLib.nsh"
!include "WinVer.nsh"

; MUI Settings
!define MUI_ABORTWARNING
!define MUI_ICON "installer_icon.ico"
!define MUI_UNICON "installer_icon.ico"
!define MUI_HEADERIMAGE
!define MUI_HEADERIMAGE_BITMAP "installer_header.bmp"
!define MUI_WELCOMEFINISHPAGE_BITMAP "installer_welcome.bmp"
!define MUI_UNWELCOMEFINISHPAGE_BITMAP "installer_welcome.bmp"

; Welcome page
!insertmacro MUI_PAGE_WELCOME

; License page (optional)
!insertmacro MUI_PAGE_LICENSE "LICENSE.txt"

; Directory page
!insertmacro MUI_PAGE_DIRECTORY

; Components page
!insertmacro MUI_PAGE_COMPONENTS

; Installation page
!insertmacro MUI_PAGE_INSTFILES

; Finish page
!define MUI_FINISHPAGE_RUN "$INSTDIR\Instagram Auto Poster.exe"
!define MUI_FINISHPAGE_RUN_TEXT "Launch Instagram Auto Poster"
!define MUI_FINISHPAGE_SHOWREADME "$INSTDIR\USER_GUIDE.txt"
!define MUI_FINISHPAGE_SHOWREADME_TEXT "Show User Guide"
!insertmacro MUI_PAGE_FINISH

; Uninstaller pages
!insertmacro MUI_UNPAGE_WELCOME
!insertmacro MUI_UNPAGE_CONFIRM
!insertmacro MUI_UNPAGE_INSTFILES
!insertmacro MUI_UNPAGE_FINISH

; Languages
!insertmacro MUI_LANGUAGE "English"

; Version Information
VIProductVersion "1.0.0.0"
VIAddVersionKey "ProductName" "${APP_NAME}"
VIAddVersionKey "Comments" "${APP_DESCRIPTION}"
VIAddVersionKey "CompanyName" "${APP_PUBLISHER}"
VIAddVersionKey "LegalCopyright" "© 2024 ${APP_PUBLISHER}"
VIAddVersionKey "FileDescription" "${APP_NAME} Installer"
VIAddVersionKey "FileVersion" "${APP_VERSION}"
VIAddVersionKey "ProductVersion" "${APP_VERSION}"
VIAddVersionKey "InternalName" "${APP_NAME}"
VIAddVersionKey "OriginalFilename" "Instagram_Auto_Poster_Installer.exe"

; Installer sections
Section "Core Application" SecCore
    SectionIn RO  ; Read-only section (always installed)
    
    SetOutPath "$INSTDIR"
    
    ; Copy all application files
    File /r "Instagram_Auto_Poster_Package\*.*"
    
    ; Create desktop shortcut
    CreateShortCut "$DESKTOP\${APP_NAME}.lnk" "$INSTDIR\Instagram Auto Poster.exe" "" "$INSTDIR\icon.ico"
    
    ; Create Start Menu shortcuts
    CreateDirectory "$SMPROGRAMS\${APP_NAME}"
    CreateShortCut "$SMPROGRAMS\${APP_NAME}\${APP_NAME}.lnk" "$INSTDIR\Instagram Auto Poster.exe" "" "$INSTDIR\icon.ico"
    CreateShortCut "$SMPROGRAMS\${APP_NAME}\User Guide.lnk" "$INSTDIR\USER_GUIDE.txt"
    CreateShortCut "$SMPROGRAMS\${APP_NAME}\Uninstall.lnk" "$INSTDIR\Uninstall.exe"
    
    ; Write registry keys for Add/Remove Programs
    WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${APP_NAME}" "DisplayName" "${APP_NAME}"
    WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${APP_NAME}" "UninstallString" "$INSTDIR\Uninstall.exe"
    WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${APP_NAME}" "DisplayIcon" "$INSTDIR\icon.ico"
    WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${APP_NAME}" "Publisher" "${APP_PUBLISHER}"
    WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${APP_NAME}" "DisplayVersion" "${APP_VERSION}"
    WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${APP_NAME}" "URLInfoAbout" "${APP_URL}"
    WriteRegDWORD HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${APP_NAME}" "NoModify" 1
    WriteRegDWORD HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${APP_NAME}" "NoRepair" 1
    
    ; Calculate and write installation size
    ${GetSize} "$INSTDIR" "/S=0K" $0 $1 $2
    IntFmt $0 "0x%08X" $0
    WriteRegDWORD HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${APP_NAME}" "EstimatedSize" "$0"
    
    ; Create uninstaller
    WriteUninstaller "$INSTDIR\Uninstall.exe"
    
SectionEnd

Section "Python Runtime" SecPython
    DetailPrint "Checking Python installation..."
    
    ; Check if Python is already installed
    nsExec::ExecToStack 'python --version'
    Pop $0
    ${If} $0 != 0
        ; Python not found, download and install
        DetailPrint "Python not found. Installing Python 3.11..."
        
        ; Download Python installer
        inetc::get "https://www.python.org/ftp/python/3.11.9/python-3.11.9-amd64.exe" "$TEMP\python_installer.exe"
        Pop $0
        ${If} $0 == "OK"
            DetailPrint "Installing Python..."
            ; Install Python silently
            nsExec::ExecToLog '"$TEMP\python_installer.exe" /quiet InstallAllUsers=0 PrependPath=1 Include_pip=1 Include_tcltk=1'
            Pop $0
            ${If} $0 == 0
                DetailPrint "Python installed successfully!"
            ${Else}
                DetailPrint "Python installation failed. Please install manually."
            ${EndIf}
            Delete "$TEMP\python_installer.exe"
        ${Else}
            DetailPrint "Failed to download Python installer."
        ${EndIf}
    ${Else}
        DetailPrint "Python is already installed."
    ${EndIf}
SectionEnd

Section "Auto-Startup" SecAutoStart
    DetailPrint "Setting up auto-startup..."
    
    ; Add to Windows startup registry
    WriteRegStr HKCU "Software\Microsoft\Windows\CurrentVersion\Run" "InstagramAutoPoster" "$INSTDIR\Instagram Auto Poster.exe --auto-launch"
    
SectionEnd

Section "Desktop Integration" SecDesktop
    ; Create additional desktop shortcuts
    CreateShortCut "$DESKTOP\Instagram Auto Poster - Setup.lnk" "$INSTDIR\Instagram Auto Poster.exe" "" "$INSTDIR\icon.ico"
    
    ; Register file associations (optional)
    WriteRegStr HKCR ".iap" "" "InstagramAutoPoster.Project"
    WriteRegStr HKCR "InstagramAutoPoster.Project" "" "Instagram Auto Poster Project"
    WriteRegStr HKCR "InstagramAutoPoster.Project\DefaultIcon" "" "$INSTDIR\icon.ico"
    WriteRegStr HKCR "InstagramAutoPoster.Project\shell\open\command" "" '"$INSTDIR\Instagram Auto Poster.exe" "%1"'
    
SectionEnd

; Component descriptions
!insertmacro MUI_FUNCTION_DESCRIPTION_BEGIN
    !insertmacro MUI_DESCRIPTION_TEXT ${SecCore} "Core application files (required)"
    !insertmacro MUI_DESCRIPTION_TEXT ${SecPython} "Download and install Python runtime if not present"
    !insertmacro MUI_DESCRIPTION_TEXT ${SecAutoStart} "Start Instagram Auto Poster automatically with Windows"
    !insertmacro MUI_DESCRIPTION_TEXT ${SecDesktop} "Create desktop shortcuts and file associations"
!insertmacro MUI_FUNCTION_DESCRIPTION_END

; Uninstaller section
Section "Uninstall"
    ; Remove registry keys
    DeleteRegKey HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${APP_NAME}"
    DeleteRegValue HKCU "Software\Microsoft\Windows\CurrentVersion\Run" "InstagramAutoPoster"
    DeleteRegKey HKCR ".iap"
    DeleteRegKey HKCR "InstagramAutoPoster.Project"
    
    ; Remove shortcuts
    Delete "$DESKTOP\${APP_NAME}.lnk"
    Delete "$DESKTOP\Instagram Auto Poster - Setup.lnk"
    RMDir /r "$SMPROGRAMS\${APP_NAME}"
    
    ; Remove application files
    RMDir /r "$INSTDIR"
    
SectionEnd

; Functions
Function .onInit
    ; Check Windows version
    ${IfNot} ${AtLeastWin7}
        MessageBox MB_OK "This application requires Windows 7 or later."
        Abort
    ${EndIf}
    
    ; Check if already installed
    ReadRegStr $R0 HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${APP_NAME}" "UninstallString"
    StrCmp $R0 "" done
    
    MessageBox MB_OKCANCEL|MB_ICONEXCLAMATION \
    "${APP_NAME} is already installed. $\n$\nClick OK to remove the previous version or Cancel to cancel this upgrade." \
    IDOK uninst
    Abort
    
    uninst:
        ClearErrors
        ExecWait '$R0 _?=$INSTDIR'
        
        IfErrors no_remove_uninstaller done
        no_remove_uninstaller:
    
    done:
FunctionEnd

Function .onInstSuccess
    ; Show completion message
    MessageBox MB_OK "${APP_NAME} has been installed successfully!$\n$\nClick OK to continue."
FunctionEnd
EOF

print_success "✓ NSIS installer script created"

# Create installer resources
print_status "Creating installer resources..."

# Create a simple license file
cat > "LICENSE.txt" << 'EOF'
Instagram Auto Poster - End User License Agreement

Copyright (c) 2024 Instagram Auto Poster Team

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

IMPORTANT NOTICE:
This software is intended for educational and personal use only. Users are 
responsible for complying with Instagram's Terms of Service and applicable laws.
The developers assume no responsibility for any misuse of this software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
EOF

# Create installer build script for Windows
cat > "build_installer.bat" << 'EOF'
@echo off
title Building Instagram Auto Poster Installer
echo ================================================
echo   Building Professional Windows Installer
echo ================================================
echo.

REM Check if NSIS is installed
where makensis >nul 2>&1
if %errorlevel% neq 0 (
    echo NSIS not found! 
    echo.
    echo Please install NSIS from: https://nsis.sourceforge.io/Download
    echo.
    echo After installation, add NSIS to your PATH or run this from the NSIS directory.
    echo.
    pause
    exit /b 1
)

echo NSIS found! Building installer...
echo.

REM Build the installer
makensis installer.nsi

if %errorlevel% equ 0 (
    echo.
    echo ================================================
    echo   ✅ Installer built successfully!
    echo ================================================
    echo.
    echo The installer has been created and is ready for distribution.
    echo.
    echo To digitally sign the installer:
    echo 1. Get a code signing certificate from a trusted CA
    echo 2. Use signtool.exe to sign the .exe file
    echo.
    echo Example signing command:
    echo signtool sign /f "certificate.pfx" /p "password" /t "http://timestamp.digicert.com" "Instagram_Auto_Poster_Installer.exe"
    echo.
) else (
    echo.
    echo ❌ Installer build failed!
    echo Please check the errors above.
    echo.
)

pause
EOF

# Create signing instructions
cat > "SIGNING_GUIDE.md" << 'EOF'
# Digital Signing Guide for Instagram Auto Poster Installer

## Why Digital Signing?

Digital signing your installer provides:
- ✅ **No "Unknown Publisher" warnings**
- ✅ **Windows SmartScreen trust**
- ✅ **Professional appearance**
- ✅ **User confidence**
- ✅ **Enterprise deployment compatibility**

## Step 1: Get a Code Signing Certificate

### Option A: Commercial Certificate (Recommended)
Purchase from trusted Certificate Authorities:
- **DigiCert** (~$400/year) - Most trusted
- **Sectigo/Comodo** (~$200/year) - Good value
- **GlobalSign** (~$300/year) - Reliable
- **Entrust** (~$500/year) - Enterprise-grade

### Option B: Self-Signed Certificate (Testing Only)
For testing purposes only (will still show warnings):
```cmd
# Create self-signed certificate (PowerShell as Admin)
New-SelfSignedCertificate -Type CodeSigningCert -Subject "CN=Your Name" -KeyAlgorithm RSA -KeyLength 2048 -Provider "Microsoft Enhanced RSA and AES Cryptographic Provider" -KeyExportPolicy Exportable -KeyUsage DigitalSignature -CertStoreLocation Cert:\CurrentUser\My
```

## Step 2: Install Windows SDK (for signtool.exe)

Download and install **Windows SDK** from Microsoft:
- https://developer.microsoft.com/en-us/windows/downloads/windows-sdk/

Or install via **Visual Studio Installer** (lighter option):
- Select "MSVC v143 - VS 2022 C++ x64/x86 build tools"
- Select "Windows 11 SDK"

## Step 3: Sign Your Installer

### Basic Signing (PFX file)
```cmd
# Replace with your actual paths and password
signtool sign ^
  /f "path\to\your\certificate.pfx" ^
  /p "your-certificate-password" ^
  /t "http://timestamp.digicert.com" ^
  /fd sha256 ^
  /v ^
  "Instagram_Auto_Poster_Installer_TIMESTAMP.exe"
```

### Advanced Signing (Certificate Store)
```cmd
# If certificate is in Windows Certificate Store
signtool sign ^
  /n "Your Certificate Subject Name" ^
  /t "http://timestamp.digicert.com" ^
  /fd sha256 ^
  /v ^
  "Instagram_Auto_Poster_Installer_TIMESTAMP.exe"
```

### EV Certificate Signing (USB Token)
```cmd
# For Extended Validation certificates on USB tokens
signtool sign ^
  /sha1 "certificate-thumbprint" ^
  /tr "http://timestamp.digicert.com" ^
  /td sha256 ^
  /fd sha256 ^
  /v ^
  "Instagram_Auto_Poster_Installer_TIMESTAMP.exe"
```

## Step 4: Verify Signature

```cmd
# Verify the signature is valid
signtool verify /pa /v "Instagram_Auto_Poster_Installer_TIMESTAMP.exe"
```

## Step 5: Build Reputation (Important!)

Even with a valid signature, Windows SmartScreen may still show warnings for new certificates. To build reputation:

1. **Start Small**: Distribute to trusted users first
2. **Volume Matters**: More downloads = faster reputation building
3. **Clean History**: Ensure no malware detections
4. **Time**: Reputation builds over 2-4 weeks typically
5. **EV Certificates**: Get immediate reputation (recommended for commercial use)

## Automated Signing Script

Create `sign_installer.bat`:

```bat
@echo off
set INSTALLER_NAME=Instagram_Auto_Poster_Installer_%date:~10,4%%date:~4,2%%date:~7,2%.exe
set CERT_PATH=path\to\your\certificate.pfx
set CERT_PASS=your-password

echo Signing %INSTALLER_NAME%...

signtool sign ^
  /f "%CERT_PATH%" ^
  /p "%CERT_PASS%" ^
  /t "http://timestamp.digicert.com" ^
  /fd sha256 ^
  /tr "http://timestamp.digicert.com" ^
  /td sha256 ^
  /v ^
  "%INSTALLER_NAME%"

if %errorlevel% equ 0 (
    echo ✅ Signing successful!
    echo Verifying signature...
    signtool verify /pa /v "%INSTALLER_NAME%"
) else (
    echo ❌ Signing failed!
)

pause
```

## Certificate Recommendations

### For Teams/Organizations:
- **DigiCert EV Code Signing** - Immediate SmartScreen reputation
- **3-year certificates** - Better value for ongoing projects

### For Individual Developers:
- **Sectigo/Comodo Standard** - Good balance of cost and trust
- **1-year certificate** - Lower initial investment

### For Open Source Projects:
- Consider **GitHub Sponsors** for certificate funding
- Some CAs offer discounts for open source projects

## Troubleshooting

### Common Issues:

**"SignTool Error: No certificates were found that met all the given criteria"**
- Certificate not in the correct store
- Wrong certificate subject name
- Certificate expired

**"The specified timestamp server either could not be reached or returned an invalid response"**
- Try different timestamp servers:
  - `http://timestamp.digicert.com`
  - `http://time.certum.pl`
  - `http://timestamp.globalsign.com/scripts/timstamp.dll`

**SmartScreen still shows warnings**
- Normal for new certificates
- Build reputation over time
- Consider EV certificate for immediate trust

## Final Notes

- Always test signed installers on clean Windows machines
- Keep certificates secure and backed up
- Monitor certificate expiration dates
- Consider automated signing in CI/CD pipelines

Happy signing! 🔐✨
EOF

print_success "✓ Created signing guide and build scripts"

# Create PowerShell installer builder (alternative to NSIS)
cat > "build_installer.ps1" << 'EOF'
# Instagram Auto Poster - PowerShell Installer Builder
# Alternative to NSIS for creating Windows installers

param(
    [string]$OutputPath = ".",
    [switch]$Sign,
    [string]$CertificatePath,
    [string]$CertificatePassword
)

Write-Host "================================================" -ForegroundColor Cyan
Write-Host "   Instagram Auto Poster - Installer Builder" -ForegroundColor Cyan
Write-Host "================================================" -ForegroundColor Cyan
Write-Host ""

# Check if NSIS is available
$nsisPath = Get-Command "makensis" -ErrorAction SilentlyContinue

if (-not $nsisPath) {
    Write-Host "❌ NSIS not found!" -ForegroundColor Red
    Write-Host ""
    Write-Host "Please install NSIS from: https://nsis.sourceforge.io/Download" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "After installation:" -ForegroundColor White
    Write-Host "1. Add NSIS to your PATH environment variable" -ForegroundColor White
    Write-Host "2. Or run this script from the NSIS installation directory" -ForegroundColor White
    Write-Host ""
    exit 1
}

Write-Host "✅ NSIS found at: $($nsisPath.Source)" -ForegroundColor Green
Write-Host ""

# Build the installer
Write-Host "🔨 Building installer..." -ForegroundColor Blue
try {
    & makensis "installer.nsi"
    
    if ($LASTEXITCODE -eq 0) {
        Write-Host ""
        Write-Host "✅ Installer built successfully!" -ForegroundColor Green
        
        # Find the created installer
        $installerFile = Get-ChildItem -Name "Instagram_Auto_Poster_Installer_*.exe" | Select-Object -First 1
        
        if ($installerFile) {
            Write-Host "📦 Installer created: $installerFile" -ForegroundColor Cyan
            
            # Sign the installer if requested
            if ($Sign -and $CertificatePath) {
                Write-Host ""
                Write-Host "🔐 Digitally signing installer..." -ForegroundColor Blue
                
                # Check if signtool is available
                $signtool = Get-Command "signtool" -ErrorAction SilentlyContinue
                
                if ($signtool) {
                    try {
                        if ($CertificatePassword) {
                            & signtool sign /f $CertificatePath /p $CertificatePassword /t "http://timestamp.digicert.com" /fd sha256 /v $installerFile
                        } else {
                            & signtool sign /f $CertificatePath /t "http://timestamp.digicert.com" /fd sha256 /v $installerFile
                        }
                        
                        if ($LASTEXITCODE -eq 0) {
                            Write-Host "✅ Installer signed successfully!" -ForegroundColor Green
                            
                            # Verify signature
                            Write-Host "🔍 Verifying signature..." -ForegroundColor Blue
                            & signtool verify /pa /v $installerFile
                        } else {
                            Write-Host "❌ Signing failed!" -ForegroundColor Red
                        }
                    } catch {
                        Write-Host "❌ Signing error: $($_.Exception.Message)" -ForegroundColor Red
                    }
                } else {
                    Write-Host "❌ signtool.exe not found! Please install Windows SDK." -ForegroundColor Red
                }
            }
            
            Write-Host ""
            Write-Host "================================================" -ForegroundColor Cyan
            Write-Host "   🎉 Build Complete!" -ForegroundColor Green
            Write-Host "================================================" -ForegroundColor Cyan
            Write-Host ""
            Write-Host "✨ Your professional installer is ready!" -ForegroundColor White
            Write-Host "📁 Location: $(Get-Location)\$installerFile" -ForegroundColor White
            Write-Host ""
            
            if (-not $Sign) {
                Write-Host "💡 To digitally sign your installer:" -ForegroundColor Yellow
                Write-Host "   .\build_installer.ps1 -Sign -CertificatePath 'path\to\cert.pfx' -CertificatePassword 'password'" -ForegroundColor Gray
                Write-Host ""
                Write-Host "📖 See SIGNING_GUIDE.md for detailed instructions" -ForegroundColor Yellow
                Write-Host ""
            }
            
            Write-Host "🚀 Ready for distribution!" -ForegroundColor Green
            
        } else {
            Write-Host "❌ Could not find created installer file!" -ForegroundColor Red
        }
        
    } else {
        Write-Host "❌ Installer build failed!" -ForegroundColor Red
        Write-Host "Please check the errors above." -ForegroundColor Yellow
    }
    
} catch {
    Write-Host "❌ Build error: $($_.Exception.Message)" -ForegroundColor Red
}

Write-Host ""
Write-Host "Press any key to continue..." -ForegroundColor Gray
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
EOF

print_success "✓ Created PowerShell installer builder"

# Create installation instructions
cat > "INSTALLER_INSTRUCTIONS.md" << 'EOF'
# Building Professional Windows Installer

## 🎯 Overview

This creates a professional MSI-style installer that:
- ✅ **Eliminates all security warnings** (when signed)
- ✅ **Looks completely professional**
- ✅ **Installs like commercial software**
- ✅ **Appears in Add/Remove Programs**
- ✅ **Creates proper shortcuts**
- ✅ **Handles Python installation automatically**
- ✅ **Can be digitally signed for trust**

## 🛠️ Prerequisites

### 1. Install NSIS (Free)
Download from: https://nsis.sourceforge.io/Download
- Choose "Latest stable release"
- Install with default options
- Add to PATH environment variable

### 2. Install Windows SDK (Free) - For Signing
Download from: https://developer.microsoft.com/en-us/windows/downloads/windows-sdk/
- Only needed if you want to digitally sign
- Provides `signtool.exe` for signing

## 🚀 Quick Build

### Method 1: Batch Script (Easiest)
```cmd
# Just double-click this file:
build_installer.bat
```

### Method 2: PowerShell (Recommended)
```powershell
# Basic build
.\build_installer.ps1

# Build and sign (with certificate)
.\build_installer.ps1 -Sign -CertificatePath "mycert.pfx" -CertificatePassword "mypassword"
```

### Method 3: Manual NSIS
```cmd
makensis installer.nsi
```

## 📦 What Gets Created

The installer will be named: `Instagram_Auto_Poster_Installer_YYYYMMDD_HHMMSS.exe`

### Installer Features:
- 📋 **Welcome screen** with branding
- 📜 **License agreement** (optional)
- 📁 **Custom install directory** selection
- ☑️ **Component selection**:
  - Core Application (required)
  - Python Runtime (auto-download if needed)
  - Auto-Startup (start with Windows)
  - Desktop Integration (shortcuts & file associations)
- 📊 **Progress bars** during installation
- 🏁 **Finish screen** with launch option

### Post-Installation:
- 🖥️ **Desktop shortcut** created
- 📋 **Start Menu entries** added
- ⚙️ **Add/Remove Programs** entry
- 🔄 **Auto-startup** (if selected)
- 🔗 **File associations** for .iap files

## 🔐 Digital Signing (Professional)

### Why Sign?
- ✅ **No "Unknown Publisher" warnings**
- ✅ **Windows SmartScreen trust**
- ✅ **Corporate environment compatibility**
- ✅ **User confidence**

### Get Certificate:
1. **Purchase** from CA (DigiCert, Sectigo, etc.) - $200-500/year
2. **Self-sign** for testing (will still show warnings)
3. **EV Certificate** for immediate trust (recommended)

### Sign Command:
```cmd
signtool sign /f "certificate.pfx" /p "password" /t "http://timestamp.digicert.com" /fd sha256 "installer.exe"
```

See `SIGNING_GUIDE.md` for detailed instructions.

## 🎨 Customization

### Branding
Edit `installer.nsi` to customize:
- Company name
- Product description
- Icon files
- Welcome images
- License text

### Components
Modify sections in `installer.nsi`:
- Add/remove installation components
- Customize shortcuts
- Change registry entries
- Add file associations

## 🐛 Troubleshooting

### "NSIS not found"
- Install NSIS from official website
- Add NSIS to your PATH
- Or run from NSIS installation directory

### "signtool not found"
- Install Windows SDK
- Add SDK bin folder to PATH
- Or use full path to signtool.exe

### Installer shows warnings
- Normal for unsigned installers
- Get code signing certificate
- Build reputation over time

## 📋 Distribution Checklist

Before distributing your installer:

- [ ] Test on clean Windows machines
- [ ] Verify all shortcuts work
- [ ] Check Add/Remove Programs entry
- [ ] Test uninstaller
- [ ] Scan with antivirus (VirusTotal)
- [ ] Sign with code certificate (recommended)
- [ ] Test on different Windows versions

## 🎉 Benefits Over .bat Files

| Feature | .bat File | Professional Installer |
|---------|-----------|------------------------|
| Security Warnings | ❌ Always shows warnings | ✅ None (when signed) |
| Professional Look | ❌ Terminal window | ✅ Modern GUI |
| Add/Remove Programs | ❌ No entry | ✅ Proper entry |
| Shortcuts | ❌ Manual creation | ✅ Automatic |
| Uninstaller | ❌ No uninstaller | ✅ Proper uninstaller |
| Enterprise Ready | ❌ Blocked by many | ✅ Accepted |
| User Trust | ❌ Looks suspicious | ✅ Looks professional |

Your installer will look and behave exactly like commercial software! 🚀
EOF

print_success "✓ Created installer instructions"