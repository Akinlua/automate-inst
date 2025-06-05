#!/bin/bash

# Instagram Chrome Profile Setup - Universal Installer
# This script detects your system, installs all dependencies, and sets up Chrome profile for Instagram
# Compatible with: macOS, Ubuntu/Debian, CentOS/RHEL, Fedora, Arch Linux

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Logging functions
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

log_step() {
    echo -e "${PURPLE}[STEP]${NC} $1"
}

# System detection
detect_system() {
    log_step "Detecting operating system..."
    
    if [[ "$OSTYPE" == "darwin"* ]]; then
        OS="macos"
        DISTRO="macos"
        log_info "Detected: macOS"
    elif [[ -f /etc/os-release ]]; then
        source /etc/os-release
        OS="linux"
        DISTRO="${ID}"
        log_info "Detected: ${NAME} (${ID})"
    else
        log_error "Unsupported operating system"
        exit 1
    fi
}

# Check if running as root (not recommended except for Docker)
check_user() {
    if [[ $EUID -eq 0 ]]; then
        log_warning "Running as root. This is not recommended unless you're in a Docker container."
        read -p "Continue anyway? (y/N): " -n 1 -r
        echo
        if [[ ! $REPLY =~ ^[Yy]$ ]]; then
            log_error "Exiting. Please run as a regular user."
            exit 1
        fi
    fi
}

# Install system dependencies based on OS
install_system_dependencies() {
    log_step "Installing system dependencies..."
    
    case $OS in
        "macos")
            install_macos_dependencies
            ;;
        "linux")
            case $DISTRO in
                "ubuntu"|"debian")
                    install_debian_dependencies
                    ;;
                "centos"|"rhel"|"rocky"|"almalinux")
                    install_rhel_dependencies
                    ;;
                "fedora")
                    install_fedora_dependencies
                    ;;
                "arch"|"manjaro")
                    install_arch_dependencies
                    ;;
                *)
                    log_warning "Unsupported Linux distribution: $DISTRO"
                    log_info "Trying generic Linux installation..."
                    install_generic_linux_dependencies
                    ;;
            esac
            ;;
        *)
            log_error "Unsupported OS: $OS"
            exit 1
            ;;
    esac
}

install_macos_dependencies() {
    log_info "Installing macOS dependencies..."
    
    # Install Homebrew if not present
    if ! command -v brew &> /dev/null; then
        log_info "Installing Homebrew..."
        /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
        
        # Add Homebrew to PATH for current session
        if [[ -f /opt/homebrew/bin/brew ]]; then
            export PATH="/opt/homebrew/bin:$PATH"
        else
            export PATH="/usr/local/bin:$PATH"
        fi
    fi
    
    # Update Homebrew
    brew update
    
    # Install Python 3.13 if not present or wrong version
    install_python_macos
    
    # Install wget and curl (usually present but just in case)
    brew install wget curl || true
}

install_debian_dependencies() {
    log_info "Installing Debian/Ubuntu dependencies..."
    
    # Update package list
    sudo apt-get update
    
    # Install essential packages
    sudo apt-get install -y \
        wget \
        curl \
        software-properties-common \
        build-essential \
        libssl-dev \
        libffi-dev \
        libbz2-dev \
        libreadline-dev \
        libsqlite3-dev \
        libncurses5-dev \
        libncursesw5-dev \
        xz-utils \
        tk-dev \
        libxml2-dev \
        libxmlsec1-dev \
        liblzma-dev \
        git \
        unzip
    
    # Install Python 3.13
    install_python_debian
}

