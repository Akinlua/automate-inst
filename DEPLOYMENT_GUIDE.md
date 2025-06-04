# 🚀 Instagram Auto Poster - Deployment Guide

This guide will help you deploy the Instagram Auto Poster to your VPS server using Docker and GitHub Actions for automated deployment.

## 📋 Prerequisites

### VPS Server Requirements
- **OS**: Ubuntu 20.04+ (recommended) or similar Linux distribution
- **RAM**: Minimum 2GB (4GB+ recommended)
- **CPU**: 2+ cores recommended
- **Storage**: 10GB+ free space
- **Network**: Stable internet connection

### Software Requirements (installed automatically via Docker)
- Docker & Docker Compose
- Chrome browser
- VNC server
- Python 3.8+

## 🛠️ Setup Methods

### Method 1: Automated Deployment with GitHub Actions (Recommended)

#### Step 1: Fork/Clone Repository
```bash
# Clone the repository
git clone https://github.com/your-username/instagram-auto-poster.git
cd instagram-auto-poster
```

#### Step 2: Configure GitHub Secrets
Go to your GitHub repository → Settings → Secrets and variables → Actions

Add these secrets:
- `VPS_HOST`: Your VPS IP address (e.g., `123.456.789.0`)
- `VPS_USERNAME`: Your VPS username (e.g., `ubuntu`, `root`)
- `VPS_SSH_KEY`: Your private SSH key content
- `VPS_PORT`: SSH port (optional, defaults to 22)

#### Step 3: Prepare Your VPS
```bash
# Connect to your VPS
ssh username@your-vps-ip

# Install Docker and Docker Compose
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo usermod -aG docker $USER

# Install Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

# Logout and login again to apply Docker group changes
exit
ssh username@your-vps-ip
```

#### Step 4: Trigger Deployment
1. Push to `main` or `master` branch
2. GitHub Actions will automatically:
   - Build the Docker image
   - Test the application
   - Deploy to your VPS
   - Start the services

#### Step 5: Configure Instagram Credentials
```bash
# SSH to your VPS
ssh username@your-vps-ip

# Navigate to deployment directory
cd ~/instagram-auto-poster

# Edit the .env file with your Instagram credentials
nano .env
```

Update these values:
```env
INSTAGRAM_USERNAME=your_instagram_username
INSTAGRAM_PASSWORD=your_instagram_password
VNC_PASSWORD=your_secure_vnc_password
```

```bash
# Restart the container with new settings
docker-compose down
docker-compose up -d
```

### Method 2: Manual Docker Deployment

#### Step 1: Prepare VPS
Follow the VPS preparation steps from Method 1.

#### Step 2: Deploy Manually
```bash
# Clone repository on VPS
git clone https://github.com/your-username/instagram-auto-poster.git
cd instagram-auto-poster

# Copy and configure environment
cp .env.example .env
nano .env  # Edit with your credentials

# Build and start
docker-compose up -d --build
```

## 🌐 Accessing Your Application

After successful deployment, you can access:

### Web Interface
- **Main App**: `http://your-vps-ip:5002`
- **Settings**: `http://your-vps-ip:5002/settings`

### VNC Remote Access
- **Web VNC**: `http://your-vps-ip:6080`
- **VNC Client**: `your-vps-ip:5901`
- **Default Password**: `instagram123` (change in .env)

## ⚙️ Configuration

### Environment Variables

Edit `/home/username/instagram-auto-poster/.env`:

```env
# Required - Instagram credentials
INSTAGRAM_USERNAME=your_username
INSTAGRAM_PASSWORD=your_password

# VNC configuration
VNC_PASSWORD=your_secure_password

# Optional - OpenAI for text enhancement
OPENAI_API_KEY=sk-your-api-key
USE_CHATGPT=true

# Posting schedule
POST_HOUR=12
POST_MINUTE=0
```

### Adding Content

1. Access the web interface at `http://your-vps-ip:5002`
2. Upload images and add captions
3. Configure posting times in Settings
4. Enable automatic posting

## 🔒 Security Recommendations

