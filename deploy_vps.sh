#!/bin/bash

# 🚀 Instagram Auto Poster - VPS Deployment Script
# This script sets up the Instagram Auto Poster on your VPS server

set -e  # Exit on any error

echo "🚀 Instagram Auto Poster - VPS Deployment Script"
echo "================================================="

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

print_step() {
    echo -e "\n${BLUE}[STEP]${NC} $1"
}

# Check if running as root
if [[ $EUID -eq 0 ]]; then
   print_error "This script should not be run as root for security reasons."
   print_status "Please run as a regular user with sudo privileges."
   exit 1
fi

# Check if sudo is available
if ! command -v sudo &> /dev/null; then
    print_error "sudo is required but not installed. Please install sudo first."
    exit 1
fi

print_step "1. Updating system packages"
sudo apt update && sudo apt upgrade -y

print_step "2. Installing required system packages"
sudo apt install -y curl wget git ufw htop nano

print_step "3. Installing Docker"
if ! command -v docker &> /dev/null; then
    print_status "Installing Docker..."
    curl -fsSL https://get.docker.com -o get-docker.sh
    sudo sh get-docker.sh
    sudo usermod -aG docker $USER
    rm get-docker.sh
    print_status "Docker installed successfully!"
else
    print_status "Docker is already installed."
fi

print_step "4. Installing Docker Compose"
if ! command -v docker-compose &> /dev/null; then
    print_status "Installing Docker Compose..."
    sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
    sudo chmod +x /usr/local/bin/docker-compose
    print_status "Docker Compose installed successfully!"
else
    print_status "Docker Compose is already installed."
fi

print_step "5. Configuring firewall"
print_status "Setting up UFW firewall rules..."
sudo ufw --force enable
sudo ufw allow ssh
sudo ufw allow 5002/tcp  # Web interface
sudo ufw allow 6080/tcp  # VNC web access
sudo ufw allow 5901/tcp  # VNC direct access
print_status "Firewall configured successfully!"

print_step "6. Creating application directory"
APP_DIR="$HOME/instagram-auto-poster"
if [ -d "$APP_DIR" ]; then
    print_warning "Directory $APP_DIR already exists."
    read -p "Do you want to remove it and start fresh? (y/N): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        rm -rf "$APP_DIR"
        print_status "Removed existing directory."
    else
        print_status "Using existing directory."
    fi
fi

print_step "7. Cloning repository"
if [ ! -d "$APP_DIR" ]; then
    # Try to get the repository URL from user or use default
    read -p "Enter your GitHub repository URL (or press Enter for default): " REPO_URL
    if [ -z "$REPO_URL" ]; then
        REPO_URL="https://github.com/your-username/instagram-auto-poster.git"
        print_warning "Using default repository URL. You may need to update this."
    fi
    
    git clone "$REPO_URL" "$APP_DIR" || {
        print_error "Failed to clone repository. Please check the URL and try again."
        exit 1
    }
fi

cd "$APP_DIR"

print_step "8. Setting up environment configuration"
if [ ! -f ".env" ]; then
    cp .env.example .env
    print_status "Created .env file from template."
    
    # Prompt for Instagram credentials
    echo
    print_status "Please provide your Instagram credentials:"
    read -p "Instagram username: " IG_USERNAME
    read -s -p "Instagram password: " IG_PASSWORD
    echo
    
    # Generate secure VNC password
    VNC_PASSWORD=$(openssl rand -base64 12 | tr -d "=+/" | cut -c1-12)
    
    # Update .env file
    sed -i "s/your_instagram_username/$IG_USERNAME/" .env
    sed -i "s/your_instagram_password/$IG_PASSWORD/" .env
    sed -i "s/instagram123/$VNC_PASSWORD/" .env
    
    print_status "Environment file configured with your credentials."
    print_status "VNC Password: $VNC_PASSWORD"
    
    # Ask for OpenAI API key (optional)
    echo
    read -p "Do you have an OpenAI API key for ChatGPT integration? (y/N): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        read -p "Enter your OpenAI API key: " OPENAI_KEY
        sed -i "s/sk-your-api-key/$OPENAI_KEY/" .env
        sed -i "s/USE_CHATGPT=false/USE_CHATGPT=true/" .env
        print_status "OpenAI API key configured."
    fi
