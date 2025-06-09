#!/bin/bash

# Instagram Auto Poster - Setup and Launch Script for Linux/macOS
# This script will install all dependencies and start the application

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Print colored output
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

print_header() {
    echo ""
    echo "=============================================="
    echo "   Instagram Auto Poster - Setup & Launch"
    echo "=============================================="
    echo ""
    echo "This script will:"
    echo "1. Check and install Python if needed"
    echo "2. Create virtual environment"
    echo "3. Install all dependencies"
    echo "4. Create necessary folders"
    echo "5. Start the web application"
    echo ""
}

# Check if running on macOS or Linux
detect_os() {
    if [[ "$OSTYPE" == "darwin"* ]]; then
        OS="macos"
        print_status "Detected macOS"
    elif [[ "$OSTYPE" == "linux-gnu"* ]]; then
        OS="linux"
        print_status "Detected Linux"
    else
        OS="unknown"
        print_warning "Unknown OS type: $OSTYPE"
    fi
}

# Check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Install Python on macOS using Homebrew
install_python_macos() {
    print_status "Installing Python on macOS..."
    
    if ! command_exists brew; then
        print_status "Installing Homebrew first..."
        /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
        
        # Add Homebrew to PATH
        if [[ -f "/opt/homebrew/bin/brew" ]]; then
            echo 'export PATH="/opt/homebrew/bin:$PATH"' >> ~/.zshrc
            export PATH="/opt/homebrew/bin:$PATH"
        else
            echo 'export PATH="/usr/local/bin:$PATH"' >> ~/.zshrc
            export PATH="/usr/local/bin:$PATH"
        fi
    fi
    
    brew install python
    print_success "Python installed successfully!"
}

# Install Python on Linux
install_python_linux() {
    print_status "Installing Python on Linux..."
    
    if command_exists apt-get; then
        # Ubuntu/Debian
        sudo apt-get update
        sudo apt-get install -y python3 python3-pip python3-venv python3-dev
    elif command_exists yum; then
        # CentOS/RHEL
        sudo yum install -y python3 python3-pip python3-venv python3-devel
    elif command_exists dnf; then
        # Fedora
        sudo dnf install -y python3 python3-pip python3-venv python3-devel
    elif command_exists pacman; then
        # Arch Linux
        sudo pacman -S --noconfirm python python-pip
    else
        print_error "Unsupported Linux distribution. Please install Python 3.8+ manually."
        exit 1
    fi
    
    print_success "Python installed successfully!"
}

# Check and install Python
check_python() {
    print_status "Checking Python installation..."
    
    PYTHON_CMD=""
    
    # Try different Python commands (including specific versions)
    for cmd in python3.13 python3.12 python3.11 python3.10 python3.9 python3.8 python3 python; do
        if command_exists $cmd; then
            # Use awk for better cross-platform compatibility
            VERSION=$($cmd --version 2>&1 | awk '{print $2}' | cut -d. -f1,2)
            
            if [[ -n "$VERSION" ]]; then
                MAJOR=$(echo $VERSION | cut -d. -f1)
                MINOR=$(echo $VERSION | cut -d. -f2)
                
                if [[ $MAJOR -ge 3 ]] && [[ $MINOR -ge 8 ]]; then
                    PYTHON_CMD=$cmd
                    print_success "Found Python $VERSION using command: $cmd"
                    break
                fi
            fi
        fi
    done
    
    if [[ -z "$PYTHON_CMD" ]]; then
        print_warning "Python 3.8+ not found. Installing..."
        
        if [[ "$OS" == "macos" ]]; then
            install_python_macos
        elif [[ "$OS" == "linux" ]]; then
            install_python_linux
        else
            print_error "Please install Python 3.8+ manually from https://www.python.org/downloads/"
            exit 1
        fi
        
        # Re-check after installation
        for cmd in python3.13 python3.12 python3.11 python3.10 python3.9 python3.8 python3 python; do
            if command_exists $cmd; then
                # Use awk for better cross-platform compatibility
                VERSION=$($cmd --version 2>&1 | awk '{print $2}' | cut -d. -f1,2)
                
                if [[ -n "$VERSION" ]]; then
                    MAJOR=$(echo $VERSION | cut -d. -f1)
                    MINOR=$(echo $VERSION | cut -d. -f2)
                    
                    if [[ $MAJOR -ge 3 ]] && [[ $MINOR -ge 8 ]]; then
                        PYTHON_CMD=$cmd
                        break
                    fi
                fi
            fi
        done
        
        if [[ -z "$PYTHON_CMD" ]]; then
            print_error "Failed to install Python. Please install manually."
            exit 1
        fi
    fi
}

