# Automated Instagram Chrome Profile Setup

This guide explains how to use the automated Chrome profile setup that will automatically log in to Instagram and save your session.

## Prerequisites

1. Make sure you have all dependencies installed:
   ```bash
   pip install -r requirements.txt
   ```

2. Configure your Instagram credentials in the `.env` file:
   ```
   INSTAGRAM_USERNAME=your_instagram_username
   INSTAGRAM_PASSWORD=your_instagram_password
   ```

## How to Use

1. **Add your credentials to `.env` file:**
   Open the `.env` file and fill in your Instagram username and password:
   ```
   INSTAGRAM_USERNAME=your_actual_username
   INSTAGRAM_PASSWORD=your_actual_password
   ```

2. **Run the automated setup:**
   ```bash
   python3 setup_chrome.py
   ```

3. **What the script does automatically:**
   - Opens Chrome with a custom profile
   - Checks if you're already logged in (skips login if already authenticated)
   - Navigates to Instagram login page (if needed)
   - Automatically fills in your username and password
   - Clicks the login button
   - **Handles email verification** if Instagram requires it
   - Handles the "Save Info" prompt if it appears
   - Verifies that login was successful
   - Saves the session to the Chrome profile

4. **Email Verification Handling:**
   - If Instagram requires email verification, the script will detect it automatically
   - You'll see a prompt asking you to enter the verification code
   - Check your email for the code and enter it when prompted
   - The script will automatically submit the code and continue
   - You get 3 attempts to enter the correct code

5. **After setup:**
   - The browser will stay open for 2 minutes to ensure the session is saved
   - You can close the terminal once you see "Setup completed successfully!"
   - Your Instagram session is now saved and ready to use

## What Gets Saved

- **Chrome Profile:** Saved to `chrome_profile_instagram/` directory
- **Instagram Session:** Login cookies and session data
- **Profile Path:** Automatically added to `.env` file as `CHROME_PROFILE_PATH`

## Troubleshooting

### If you're already logged in:
- The script will detect this and skip the login process
- Your existing session will be preserved

### If automatic login fails:
- Check that your username and password are correct in the `.env` file
- The script will prompt you to complete login manually
- After manual login, press Enter to continue

### If email verification appears:
- Check your email for the verification code
- Enter the code when prompted (you have 3 attempts)
- The script will automatically continue after successful verification

### If "Save Info" button doesn't appear:
- This is normal - Instagram doesn't always show this prompt
- The script will continue and save the session anyway

### If you see "Login verification failed":
- The script will ask you to confirm if you're logged in
- Check the browser - if you see your Instagram home feed, answer "y"
- If you're not logged in, answer "n" and try running the script again

## Security Notes

- Your credentials are stored only in your local `.env` file
- The Chrome profile is saved locally on your machine
- No credentials are sent anywhere except to Instagram's official login
- Email verification codes are entered locally and sent directly to Instagram

## Next Steps

After successful setup:
1. Run the main application: `python3 app.py`
2. The app will automatically use your saved Instagram session
3. No need to log in manually each time

## Advanced Features

### Smart Login Detection
- Automatically detects if you're already logged in
- Skips unnecessary login steps if session exists
- Preserves existing authentication state

### Email Verification Support
- Handles Instagram's email verification challenge
- Interactive prompts for verification codes
- Multiple attempts with error handling

### Comprehensive Error Handling
- Multiple fallback strategies for each step
- Manual override options when automation fails
- Detailed logging for troubleshooting

## CSS Classes Used

The script uses these Instagram CSS classes to identify elements:
- Username/Email field: `._aa4b._add6._ac4d._ap35`
- Password field: `._aa4b._add6._ac4d._ap35[type="password"]`
- Login button: `._aswp._aswr._aswu._asw_._asx2[type="submit"]`
- Save Info button: `._aswp._aswr._aswu._asw_._asx2[type="button"]`
- Verification code input: `.x1i10hfl.xggy1nq.xtpw4lu...` (long class chain)
- Continue button: `.x1ja2u2z.x78zum5.x2lah0s...` (long class chain)

If Instagram updates their UI, these classes might change and the script may need updates. 