# Instagram Auto Poster - Distribution Package Files

## Files to Include in ZIP Package

### Core Application Files
- `app.py` - Main Flask web application
- `instagram_poster.py` - Core Instagram posting functionality
- `requirements.txt` - Python dependencies
- `setup_integration.py` - Chrome setup integration
- `vnc_setup.py` - VNC support for remote access
- `run_scheduler.py` - Background scheduler service

### Setup Scripts
- `setup.bat` - Windows automatic setup script
- `setup.sh` - Linux/macOS automatic setup script (make executable)
- `start.bat` - Windows quick start script
- `start.sh` - Linux/macOS quick start script (make executable)

### Configuration Files
- `.env.example` - Environment variables template
- `scheduler_settings.json` - Default scheduler settings (if exists)

### Documentation
- `README.md` - Main project documentation
- `SETUP_README.md` - Setup instructions for end users
- `DISTRIBUTION_FILES.md` - This file (for reference)

### Web Interface Files
- `templates/` - All HTML templates
- `static/` - CSS, JS, and other static files

### Sample Content (Optional)
- `content/` - Sample content structure (empty folders)

## Files to EXCLUDE from ZIP Package

### Development Files
- `.git/` - Git repository data
- `.github/` - GitHub workflows
- `__pycache__/` - Python cache files
- `.cursor/` - Cursor IDE files
- `.DS_Store` - macOS system files

### User Data Files
- `venv/` - Virtual environment (will be created by setup)
- `chrome_profile_instagram/` - User's Chrome profile
- `posted_content.json` - User's posting history
- `image_order.json` - User's image ordering
- `*.log` - Log files
- `scheduler_errors.json` - Error logs

### Environment Files
- `.env` - User's environment variables (contains sensitive data)

### Temporary Files
- `downloads/` - Downloaded files
- `*.tmp` - Temporary files
- `*.temp` - Temporary files

## Pre-Package Checklist

Before creating the ZIP package:

1. ✅ Test setup.bat on Windows
2. ✅ Test setup.sh on Linux/macOS  
3. ✅ Make shell scripts executable: `chmod +x setup.sh start.sh`
4. ✅ Verify all template and static files are included
5. ✅ Remove any sensitive data from included files
6. ✅ Test with fresh Python installation
7. ✅ Verify requirements.txt is up to date
8. ✅ Create clean content folder structure

## Distribution Commands

### Create ZIP Package (Linux/macOS)
```bash
# Make scripts executable
chmod +x setup.sh start.sh

# Create ZIP excluding unwanted files
zip -r instagram_auto_poster.zip . \
  -x "*.git*" "*__pycache__*" "*venv*" "*.log" \
  "*chrome_profile_instagram*" "*posted_content.json*" \
  "*image_order.json*" "*scheduler_errors.json*" \
  "*.DS_Store" "*downloads*" "*.env" ".cursor*" \
  "*.tmp" "*.temp"
```

### Create ZIP Package (Windows - PowerShell)
```powershell
# Create exclusion list
$exclude = @(
    ".git*", "__pycache__*", "venv*", "*.log",
    "chrome_profile_instagram*", "posted_content.json",
    "image_order.json", "scheduler_errors.json",
    ".DS_Store", "downloads*", ".env", ".cursor*",
    "*.tmp", "*.temp"
)

# Compress files
Compress-Archive -Path * -DestinationPath instagram_auto_poster.zip -Force
```

## Post-Distribution Testing

Test the package by:

1. Extract ZIP to new folder
2. Run setup script
3. Verify web interface loads
4. Test basic functionality
5. Confirm all dependencies install correctly

---

**Note**: Always test the distribution package on a clean system before releasing! 