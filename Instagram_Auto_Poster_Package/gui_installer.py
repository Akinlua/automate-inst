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
