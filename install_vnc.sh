#!/bin/bash

# VNC Server Installation Script for Instagram Auto Poster
# This script installs VNC server and all required dependencies for remote Chrome access

set -e  # Exit on any error

echo "🚀 Instagram Auto Poster - VNC Setup Script"
echo "=============================================="
echo ""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Logging function
log() {
    echo -e "${GREEN}[$(date +'%Y-%m-%d %H:%M:%S')] $1${NC}"
}

warn() {
    echo -e "${YELLOW}[$(date +'%Y-%m-%d %H:%M:%S')] WARNING: $1${NC}"
}

error() {
    echo -e "${RED}[$(date +'%Y-%m-%d %H:%M:%S')] ERROR: $1${NC}"
}

info() {
    echo -e "${BLUE}[$(date +'%Y-%m-%d %H:%M:%S')] INFO: $1${NC}"
}

# Check if running as root
check_root() {
    if [[ $EUID -ne 0 ]]; then
        error "This script must be run as root or with sudo"
        echo "Usage: sudo bash install_vnc.sh"
        exit 1
    fi
}

# Check Linux distribution
check_distribution() {
    if [[ -f /etc/os-release ]]; then
        . /etc/os-release
        DISTRO=$ID
        VERSION=$VERSION_ID
        log "Detected distribution: $PRETTY_NAME"
    else
        error "Cannot determine Linux distribution"
        exit 1
    fi
}

# Update package lists
update_packages() {
    log "Updating package lists..."
    
    case $DISTRO in
        ubuntu|debian)
            apt-get update -y
            ;;
        centos|rhel|fedora)
            if command -v dnf &> /dev/null; then
                dnf update -y
            else
                yum update -y
            fi
            ;;
        *)
            warn "Unsupported distribution: $DISTRO"
            warn "Proceeding anyway, but manual package installation may be required"
            ;;
    esac
}

# Install VNC server and dependencies
install_vnc_dependencies() {
    log "Installing VNC server and dependencies..."
    
    case $DISTRO in
        ubuntu|debian)
            apt-get install -y \
                tightvncserver \
                tigervnc-standalone-server \
                tigervnc-common \
                xvfb \
                fluxbox \
                x11vnc \
                websockify \
                python3-websockify \
                xterm \
                firefox \
                fonts-liberation \
                fonts-dejavu-core \
                fonts-dejavu \
                fonts-dejavu-extra \
                xfonts-base \
                xfonts-75dpi \
                xfonts-100dpi \
                xfonts-scalable \
                fonts-noto \
                fonts-noto-core \
                xfonts-utils \
                fontconfig \
                curl \
                wget \
                gnupg \
                software-properties-common \
                apt-transport-https \
                ca-certificates \
                lsb-release \
                libasound2-dev
            ;;
        centos|rhel|fedora)
            # For CentOS/RHEL/Fedora
            if command -v dnf &> /dev/null; then
                PKG_MANAGER="dnf"
            else
                PKG_MANAGER="yum"
            fi
            
            $PKG_MANAGER install -y \
                tigervnc-server \
                tightvnc-server \
                xorg-x11-server-Xvfb \
                fluxbox \
                x11vnc \
                python3-websockify \
                xterm \
                firefox \
                liberation-fonts \
                liberation-fonts-common \
                dejavu-sans-fonts \
                dejavu-serif-fonts \
                dejavu-sans-mono-fonts \
                xorg-x11-fonts-base \
                xorg-x11-fonts-75dpi \
                xorg-x11-fonts-100dpi \
                xorg-x11-fonts-misc \
                xorg-x11-font-utils \
                fontconfig \
                curl \
                wget \
                gnupg
            ;;
        *)
            error "Automatic package installation not supported for $DISTRO"
            info "Please install the following packages manually:"
            info "- VNC server (tightvncserver or tigervnc-server)"
            info "- Xvfb (virtual framebuffer)"
            info "- fluxbox (window manager)"
            info "- websockify (web VNC client)"
            info "- xterm (terminal emulator)"
            info "- fonts (liberation, dejavu, base fonts)"
            exit 1
            ;;
    esac
    
    # Additional font setup
    setup_fonts
}

