#!/bin/bash

# 🔧 Instagram Auto Poster - Quick Permissions Fix
# Run this script to fix permission issues with content directories

echo "🔧 Quick Permissions Fix for Instagram Auto Poster"
echo "================================================="

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

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

# Check if we're in the right directory
if [ ! -f "docker-compose.yml" ] || [ ! -f "app.py" ]; then
    print_error "This doesn't appear to be the Instagram Auto Poster directory"
    print_info "Please run this script from the instagram-auto-poster directory"
    exit 1
fi

print_info "Creating necessary directories if they don't exist..."
mkdir -p content logs uploads

print_info "Setting proper permissions for content directories..."
chmod 755 content logs uploads

print_info "Setting ownership to match Docker container user..."
# Try to set ownership to UID 1000 (appuser in container)
if sudo chown -R 1000:1000 content logs uploads 2>/dev/null; then
    print_success "Set ownership to container user (UID 1000)"
else
    print_warning "Could not set ownership to UID 1000, using current user"
    chown -R $(id -u):$(id -g) content logs uploads
fi

print_info "Restarting container to apply changes..."
docker-compose restart

print_info "Waiting for container to restart..."
sleep 15

# Check if container is running
if docker-compose ps | grep -q "Up"; then
    print_success "Container restarted successfully!"
    
    print_info "Testing health endpoint..."
    if curl -s -f http://localhost:5002/health &> /dev/null; then
        print_success "Application is healthy!"
        print_success "Permissions fix completed successfully!"
        echo
        echo "🌐 You can now access your application at:"
        echo "   Web Interface: http://$(curl -s ipinfo.io/ip 2>/dev/null || echo 'your-server-ip'):5002"
        echo "   VNC Web Access: http://$(curl -s ipinfo.io/ip 2>/dev/null || echo 'your-server-ip'):6080"
    else
        print_warning "Health check failed, but container is running. Give it a few more minutes."
    fi
else
    print_error "Container failed to restart. Check logs:"
    docker-compose logs --tail=20
    exit 1
fi 