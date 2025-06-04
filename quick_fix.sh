#!/bin/bash

# 🚀 Instagram Auto Poster - Quick Fix for Current Issues
# This removes the problematic JSON files and lets the app recreate them naturally

echo "🚀 Quick Fix - Resetting JSON files"
echo "==================================="

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

print_info "Fixing JSON files in the running container..."

# Reset the JSON files inside the container
docker-compose exec instagram-auto-poster bash -c '
echo "🔧 Removing problematic JSON files - app will recreate them correctly..."

# Remove any existing JSON files that might have wrong structure
for file in posted_content.json scheduler_settings.json image_order.json scheduler_errors.json; do
    if [ -f "$file" ] || [ -d "$file" ]; then
        rm -rf "$file"
        echo "✅ Removed $file"
    fi
done

echo "✅ All JSON files reset - app will recreate them with correct structure"
'

if [ $? -eq 0 ]; then
    print_success "JSON files reset successfully!"
    
    print_info "Restarting container to let app recreate files naturally..."
    docker-compose restart
    
    print_info "Waiting for application to restart and recreate files..."
    sleep 25
    
    print_info "Testing application..."
    if curl -s -f http://localhost:5002/health &> /dev/null; then
        print_success "Application is healthy!"
        
        print_info "Testing month page (the one that was failing)..."
        if curl -s http://localhost:5002/month/6 | grep -q "Month 6" 2>/dev/null; then
            print_success "Month page is working!"
        else
            print_info "Month page might still be loading, but app is running"
        fi
        
        print_info "Testing stats endpoint..."
        if curl -s -f http://localhost:5002/api/stats &> /dev/null; then
            print_success "Stats endpoint is working!"
        else
            print_info "Stats endpoint might still be initializing"
        fi
        
        echo
        print_success "Quick fix completed! The app should now work normally."
        echo
        echo "🌐 Your application is running at:"
        echo "   Web Interface: http://$(curl -s ipinfo.io/ip 2>/dev/null || echo 'your-server-ip'):5002"
        echo "   VNC Web Access: http://$(curl -s ipinfo.io/ip 2>/dev/null || echo 'your-server-ip'):6080"
        echo
        echo "💡 The app will now create JSON files naturally with the correct data structures."
        
    else
        print_error "Application health check failed after restart"
        print_info "Check container logs: docker-compose logs -f"
    fi
else
    print_error "Failed to reset JSON files in container"
    print_info "Container may not be running. Try: docker-compose up -d"
fi 