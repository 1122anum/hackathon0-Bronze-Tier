# Gmail API Setup Guide

**Complete step-by-step instructions for enabling Gmail API and OAuth2 authentication**

---

## Prerequisites

- Google account with Gmail
- Python 3.13+ installed
- Personal AI Employee project set up

---

## Step 1: Create Google Cloud Project

1. **Go to Google Cloud Console**
   - Visit: https://console.cloud.google.com/

2. **Create New Project**
   - Click "Select a project" dropdown at the top
   - Click "NEW PROJECT"
   - Project name: `AI-Employee-Gmail` (or your choice)
   - Click "CREATE"
   - Wait for project creation (takes ~30 seconds)

3. **Select Your Project**
   - Click "Select a project" dropdown
   - Choose your newly created project

---

## Step 2: Enable Gmail API

1. **Navigate to APIs & Services**
   - In the left sidebar, click "APIs & Services" → "Library"
   - Or visit: https://console.cloud.google.com/apis/library

2. **Search for Gmail API**
   - In the search bar, type "Gmail API"
   - Click on "Gmail API" from results

3. **Enable the API**
   - Click the blue "ENABLE" button
   - Wait for activation (~10 seconds)
   - You should see "API enabled" confirmation

---

## Step 3: Configure OAuth Consent Screen

**This is required before creating credentials**

1. **Navigate to OAuth Consent Screen**
   - Left sidebar: "APIs & Services" → "OAuth consent screen"
   - Or visit: https://console.cloud.google.com/apis/credentials/consent

2. **Choose User Type**
   - Select "External" (unless you have Google Workspace)
   - Click "CREATE"

3. **Fill App Information**

   **App information:**
   - App name: `AI Employee Gmail Watcher`
   - User support email: (your email)
   - App logo: (optional, skip for now)

   **App domain:**
   - Leave blank (not required for testing)

   **Developer contact information:**
   - Email addresses: (your email)

   - Click "SAVE AND CONTINUE"

4. **Scopes**
   - Click "ADD OR REMOVE SCOPES"
   - Search for: `gmail.modify`
   - Check the box for: `https://www.googleapis.com/auth/gmail.modify`
   - This allows reading emails and marking them as read
   - Click "UPDATE"
   - Click "SAVE AND CONTINUE"

5. **Test Users**
   - Click "ADD USERS"
   - Enter your Gmail address
   - Click "ADD"
   - Click "SAVE AND CONTINUE"

6. **Summary**
   - Review your settings
   - Click "BACK TO DASHBOARD"

---

## Step 4: Create OAuth2 Credentials

1. **Navigate to Credentials**
   - Left sidebar: "APIs & Services" → "Credentials"
   - Or visit: https://console.cloud.google.com/apis/credentials

2. **Create Credentials**
   - Click "CREATE CREDENTIALS" at the top
   - Select "OAuth client ID"

3. **Configure OAuth Client**

   **Application type:**
   - Select "Desktop app"

   **Name:**
   - Enter: `AI Employee Desktop Client`

   - Click "CREATE"

4. **Download Credentials**
   - A popup will appear with your Client ID and Client Secret
   - Click "DOWNLOAD JSON"
   - Save the file as `credentials.json`
   - Click "OK" to close the popup

---

## Step 5: Install Credentials File

1. **Move credentials.json to Project Root**
   ```bash
   # Move the downloaded file to your project directory
   # It should be in the same folder as run.py

   Personal_AI_Employee/
   ├── credentials.json  ← Place here
   ├── run.py
   ├── vault/
   └── watchers/
   ```

2. **Verify File Location**
   ```bash
   cd "C:\Users\Tech Trends\Desktop\Building Autonomous FTEs\Personal_AI_Employee"
   dir credentials.json
   ```

   You should see the file listed.

---

## Step 6: Install Python Dependencies

1. **Activate Virtual Environment**
   ```bash
   cd "C:\Users\Tech Trends\Desktop\Building Autonomous FTEs\Personal_AI_Employee"
   venv\Scripts\activate
   ```

2. **Install Gmail API Libraries**
   ```bash
   pip install google-auth google-auth-oauthlib google-auth-httplib2 google-api-python-client
   ```

   Or install all dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. **Verify Installation**
   ```bash
   python -c "import google.auth; print('Gmail API libraries installed successfully')"
   ```

---

## Step 7: Configure Environment Variables

1. **Copy .env.example to .env**
   ```bash
   copy .env.example .env
   ```

2. **Edit .env File**

   Open `.env` in your editor and verify these settings:
   ```bash
   GMAIL_CREDENTIALS_FILE=credentials.json
   GMAIL_TOKEN_FILE=token.json
   POLL_INTERVAL=60
   ```

   **Note:** `token.json` will be auto-generated on first run.

---

## Step 8: First Run - OAuth2 Authentication

1. **Start Gmail Watcher**
   ```bash
   python watchers/gmail_watcher.py
   ```

2. **Browser Authentication Flow**

   On first run, a browser window will automatically open:

   a. **Sign in to Google**
      - Enter your Gmail address
      - Enter your password

   b. **App Verification Warning**
      - You'll see: "Google hasn't verified this app"
      - Click "Advanced"
      - Click "Go to AI Employee Gmail Watcher (unsafe)"
      - This is safe - it's YOUR app

   c. **Grant Permissions**
      - You'll see: "AI Employee Gmail Watcher wants to access your Google Account"
      - Review the permissions:
        - "Read, compose, send, and permanently delete all your email from Gmail"
      - Click "Allow"

   d. **Success**
      - Browser will show: "The authentication flow has completed"
      - You can close the browser window

