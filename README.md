# 📸 Instagram Auto Poster

[![Docker](https://img.shields.io/badge/Docker-Ready-blue.svg)](https://docker.com)
[![Python](https://img.shields.io/badge/Python-3.8+-green.svg)](https://python.org)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![VNC](https://img.shields.io/badge/VNC-Enabled-purple.svg)](docs/VNC_INTEGRATION.md)

A comprehensive Instagram automation tool that allows you to schedule and automatically post content to Instagram. Features a modern web interface, VNC remote access for manual intervention, and robust error handling.

## ✨ Features

- 🤖 **Automated Instagram Posting** - Schedule posts with images and captions
- 🌐 **Modern Web Interface** - Clean, responsive dashboard for content management
- 🖥️ **VNC Remote Access** - Handle 2FA, CAPTCHA, and manual login when needed
- 🔄 **Smart Error Handling** - Automatic fallback to manual options when automation fails
- 📊 **Content Management** - Upload, organize, and schedule your posts
- 🎨 **AI-Powered Captions** - Optional ChatGPT integration for caption enhancement
- 🐳 **Docker Ready** - One-click deployment with full containerization
- 🚀 **GitHub Actions** - Automated CI/CD pipeline for VPS deployment
- 📱 **Mobile Responsive** - Access your dashboard from any device
- 🔒 **Secure Configuration** - Environment-based credential management

## 🚀 Quick Start

### Option 1: One-Click VPS Deployment (Recommended)

```bash
# SSH to your VPS and run:
curl -fsSL https://raw.githubusercontent.com/your-username/instagram-auto-poster/main/deploy_vps.sh | bash
```

This script will:
- ✅ Install Docker and dependencies
- ✅ Configure firewall settings
- ✅ Clone and set up the application
- ✅ Configure environment variables
- ✅ Start all services
- ✅ Provide access URLs and credentials

### Option 2: Manual Docker Deployment

```bash
# Clone the repository
git clone https://github.com/your-username/instagram-auto-poster.git
cd instagram-auto-poster

# Configure environment
cp .env.example .env
nano .env  # Add your Instagram credentials

# Deploy with Docker
docker-compose up -d --build
```

### Option 3: GitHub Actions Auto-Deployment

1. Fork this repository
2. Set up GitHub Secrets:
   - `VPS_HOST`: Your server IP
   - `VPS_USERNAME`: SSH username
   - `VPS_SSH_KEY`: Private SSH key
3. Push to `main` branch - automatic deployment!

## 📊 Dashboard Preview

Access your dashboard at `http://your-server:5002`

- **📋 Main Dashboard**: Upload and schedule posts
- **⚙️ Settings**: Configure Instagram login and posting schedule
- **🖥️ VNC Access**: Remote desktop for manual intervention
- **📈 Analytics**: Track posting history and performance

## 🛠️ System Requirements

### Minimum VPS Specifications
- **OS**: Ubuntu 20.04+ or similar Linux distribution
- **RAM**: 2GB (4GB+ recommended)
- **CPU**: 2+ cores
- **Storage**: 10GB+ free space
- **Network**: Stable internet connection

### Included Software (via Docker)
- Chrome browser with automation drivers
- VNC server with web interface
- Python 3.8+ with all dependencies
- Flask web framework
- Selenium automation tools

## 🔧 Configuration

### Environment Variables (.env)

```env
# Instagram credentials
INSTAGRAM_USERNAME=your_username
INSTAGRAM_PASSWORD=your_password

# VNC configuration
VNC_PASSWORD=your_secure_password
VNC_DISPLAY=:1
VNC_PORT=5901
VNC_WEB_PORT=6080

# OpenAI integration (optional)
OPENAI_API_KEY=sk-your-api-key
USE_CHATGPT=true

# Posting schedule
POST_HOUR=12
POST_MINUTE=0
CONTENT_DIR=/app/content
```

### Access Points

After deployment, access your application at:

- **Web Interface**: `http://your-server:5002`
- **Settings Page**: `http://your-server:5002/settings`
- **VNC Web Access**: `http://your-server:6080`
- **Health Check**: `http://your-server:5002/health`

## 🔒 Security Features

- 🔐 **Environment-based credentials** - No hardcoded passwords
- 🛡️ **Firewall configuration** - Only necessary ports exposed
- 🔑 **SSH key authentication** - Secure server access
- 📝 **Audit logging** - Track all posting activities
- 🚫 **Root user protection** - Runs with minimal privileges

## 🎯 Use Cases

- **Content Creators**: Schedule posts across multiple accounts
- **Businesses**: Maintain consistent social media presence
- **Marketing Agencies**: Manage client Instagram accounts
- **Personal Use**: Automate your Instagram posting workflow

## 🔄 Workflow

1. **Upload Content**: Add images and captions through web interface
2. **Schedule Posts**: Set posting times and dates
3. **Automated Login**: System attempts Instagram login
4. **Smart Fallback**: If automation fails, VNC access provided
5. **Manual Override**: Handle 2FA/CAPTCHA through remote desktop
6. **Post Publishing**: Content published at scheduled times
7. **Status Tracking**: Monitor success/failure in dashboard

## 🚨 Troubleshooting

### Instagram Login Issues
- Use VNC web interface at `http://your-server:6080`
- Navigate to Instagram manually
- Handle 2FA/CAPTCHA challenges
- Return to web interface and refresh

### Container Issues
```bash
# Check status
docker-compose ps

# View logs
docker-compose logs -f

# Restart services
docker-compose restart
```

### Common Solutions
- **Memory issues**: Increase VPS RAM or restart container
- **Login failures**: Clear Instagram cookies in VNC browser
- **Network issues**: Check firewall and port accessibility
- **Permission errors**: Ensure proper Docker group membership

## 📚 Documentation

- 📖 [Deployment Guide](DEPLOYMENT_GUIDE.md) - Comprehensive setup instructions
- 🖥️ [VNC Integration](docs/VNC_INTEGRATION.md) - Remote access documentation
- 🔧 [API Reference](docs/API.md) - Development and integration guide
- 🐛 [Troubleshooting](docs/TROUBLESHOOTING.md) - Common issues and solutions

## 🔄 Updates & Maintenance

### Auto-updates via GitHub Actions
- Push changes to main branch
- Automatic testing and deployment
- Zero-downtime updates

### Manual Updates
```bash
cd ~/instagram-auto-poster
git pull
docker-compose down
docker-compose up -d --build
```

### Backup & Restore
```bash
# Backup
tar -czf backup-$(date +%Y%m%d).tar.gz content/ logs/ .env

# Restore
tar -xzf backup-YYYYMMDD.tar.gz
docker-compose restart
```

## 🤝 Contributing

We welcome contributions! Please see our [Contributing Guide](CONTRIBUTING.md) for details.

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## ⚠️ Disclaimer

This tool is for educational and legitimate business purposes only. Please:
- Respect Instagram's Terms of Service
- Use appropriate rate limiting
- Avoid spammy behavior
- Comply with local laws and regulations

## 🆘 Support

- 🐛 **Bug Reports**: [GitHub Issues](https://github.com/your-username/instagram-auto-poster/issues)
- 💡 **Feature Requests**: [GitHub Discussions](https://github.com/your-username/instagram-auto-poster/discussions)
- 📖 **Documentation**: [Project Wiki](https://github.com/your-username/instagram-auto-poster/wiki)
- 💬 **Community**: [Discord Server](https://discord.gg/your-server)

## 🙏 Acknowledgments

- [Selenium](https://selenium.dev/) - Web automation framework
- [Flask](https://flask.palletsprojects.com/) - Web framework
- [Docker](https://docker.com) - Containerization platform
- [VNC](https://www.realvnc.com/) - Remote desktop technology

---

<div align="center">

**🚀 Ready to automate your Instagram posting?**

[Quick Deploy](#-quick-start) • [Documentation](DEPLOYMENT_GUIDE.md) • [Support](#-support)

⭐ Star this repo if it helps you!

</div>