install_rhel_dependencies() {
    log_info "Installing RHEL/CentOS dependencies..."
    
    # Enable EPEL repository
    if command -v dnf &> /dev/null; then
        sudo dnf install -y epel-release
        sudo dnf groupinstall -y "Development Tools"
        sudo dnf install -y \
            wget \
            curl \
            openssl-devel \
            libffi-devel \
            bzip2-devel \
            readline-devel \
            sqlite-devel \
            ncurses-devel \
            xz-devel \
            tk-devel \
            libxml2-devel \
            xmlsec1-devel \
            git \
            unzip
    else
        sudo yum install -y epel-release
        sudo yum groupinstall -y "Development Tools"
        sudo yum install -y \
            wget \
            curl \
            openssl-devel \
            libffi-devel \
            bzip2-devel \
            readline-devel \
            sqlite-devel \
            ncurses-devel \
            xz-devel \
            tk-devel \
            libxml2-devel \
            xmlsec1-devel \
            git \
            unzip
    fi
    
    install_python_rhel
}

install_fedora_dependencies() {
    log_info "Installing Fedora dependencies..."
    
    sudo dnf groupinstall -y "Development Tools"
    sudo dnf install -y \
        wget \
        curl \
        openssl-devel \
        libffi-devel \
        bzip2-devel \
        readline-devel \
        sqlite-devel \
        ncurses-devel \
        xz-devel \
        tk-devel \
        libxml2-devel \
        xmlsec1-devel \
        git \
        unzip
    
    install_python_fedora
}

install_arch_dependencies() {
    log_info "Installing Arch Linux dependencies..."
    
    sudo pacman -Syu --noconfirm
    sudo pacman -S --noconfirm \
        base-devel \
        wget \
        curl \
        openssl \
        libffi \
        bzip2 \
        readline \
        sqlite \
        ncurses \
        xz \
        tk \
        libxml2 \
        xmlsec \
        git \
        unzip
    
    install_python_arch
}

install_generic_linux_dependencies() {
    log_warning "Attempting generic Linux installation..."
    # Try to install Python 3.13 from source as fallback
    install_python_from_source
}

# Python installation functions for different systems
install_python_macos() {
    local current_python=""
    if command -v python3.13 &> /dev/null; then
        current_python=$(python3.13 --version 2>&1 | grep "Python 3.13")
        if [[ -n "$current_python" ]]; then
            log_success "Python 3.13 already installed: $current_python"
            return
        fi
    fi
    
    log_info "Installing Python 3.13 via Homebrew..."
    brew install python@3.13 || {
        log_warning "Homebrew Python 3.13 not available, trying pyenv..."
        install_python_via_pyenv "3.13.3"
    }
    
    # Create symlink if needed
    if [[ ! -f /usr/local/bin/python3.13 ]] && [[ ! -f /opt/homebrew/bin/python3.13 ]]; then
        # Try to find where Homebrew installed it
        if [[ -f /opt/homebrew/bin/python3 ]]; then
            sudo ln -sf /opt/homebrew/bin/python3 /usr/local/bin/python3.13 2>/dev/null || true
        fi
    fi
}

install_python_debian() {
    local current_python=""
    if command -v python3.13 &> /dev/null; then
        current_python=$(python3.13 --version 2>&1 | grep "Python 3.13")
        if [[ -n "$current_python" ]]; then
            log_success "Python 3.13 already installed: $current_python"
            return
        fi
    fi
    
    log_info "Installing Python 3.13..."
    
    # Try deadsnakes PPA for Ubuntu
    if command -v add-apt-repository &> /dev/null; then
        sudo add-apt-repository -y ppa:deadsnakes/ppa || true
        sudo apt-get update
        sudo apt-get install -y python3.13 python3.13-dev python3.13-venv python3.13-distutils || {
            log_warning "PPA installation failed, trying pyenv..."
            install_python_via_pyenv "3.13.3"
        }
    else
        install_python_via_pyenv "3.13.3"
    fi
}

install_python_rhel() {
    install_python_via_pyenv "3.13.3"
}

install_python_fedora() {
    # Fedora usually has recent Python versions
    sudo dnf install -y python3.13 python3.13-devel python3.13-pip || {
        log_warning "System Python 3.13 not available, trying pyenv..."
        install_python_via_pyenv "3.13.3"
    }
}

