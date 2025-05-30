# Instagram Auto Poster 📸

Automatically post content to Instagram from organized monthly folders. This script reads text files and images from monthly directories and posts them to Instagram on a schedule, with optional ChatGPT text enhancement.

## Features ✨

- 📁 **Monthly Organization**: Organize content by month (folders 1-12)
- 🤖 **ChatGPT Integration**: Enhance text with AI (optional)
- 📅 **Smart Scheduling**: Daily posting with customizable time
- 🔄 **Duplicate Prevention**: Tracks posted content to avoid repeats
- 🖼️ **Image Processing**: Automatic image resizing for Instagram
- 📝 **Multiple Text Files**: Support for multiple posts per month
- 🔐 **Secure**: Environment-based credential management
- 📊 **Logging**: Comprehensive logging for monitoring

## Folder Structure 📂

```
content/
├── 1/          # January
│   ├── image1.jpg
│   ├── image2.png
│   ├── post1.txt
│   └── post2.txt
├── 2/          # February
│   ├── photo1.jpg
│   └── caption1.txt
├── 3/          # March
│   └── ...
└── 12/         # December
    └── ...
```

## Quick Start 🚀

### 1. Setup

```bash
# Clone or download the files
cd instagram_api

# Run the setup script
python setup.py
```

The setup script will:
- Install required dependencies
- Configure your Instagram credentials
- Set up ChatGPT integration (optional)
- Create the monthly folder structure
- Set posting schedule

### 2. Add Your Content

1. **Add Images**: Place your images in the appropriate monthly folders (1-12)
   - Supported formats: JPG, JPEG, PNG, WEBP
   - Images will be automatically resized for Instagram

2. **Add Text**: Create `.txt` files with your captions
   - You can have multiple text files per month
   - The script will randomly combine images and texts

### 3. Test and Run

```bash
# Test posting immediately
python instagram_poster.py post-now

# Start the scheduler (runs continuously)
python instagram_poster.py schedule

# Create sample structure only
python instagram_poster.py create-sample
```

## Manual Setup 🔧

If you prefer manual setup:

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Configure Environment

Copy `.env.example` to `.env` and fill in your details:

```bash
cp .env.example .env
```

Edit `.env`:
```env
INSTAGRAM_USERNAME=your_username
INSTAGRAM_PASSWORD=your_password
OPENAI_API_KEY=your_openai_key  # Optional
CONTENT_DIR=content
POST_HOUR=12
POST_MINUTE=0
USE_CHATGPT=false
```

### 3. Create Folder Structure

```bash
python instagram_poster.py create-sample
```

## Configuration Options ⚙️

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `INSTAGRAM_USERNAME` | Your Instagram username | Required |
| `INSTAGRAM_PASSWORD` | Your Instagram password | Required |
| `OPENAI_API_KEY` | OpenAI API key for ChatGPT | Optional |
| `CONTENT_DIR` | Directory containing monthly folders | `content` |
| `POST_HOUR` | Hour to post (0-23) | `12` |
| `POST_MINUTE` | Minute to post (0-59) | `0` |
| `USE_CHATGPT` | Enable ChatGPT enhancement | `false` |

### ChatGPT Integration

When enabled, ChatGPT will:
- Enhance your text to be more engaging
- Add relevant hashtags
- Maintain the original message intent
- Make content more Instagram-friendly

## Usage Examples 💡

### Basic Usage

```bash
# Post content for current month immediately
python instagram_poster.py post-now

# Start scheduler (posts daily at configured time)
python instagram_poster.py schedule
```

### Content Organization

**Example for March (folder `3`):**
```
content/3/
├── beach_sunset.jpg
├── mountain_view.png
├── vacation_post.txt      # "Amazing sunset at the beach! 🌅"
└── adventure_post.txt     # "Mountain adventures are the best!"
```

The script will randomly combine:
- `beach_sunset.jpg` + `vacation_post.txt`, OR
- `beach_sunset.jpg` + `adventure_post.txt`, OR
- `mountain_view.png` + `vacation_post.txt`, OR
- `mountain_view.png` + `adventure_post.txt`

### Running as a Server

For continuous operation on a server:

```bash
# Using screen (recommended for servers)
screen -S instagram_poster
python instagram_poster.py schedule
# Press Ctrl+A, then D to detach

# Using nohup
nohup python instagram_poster.py schedule > poster.log 2>&1 &
```

## Monitoring 📊

### Log Files

- `instagram_poster.log`: Application logs
- `posted_content.json`: Tracks posted content to prevent duplicates

### Log Levels

The script logs:
- ✅ Successful posts
- ⚠️ Warnings (missing content, etc.)
- ❌ Errors (login failures, API issues)
- ℹ️ Info (startup, scheduling)

## Troubleshooting 🔧

### Common Issues

**1. Login Failed**
```
Error: Failed to login to Instagram
```
- Check username/password in `.env`
- Instagram may require 2FA - use app passwords
- Try logging in manually first

**2. No Content Found**
```
Warning: No folder found for current month
```
- Ensure folder exists (e.g., `content/5/` for May)
- Check folder contains both images and text files

**3. Image Upload Failed**
```
Error: Error posting to Instagram
```
- Check image format (JPG, PNG, WEBP)
- Ensure image isn't corrupted
- Check Instagram API limits

**4. ChatGPT Not Working**
```
Error: Error enhancing text with ChatGPT
```
- Verify OpenAI API key in `.env`
- Check API quota/billing
- Set `USE_CHATGPT=false` to disable

### Instagram API Limits

- **Posts per day**: ~50-100 (varies by account)
- **Rate limiting**: Built-in delays between requests
- **Account age**: Newer accounts have stricter limits

### Best Practices

1. **Start Small**: Test with a few posts before full automation
2. **Vary Content**: Use different images and texts
3. **Monitor Logs**: Check logs regularly for issues
4. **Backup**: Keep backups of your content and `posted_content.json`
5. **Security**: Never share your `.env` file

## File Structure 📁

```
instagram_api/
├── instagram_poster.py     # Main application
├── setup.py               # Setup script
├── requirements.txt       # Python dependencies
├── .env.example          # Environment template
├── .env                  # Your credentials (create this)
├── README.md             # This file
├── content/              # Your content directory
│   ├── 1/               # January
│   ├── 2/               # February
│   └── ...
├── instagram_poster.log  # Application logs
└── posted_content.json   # Posted content tracking
```

## Security 🔐

- **Never commit `.env`** to version control
- **Use strong passwords** for Instagram
- **Enable 2FA** on Instagram account
- **Rotate API keys** regularly
- **Monitor account activity** for unusual behavior

## Contributing 🤝

Feel free to submit issues and enhancement requests!

## License 📄

This project is for educational purposes. Please comply with Instagram's Terms of Service and API guidelines.

---

**⚠️ Disclaimer**: Use responsibly and in compliance with Instagram's Terms of Service. The authors are not responsible for any account restrictions or violations. # automate-inst