else
    print_status ".env file already exists. Skipping configuration."
fi

print_step "9. Creating required directories"
mkdir -p content uploads logs
print_status "Created application directories."

print_step "10. Building and starting Docker containers"
print_status "This may take several minutes on first run..."

# Check if user is in docker group
if ! groups $USER | grep -q docker; then
    print_warning "User is not in docker group. You may need to logout and login again."
    print_status "For now, we'll use sudo for Docker commands."
    DOCKER_CMD="sudo docker-compose"
else
    DOCKER_CMD="docker-compose"
fi

# Build and start containers
$DOCKER_CMD up -d --build

# Wait for containers to start
print_status "Waiting for containers to start..."
sleep 30

# Check if containers are running
if $DOCKER_CMD ps | grep -q "instagram-auto-poster"; then
    print_status "Containers started successfully!"
else
    print_error "Containers failed to start. Checking logs..."
    $DOCKER_CMD logs
    exit 1
fi

print_step "11. Running health check"
sleep 10
if curl -s http://localhost:5002/health | grep -q "healthy"; then
    print_status "Health check passed!"
else
    print_warning "Health check failed. The application may still be starting up."
fi

print_step "12. Setting up log rotation"
sudo tee /etc/logrotate.d/instagram-auto-poster > /dev/null <<EOF
$APP_DIR/logs/*.log {
    daily
    missingok
    rotate 52
    compress
    delaycompress
    notifempty
    create 644 $USER $USER
}
EOF
print_status "Log rotation configured."

print_step "13. Creating systemd service (optional)"
read -p "Do you want to create a systemd service for auto-start on boot? (y/N): " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    sudo tee /etc/systemd/system/instagram-auto-poster.service > /dev/null <<EOF
[Unit]
Description=Instagram Auto Poster
Requires=docker.service
After=docker.service

[Service]
Type=oneshot
RemainAfterExit=yes
WorkingDirectory=$APP_DIR
ExecStart=$DOCKER_CMD up -d
ExecStop=$DOCKER_CMD down
TimeoutStartSec=0
User=$USER

[Install]
WantedBy=multi-user.target
EOF
    
    sudo systemctl daemon-reload
    sudo systemctl enable instagram-auto-poster.service
    print_status "Systemd service created and enabled."
fi

# Get server IP
SERVER_IP=$(curl -s ipinfo.io/ip 2>/dev/null || echo "your-server-ip")

print_step "✅ Deployment Complete!"
echo
print_status "🎉 Instagram Auto Poster has been successfully deployed!"
echo
echo "📊 Access Information:"
echo "  🌐 Web Interface: http://$SERVER_IP:5002"
echo "  ⚙️  Settings Page: http://$SERVER_IP:5002/settings"
echo "  🖥️  VNC Web Access: http://$SERVER_IP:6080"
echo "  🔐 VNC Password: $VNC_PASSWORD"
echo
echo "🔧 Useful Commands:"
echo "  📋 Check status:    cd $APP_DIR && $DOCKER_CMD ps"
echo "  📝 View logs:       cd $APP_DIR && $DOCKER_CMD logs -f"
echo "  🔄 Restart:         cd $APP_DIR && $DOCKER_CMD restart"
echo "  ⬇️  Stop:            cd $APP_DIR && $DOCKER_CMD down"
echo "  ⬆️  Start:           cd $APP_DIR && $DOCKER_CMD up -d"
echo
echo "📚 Next Steps:"
echo "  1. Open http://$SERVER_IP:5002 in your browser"
echo "  2. Upload your first image and caption"
echo "  3. Configure posting schedule in Settings"
echo "  4. Test VNC access if Instagram login fails"
echo
print_status "For troubleshooting, check the deployment guide: $APP_DIR/DEPLOYMENT_GUIDE.md"

# Reminder about docker group
if ! groups $USER | grep -q docker; then
    echo
    print_warning "⚠️  IMPORTANT: Please logout and login again to use Docker without sudo"
    print_status "   Or run: newgrp docker"
fi

echo
print_status "🚀 Happy posting! Your Instagram Auto Poster is ready to use!" 