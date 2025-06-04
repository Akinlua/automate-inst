#!/bin/bash

# 🔧 Instagram Auto Poster - JSON Files Fix Script
# Run this script to fix the "Is a directory" error for JSON files

set -e

echo "🔧 Instagram Auto Poster - JSON Files Fix"
echo "========================================"

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

print_info "Stopping Docker containers..."
docker-compose down || true

print_info "Removing problematic Docker volumes..."
docker volume rm $(docker volume ls -q | grep -E "(posted_content|image_order|scheduler_settings|scheduler_errors|vnc_profile)") 2>/dev/null || true

print_info "Cleaning up directory versions of JSON files..."
for file in posted_content.json scheduler_settings.json image_order.json scheduler_errors.json; do
    if [ -d "$file" ]; then
        print_warning "Removing directory: $file"
        rm -rf "$file"
        print_success "Removed directory: $file"
    elif [ -f "$file" ]; then
        print_info "File already exists: $file"
    else
        print_info "File doesn't exist (will be created): $file"
    fi
done

print_info "Rebuilding and starting containers..."
docker-compose up -d --build

print_info "Waiting for container to start..."
sleep 30

print_info "Checking container status..."
if docker-compose ps | grep -q "Up"; then
    print_success "Container is running!"
    
    print_info "Checking JSON files..."
    docker-compose exec instagram-auto-poster ls -la *.json 2>/dev/null || print_warning "JSON files not visible yet (they will be created when needed)"
    
    print_info "Testing health endpoint..."
    if curl -s -f http://localhost:5002/health &> /dev/null; then
        print_success "Application is healthy!"
    else
        print_warning "Health check failed, but container is running. Give it a few more minutes."
    fi
    
    echo
    print_success "Fix completed! Your Instagram Auto Poster should now work correctly."
    echo
    echo "🌐 Access your application at:"
    echo "   Web Interface: http://$(curl -s ipinfo.io/ip):5002"
    echo "   VNC Web Access: http://$(curl -s ipinfo.io/ip):6080"
    
else
    print_error "Container failed to start. Check logs:"
    docker-compose logs
    exit 1
fi 