install_python_arch() {
    # Try to install from official repos first
    sudo pacman -S --noconfirm python || true
    
    # Check if it's 3.13+
    if command -v python3 &> /dev/null; then
        local version=$(python3 --version 2>&1 | grep -o "3\.[0-9]\+")
        if [[ "$version" == "3.13" ]] || [[ "$version" > "3.13" ]]; then
            log_success "Python $version installed"
            return
        fi
    fi
    
    log_info "Installing Python 3.13 via pyenv..."
    install_python_via_pyenv "3.13.3"
}

install_python_via_pyenv() {
    local python_version="$1"
    
    log_info "Installing Python $python_version via pyenv..."
    
    # Install pyenv if not present
    if ! command -v pyenv &> /dev/null; then
        log_info "Installing pyenv..."
        curl https://pyenv.run | bash
        
        # Add pyenv to PATH
        export PYENV_ROOT="$HOME/.pyenv"
        export PATH="$PYENV_ROOT/bin:$PATH"
        eval "$(pyenv init -)"
        eval "$(pyenv virtualenv-init -)"
        
        # Add to shell profile
        local shell_profile=""
        if [[ -n "$ZSH_VERSION" ]]; then
            shell_profile="$HOME/.zshrc"
        elif [[ -n "$BASH_VERSION" ]]; then
            shell_profile="$HOME/.bashrc"
        fi
        
        if [[ -n "$shell_profile" ]] && [[ -f "$shell_profile" ]]; then
            echo 'export PYENV_ROOT="$HOME/.pyenv"' >> "$shell_profile"
            echo 'export PATH="$PYENV_ROOT/bin:$PATH"' >> "$shell_profile"
            echo 'eval "$(pyenv init -)"' >> "$shell_profile"
            echo 'eval "$(pyenv virtualenv-init -)"' >> "$shell_profile"
        fi
    fi
    
    # Install Python version
    pyenv install -s "$python_version"
    pyenv global "$python_version"
    
    # Create symlink for python3.13
    local pyenv_python_path="$HOME/.pyenv/versions/$python_version/bin/python"
    if [[ -f "$pyenv_python_path" ]]; then
        sudo ln -sf "$pyenv_python_path" /usr/local/bin/python3.13 2>/dev/null || {
            # If sudo fails, create local bin directory
            mkdir -p "$HOME/.local/bin"
            ln -sf "$pyenv_python_path" "$HOME/.local/bin/python3.13"
            export PATH="$HOME/.local/bin:$PATH"
        }
    fi
}

install_python_from_source() {
    local python_version="3.13.3"
    log_info "Installing Python $python_version from source..."
    
    # Download and compile Python
    cd /tmp
    wget "https://www.python.org/ftp/python/$python_version/Python-$python_version.tgz"
    tar -xzf "Python-$python_version.tgz"
    cd "Python-$python_version"
    
    ./configure --enable-optimizations --with-ensurepip=install
    make -j$(nproc 2>/dev/null || sysctl -n hw.ncpu 2>/dev/null || echo 2)
    sudo make altinstall
    
    # Cleanup
    cd /
    rm -rf "/tmp/Python-$python_version"*
}

# Verify Python installation
verify_python() {
    log_step "Verifying Python installation..."
    
    local python_cmd=""
    for cmd in python3.13 python3 python; do
        if command -v "$cmd" &> /dev/null; then
            local version=$($cmd --version 2>&1)
            if [[ "$version" == *"3.13"* ]]; then
                python_cmd="$cmd"
                break
            fi
        fi
    done
    
    if [[ -z "$python_cmd" ]]; then
        log_error "Python 3.13 not found. Installation may have failed."
        exit 1
    fi
    
    log_success "Python verified: $($python_cmd --version)"
    export PYTHON_CMD="$python_cmd"
}

