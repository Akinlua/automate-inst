# Instagram Auto Poster - Production Dockerfile
FROM ubuntu:22.04

# Prevent interactive prompts during package installation
ENV DEBIAN_FRONTEND=noninteractive
ENV TZ=UTC

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV DISPLAY=:1
ENV VNC_DISPLAY=:1
ENV VNC_PORT=5901
ENV VNC_WEB_PORT=6080
ENV FLASK_ENV=production
ENV FLASK_APP=app.py

# Create app user and directory
RUN useradd -m -s /bin/bash appuser && \
    mkdir -p /app && \
    chown -R appuser:appuser /app

# Install system dependencies
RUN apt-get update && \
    apt-get install -y \
    python3 \
    python3-pip \
    python3-venv \
    wget \
    curl \
    gnupg \
    software-properties-common \
    apt-transport-https \
    ca-certificates \
    unzip \
    xvfb \
    fluxbox \
    x11vnc \
    tightvncserver \
    websockify \
    xterm \
    sudo \
    fonts-dejavu-core \
    fonts-liberation \
    libnss3 \
    libatk-bridge2.0-0 \
    libdrm2 \
    libxss1 \
    libgconf-2-4 \
    libxrandr2 \
    libasound2 \
    libpangocairo-1.0-0 \
    libatk1.0-0 \
    libcairo-gobject2 \
    libgtk-3-0 \
    libgdk-pixbuf2.0-0 \
    libxcomposite1 \
    libxcursor1 \
    libxdamage1 \
    libxext6 \
    libxfixes3 \
    libxi6 \
    libxrender1 \
    libxtst6 \
    gconf-service \
    libasound2 \
    libatk1.0-0 \
    libc6 \
    libcairo2 \
    libcups2 \
    libdbus-1-3 \
    libexpat1 \
    libfontconfig1 \
    libgcc1 \
    libgconf-2-4 \
    libgdk-pixbuf2.0-0 \
    libglib2.0-0 \
    libgtk-3-0 \
    libnspr4 \
    libpango-1.0-0 \
    libpangocairo-1.0-0 \
    libstdc++6 \
    libx11-6 \
    libx11-xcb1 \
    libxcb1 \
    libxcomposite1 \
    libxcursor1 \
    libxdamage1 \
    libxext6 \
    libxfixes3 \
    libxi6 \
    libxrandr2 \
    libxrender1 \
    libxss1 \
    libxtst6 \
    ca-certificates \
    fonts-liberation \
    libappindicator1 \
    libnss3 \
    lsb-release \
    xdg-utils \
    && rm -rf /var/lib/apt/lists/*

# Install Google Chrome
RUN wget -q -O - https://dl.google.com/linux/linux_signing_key.pub | apt-key add - && \
    echo "deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main" > /etc/apt/sources.list.d/google-chrome.list && \
    apt-get update && \
    apt-get install -y google-chrome-stable && \
    rm -rf /var/lib/apt/lists/*

# Install ChromeDriver
RUN CHROMEDRIVER_VERSION=$(wget -qO- https://chromedriver.storage.googleapis.com/LATEST_RELEASE) && \
    wget -O /tmp/chromedriver.zip https://chromedriver.storage.googleapis.com/${CHROMEDRIVER_VERSION}/chromedriver_linux64.zip && \
    unzip /tmp/chromedriver.zip -d /tmp/ && \
    mv /tmp/chromedriver /usr/local/bin/chromedriver && \
    chmod +x /usr/local/bin/chromedriver && \
    rm /tmp/chromedriver.zip

# Set working directory
WORKDIR /app

# Copy requirements first (for better caching)
COPY requirements.txt .

# Install Python dependencies
RUN pip3 install --no-cache-dir -r requirements.txt

# Copy application code
COPY --chown=appuser:appuser . .

# Create necessary directories
RUN mkdir -p /app/content /app/uploads /app/logs /app/chrome_profile_instagram /app/.vnc && \
    chown -R appuser:appuser /app

# Give appuser sudo privileges for fixing permissions
RUN echo "appuser ALL=(ALL) NOPASSWD: /bin/chown, /bin/chmod" >> /etc/sudoers

# Copy and set up VNC configuration
RUN mkdir -p /home/appuser/.vnc && \
    echo "#!/bin/bash\nfluxbox &" > /home/appuser/.vnc/xstartup && \
    chmod +x /home/appuser/.vnc/xstartup && \
    chown -R appuser:appuser /home/appuser/.vnc

# Set VNC password (will be overridden by environment variable)
RUN echo "password" | vncpasswd -f > /home/appuser/.vnc/passwd && \
    chmod 600 /home/appuser/.vnc/passwd && \
    chown appuser:appuser /home/appuser/.vnc/passwd

# Switch to app user
USER appuser

# Create startup script
RUN echo '#!/bin/bash\n\
set -e\n\
\n\
echo "Starting Instagram Auto Poster Docker Container..."\n\
\n\
# Fix permissions for mounted directories\n\
echo "Setting up directory permissions..."\n\
sudo chown -R appuser:appuser /app/content /app/logs /app/uploads 2>/dev/null || true\n\
chmod -R 755 /app/content /app/logs /app/uploads 2>/dev/null || true\n\
\n\
# Ensure JSON files exist and are proper files (not directories)\n\
echo "Initializing application files..."\n\
for file in posted_content.json scheduler_settings.json image_order.json scheduler_errors.json; do\n\
    if [ -d "$file" ]; then\n\
        echo "Removing directory $file and creating as file"\n\
        rm -rf "$file"\n\
    fi\n\
    if [ ! -f "$file" ]; then\n\
        case "$file" in\n\
            "posted_content.json") echo "{}" > "$file" ;;\n\
            "scheduler_settings.json") echo "{\"enabled\": false, \"hour\": 12, \"minute\": 0}" > "$file" ;;\n\
            "image_order.json") echo "[]" > "$file" ;;\n\
            "scheduler_errors.json") echo "[]" > "$file" ;;\n\
        esac\n\
        echo "Created $file"\n\
    fi\n\
done\n\
\n\
# Set VNC password from environment variable\n\
if [ ! -z "$VNC_PASSWORD" ]; then\n\
    echo "$VNC_PASSWORD" | vncpasswd -f > ~/.vnc/passwd\n\
    chmod 600 ~/.vnc/passwd\n\
fi\n\
\n\
# Start VNC server in background\n\
echo "Starting VNC server..."\n\
vncserver :1 -geometry 1920x1080 -depth 24 -dpi 96 > /dev/null 2>&1 || true\n\
\n\
# Start websockify for web VNC access\n\
echo "Starting websockify..."\n\
websockify --web=/usr/share/novnc/ 6080 localhost:5901 > /dev/null 2>&1 &\n\
\n\
# Wait a moment for services to start\n\
sleep 3\n\
\n\
echo "Starting Flask application..."\n\
# Start the Flask application\n\
python3 app.py\n\
' > /app/start.sh && chmod +x /app/start.sh

# Expose ports
EXPOSE 5002 6080 5901

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:5002/health || exit 1

# Set the startup command
CMD ["/app/start.sh"] 