### VNC Security
```bash
# Change default VNC password
nano ~/instagram-auto-poster/.env
# Update VNC_PASSWORD=your_secure_password
docker-compose restart
```

### Firewall Configuration
```bash
# Configure UFW firewall
sudo ufw enable
sudo ufw allow ssh
 # Web interface
sudo ufw allow 6080  # VNC web access
sudo ufw allow 5901  # VNC direct access
```

### SSH Key Authentication
```bash
# Disable password authentication (recommended)
sudo nano /etc/ssh/sshd_config
# Set: PasswordAuthentication no
sudo systemctl restart ssh
```

## 📊 Monitoring & Maintenance

### Check Application Status
```bash
# View running containers
docker-compose ps

# View logs
docker-compose logs -f

# Check health
curl http://localhost:5002/health
```

### Update Application
```bash
# Method 1: GitHub Actions (automatic on git push)
git pull origin main

# Method 2: Manual update
cd ~/instagram-auto-poster
git pull
docker-compose down
docker-compose up -d --build
```

### Backup Data
```bash
# Backup important data
cd ~/instagram-auto-poster
tar -czf backup-$(date +%Y%m%d).tar.gz content/ logs/ .env

# Backup Docker volumes
docker run --rm -v instagram-auto-poster_chrome_profile:/data -v $(pwd):/backup alpine tar -czf /backup/chrome_profile_backup.tar.gz -C /data .
```

## 🔧 Troubleshooting

### Container Won't Start
```bash
# Check logs
docker-compose logs

# Check system resources
df -h
free -h
docker system df
```

### VNC Not Working
```bash
# Check VNC process
docker-compose exec instagram-auto-poster ps aux | grep vnc

# Test VNC connection
docker-compose exec instagram-auto-poster vncviewer localhost:1
```

### Instagram Login Issues
1. Use VNC web interface: `http://your-vps-ip:6080`
2. Navigate to Instagram and login manually
3. Handle 2FA/CAPTCHA challenges
4. Return to web interface and refresh

### Memory Issues
```bash
# Clean up Docker
docker system prune -f
docker volume prune -f

# Restart container
docker-compose restart
```

## 🚦 Common Commands

```bash
# Start services
docker-compose up -d

# Stop services  
docker-compose down

# View logs
docker-compose logs -f

# Restart specific service
docker-compose restart instagram-auto-poster

# Update and restart
git pull && docker-compose down && docker-compose up -d --build

# Connect to container shell
docker-compose exec instagram-auto-poster bash

# Check disk usage
docker system df

# Clean up unused resources
docker system prune -f
```

## 📈 Scaling & Optimization

### Performance Tuning
```yaml
# In docker-compose.yml, add resource limits:
services:
  instagram-auto-poster:
    deploy:
      resources:
        limits:
          memory: 2G
          cpus: '1.0'
        reservations:
          memory: 1G
          cpus: '0.5'
```

### Multiple Accounts
To run multiple Instagram accounts, create separate directories:
```bash
# Copy deployment for second account
cp -r ~/instagram-auto-poster ~/instagram-auto-poster-2
cd ~/instagram-auto-poster-2

# Edit docker-compose.yml to use different ports
# Update .env with different credentials
# Start second instance
docker-compose up -d
```

## 📞 Support

### GitHub Issues
- Report bugs: [GitHub Issues](https://github.com/your-username/instagram-auto-poster/issues)
- Feature requests: [GitHub Discussions](https://github.com/your-username/instagram-auto-poster/discussions)

### Logs Location
- Application logs: `~/instagram-auto-poster/logs/`
- Docker logs: `docker-compose logs`
- System logs: `/var/log/syslog`

### Health Checks
- Application health: `http://your-vps-ip:5002/health`
- VNC status: Available in web interface settings
- System resources: `htop`, `df -h`, `free -h`

---

## 🎉 Success!

Your Instagram Auto Poster should now be running successfully! 

🌐 **Access your app**: `http://your-vps-ip:5002`  
🖥️ **VNC access**: `http://your-vps-ip:6080`  
⚙️ **Configure settings**: Login and set up your posting schedule

Happy posting! 📸✨ 