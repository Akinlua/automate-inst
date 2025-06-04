#!/bin/bash

# 🔍 Instagram Auto Poster - Setup Verification Script
# This script verifies that all components are working correctly

set -e

echo "🔍 Instagram Auto Poster - Setup Verification"
echo "============================================="

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

print_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

print_step() {
    echo -e "\n${BLUE}[CHECKING]${NC} $1"
}

# Track overall status
OVERALL_STATUS=0

# Function to check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Function to check if port is open
check_port() {
    local port=$1
    local service=$2
    if nc -z localhost $port 2>/dev/null; then
        print_success "$service is running on port $port"
        return 0
    else
        print_error "$service is not accessible on port $port"
        return 1
    fi
}

# Function to check HTTP endpoint
check_http() {
    local url=$1
    local service=$2
    local expected=$3
    
    if curl -s "$url" | grep -q "$expected"; then
        print_success "$service is responding correctly"
        return 0
    else
        print_error "$service is not responding correctly at $url"
        return 1
    fi
}

print_step "1. Docker Installation"
if command_exists docker; then
    print_success "Docker is installed"
    docker --version
else
    print_error "Docker is not installed"
    OVERALL_STATUS=1
fi

print_step "2. Docker Compose Installation"
if command_exists docker-compose; then
    print_success "Docker Compose is installed"
    docker-compose --version
else
    print_error "Docker Compose is not installed"
    OVERALL_STATUS=1
fi

print_step "3. Application Directory"
APP_DIR="$HOME/instagram-auto-poster"
if [ -d "$APP_DIR" ]; then
    print_success "Application directory exists: $APP_DIR"
    cd "$APP_DIR"
else
    print_error "Application directory not found: $APP_DIR"
    OVERALL_STATUS=1
    exit 1
fi

print_step "4. Environment Configuration"
if [ -f ".env" ]; then
    print_success ".env file exists"
    
    # Check for required variables
    if grep -q "INSTAGRAM_USERNAME=" .env && ! grep -q "your_instagram_username" .env; then
        print_success "Instagram username configured"
    else
        print_warning "Instagram username not configured"
    fi
    
    if grep -q "INSTAGRAM_PASSWORD=" .env && ! grep -q "your_instagram_password" .env; then
        print_success "Instagram password configured"
    else
        print_warning "Instagram password not configured"
    fi
    
    if grep -q "VNC_PASSWORD=" .env && ! grep -q "instagram123" .env; then
        print_success "VNC password changed from default"
    else
        print_warning "VNC password is still default - consider changing it"
    fi
else
    print_error ".env file not found"
    OVERALL_STATUS=1
fi

print_step "5. Docker Containers Status"
if docker-compose ps | grep -q "instagram-auto-poster"; then
    print_success "Container is running"
    
    # Show container status
    echo
    print_info "Container Status:"
    docker-compose ps
    echo
else
    print_error "Container is not running"
    print_info "Try: docker-compose up -d"
    OVERALL_STATUS=1
fi

print_step "6. Network Connectivity"

# Check if nc (netcat) is available
if ! command_exists nc; then
    print_warning "netcat not installed, skipping port checks"
else
    # Check Flask app
    if check_port 5002 "Flask Web Application"; then
        :
    else
        OVERALL_STATUS=1
    fi

    # Check VNC web
    if check_port 6080 "VNC Web Interface"; then
        :
    else
        OVERALL_STATUS=1
    fi

    # Check VNC direct
    if check_port 5901 "VNC Direct Access"; then
        :
    else
        OVERALL_STATUS=1
    fi
fi

print_step "7. Application Health Check"
if command_exists curl; then
    sleep 5  # Give services time to start
    if check_http "http://localhost:5002/health" "Health Endpoint" "healthy"; then
        :
    else
        print_warning "Application health check failed - it might still be starting"
    fi
    
    if check_http "http://localhost:5002" "Main Application" "Instagram Auto Poster"; then
        :
    else
        print_warning "Main application page not accessible"
    fi
else
    print_warning "curl not installed, skipping HTTP checks"
fi

print_step "8. Required Directories"
required_dirs=("content" "uploads" "logs")
for dir in "${required_dirs[@]}"; do
    if [ -d "$dir" ]; then
        print_success "Directory exists: $dir"
    else
        print_error "Directory missing: $dir"
        mkdir -p "$dir"
        print_info "Created directory: $dir"
    fi
done

print_step "9. File Permissions"
if [ -r "docker-compose.yml" ]; then
    print_success "docker-compose.yml is readable"
else
    print_error "docker-compose.yml is not readable"
    OVERALL_STATUS=1
fi

if [ -r ".env" ]; then
    print_success ".env file is readable"
else
    print_error ".env file is not readable"
    OVERALL_STATUS=1
fi

print_step "10. System Resources"
# Check available memory
MEMORY_MB=$(free -m | awk 'NR==2{printf "%.0f", $2}')
if [ "$MEMORY_MB" -ge 2048 ]; then
    print_success "Sufficient memory: ${MEMORY_MB}MB"
else
    print_warning "Low memory: ${MEMORY_MB}MB (recommended: 2048MB+)"
fi

# Check available disk space
DISK_AVAILABLE=$(df . | awk 'NR==2{print $4}')
if [ "$DISK_AVAILABLE" -ge 5000000 ]; then  # 5GB in KB
    print_success "Sufficient disk space available"
else
    print_warning "Low disk space available"
fi

# Get server IP for display
SERVER_IP=$(curl -s ipinfo.io/ip 2>/dev/null || hostname -I | awk '{print $1}' || echo "localhost")

print_step "🎯 Verification Summary"
echo

if [ $OVERALL_STATUS -eq 0 ]; then
    print_success "All checks passed! Your Instagram Auto Poster is ready to use!"
    echo
    echo "🌐 Access your application:"
    echo "  📱 Web Interface: http://$SERVER_IP:5002"
    echo "  ⚙️  Settings:     http://$SERVER_IP:5002/settings"
    echo "  🖥️  VNC Web:      http://$SERVER_IP:6080"
    echo
    echo "🚀 Next Steps:"
    echo "  1. Open the web interface"
    echo "  2. Go to Settings and configure Instagram login"
    echo "  3. Upload your first image and caption"
    echo "  4. Test the posting functionality"
    echo
else
    print_error "Some checks failed. Please review the errors above and fix them."
    echo
    echo "🔧 Common Solutions:"
    echo "  - Run: docker-compose up -d --build"
    echo "  - Check: docker-compose logs"
    echo "  - Verify: .env configuration"
    echo "  - Ensure: sufficient system resources"
    echo
    exit 1
fi

echo "📚 Documentation:"
echo "  - Deployment Guide: $APP_DIR/DEPLOYMENT_GUIDE.md"
echo "  - VNC Setup: $APP_DIR/docs/VNC_INTEGRATION.md"
echo "  - Troubleshooting: Check logs with 'docker-compose logs'"
echo

print_info "Verification completed successfully! 🎉" 