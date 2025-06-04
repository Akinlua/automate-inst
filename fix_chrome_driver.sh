#!/bin/bash

# 🔧 Chrome Driver Fix Script
# This script fixes Chrome driver timeout issues in Docker

echo "🔧 Chrome Driver Fix Script"
echo "=========================="

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

# Stop current container
print_info "Stopping current container..."
docker-compose down

# Rebuild with no cache to ensure Chrome fixes are applied
print_info "Rebuilding Docker image with Chrome fixes..."
docker-compose build --no-cache

if [ $? -ne 0 ]; then
    print_error "Docker build failed"
    exit 1
fi

# Start the new container
print_info "Starting container with Chrome optimizations..."
docker-compose up -d

if [ $? -ne 0 ]; then
    print_error "Failed to start container"
    exit 1
fi

# Wait for container to be ready
print_info "Waiting for container to initialize..."
sleep 30

# Check if container is running
if docker-compose ps | grep -q "Up"; then
    print_success "Container is running"
else
    print_error "Container failed to start"
    print_info "Check logs: docker-compose logs -f"
    exit 1
fi

# Run Chrome diagnostics inside container
print_info "Running Chrome driver diagnostics..."
docker-compose exec instagram-auto-poster python3 test_chrome_docker.py

# Test the application
print_info "Testing application health..."
sleep 10

if curl -s -f http://localhost:5002/health &> /dev/null; then
    print_success "Application is healthy!"
    
    print_info "Testing login functionality (this will use VNC if needed)..."
    echo
    print_success "🎉 Chrome driver fix completed!"
    echo
    echo "🌐 Your application is running at:"
    echo "   Web Interface: http://$(curl -s ipinfo.io/ip 2>/dev/null || echo 'your-server-ip'):5002"
    echo "   VNC Web Access: http://$(curl -s ipinfo.io/ip 2>/dev/null || echo 'your-server-ip'):6080"
    echo
    echo "💡 Chrome driver should now work properly. Key improvements:"
    echo "   - Increased shared memory to 2GB"
    echo "   - Added Chrome-specific Docker optimizations"
    echo "   - Better error handling and fallback options"
    echo "   - Resource limits to prevent memory issues"
    echo
    echo "🔑 Next steps:"
    echo "   1. Go to Settings and configure your Instagram credentials"
    echo "   2. If login fails, use VNC to handle 2FA manually"
    echo "   3. Upload content and test posting"
    
else
    print_error "Application health check failed"
    print_info "Container might still be starting. Wait a few more minutes and check:"
    print_info "  docker-compose logs -f"
    print_info "  docker-compose ps"
fi

echo
print_info "For additional troubleshooting, run:"
print_info "  docker-compose exec instagram-auto-poster python3 test_chrome_docker.py" 