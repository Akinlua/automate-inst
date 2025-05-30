# 🤖 Instagram Auto Poster - Complete Automation Workflow

## 🚨 **INTEGRATED SELENIUM SOLUTION**

This Instagram automation tool now uses **Selenium** for reliable Instagram interaction with a well-structured workflow. The system combines the best of both approaches:

- ✅ **Selenium-based Instagram interaction** (no API limitations)
- ✅ **Professional code structure** with proper logging and error handling
- ✅ **Chrome profile management** to eliminate popup issues
- ✅ **Scheduled posting** with content management
- ✅ **ChatGPT integration** for caption enhancement

---

## 📁 **File Overview**

### **Main Files**
- **`instagram_poster.py`** - Main automation script (Selenium-based)
- **`setup.py`** - Configuration setup script
- **`setup_chrome.py`** - Chrome profile setup for Instagram login
- **`test_setup.py`** - System verification and testing
- **`troubleshoot_chrome.py`** - Chrome/ChromeDriver troubleshooting

### **Legacy Files (V1)**
- **`test.py`** - Original Selenium script (now integrated into instagram_poster.py)

---

## 🚀 **Quick Start Guide**

### **Step 1: Install Dependencies**
```bash
pip install -r requirements.txt
```

### **Step 2: Install ChromeDriver**
```bash
# On macOS with Homebrew
brew install chromedriver

# Or download from: https://chromedriver.chromium.org/
```

### **Step 3: Run Setup**
```bash
python setup.py
```

### **Step 4: Set Up Chrome Profile & Login**
```bash
python setup_chrome.py
```
- Browser will open to Instagram
- **Log in manually** and complete 2FA if needed
- **Keep browser open** for 30 minutes to save session
- Your login will be saved to Chrome profile

### **Step 5: Test the System**
```bash
python test_setup.py
```

### **Step 6: Add Your Content**
- Add images to monthly folders (`content/1/`, `content/2/`, etc.)
- Edit text files in each folder with your captions

### **Step 7: Test Posting**
```bash
python instagram_poster.py post-now
```

### **Step 8: Start Scheduler**
```bash
python instagram_poster.py schedule
```

---

## 📋 **Posting Workflow**

### **Content Structure**
```
content/
├── 1/          # January
│   ├── image1.jpg
│   ├── image2.png
│   ├── post1.txt
│   └── post2.txt
├── 2/          # February
│   ├── image1.jpg
│   └── post1.txt
└── ...
```

### **How It Works**
1. **Scheduled Posting**: Runs daily at configured time
2. **Content Selection**: Randomly picks unused image + text combinations
3. **Caption Enhancement**: Uses ChatGPT to improve captions (optional)
4. **Selenium Automation**: Complete Instagram posting workflow
5. **Tracking**: Logs posted content to avoid duplicates

---

## ⚙️ **Environment Variables (.env)**

```bash
# Content Settings
CONTENT_DIR=content
POST_HOUR=12
POST_MINUTE=0

# ChatGPT Enhancement (Optional)
USE_CHATGPT=true
OPENAI_API_KEY=your_openai_api_key

# Chrome Profile (Set by setup_chrome.py)
CHROME_PROFILE_PATH=/path/to/chrome/profile
# OR for V2 approach:
CHROME_USER_DATA_DIR=/Users/user/Library/Application Support/Google/Chrome
CHROME_PROFILE_NAME=InstagramBot
```

---

## 🛠️ **Commands Reference**

### **Setup Commands**
```bash
python setup.py                    # Initial configuration
python setup_chrome.py             # Chrome profile setup
python test_setup.py               # Verify installation
python troubleshoot_chrome.py      # Diagnose Chrome issues
```

### **Posting Commands**
```bash
python instagram_poster.py create-sample   # Create sample folder structure
python instagram_poster.py post-now        # Post immediately
python instagram_poster.py schedule        # Start scheduler
```

---

## 🔧 **Troubleshooting**

### **Chrome Issues**
```bash
python troubleshoot_chrome.py
```

### **Common Problems**

**1. ChromeDriver not found**
```bash
brew install chromedriver
```

**2. Chrome popups**
- The integrated solution eliminates popup issues
- Uses Chrome's built-in profile system

**3. Login issues**
- Run `setup_chrome.py` again
- Make sure to complete manual login
- Keep browser open for full 30 minutes

**4. No content found**
```bash
python instagram_poster.py create-sample
```

---

## ✨ **Features**

### **🎯 Selenium Automation**
- Complete Instagram posting workflow
- Handles image upload, cropping, captions, and sharing
- Robust error handling with fallback selectors

### **📅 Smart Scheduling**
- Daily posting at configured time
- Avoids duplicate posts
- Tracks posting history

### **🤖 AI Enhancement**
- ChatGPT caption improvement
- Maintains original message intent
- Adds relevant hashtags

### **🔒 Secure Profile Management**
- Uses Chrome's built-in profile system
- No popup issues
- Persistent login sessions

### **📊 Professional Structure**
- Comprehensive logging
- Error handling and recovery
- Modular, maintainable code

---

## 🎉 **Success Indicators**

✅ **All tests pass** in `test_setup.py`  
✅ **Chrome opens without popups**  
✅ **Instagram login persists**  
✅ **Posts upload successfully**  
✅ **Scheduler runs continuously**  

---

## 📞 **Support**

If you encounter issues:

1. **Run diagnostics**: `python test_setup.py`
2. **Check Chrome**: `python troubleshoot_chrome.py`
3. **Verify content**: Check monthly folders have images and text files
4. **Test posting**: `python instagram_poster.py post-now`

The integrated solution provides a robust, professional Instagram automation system with excellent error handling and user experience! 