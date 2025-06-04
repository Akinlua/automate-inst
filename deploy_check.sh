#!/bin/bash

# 🔍 Instagram Auto Poster - Post-Deployment Verification Script
# Run this script after deployment to verify everything is working correctly

set -e

echo "🔍 Instagram Auto Poster - Deployment Verification"
echo "================================================="

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

ERRORS=0

echo
print_info "Step 1: Checking if deployment directory exists..."
if [ -d "$HOME/instagram-auto-poster" ]; then
    print_success "Deployment directory found"
    cd "$HOME/instagram-auto-poster"
else
    print_error "Deployment directory not found at $HOME/instagram-auto-poster"
    exit 1
fi

echo
print_info "Step 2: Checking essential files..."
for file in "Dockerfile" "docker-compose.yml" "app.py" "requirements.txt"; do
    if [ -f "$file" ]; then
        print_success "$file exists"
    else
        print_error "$file is missing"
        ERRORS=$((ERRORS + 1))
    fi
done

echo
print_info "Step 3: Checking environment configuration..."
if [ -f ".env" ]; then
    print_success ".env file exists"
    
    # Check if critical environment variables are set
    if grep -q "INSTAGRAM_USERNAME=your_instagram_username" .env; then
        print_warning ".env file still contains default Instagram username"
        print_info "Please update your Instagram credentials in .env file"
    else
        print_success "Instagram username has been configured"
    fi
    
    if grep -q "VNC_PASSWORD=instagram123" .env; then
        print_warning ".env file contains default VNC password"
        print_info "Consider changing the VNC password for security"
    else
        print_success "VNC password has been customized"
    fi
else
    print_error ".env file is missing"
    ERRORS=$((ERRORS + 1))
fi

echo
print_info "Step 4: Checking Docker and Docker Compose..."
if command -v docker &> /dev/null; then
    print_success "Docker is installed"
    
    if command -v docker-compose &> /dev/null; then
        print_success "Docker Compose is installed"
    else
        print_error "Docker Compose is not installed"
        ERRORS=$((ERRORS + 1))
    fi
else
    print_error "Docker is not installed"
    ERRORS=$((ERRORS + 1))
fi

echo
print_info "Step 5: Checking container status..."
if docker-compose ps | grep -q "instagram-auto-poster"; then
    if docker-compose ps | grep -q "Up"; then
        print_success "Instagram Auto Poster container is running"
    else
        print_error "Instagram Auto Poster container exists but is not running"
        print_info "Try: docker-compose up -d"
        ERRORS=$((ERRORS + 1))
    fi
else
    print_error "Instagram Auto Poster container not found"
    print_info "Try: docker-compose up -d --build"
    ERRORS=$((ERRORS + 1))
fi

echo
print_info "Step 6: Checking application health..."
if curl -s -f http://localhost:5002/health &> /dev/null; then
    print_success "Application health check passed"
    
    # Check if main page is accessible
    if curl -s -f http://localhost:5002/ &> /dev/null; then
        print_success "Main application page is accessible"
    else
        print_warning "Main application page may not be fully loaded yet"
    fi
else
    print_error "Application health check failed"
    print_info "The application may still be starting up. Wait a few minutes and try again."
    ERRORS=$((ERRORS + 1))
fi

echo
print_info "Step 7: Checking network ports..."
for port in 5002 6080 5901; do
    if netstat -tuln 2>/dev/null | grep -q ":$port "; then
        print_success "Port $port is open"
    else
        print_warning "Port $port may not be accessible"
        print_info "Check firewall settings: sudo ufw allow $port"
    fi
done

echo
print_info "Step 8: Checking directories..."
for dir in "content" "logs" "uploads"; do
    if [ -d "$dir" ]; then
        print_success "$dir directory exists"
    else
        print_warning "$dir directory not found - creating it"
        mkdir -p "$dir"
    fi
done

# Get server IP
SERVER_IP=$(curl -s ipinfo.io/ip 2>/dev/null || echo "your-server-ip")

echo
echo "======================================"
if [ $ERRORS -eq 0 ]; then
    print_success "All checks passed! Your Instagram Auto Poster is ready to use."
    echo
    echo "🌐 Access URLs:"
    echo "   Web Interface: http://$SERVER_IP:5002"
    echo "   Settings Page: http://$SERVER_IP:5002/settings"
    echo "   VNC Web Access: http://$SERVER_IP:6080"
    echo
    echo "🔧 Next Steps:"
    echo "   1. Configure your Instagram credentials in Settings"
    echo "   2. Upload your first image and caption"
    echo "   3. Test the posting functionality"
    echo "   4. Set up your posting schedule"
else
    print_error "$ERRORS error(s) found. Please fix the issues above before proceeding."
    echo
    echo "🔧 Common Solutions:"
    echo "   • Run: docker-compose up -d --build"
    echo "   • Check logs: docker-compose logs -f"
    echo "   • Verify .env file: nano .env"
    echo "   • Check firewall: sudo ufw status"
fi
echo "======================================" 