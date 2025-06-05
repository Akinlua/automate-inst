# Instagram Chrome Profile Setup - Windows PowerShell Version
# This script contains everything needed to set up Instagram Chrome automation on Windows
# Compatible with PowerShell 5.1+ and PowerShell Core 7+

param(
    [switch]$SkipChromeCheck,
    [switch]$Quiet
)

# Enable strict mode
Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

# Colors for output
$Colors = @{
    Red = "Red"
    Green = "Green"
    Yellow = "Yellow"
    Blue = "Cyan"
    Purple = "Magenta"
    White = "White"
}

function Write-Log {
    param(
        [string]$Message,
        [string]$Level = "INFO",
        [string]$Color = "White"
    )
    
    $timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    $formattedMessage = "[$Level] $Message"
    
    if (-not $Quiet) {
        Write-Host $formattedMessage -ForegroundColor $Color
    }
}

function Write-LogInfo { param([string]$Message) Write-Log $Message "INFO" $Colors.Blue }
function Write-LogSuccess { param([string]$Message) Write-Log $Message "SUCCESS" $Colors.Green }
function Write-LogWarning { param([string]$Message) Write-Log $Message "WARNING" $Colors.Yellow }
function Write-LogError { param([string]$Message) Write-Log $Message "ERROR" $Colors.Red }
function Write-LogStep { param([string]$Message) Write-Log $Message "STEP" $Colors.Purple }

function Test-Administrator {
    $currentUser = [Security.Principal.WindowsIdentity]::GetCurrent()
    $principal = New-Object Security.Principal.WindowsPrincipal($currentUser)
    return $principal.IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)
}

function Get-PackageManager {
    $managers = @()
    
    # Check for winget
    try {
        winget --version | Out-Null
        $managers += "winget"
    } catch { }
    
    # Check for chocolatey
    try {
        choco --version | Out-Null
        $managers += "chocolatey"
    } catch { }
    
    # Check for scoop
    try {
        scoop --version | Out-Null
        $managers += "scoop"
    } catch { }
    
    return $managers
}

function Install-Python {
    Write-LogStep "Checking Python installation..."
    
    # Check if Python 3.13 is already installed
    $pythonCommands = @("python3.13", "python3", "python", "py")
    $pythonCmd = $null
    
    foreach ($cmd in $pythonCommands) {
        try {
            $version = & $cmd --version 2>&1
            if ($version -match "Python 3\.13") {
                Write-LogSuccess "Python 3.13 already installed: $version"
                return $cmd
            }
        } catch { }
    }
    
    Write-LogInfo "Python 3.13 not found. Installing..."
    
    $packageManagers = Get-PackageManager
    
    if ($packageManagers -contains "winget") {
        Write-LogInfo "Installing Python via winget..."
        try {
            winget install Python.Python.3.13 --accept-source-agreements --accept-package-agreements
            RefreshEnv
        } catch {
            Write-LogWarning "Winget installation failed: $($_.Exception.Message)"
        }
    } elseif ($packageManagers -contains "chocolatey") {
        Write-LogInfo "Installing Python via Chocolatey..."
        try {
            choco install python --version=3.13.0 -y
            RefreshEnv
        } catch {
            Write-LogWarning "Chocolatey installation failed: $($_.Exception.Message)"
        }
    } elseif ($packageManagers -contains "scoop") {
        Write-LogInfo "Installing Python via Scoop..."
        try {
            scoop install python
            RefreshEnv
        } catch {
            Write-LogWarning "Scoop installation failed: $($_.Exception.Message)"
        }
    } else {
        Write-LogError "No package manager found. Please install Python 3.13 manually:"
        Write-LogInfo "1. Go to https://www.python.org/downloads/release/python-3133/"
        Write-LogInfo "2. Download 'Windows installer (64-bit)'"
        Write-LogInfo "3. Run installer and CHECK 'Add Python to PATH'"
        Write-LogInfo "4. Restart PowerShell and run this script again"
        Read-Host "Press Enter after installing Python 3.13"
        exit 1
    }
    
    # Try to find Python again after installation
    foreach ($cmd in $pythonCommands) {
        try {
            $version = & $cmd --version 2>&1
            if ($version -match "Python 3\.13") {
                Write-LogSuccess "Python 3.13 installed: $version"
                return $cmd
            }
        } catch { }
    }
    
    Write-LogError "Python 3.13 installation failed or not found in PATH"
    exit 1
}

