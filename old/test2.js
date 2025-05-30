const Instagram = require('instagram-web-api');
const fs = require('fs');
const path = require('path');
const request = require('request-promise-native');
const { Cookie } = require('tough-cookie');
require('dotenv').config();

class InstagramWebAutomation {
    constructor() {
        this.client = null;
        this.isLoggedIn = false;
    }

    async loginWithManualCookies() {
        /**
         * MANUAL COOKIE EXTRACTION METHOD
         * 
         * Step 1: Go to Instagram.com in Chrome while logged in
         * Step 2: Open DevTools (F12)
         * Step 3: Go to Application tab → Cookies → https://www.instagram.com
         * Step 4: Copy the EXACT values and paste them in your .env file:
         * 
         * IMPORTANT: Cookies must be fresh (extracted within the last few hours)
         * 
         * How to extract:
         * - sessionid: Copy the entire value (looks like: 48495039000%3ATDmeMi8QeeqALA%3A2%3A...)
         * - csrftoken: Copy the value (32 random characters)
         * - ds_user_id: Copy the number (your Instagram user ID)
         * 
         * INSTAGRAM_SESSION_ID=your_sessionid_value_here
         * INSTAGRAM_CSRF_TOKEN=your_csrftoken_value_here
         * INSTAGRAM_DS_USER_ID=your_ds_user_id_value_here
         */
        
        let sessionId = process.env.INSTAGRAM_SESSION_ID;
        let csrfToken = process.env.INSTAGRAM_CSRF_TOKEN;
        let dsUserId = process.env.INSTAGRAM_DS_USER_ID;

        if (!sessionId || !csrfToken) {
            console.error('Missing Instagram cookies in .env file');
            console.log('Please add these to your .env file:');
            console.log('INSTAGRAM_SESSION_ID=your_sessionid_value');
            console.log('INSTAGRAM_CSRF_TOKEN=your_csrftoken_value');
            console.log('INSTAGRAM_DS_USER_ID=your_ds_user_id_value (optional)');
            return false;
        }

        try {
            // Decode URL-encoded cookie values and trim any whitespace
            sessionId = decodeURIComponent(sessionId.trim());
            csrfToken = csrfToken.trim();
            if (dsUserId) {
                dsUserId = dsUserId.trim();
            }

            console.log('Using session ID (first 10 chars):', sessionId.substring(0, 10) + '...');
            console.log('Using CSRF token (first 10 chars):', csrfToken.substring(0, 10) + '...');

            // Create a cookie jar and manually add cookies
            const cookieJar = request.jar();
            
            // Add cookies using cookie strings format
            cookieJar.setCookie(`sessionid=${sessionId}; Domain=.instagram.com; Path=/; Secure; HttpOnly`, 'https://www.instagram.com');
            cookieJar.setCookie(`csrftoken=${csrfToken}; Domain=.instagram.com; Path=/; Secure`, 'https://www.instagram.com');

            // Add ds_user_id cookie if provided
            if (dsUserId) {
                cookieJar.setCookie(`ds_user_id=${dsUserId}; Domain=.instagram.com; Path=/; Secure`, 'https://www.instagram.com');
            }

            console.log('Cookie jar created successfully');

            // Create Instagram client with the prepared cookie store
            this.client = new Instagram({
                cookieStore: cookieJar.store
            });

            console.log('Instagram client created, testing connection...');

            // Test the session by getting profile info
            const profile = await this.client.getProfile();
            console.log('Profile response:', profile);
            
            if (!profile || !profile.username) {
                console.error('\n❌ Cookie authentication failed!');
                console.log('\n🔧 To fix this:');
                console.log('1. Go to https://www.instagram.com in Chrome (while logged in)');
                console.log('2. Press F12 to open DevTools');
                console.log('3. Go to Application tab → Storage → Cookies → https://www.instagram.com');
                console.log('4. Copy these cookie values and update your .env file:');
                console.log('   - sessionid (the long encoded string)');
                console.log('   - csrftoken (32 random characters)');
                console.log('   - ds_user_id (your user ID number)');
                console.log('\n⚠️  Make sure cookies are fresh (extracted within the last few hours)');
                throw new Error('Invalid response from getProfile - cookies may be expired or invalid');
            }
            
            console.log(`✅ Successfully logged in using manual cookies for: ${profile.username}`);
            
            this.isLoggedIn = true;
            return true;

        } catch (error) {
            console.error('Failed to login with manual cookies:', error.message);
            if (error.message.includes('getProfile')) {
                console.log('\n💡 Tip: Try extracting fresh cookies from Instagram.com in your browser');
            }
            return false;
        }
    }

    async loginWithSavedCookies() {
        /**
         * Use previously saved cookie file
         */
        const cookieFile = './instagram_cookies.json';
        
        if (!fs.existsSync(cookieFile)) {
            console.log('No saved cookies found');
            return false;
        }

        try {
            this.client = new Instagram({
                cookiesPath: cookieFile
            });

            // Test if saved cookies still work
            const profile = await this.client.getProfile();
            console.log(`Successfully logged in using saved cookies for: ${profile.username}`);
            
            this.isLoggedIn = true;
            return true;

        } catch (error) {
            console.error('Saved cookies are invalid:', error.message);
            // Delete invalid cookie file
            fs.unlinkSync(cookieFile);
            return false;
        }
    }

