# Instagram Auto Poster 📱

**Professional Instagram automation tool with Selenium and beautiful web interface**

## 🎯 Key Features

- **🌟 Beautiful Web Interface** - Modern Flask-based dashboard for easy management
- **⏰ Smart Scheduler** - Automated posting every 4 hours (configurable 1-24 hours)
- **📊 CSV-Based Content** - Organized monthly content with CSV captions
- **🖼️ Multiple Images** - Support for 1-10 images per post (configurable)
- **🤖 ChatGPT Integration** - AI-enhanced captions for better engagement
- **🔄 No Duplicates** - Advanced tracking to avoid reposting content
- **📱 Mobile Responsive** - Works perfectly on desktop and mobile
- **⚙️ Easy Configuration** - Web-based settings management

## 🚀 Quick Start

### 1. Installation
```bash
# Clone the repository
git clone <repository-url>
cd instagram_api

# Install dependencies
pip install -r requirements.txt
```

### 2. Setup Environment
Create a `.env` file:
```env
# Basic Settings
CONTENT_DIR=content
USE_CHATGPT=true
OPENAI_API_KEY=your_openai_api_key_here

# Chrome Settings (optional - auto-detected)
CHROME_PROFILE_PATH=/path/to/chrome/profile
CHROME_USER_DATA_DIR=/path/to/chrome/user/data
CHROME_PROFILE_NAME=InstagramBot
```

### 3. Launch Web Interface
```bash
python run.py
```
Visit **http://localhost:5000** to access the dashboard

### 4. Setup Content Structure
```bash
python instagram_poster.py create-sample
```

## 📋 Usage Guide

### 🌐 Web Interface (Recommended)

1. **Start the web server:**
   ```bash
   python run.py
   ```

2. **Access the dashboard:** http://localhost:5000

3. **Manage content by month:**
   - Upload images for each month
   - Upload CSV files with captions
   - View progress and statistics
   - Post content immediately

4. **Configure scheduler:**
   - Go to Settings page
   - Set number of images per post (1-10)
   - Configure posting interval (1-24 hours, default: 4 hours)
   - Enable/disable automatic posting

### ⏰ Background Scheduler

Start the automated posting service:
```bash
python run_scheduler.py
```

This will:
- Post content every 4 hours (or your configured interval)
- Use the number of images setting from web interface
- Select images randomly and captions sequentially
- Track used content to avoid duplicates

### 📱 Command Line Usage

```bash
# Create sample structure
python instagram_poster.py create-sample

# Post immediately
python instagram_poster.py post-now

# Run scheduler (deprecated - use run_scheduler.py)
python instagram_poster.py schedule
```

## 🔧 Configuration

### Scheduler Settings

Configure via web interface at `/settings` or using API:

```bash
# Get current settings
curl http://localhost:5000/api/scheduler/settings

# Update settings
curl -X POST http://localhost:5000/api/scheduler/settings \
  -H "Content-Type: application/json" \
  -d '{
    "num_images": 3,
    "post_interval_hours": 6,
    "enabled": true
  }'
```

**Available Settings:**
- `num_images`: Number of images per post (1-10)
- `post_interval_hours`: Posting interval in hours (1-24)
- `enabled`: Enable/disable automatic posting

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `CONTENT_DIR` | Content directory path | `content` |
| `USE_CHATGPT` | Enable ChatGPT enhancement | `false` |
| `OPENAI_API_KEY` | Your OpenAI API key | - |
| `CHROME_PROFILE_PATH` | Chrome profile path | Auto-detected |
| `CHROME_USER_DATA_DIR` | Chrome user data directory | Auto-detected |
| `CHROME_PROFILE_NAME` | Chrome profile name | `InstagramBot` |

## 📁 Content Structure

```
content/
├── 1/                  # January
│   ├── captions.csv    # Captions file
│   ├── image1.jpg      # Images
│   ├── image2.png
│   └── ...
├── 2/                  # February
│   ├── captions.csv
│   └── ...
└── ...                 # Other months (3-12)
```

### CSV Format