function RefreshEnv {
    # Refresh environment variables
    $env:Path = [System.Environment]::GetEnvironmentVariable("Path","Machine") + ";" + [System.Environment]::GetEnvironmentVariable("Path","User")
}

function Install-PythonDependencies {
    param([string]$PythonCmd)
    
    Write-LogStep "Setting up pip and dependencies..."
    
    # Ensure pip is available and upgraded
    try {
        & $PythonCmd -m pip --version | Out-Null
    } catch {
        Write-LogInfo "Installing pip..."
        $pipInstaller = "$env:TEMP\get-pip.py"
        Invoke-WebRequest -Uri "https://bootstrap.pypa.io/get-pip.py" -OutFile $pipInstaller
        & $PythonCmd $pipInstaller
        Remove-Item $pipInstaller
    }
    
    Write-LogInfo "Upgrading pip and setuptools..."
    & $PythonCmd -m pip install --upgrade pip setuptools wheel
    
    Write-LogInfo "Installing Python dependencies..."
    $dependencies = @(
        "selenium>=4.15.0",
        "python-dotenv>=1.0.0", 
        "urllib3>=2.0.0",
        "undetected-chromedriver>=3.5.0"
    )
    
    & $PythonCmd -m pip install $dependencies
    Write-LogSuccess "Python dependencies installed successfully"
}

function Test-ChromeInstallation {
    if ($SkipChromeCheck) {
        Write-LogInfo "Skipping Chrome check as requested"
        return
    }
    
    Write-LogStep "Checking Chrome installation..."
    
    $chromePaths = @(
        "${env:ProgramFiles}\Google\Chrome\Application\chrome.exe",
        "${env:ProgramFiles(x86)}\Google\Chrome\Application\chrome.exe"
    )
    
    $chromeFound = $false
    $chromePath = $null
    
    foreach ($path in $chromePaths) {
        if (Test-Path $path) {
            $chromeFound = $true
            $chromePath = $path
            break
        }
    }
    
    if (-not $chromeFound) {
        # Try to find in PATH
        try {
            $chromePath = (Get-Command chrome.exe -ErrorAction Stop).Source
            $chromeFound = $true
        } catch { }
    }
    
    if (-not $chromeFound) {
        Write-LogWarning "Chrome not found. Please install Google Chrome:"
        Write-LogInfo "Download from: https://www.google.com/chrome/"
        
        $packageManagers = Get-PackageManager
        if ($packageManagers -contains "winget") {
            Write-LogInfo "Or run: winget install Google.Chrome"
        } elseif ($packageManagers -contains "chocolatey") {
            Write-LogInfo "Or run: choco install googlechrome"
        } elseif ($packageManagers -contains "scoop") {
            Write-LogInfo "Or run: scoop bucket add extras && scoop install googlechrome"
        }
        
        $continue = Read-Host "Continue without Chrome verification? (y/N)"
        if ($continue -ne "y" -and $continue -ne "Y") {
            Write-LogError "Chrome is required. Please install Chrome and run this script again."
            exit 1
        }
        return
    }
    
    Write-LogSuccess "Chrome found: $chromePath"
    
    # Test Chrome version
    try {
        $version = & $chromePath --version 2>&1
        Write-LogSuccess "Chrome version: $version"
    } catch {
        Write-LogWarning "Could not get Chrome version, but executable found"
    }
}

function New-EnvFile {
    Write-LogStep "Setting up .env file..."
    
    if (-not (Test-Path ".env")) {
        Write-LogInfo "Creating .env file..."
        $envContent = @"
# Instagram Chrome Profile Configuration
# This file will be updated automatically by the setup script

# Chrome Profile Path (will be set by setup_chromev1.py)
CHROME_PROFILE_PATH=

# Optional: Chrome User Data Directory and Profile Name (V2 method)
# CHROME_USER_DATA_DIR=
# CHROME_PROFILE_NAME=

# Optional: ChromeDriver path (leave empty to use system PATH)
CHROMEDRIVER_PATH=

# Logging level
LOG_LEVEL=INFO
"@
        $envContent | Out-File -FilePath ".env" -Encoding UTF8
        Write-LogSuccess ".env file created"
    } else {
        Write-LogInfo ".env file already exists, keeping current configuration"
    }
}

