#!/bin/bash

# 🔧 Instagram Auto Poster - Data Structure Fix
# Run this script to fix JSON data structure issues

echo "🔧 Instagram Auto Poster - Data Structure Fix"
echo "=============================================="

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

print_info "Fixing JSON data structures in the running container..."

# Fix the JSON files inside the container
docker-compose exec instagram-auto-poster bash -c '
echo "Fixing posted_content.json data structure..."
if [ -f "posted_content.json" ]; then
    # Check if it contains an array [] instead of object {}
    if grep -q "^\[\]$" posted_content.json || grep -q "^\[$" posted_content.json; then
        echo "{}" > posted_content.json
        echo "✅ Fixed posted_content.json (changed from array to object)"
    else
        echo "ℹ️  posted_content.json already has correct structure"
    fi
else
    echo "{}" > posted_content.json
    echo "✅ Created posted_content.json as object"
fi

echo "Checking scheduler_settings.json..."
if [ ! -f "scheduler_settings.json" ] || [ -d "scheduler_settings.json" ]; then
    echo "{\"enabled\": false, \"hour\": 12, \"minute\": 0}" > scheduler_settings.json
    echo "✅ Fixed scheduler_settings.json"
fi

echo "Checking image_order.json..."
if [ ! -f "image_order.json" ] || [ -d "image_order.json" ]; then
    echo "[]" > image_order.json
    echo "✅ Fixed image_order.json"
fi

echo "Checking scheduler_errors.json..."
if [ ! -f "scheduler_errors.json" ] || [ -d "scheduler_errors.json" ]; then
    echo "[]" > scheduler_errors.json
    echo "✅ Fixed scheduler_errors.json"
fi

echo "All JSON files checked and fixed!"
'

if [ $? -eq 0 ]; then
    print_success "JSON data structures fixed successfully!"
    
    print_info "Restarting Flask application..."
    docker-compose restart
    
    print_info "Waiting for application to restart..."
    sleep 20
    
    print_info "Testing application..."
    if curl -s -f http://localhost:5002/health &> /dev/null; then
        print_success "Application is healthy!"
        
        print_info "Testing stats endpoint..."
        if curl -s -f http://localhost:5002/api/stats &> /dev/null; then
            print_success "Stats endpoint is working!"
        else
            print_warning "Stats endpoint still has issues, but main app is working"
        fi
        
        echo
        print_success "Data structure fix completed successfully!"
        echo
        echo "🌐 Your application should now work correctly at:"
        echo "   Web Interface: http://$(curl -s ipinfo.io/ip 2>/dev/null || echo 'your-server-ip'):5002"
        echo "   VNC Web Access: http://$(curl -s ipinfo.io/ip 2>/dev/null || echo 'your-server-ip'):6080"
    else
        print_error "Application health check failed after restart"
        print_info "Check container logs: docker-compose logs -f"
    fi
else
    print_error "Failed to fix JSON files in container"
    print_info "Container may not be running. Try: docker-compose up -d"
fi 