# Install pip and upgrade it
setup_pip() {
    log_step "Setting up pip..."
    
    # Ensure pip is available
    if ! $PYTHON_CMD -m pip --version &> /dev/null; then
        log_info "Installing pip..."
        curl https://bootstrap.pypa.io/get-pip.py -o get-pip.py
        $PYTHON_CMD get-pip.py
        rm get-pip.py
    fi
    
    # Upgrade pip and setuptools
    log_info "Upgrading pip and setuptools..."
    $PYTHON_CMD -m pip install --upgrade pip setuptools wheel
    
    log_success "Pip setup complete: $($PYTHON_CMD -m pip --version)"
}

# Install Python dependencies
install_python_dependencies() {
    log_step "Installing Python dependencies..."
    
    local requirements=(
        "selenium>=4.15.0"
        "python-dotenv>=1.0.0"
        "urllib3>=2.0.0"
        "undetected-chromedriver>=3.5.0"
    )
    
    log_info "Installing packages: ${requirements[*]}"
    $PYTHON_CMD -m pip install "${requirements[@]}"
    
    log_success "Python dependencies installed successfully"
}

# Check Chrome installation and compatibility
check_chrome_installation() {
    log_step "Checking Chrome installation..."
    
    local chrome_paths=()
    local chrome_cmd=""
    
    case $OS in
        "macos")
            chrome_paths=(
                "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
                "/Applications/Chromium.app/Contents/MacOS/Chromium"
            )
            ;;
        "linux")
            chrome_paths=(
                "google-chrome"
                "google-chrome-stable"
                "chromium-browser"
                "chromium"
                "/usr/bin/google-chrome"
                "/usr/bin/chromium-browser"
                "/opt/google/chrome/google-chrome"
            )
            ;;
    esac
    
    # Find Chrome executable
    for chrome_path in "${chrome_paths[@]}"; do
        if [[ -x "$chrome_path" ]] || command -v "$chrome_path" &> /dev/null; then
            chrome_cmd="$chrome_path"
            break
        fi
    done
    
    if [[ -z "$chrome_cmd" ]]; then
        log_warning "Chrome not found. Please install Google Chrome manually:"
        case $OS in
            "macos")
                log_info "Download from: https://www.google.com/chrome/"
                ;;
            "linux")
                case $DISTRO in
                    "ubuntu"|"debian")
                        log_info "Run: wget -q -O - https://dl.google.com/linux/linux_signing_key.pub | sudo apt-key add -"
                        log_info "     echo 'deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main' | sudo tee /etc/apt/sources.list.d/google-chrome.list"
                        log_info "     sudo apt-get update && sudo apt-get install google-chrome-stable"
                        ;;
                    *)
                        log_info "Download from: https://www.google.com/chrome/"
                        ;;
                esac
                ;;
        esac
        
        read -p "Do you want to continue without Chrome verification? (y/N): " -n 1 -r
        echo
        if [[ ! $REPLY =~ ^[Yy]$ ]]; then
            log_error "Chrome is required. Please install Chrome and run this script again."
            exit 1
        fi
        return
    fi
    
    # Test Chrome
    log_info "Testing Chrome executable: $chrome_cmd"
    local chrome_version=""
    if [[ "$OS" == "macos" ]]; then
        chrome_version=$("$chrome_cmd" --version 2>/dev/null || echo "unknown")
    else
        chrome_version=$(timeout 10s "$chrome_cmd" --version 2>/dev/null || echo "unknown")
    fi
    
    if [[ "$chrome_version" != "unknown" ]]; then
        log_success "Chrome found: $chrome_version"
    else
        log_warning "Chrome found but version check failed. This might still work."
    fi
    
    # Test Chrome headless mode
    log_info "Testing Chrome headless mode..."
    local test_result=""
    if [[ "$OS" == "macos" ]]; then
        test_result=$("$chrome_cmd" --headless --dump-dom --virtual-time-budget=1000 "data:text/html,<html><head><title>Test</title></head><body>Test</body></html>" 2>/dev/null | grep -o "Test" | head -1 || echo "")
    else
        test_result=$(timeout 10s "$chrome_cmd" --headless --no-sandbox --dump-dom --virtual-time-budget=1000 "data:text/html,<html><head><title>Test</title></head><body>Test</body></html>" 2>/dev/null | grep -o "Test" | head -1 || echo "")
    fi
    
    if [[ "$test_result" == "Test" ]]; then
        log_success "Chrome headless test passed"
    else
        log_warning "Chrome headless test failed, but this might not affect the Instagram setup"
    fi
}

