# VNC Server with Proxy Support - Usage Guide

## Overview
The updated VNC setup now includes comprehensive proxy server support for Chrome browser sessions. This allows you to route Instagram login traffic through HTTP, HTTPS, or SOCKS proxies for enhanced privacy and bypassing geo-restrictions.

## Key Fixes Applied

### 1. Package Installation Issues Fixed
- Replaced `firefox-esr` with `firefox` (standard Firefox package)
- Removed `file-manager-actions` (not available in all Ubuntu versions)
- Changed `libasound2` to `libasound2-dev` (development package)
- Added `tigervnc-common` instead of problematic extensions
- Added batch installation with fallback for individual packages

### 2. Proxy Server Support Added
- HTTP proxy support: `http://proxy.server:port`
- HTTPS proxy support: `https://proxy.server:port`
- SOCKS5 proxy support: `socks5://proxy.server:port`
- Dynamic proxy switching during runtime
- Proxy status monitoring

## Usage Examples

### 1. Basic VNC Setup (No Proxy)
```python
from vnc_setup import start_vnc_chrome_session

profile_path = "chrome_profile_instagram"
result = start_vnc_chrome_session(profile_path)

if result['success']:
    print(f"VNC Web Access: {result['access_info']['web_url']}")
    print(f"VNC Password: {result['access_info']['vnc_password']}")
```

### 2. VNC Setup with HTTP Proxy
```python
from vnc_setup import start_vnc_chrome_session

profile_path = "chrome_profile_instagram"
proxy_server = "http://proxy.example.com:8080"

result = start_vnc_chrome_session(profile_path, proxy_server)
```

### 3. VNC Setup with SOCKS5 Proxy
```python
from vnc_setup import start_vnc_chrome_session

profile_path = "chrome_profile_instagram"
proxy_server = "socks5://127.0.0.1:1080"

result = start_vnc_chrome_session(profile_path, proxy_server)
```

### 4. Change Proxy on Running Session
```python
from vnc_setup import set_vnc_proxy, restart_chrome_fresh_session

# Change proxy
set_vnc_proxy("http://new.proxy.com:3128")

# Restart Chrome with new proxy
restart_chrome_fresh_session("chrome_profile_instagram")
```

## Testing the Setup

### Quick Test
```bash
# Run the test script
sudo python3 test_vnc_proxy.py

# Or test proxy change on running session
sudo python3 test_vnc_proxy.py change-proxy
```

### Manual Installation
```bash
# Install dependencies first
sudo bash install_vnc.sh

# Then test Python VNC setup
sudo python3 vnc_setup.py
```

## Access Methods

### 1. Web Browser Access
- URL: `http://localhost:6080/vnc.html`
- Password: `instagram123` (default)
- Works in any modern browser

### 2. VNC Client Access
- Address: `localhost:5901`
- Display: `:1`
- Password: `instagram123`

## Proxy Configuration Details

### Supported Proxy Types
1. **HTTP Proxy**: `http://host:port`
2. **HTTPS Proxy**: `https://host:port`
3. **SOCKS5 Proxy**: `socks5://host:port`

### Proxy Authentication
For proxies requiring authentication, use this format:
```python
proxy_server = "http://username:password@proxy.server:8080"
proxy_server = "socks5://username:password@proxy.server:1080"
```

## Troubleshooting

### Common Issues and Solutions

1. **Package Installation Fails**
   - The script now handles failed packages gracefully
   - Individual packages are retried if batch installation fails
   - Check `vnc_setup.log` for detailed error information

2. **VNC Server Won't Start**
   - Ensure running as root: `sudo python3 vnc_setup.py`
   - Check if ports 5901 and 6080 are available
   - Kill existing VNC sessions: `vncserver -kill :1`

3. **Chrome Won't Start**
   - Verify Chrome is installed: `which google-chrome`
   - Check display environment: `echo $DISPLAY`
   - Review Chrome flags in the log file

4. **Proxy Not Working**
   - Verify proxy server is accessible
   - Check proxy format and credentials
   - Test proxy with curl: `curl --proxy http://proxy:port http://google.com`

### Logs and Debugging
- VNC setup log: `vnc_setup.log`
- Check running processes: `ps aux | grep vnc`
- Test VNC connection: `vncviewer localhost:5901`

## Security Considerations

1. **Default Password**: Change the default VNC password in production
2. **Firewall**: Ensure ports 5901 and 6080 are properly secured
3. **Proxy Credentials**: Use environment variables for proxy authentication
4. **SSH Tunneling**: Consider SSH tunneling for remote access

## Advanced Configuration

### Custom VNC Settings
```python
from vnc_setup import VNCServerManager

vnc = VNCServerManager(proxy_server="http://proxy:8080")
vnc.vnc_password = "your_secure_password"
vnc.vnc_port = 5902  # Custom port
vnc.vnc_web_port = 6081  # Custom web port
```

### Multiple Chrome Instances
```python
# Start multiple Chrome instances with different profiles
profiles = ["profile1", "profile2", "profile3"]
for profile in profiles:
    result = start_vnc_chrome_session(profile, proxy_server)
```

## Integration with Instagram Auto Poster

The VNC setup integrates seamlessly with your Instagram auto poster:

1. **Automatic Fallback**: When automated login fails, VNC starts automatically
2. **Manual Login**: Complete Instagram 2FA or captcha manually
3. **Session Transfer**: Return control to automated script after manual login
4. **Proxy Consistency**: Use same proxy for both automated and manual sessions

## Performance Tips

1. **Use Lightweight Desktop**: XFCE is pre-configured for optimal performance
2. **Proxy Selection**: Choose geographically close proxy servers
3. **Resource Monitoring**: Monitor CPU and memory usage during VNC sessions
4. **Clean Profiles**: Regularly clean Chrome profiles to prevent bloat 