# Setup additional fonts and font caching
setup_fonts() {
    log "Setting up fonts and font cache..."
    
    # Update font cache
    if command -v fc-cache &> /dev/null; then
        fc-cache -fv
        log "Font cache updated"
    fi
    
    # Create fonts directory if needed
    mkdir -p /usr/share/fonts/truetype/
    mkdir -p /usr/share/fonts/X11/misc/
    
    # Set proper permissions
    chmod -R 755 /usr/share/fonts/
    
    # Generate fonts.dir if needed
    if command -v mkfontdir &> /dev/null; then
        for font_dir in /usr/share/fonts/X11/misc/ /usr/share/fonts/X11/75dpi/ /usr/share/fonts/X11/100dpi/; do
            if [ -d "$font_dir" ]; then
                mkfontdir "$font_dir" 2>/dev/null || true
            fi
        done
        log "Font directories indexed"
    fi
}

# Install Google Chrome
install_chrome() {
    log "Installing Google Chrome..."
    
    case $DISTRO in
        ubuntu|debian)
            # Add Google Chrome repository
            curl -fsSL https://dl.google.com/linux/linux_signing_key.pub | gpg --dearmor -o /usr/share/keyrings/google-chrome-keyring.gpg
            echo "deb [arch=amd64 signed-by=/usr/share/keyrings/google-chrome-keyring.gpg] http://dl.google.com/linux/chrome/deb/ stable main" > /etc/apt/sources.list.d/google-chrome.list
            
            apt-get update -y
            apt-get install -y google-chrome-stable
            ;;
        centos|rhel|fedora)
            # Add Google Chrome repository
            cat > /etc/yum.repos.d/google-chrome.repo << 'EOF'
[google-chrome]
name=google-chrome
baseurl=http://dl.google.com/linux/chrome/rpm/stable/x86_64
enabled=1
gpgcheck=1
gpgkey=https://dl.google.com/linux/linux_signing_key.pub
EOF
            
            if command -v dnf &> /dev/null; then
                dnf install -y google-chrome-stable
            else
                yum install -y google-chrome-stable
            fi
            ;;
        *)
            warn "Chrome installation not automated for $DISTRO"
            info "Please install Chrome manually from https://www.google.com/chrome/"
            ;;
    esac
}