# Create .env file if it doesn't exist
create_env_file() {
    log_step "Setting up .env file..."
    
    if [[ ! -f ".env" ]]; then
        log_info "Creating .env file..."
        cat > .env << EOF
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
EOF
        log_success ".env file created"
    else
        log_info ".env file already exists, keeping current configuration"
    fi
}

# Run the Chrome setup script
run_chrome_setup() {
    log_step "Running Chrome profile setup..."
    
    if [[ ! -f "setup_chromev1.py" ]]; then
        log_error "setup_chromev1.py not found in current directory"
        log_error "Please make sure you're running this script in the same directory as setup_chromev1.py"
        exit 1
    fi
    
    log_info "Starting Chrome setup for Instagram login..."
    log_info "This will:"
    log_info "  1. Open Chrome browser"
    log_info "  2. Navigate to Instagram"
    log_info "  3. Wait for you to log in manually"
    log_info "  4. Save your login session to a profile"
    echo
    log_warning "Important: Do NOT close the Chrome window that opens!"
    log_warning "Wait for the login process to complete before closing anything."
    echo
    
    read -p "Press Enter to continue with Chrome setup..."
    
    # Run the Python setup script
    log_info "Launching Chrome setup script..."
    $PYTHON_CMD setup_chromev1.py
    
    log_success "Chrome setup completed!"
    echo
    log_info "Your Chrome profile has been saved."
    log_info "You can now use other scripts that depend on this profile."
}

# Print summary
print_summary() {
    echo
    log_success "🎉 Installation and setup completed successfully!"
    echo
    echo -e "${CYAN}Summary:${NC}"
    echo -e "  • Operating System: ${BLUE}$OS ($DISTRO)${NC}"
    echo -e "  • Python Version: ${BLUE}$($PYTHON_CMD --version)${NC}"
    echo -e "  • Chrome Profile: ${BLUE}Configured${NC}"
    echo -e "  • Dependencies: ${BLUE}Installed${NC}"
    echo
    echo -e "${CYAN}Next Steps:${NC}"
    echo -e "  • Your Instagram login session is saved"
    echo -e "  • You can now run other Instagram automation scripts"
    echo -e "  • The Chrome profile will be reused for future sessions"
    echo
    echo -e "${CYAN}Profile Location:${NC}"
    if [[ -f ".env" ]]; then
        local profile_path=$(grep "CHROME_PROFILE_PATH=" .env | cut -d'=' -f2)
        if [[ -n "$profile_path" ]]; then
            echo -e "  ${BLUE}$profile_path${NC}"
        else
            echo -e "  ${YELLOW}Check .env file for profile path${NC}"
        fi
    fi
    echo
}

# Main execution
main() {
    echo -e "${PURPLE}╔════════════════════════════════════════════════════════════╗${NC}"
    echo -e "${PURPLE}║             Instagram Chrome Profile Setup                 ║${NC}"
    echo -e "${PURPLE}║                Universal Installer                         ║${NC}"
    echo -e "${PURPLE}╚════════════════════════════════════════════════════════════╝${NC}"
    echo
    
    # Pre-flight checks
    detect_system
    check_user
    
    # Installation steps
    install_system_dependencies
    verify_python
    setup_pip
    install_python_dependencies
    check_chrome_installation
    create_env_file
    
    # Run Chrome setup
    run_chrome_setup
    
    # Summary
    print_summary
}

# Error handling
trap 'log_error "Script failed on line $LINENO. Exit code: $?"' ERR

# Run main function
main "$@" 