function New-PythonSetupScript {
    Write-LogStep "Creating Chrome setup script..."
    
    $pythonScript = @'
#!/usr/bin/env python3
import os
import sys
import time
import logging
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
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

class ChromeProfileSetup:
    def __init__(self):
        self.driver = None
        
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
        
        # Keep browser open after script ends
        chrome_options.add_experimental_option("detach", True)

        prefs = {
            "download.prompt_for_download": False,
            "download.directory_upgrade": True,
            "safebrowsing.enabled": False,
            "plugins.always_open_pdf_externally": True,
            "browser.download.folderList": 2,
            "browser.helperApps.neverAsk.saveToDisk": "application/pdf,application/x-pdf,application/octet-stream,text/plain,text/html",
            "browser.download.manager.showWhenStarting": False
        }
        chrome_options.add_experimental_option("prefs", prefs)
        
        try:
            # Disable SSL warnings
            urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

            # Create unverified SSL context
            ssl._create_default_https_context = ssl._create_unverified_context

            options = uc.ChromeOptions()
            options.add_argument('--no-sandbox')
            options.add_argument('--disable-dev-shm-usage')
            options.add_argument('--disable-blink-features=AutomationControlled')

            options.add_argument(f"--user-data-dir={CUSTOM_PROFILE_PATH}")
            logger.info(f"Using Chrome profile: {CUSTOM_PROFILE_PATH}")

            options.add_argument('--ignore-ssl-errors')
            options.add_argument('--ignore-certificate-errors')
            options.add_argument('--allow-running-insecure-content')

            self.driver = uc.Chrome(options=options)

            logger.info("Chrome driver setup successful with custom profile")
            return True
        except Exception as e:
            logger.error(f"Failed to setup Chrome driver: {e}")
            return False
    
    def navigate_to_instagram(self):
        """Navigate to Instagram for manual login"""
        try:
            self.driver.get("https://www.instagram.com/")
            logger.info("Navigated to Instagram - please log in manually")
            return True
        except Exception as e:
            logger.error(f"Failed to navigate to Instagram: {e}")
            return False
    
    def run_setup(self):
        """Run the Chrome profile setup"""
        logger.info("Starting Chrome Profile Setup for Instagram")
        logger.info("="*50)
        
        if not self.setup_chrome_with_custom_profile():
            logger.error("Failed to setup Chrome driver. Exiting...")
            return
            
        if not self.navigate_to_instagram():
            logger.error("Failed to navigate to Instagram. Exiting...")
            return
        
        logger.info("Chrome browser is now open at Instagram.com")
        logger.info("Please complete the following steps:")
        logger.info("1. Log in to your Instagram account")
        logger.info("2. Complete any two-factor authentication if required")
        logger.info("3. Make sure you see your Instagram home feed")
        logger.info("4. Keep the browser open - DO NOT close it")
        logger.info("")
        logger.info("The browser will stay open with 'detach' mode enabled.")
        logger.info("Your login session will be saved to the custom profile directory.")
        logger.info("")
        logger.info(f"Profile will be saved to: {CUSTOM_PROFILE_PATH}")
        logger.info("")
        logger.info("After logging in successfully, you can close this terminal.")
        logger.info("="*50)
        
        # Wait for a long time to allow manual login
        try:
            logger.info("Waiting 30 minutes for you to complete the login process...")
            logger.info("You can close this terminal once you've successfully logged in.")
            time.sleep(1800)  # Wait 30 minutes
        except KeyboardInterrupt:
            logger.info("Setup interrupted by user. Profile should be saved if login was completed.")
        except Exception as e:
            logger.error(f"Error during wait: {e}")
        
        # Update .env file with profile path
        self.update_env_file()
        
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
'@
    
    $pythonScript | Out-File -FilePath "setup_chromev1.py" -Encoding UTF8
    Write-LogSuccess "Chrome setup script created"
}

function Start-ChromeSetup {
    param([string]$PythonCmd)
    
    Write-LogStep "Running Chrome profile setup..."
    Write-Host ""
    Write-LogInfo "Starting Chrome setup for Instagram login..."
    Write-LogInfo "This will:"
    Write-LogInfo "  1. Open Chrome browser"
    Write-LogInfo "  2. Navigate to Instagram"
    Write-LogInfo "  3. Wait for you to log in manually"
    Write-LogInfo "  4. Save your login session to a profile"
    Write-Host ""
    Write-LogWarning "Important: Do NOT close the Chrome window that opens!"
    Write-LogWarning "Wait for the login process to complete before closing anything."
    Write-Host ""
    
    Read-Host "Press Enter to continue with Chrome setup"
    
    Write-LogInfo "Launching Chrome setup script..."
    & $PythonCmd setup_chromev1.py
}