# Install noVNC for web-based VNC access
install_novnc() {
    log "Installing noVNC for web-based access..."
    
    # Create noVNC directory
    mkdir -p /usr/share/novnc
    
    # Download noVNC
    if [[ ! -d "/usr/share/novnc/app" ]]; then
        cd /tmp
        wget -q https://github.com/novnc/noVNC/archive/refs/tags/v1.4.0.tar.gz
        tar -xzf v1.4.0.tar.gz
        cp -r noVNC-1.4.0/* /usr/share/novnc/
        rm -rf noVNC-1.4.0 v1.4.0.tar.gz
        log "noVNC installed successfully"
    else
        log "noVNC already installed"
    fi
}

# Configure firewall (if UFW is available)
configure_firewall() {
    log "Configuring firewall rules..."
    
    if command -v ufw &> /dev/null; then
        # Allow VNC ports
        ufw allow 5901/tcp comment "VNC Server"
        ufw allow 6080/tcp comment "VNC Web Access"
        
        # Check if UFW is active
        if ufw status | grep -q "Status: active"; then
            log "UFW firewall rules added"
        else
            warn "UFW is installed but not active. Consider enabling it with: sudo ufw enable"
        fi
    elif command -v firewall-cmd &> /dev/null; then
        # For CentOS/RHEL with firewalld
        firewall-cmd --permanent --add-port=5901/tcp
        firewall-cmd --permanent --add-port=6080/tcp
        firewall-cmd --reload
        log "Firewalld rules added"
    else
        warn "No firewall management tool detected"
        info "Make sure ports 5901 and 6080 are open for VNC access"
    fi
}

# Create VNC service script
create_vnc_service() {
    log "Creating VNC service management script..."
    
    cat > /usr/local/bin/vnc-instagram.sh << 'EOF'
#!/bin/bash

# VNC Service Management for Instagram Auto Poster
VNC_DISPLAY=":1"
VNC_PORT="5901"
WEB_PORT="6080"
VNC_PASSWORD="instagram123"

case "$1" in
    start)
        echo "Starting VNC services..."
        
        # Kill existing sessions
        pkill -f "Xvnc.*:1"
        pkill -f "websockify.*6080"
        sleep 2
        
        # Start VNC server
        vncserver $VNC_DISPLAY -geometry 1280x720 -depth 24
        
        # Start websockify for web access
        websockify --web=/usr/share/novnc $WEB_PORT localhost:$VNC_PORT &
        
        echo "VNC services started"
        echo "VNC Display: $VNC_DISPLAY"
        echo "VNC Port: $VNC_PORT"
        echo "Web Access: http://localhost:$WEB_PORT/vnc.html"
        ;;
    stop)
        echo "Stopping VNC services..."
        pkill -f "Xvnc.*:1"
        pkill -f "websockify.*6080"
        vncserver -kill $VNC_DISPLAY 2>/dev/null || true
        echo "VNC services stopped"
        ;;
    restart)
        $0 stop
        sleep 2
        $0 start
        ;;
    status)
        echo "Checking VNC service status..."
        if pgrep -f "Xvnc.*:1" > /dev/null; then
            echo "VNC Server: RUNNING"
        else
            echo "VNC Server: STOPPED"
        fi
        
        if pgrep -f "websockify.*6080" > /dev/null; then
            echo "Web VNC: RUNNING"
        else
            echo "Web VNC: STOPPED"
        fi
        ;;
    *)
        echo "Usage: $0 {start|stop|restart|status}"
        exit 1
        ;;
esac
EOF

    chmod +x /usr/local/bin/vnc-instagram.sh
    log "VNC service script created at /usr/local/bin/vnc-instagram.sh"
}

# Test VNC installation
test_installation() {
    log "Testing VNC installation..."
    
    # Check if VNC server is available
    if command -v vncserver &> /dev/null || command -v tightvncserver &> /dev/null; then
        log "✓ VNC server installed"
    else
        error "✗ VNC server not found"
        return 1
    fi
    
    # Check if Chrome is available
    if command -v google-chrome &> /dev/null; then
        log "✓ Google Chrome installed"
    else
        warn "✗ Google Chrome not found"
    fi
    
    # Check if websockify is available
    if command -v websockify &> /dev/null; then
        log "✓ Websockify installed"
    else
        warn "✗ Websockify not found"
    fi
    
    # Check if fluxbox is available
    if command -v fluxbox &> /dev/null; then
        log "✓ Fluxbox window manager installed"
    else
        warn "✗ Fluxbox not found"
    fi
}

# Display final instructions
show_instructions() {
    echo ""
    echo "🎉 VNC Installation Complete!"
    echo "============================="
    echo ""
    info "VNC has been installed and configured for Instagram Auto Poster"
    echo ""
    echo "📋 Usage Instructions:"
    echo "----------------------"
    echo "1. Start VNC services:"
    echo "   sudo /usr/local/bin/vnc-instagram.sh start"
    echo ""
    echo "2. Access VNC through web browser:"
    echo "   http://your-server-ip:6080/vnc.html"
    echo "   Default password: instagram123"
    echo ""
    echo "3. Stop VNC services:"
    echo "   sudo /usr/local/bin/vnc-instagram.sh stop"
    echo ""
    echo "4. Check VNC status:"
    echo "   sudo /usr/local/bin/vnc-instagram.sh status"
    echo ""
    echo "🔧 Python Integration:"
    echo "----------------------"
    echo "The VNC functionality is now available in your Instagram Auto Poster"
    echo "through the settings page when automated login fails."
    echo ""
    echo "🔐 Security Notes:"
    echo "------------------"
    echo "- Change the default VNC password in vnc_setup.py"
    echo "- Consider using SSH tunneling for remote access"
    echo "- Firewall ports 5901 and 6080 are required for VNC access"
    echo ""
    echo "🚀 Ready to use VNC with Instagram Auto Poster!"
}

# Main installation process
main() {
    echo "Starting VNC installation for Instagram Auto Poster..."
    echo ""
    
    check_root
    check_distribution
    update_packages
    install_vnc_dependencies
    install_chrome
    install_novnc
    configure_firewall
    create_vnc_service
    test_installation
    show_instructions
}

# Run main function
main "$@" 