    async loginWithCredentials() {
        try {
            this.client = new Instagram({
                username: process.env.INSTAGRAM_USERNAME,
                password: process.env.INSTAGRAM_PASSWORD,
                cookiesPath: './instagram_cookies.json'
            });

            await this.client.login();
            console.log('Successfully logged into Instagram via credentials');
            this.isLoggedIn = true;
            return true;
        } catch (error) {
            console.error('Failed to login with credentials:', error.message);
            return false;
        }
    }

    async login() {
        // Try multiple login methods in order of preference
        console.log('Attempting login with saved cookies...');
        if (await this.loginWithSavedCookies()) {
            return true;
        }

        console.log('Attempting login with manual cookies from .env...');
        if (await this.loginWithManualCookies()) {
            return true;
        }

        console.log('Attempting login with username/password...');
        if (await this.loginWithCredentials()) {
            return true;
        }

        console.error('All login methods failed');
        return false;
    }

    async getMonthFolders() {
        const baseDir = process.env.BASE_DIR || 'content';
        const folders = fs.readdirSync(baseDir, { withFileTypes: true })
            .filter(dirent => dirent.isDirectory() && !isNaN(dirent.name))
            .map(dirent => path.join(baseDir, dirent.name))
            .sort();
        
        console.log(`Found ${folders.length} month folders`);
        return folders;
    }

    getContentForMonth(monthFolder) {
        const txtFiles = fs.readdirSync(monthFolder)
            .filter(file => file.endsWith('.txt'))
            .map(file => path.join(monthFolder, file));

        const imageFiles = fs.readdirSync(monthFolder)
            .filter(file => /\.(jpg|jpeg|png)$/i.test(file))
            .map(file => path.join(monthFolder, file));

        console.log(`Month ${path.basename(monthFolder)}: ${txtFiles.length} text files, ${imageFiles.length} images`);
        return { txtFiles, imageFiles };
    }

    readTextFiles(txtFiles) {
        let fullText = '';
        txtFiles.forEach(file => {
            try {
                const content = fs.readFileSync(file, 'utf8');
                fullText += content + '\n\n';
            } catch (error) {
                console.error(`Error reading ${file}:`, error.message);
            }
        });
        return fullText.trim();
    }

    async enhanceTextWithGPT(text) {
        // Using OpenAI API
        const { Configuration, OpenAIApi } = require('openai');
        
        const configuration = new Configuration({
            apiKey: process.env.OPENAI_API_KEY,
        });
        const openai = new OpenAIApi(configuration);

        try {
            const response = await openai.createChatCompletion({
                model: "gpt-4",
                messages: [
                    {
                        role: "system", 
                        content: "You are a social media expert who creates engaging Instagram captions."
                    },
                    {
                        role: "user", 
                        content: `Make this text more engaging as an Instagram caption: ${text}`
                    }
                ],
                max_tokens: 300
            });

            return response.data.choices[0].message.content.trim();
        } catch (error) {
            console.error('Error enhancing text with GPT:', error.message);
            return text;
        }
    }

    async postToInstagram(imagePath, caption) {
        if (!this.isLoggedIn) {
            console.error('Cannot post: Not logged in');
            return false;
        }

        try {
            // Read image file
            const imageBuffer = fs.readFileSync(imagePath);
            
            // Upload photo
            const result = await this.client.uploadPhoto({
                photo: imageBuffer,
                caption: caption + '\n\n#monthlypost #automation'
            });

            console.log(`Successfully posted: ${path.basename(imagePath)}`);
            return true;
        } catch (error) {
            console.error('Failed to post to Instagram:', error.message);
            return false;
        }
    }

    async processMonth(monthFolder, force = false) {
        const monthNumber = path.basename(monthFolder);
        const statusFile = path.join(monthFolder, '.posted');

        if (fs.existsSync(statusFile) && !force) {
            console.log(`Month ${monthNumber} already processed. Skipping...`);
            return;
        }

        const { txtFiles, imageFiles } = this.getContentForMonth(monthFolder);

        if (txtFiles.length === 0 || imageFiles.length === 0) {
            console.log(`Month ${monthNumber} missing content. Skipping...`);
            return;
        }

        const imagePath = imageFiles[Math.floor(Math.random() * imageFiles.length)];
        const fullText = this.readTextFiles(txtFiles);
        const caption = await this.enhanceTextWithGPT(fullText);
        
        const success = await this.postToInstagram(imagePath, caption);
        
        if (success) {
            fs.writeFileSync(statusFile, new Date().toISOString());
            console.log(`Month ${monthNumber} successfully processed`);
        }
    }

    async run(specificMonth = null, force = false) {
        if (!(await this.login())) {
            console.error('Failed to login. Exiting...');
            return;
        }

        const monthFolders = await this.getMonthFolders();

        if (specificMonth) {
            const targetFolder = path.join(process.env.BASE_DIR || 'content', specificMonth);
            if (fs.existsSync(targetFolder)) {
                console.log(`Processing specific month: ${specificMonth}`);
                await this.processMonth(targetFolder, force);
            } else {
                console.error(`Month folder '${specificMonth}' not found`);
            }
        } else {
            for (const monthFolder of monthFolders) {
                await this.processMonth(monthFolder, force);
                await new Promise(resolve => setTimeout(resolve, 60000));
            }
        }
    }
}

// Usage
const args = process.argv.slice(2);
const specificMonth = args.includes('--month') ? args[args.indexOf('--month') + 1] : null;
const force = args.includes('--force');

const automation = new InstagramWebAutomation();
automation.run(specificMonth, force).catch(console.error);