Each month's `captions.csv` should contain one caption per line:
```csv
"First amazing post for January! 🌟 #january #content"
"Second incredible post! ✨ #instagram #amazing"
"Third fantastic post! 🚀 #social #media"
```

## 🎯 API Endpoints

### Content Management
- `GET /` - Dashboard
- `GET /month/<int:month_num>` - Month detail page
- `POST /upload_images/<int:month_num>` - Upload images
- `POST /upload_csv/<int:month_num>` - Upload captions CSV

### Posting
- `POST /post_now` - Post content immediately

### Scheduler Management
- `GET /api/scheduler/settings` - Get scheduler settings
- `POST /api/scheduler/settings` - Update scheduler settings
- `GET /api/scheduler/status` - Get scheduler status
- `POST /api/scheduler/start` - Start scheduler command

### Statistics
- `GET /api/stats` - Get all months statistics
- `GET /api/stats?month=<num>` - Get specific month stats

## 🛠️ Advanced Features

### Multiple Images per Post
- Configure 1-10 images per post via web interface
- Images are selected randomly from the current month's folder
- Each post uses a sequential caption from the CSV file

### Smart Content Selection
- **Images**: Random selection to keep content fresh
- **Captions**: Sequential order for consistent messaging
- **Tracking**: Prevents duplicate content posting

### ChatGPT Enhancement
When enabled, captions are enhanced with AI for better engagement:
```python
# Original caption
"Great sunset photo"

# Enhanced caption
"Witnessing this breathtaking sunset reminds me why I love photography 📸✨ There's something magical about golden hour that never gets old! 🌅 #sunset #photography #goldenhour #nature #peaceful"
```

## 🔄 Workflow Example

### Daily Automated Posting (Every 4 Hours)

1. **6:00 AM** - Post with 2 random images + sequential caption #1
2. **10:00 AM** - Post with 3 random images + sequential caption #2  
3. **2:00 PM** - Post with 1 random image + sequential caption #3
4. **6:00 PM** - Post with 2 random images + sequential caption #4
5. **10:00 PM** - Post with 4 random images + sequential caption #5

### Manual Posting via Web Interface

1. Visit dashboard at http://localhost:5000
2. Click "Post Now" on current month
3. Select number of images (1-5)
4. Content posts immediately

## 📊 Statistics & Tracking

The web interface provides comprehensive statistics:
- **Images uploaded** per month
- **Captions available** per month  
- **Posts used** vs available
- **Progress tracking** with visual progress bars
- **Last post timestamp** for each month

## 🎨 Web Interface Features

### Beautiful Dashboard
- **Monthly overview** with visual statistics
- **Progress bars** showing posting progress
- **Current month highlighting**
- **Quick actions** for immediate posting

### Month Management
- **Drag & drop file uploads**
- **Image gallery** with previews
- **Caption management** with CSV support
- **Real-time statistics** updates

### Settings Panel
- **Scheduler configuration** with visual controls
- **Status monitoring** with real-time updates
- **Environment documentation**
- **One-click scheduler start**

## 🚨 Troubleshooting

### Common Issues

1. **Chrome Profile Not Set Up**
   ```bash
   # Run setup first (if available)
   python setup_chrome.py
   ```

2. **No Content Available**
   ```bash
   # Create sample structure
   python instagram_poster.py create-sample
   # Then add your own images and captions
   ```

3. **Scheduler Not Posting**
   - Check settings via web interface
   - Ensure scheduler is enabled
   - Verify content is available for current month
   - Check logs in `instagram_poster.log`

4. **Image Upload Issues**
   - Supported formats: JPG, PNG, GIF, WebP
   - Maximum file size: 16MB per image
   - Ensure proper file permissions

### Logs

Check logs for debugging:
```bash
tail -f instagram_poster.log
```

## 🔮 Future Enhancements

- **Instagram Stories** support
- **Reels automation** 
- **Advanced scheduling** (specific times, days)
- **Analytics integration**
- **Multiple account support**
- **Content templates**
- **Hashtag optimization**

## 📝 License

This project is for educational purposes. Make sure to comply with Instagram's Terms of Service when using automation tools.

---

**Built with ❤️ using Selenium, Flask, and modern web technologies**