function Remove-TemporaryFiles {
    Write-LogStep "Cleaning up temporary files..."
    
    if (Test-Path "setup_chromev1.py") {
        $cleanup = Read-Host "Remove temporary Python script? (y/N)"
        if ($cleanup -eq "y" -or $cleanup -eq "Y") {
            Remove-Item "setup_chromev1.py"
            Write-LogInfo "Temporary Python script removed"
        } else {
            Write-LogInfo "Python script kept for future use"
        }
    }
}

function Show-Summary {
    param([string]$PythonCmd)
    
    Write-Host ""
    Write-LogSuccess "🎉 Installation and setup completed successfully!"
    Write-Host ""
    Write-Host "Summary:" -ForegroundColor Cyan
    Write-Host "  • Operating System: Windows $([System.Environment]::OSVersion.Version)" -ForegroundColor Blue
    Write-Host "  • Python Version: $(& $PythonCmd --version)" -ForegroundColor Blue
    Write-Host "  • Chrome Profile: Configured" -ForegroundColor Blue
    Write-Host "  • Dependencies: Installed" -ForegroundColor Blue
    Write-Host ""
    Write-Host "Next Steps:" -ForegroundColor Cyan
    Write-Host "  • Your Instagram login session is saved"
    Write-Host "  • You can now run other Instagram automation scripts"
    Write-Host "  • The Chrome profile will be reused for future sessions"
    Write-Host ""
    Write-Host "Files Created:" -ForegroundColor Cyan
    Write-Host "  • chrome_profile_instagram\ - Chrome profile directory" -ForegroundColor Blue
    Write-Host "  • .env - Configuration file" -ForegroundColor Blue
    Write-Host "  • chrome_setup.log - Setup log file" -ForegroundColor Blue
    if (Test-Path "setup_chromev1.py") {
        Write-Host "  • setup_chromev1.py - Chrome setup script (temporary)" -ForegroundColor Blue
    }
    Write-Host ""
}

# Main execution
function Main {
    Write-Host ""
    Write-Host "╔════════════════════════════════════════════════════════════╗" -ForegroundColor Magenta
    Write-Host "║             Instagram Chrome Profile Setup                 ║" -ForegroundColor Magenta
    Write-Host "║                Windows PowerShell Installer                ║" -ForegroundColor Magenta
    Write-Host "║                                                            ║" -ForegroundColor Magenta
    Write-Host "║  This script contains everything needed for setup!        ║" -ForegroundColor Magenta
    Write-Host "║  Compatible with PowerShell 5.1+ and PowerShell Core 7+   ║" -ForegroundColor Magenta
    Write-Host "╚════════════════════════════════════════════════════════════╝" -ForegroundColor Magenta
    Write-Host ""
    
    # Check if running as administrator
    if (Test-Administrator) {
        Write-LogWarning "Running as Administrator. This is not recommended unless necessary."
        $continue = Read-Host "Continue anyway? (y/N)"
        if ($continue -ne "y" -and $continue -ne "Y") {
            Write-LogError "Please run as a regular user."
            exit 1
        }
    }
    
    # Detect Windows version
    $osVersion = [System.Environment]::OSVersion.Version
    Write-LogInfo "Detected Windows version: $osVersion"
    
    try {
        # Install Python
        $pythonCmd = Install-Python
        
        # Install Python dependencies
        Install-PythonDependencies -PythonCmd $pythonCmd
        
        # Check Chrome installation
        Test-ChromeInstallation
        
        # Create .env file
        New-EnvFile
        
        # Create Python setup script
        New-PythonSetupScript
        
        # Run Chrome setup
        Start-ChromeSetup -PythonCmd $pythonCmd
        
        # Cleanup and summary
        Remove-TemporaryFiles
        Show-Summary -PythonCmd $pythonCmd
        
    } catch {
        Write-LogError "Script failed: $($_.Exception.Message)"
        Write-LogError "Stack trace: $($_.ScriptStackTrace)"
        exit 1
    }
}

# Run main function
Main 