# Check and install pip
check_pip() {
    print_status "Checking pip installation..."
    
    if ! $PYTHON_CMD -m pip --version >/dev/null 2>&1; then
        print_status "Installing pip..."
        $PYTHON_CMD -m ensurepip --upgrade || {
            print_warning "ensurepip failed, trying alternative method..."
            if command_exists curl; then
                curl https://bootstrap.pypa.io/get-pip.py -o get-pip.py
                $PYTHON_CMD get-pip.py
                rm get-pip.py
            else
                print_error "Failed to install pip. Please install pip manually."
                exit 1
            fi
        }
    fi
    
    print_success "pip is available"
}

# Create virtual environment
setup_venv() {
    print_status "Setting up virtual environment..."
    
    if [[ ! -d "venv" ]]; then
        print_status "Creating virtual environment..."
        $PYTHON_CMD -m venv venv
        print_success "Virtual environment created"
    else
        print_status "Virtual environment already exists"
    fi
    
    # Activate virtual environment
    print_status "Activating virtual environment..."
    source venv/bin/activate
    
    # Upgrade pip in virtual environment
    print_status "Upgrading pip in virtual environment..."
    python -m pip install --upgrade pip
}

# Install dependencies
install_dependencies() {
    print_status "Installing dependencies..."
    print_status "This may take a few minutes..."
    
    if [[ -f "requirements.txt" ]]; then
        python -m pip install -r requirements.txt || {
            print_warning "requirements.txt installation failed, trying alternative..."
            python -m pip install selenium Pillow python-dotenv schedule openai requests flask werkzeug pytz psutil undetected-chromedriver setuptools selenium-driverless
        }
    else
        print_status "Installing dependencies manually..."
        python -m pip install selenium Pillow python-dotenv schedule openai requests flask werkzeug pytz psutil undetected-chromedriver setuptools selenium-driverless
    fi
    
    print_success "Dependencies installed successfully!"
}

# Create necessary directories and files
setup_files() {
    print_status "Creating necessary directories..."
    
    mkdir -p content static templates
    
    # Create .env file if it doesn't exist
    if [[ ! -f ".env" ]]; then
        print_status "Creating .env file..."
        if [[ -f ".env.example" ]]; then
            cp .env.example .env
        else
            cat > .env << EOF
# Instagram Auto Poster Configuration
CONTENT_DIR=content
USE_CHATGPT=false
OPENAI_API_KEY=
CHROME_PROFILE_PATH=
CHROME_USER_DATA_DIR=
CHROME_PROFILE_NAME=InstagramBot
EOF
        fi
        print_success ".env file created"
    fi
}

# Check if Chrome is installed
check_chrome() {
    print_status "Checking Google Chrome installation..."
    
    CHROME_FOUND=false
    
    # Check common Chrome installation paths
    if [[ "$OS" == "macos" ]]; then
        if [[ -d "/Applications/Google Chrome.app" ]]; then
            CHROME_FOUND=true
        fi
    elif [[ "$OS" == "linux" ]]; then
        if command_exists google-chrome || command_exists google-chrome-stable || command_exists chromium-browser; then
            CHROME_FOUND=true
        fi
    fi
    
    if [[ "$CHROME_FOUND" == true ]]; then
        print_success "Google Chrome found!"
    else
        print_warning "Google Chrome not detected!"
        print_warning "Please install Google Chrome from: https://www.google.com/chrome/"
        print_warning "You can continue, but Chrome setup may fail later."
        echo ""
        read -p "Press Enter to continue anyway..."
    fi
}

# Start the application
start_application() {
    print_success ""
    print_success "=============================================="
    print_success "   Setup Complete!"
    print_success "=============================================="
    print_success ""
    print_success "The web application will now start..."
    print_success ""
    print_success "Once started, open your browser and go to:"
    print_success "http://localhost:5003"
    print_success ""
    print_success "To stop the application, press Ctrl+C in this terminal."
    print_success ""
    read -p "Press Enter to start the application..."
    
    print_status ""
    print_status "Starting Instagram Auto Poster..."
    print_status ""
    
    # Start the application
    python app.py
}

# Cleanup function
cleanup() {
    print_status ""
    print_status "Cleaning up..."
    deactivate 2>/dev/null || true
}

# Set up trap for cleanup
trap cleanup EXIT

# Main execution
main() {
    print_header
    
    detect_os
    check_python
    check_pip
    setup_venv
    install_dependencies
    setup_files
    check_chrome
    start_application
}

# Run main function
main "$@" 