3. **Verify Authentication**

   Back in your terminal, you should see:
   ```
   Authentication successful!
   Credentials saved to token.json
   Gmail service initialized successfully
   ✅ Gmail authentication successful
   🔄 Starting monitoring loop...
   ```

4. **Token File Created**

   A `token.json` file is now created in your project root:
   ```
   Personal_AI_Employee/
   ├── credentials.json
   ├── token.json  ← Auto-generated
   ├── run.py
   └── ...
   ```

   **Important:** This token file contains your access credentials. Keep it secure!

---

## Step 9: Verify Gmail Watcher is Working

1. **Send Test Email**
   - From another email account (or your phone)
   - Send an email to your Gmail account
   - Subject: "Test AI Employee"
   - Body: "This is a test email for the AI Employee system"

2. **Watch the Logs**

   In the terminal running gmail_watcher.py, you should see:
   ```
   Found 1 unread email(s)
   Saved email to: 2026-02-12__test_ai_employee.md
   Marked email as read: [email_id]
   ✅ Successfully processed: Test AI Employee
   ```

3. **Check vault/Inbox/**
   ```bash
   dir vault\Inbox\
   ```

   You should see a new markdown file:
   ```
   2026-02-12__test_ai_employee.md
   ```

4. **View the Markdown File**
   ```bash
   type vault\Inbox\2026-02-12__test_ai_employee.md
   ```

   Should show:
   ```markdown
   # Email: Test AI Employee

   **From:** sender@example.com
   **Date:** 2026-02-12 17:30:00
   **Status:** New
   **Source:** Gmail

   ---

   ## Content

   This is a test email for the AI Employee system

   ---

   ## AI Notes

   (Leave blank for brain.py to process)
   ```

5. **Verify Email Marked as Read**
   - Open Gmail in your browser
   - The test email should now be marked as read
   - It will no longer appear in your unread count

---

## Troubleshooting

### Issue: "Credentials file not found"

**Solution:**
- Verify `credentials.json` is in the project root
- Check the filename is exactly `credentials.json` (not `credentials (1).json`)
- Verify path in `.env` file: `GMAIL_CREDENTIALS_FILE=credentials.json`

### Issue: "Failed to refresh credentials"

**Solution:**
- Delete `token.json`
- Run gmail_watcher.py again
- Complete OAuth2 flow again in browser

### Issue: "Access blocked: This app's request is invalid"

**Solution:**
- Go back to OAuth consent screen in Google Cloud Console
- Make sure you added your email as a test user
- Make sure you selected the correct scope: `gmail.modify`

### Issue: "The authentication flow has completed" but watcher shows error

**Solution:**
- Check terminal for specific error message
- Verify Gmail API is enabled in Google Cloud Console
- Try deleting `token.json` and re-authenticating

### Issue: No emails being processed

**Solution:**
- Verify you have unread emails in Gmail
- Check logs: `type logs\gmail_watcher.log`
- Verify poll interval: default is 60 seconds
- Send a test email and wait 60 seconds

### Issue: "HttpError 403: Request had insufficient authentication scopes"

**Solution:**
- Delete `token.json`
- Verify scope in code is: `gmail.modify`
- Re-authenticate

---

## Security Best Practices

1. **Keep credentials.json secure**
   - Never commit to git
   - Already in .gitignore
   - Contains your OAuth2 client secret

2. **Keep token.json secure**
   - Never commit to git
   - Already in .gitignore
   - Contains your access token

3. **Revoke Access (if needed)**
   - Visit: https://myaccount.google.com/permissions
   - Find "AI Employee Gmail Watcher"
   - Click "Remove Access"

4. **Rotate Credentials (if compromised)**
   - Go to Google Cloud Console → Credentials
   - Delete old OAuth2 client
   - Create new one
   - Download new credentials.json
   - Re-authenticate

---

## Next Steps

Once Gmail watcher is running:

1. **Start File Watcher** (in another terminal)
   ```bash
   python run.py
   ```
   This will process the markdown files created by gmail_watcher.py

2. **Monitor Both Watchers**
   - Terminal 1: Gmail watcher (fetches emails)
   - Terminal 2: File watcher (processes markdown files)

3. **Check Dashboard**
   - Open `vault/Dashboard.md` in Obsidian
   - See real-time processing status

4. **Review Logs**
   - `logs/gmail_watcher.log` - Gmail operations
   - `logs/watcher.log` - File processing
   - `logs/actions.log` - All actions

---

## API Quotas & Limits

**Gmail API Free Tier:**
- 1 billion quota units per day
- Reading an email: ~5 quota units
- Modifying an email: ~5 quota units
- **Effective limit:** ~100 million emails per day

**Your Usage:**
- Checking every 60 seconds: 1,440 checks/day
- Processing 50 emails per check: ~72,000 emails/day max
- Well within free tier limits

**No credit card required for these limits.**

---

## Success Checklist

- [ ] Google Cloud project created
- [ ] Gmail API enabled
- [ ] OAuth consent screen configured
- [ ] OAuth2 credentials created
- [ ] credentials.json downloaded and placed in project root
- [ ] Python dependencies installed
- [ ] .env file configured
- [ ] First authentication completed (token.json created)
- [ ] Test email sent and processed
- [ ] Markdown file created in vault/Inbox/
- [ ] Email marked as read in Gmail

**If all checked: Your Gmail watcher is fully operational! 🎉**
