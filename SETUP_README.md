# Instagram Auto Poster - Easy Setup

This package contains everything you need to run the Instagram Auto Poster application.

## Quick Start

### Windows Users
1. Double-click `setup.bat`
2. Follow the prompts
3. The application will start automatically

### Linux/macOS Users
1. Open Terminal
2. Navigate to the extracted folder
3. Run: `./setup.sh`
4. Follow the prompts
5. The application will start automatically

## What the Setup Does

The setup scripts will automatically:

1. ✅ Check if Python 3.8+ is installed (install if needed)
2. ✅ Create a virtual environment 
3. ✅ Install all required dependencies
4. ✅ Create necessary folders and configuration files
5. ✅ Check for Google Chrome installation
6. ✅ Start the web application

## After Setup

Once the setup is complete, the web application will be running at:
**http://localhost:5000**

Open this URL in your browser to:
- Upload your images and captions
- Set up Instagram login
- Configure posting schedule
- Monitor posting activity

## First Time Usage

1. **Setup Chrome Profile**: Click "Setup Chrome Profile" in the web interface
2. **Upload Content**: Add images and captions for each month
3. **Configure Schedule**: Set your posting times and preferences
4. **Start Posting**: Enable the scheduler or post manually

## Requirements

- **Python 3.8+** (will be installed automatically)
- **Google Chrome** (must be installed manually)
- **Internet connection** (for downloading dependencies)

## Troubleshooting

### Python Installation Issues
- **Windows**: Download from https://python.org and ensure "Add to PATH" is checked
- **macOS**: The script will install via Homebrew automatically
- **Linux**: The script will use your package manager (apt/yum/dnf)

### Chrome Not Found
- Download and install Google Chrome from https://google.com/chrome
- The application needs Chrome for Instagram automation

### Permission Issues (Linux/macOS)
```bash
chmod +x setup.sh
./setup.sh
```

### Port Already in Use
If port 5000 is busy, edit `app.py` and change the port number:
```python
app.run(host='0.0.0.0', port=5001, debug=False)
```

## Manual Installation

If the automatic setup fails, you can install manually:

```bash
# Install Python 3.8+ from python.org
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
python app.py
```

## Support

For issues and questions, check the main README.md or create an issue in the project repository.

---

**Note**: This application is for educational purposes. Ensure you comply with Instagram's Terms of Service. 