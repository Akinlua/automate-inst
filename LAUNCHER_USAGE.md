# App Launchers Usage

## For Users

### Windows
- Double-click `setup.bat` to install and run
- Double-click `start.bat` to start the app (after setup)

### macOS
- Double-click `Instagram-Setup.app` to install and run
- Double-click `Instagram-Start.app` to start the app (after setup)

### Linux
- Double-click `Instagram-Setup.desktop` to install and run
- Double-click `Instagram-Start.desktop` to start the app (after setup)
- Or install to applications menu: 
  `cp *.desktop ~/.local/share/applications/`

## What Each Launcher Does

### Setup Launchers
- Installs Python if needed
- Creates virtual environment
- Installs all dependencies
- Creates necessary folders
- Starts the web application
- **One-time setup only**

### Start Launchers
- Quickly starts the app if already set up
- Opens web interface at http://localhost:5003
- **Use after initial setup is complete**

## Troubleshooting

If launchers don't work:
1. Make sure all files are in the same folder
2. On Linux: `chmod +x *.sh *.desktop`
3. On macOS: Right-click → Open (first time only)

