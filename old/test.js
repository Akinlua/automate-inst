const Instagram = require('instagram-web-api');
const fs = require('fs');
const path = require('path');
require('dotenv').config();

class InstagramWebAutomation {
    constructor() {
        this.client = new Instagram({
            username: process.env.INSTAGRAM_USERNAME,
            password: process.env.INSTAGRAM_PASSWORD
        });
        this.isLoggedIn = false;
    }

    async login() {
        try {
            await this.client.login();
            console.log('Successfully logged into Instagram via Web API');
            this.isLoggedIn = true;
            return true;
        } catch (error) {
            console.error('Failed to login:', error.message);
            this.isLoggedIn = false;
            return false;
        }
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

        // Check if already processed
        if (fs.existsSync(statusFile) && !force) {
            console.log(`Month ${monthNumber} already processed. Skipping...`);
            return;
        }

        const { txtFiles, imageFiles } = this.getContentForMonth(monthFolder);

        if (txtFiles.length === 0 || imageFiles.length === 0) {
            console.log(`Month ${monthNumber} missing content. Skipping...`);
            return;
        }

        // Random image selection
        const imagePath = imageFiles[Math.floor(Math.random() * imageFiles.length)];
        
        // Get text content
        const fullText = this.readTextFiles(txtFiles);
        
        // Enhance with GPT
        const caption = await this.enhanceTextWithGPT(fullText);
        
        // Post to Instagram
        const success = await this.postToInstagram(imagePath, caption);
        
        if (success) {
            // Mark as posted
            fs.writeFileSync(statusFile, new Date().toISOString());
            console.log(`Month ${monthNumber} successfully processed`);
        }
    }

    async run(specificMonth = null, force = false) {
        console.log("run")
        const loginSuccess = await this.login();
        if (!loginSuccess) {
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
                // Wait between posts
                await new Promise(resolve => setTimeout(resolve, 60000)); // 1 minute
            }
        }
    }
}

// Command line usage
const args = process.argv.slice(2);
const specificMonth = args.includes('--month') ? args[args.indexOf('--month') + 1] : null;
const force = args.includes('--force');

const automation = new InstagramWebAutomation();
automation.run(specificMonth, force).catch(console.error);