# Gmail Watcher - Quick Start Guide

**Status: 95% Complete - Only credentials.json needed**

---

## What's Already Done ✓

- Gmail Watcher code (production-ready)
- Gmail API libraries installed
- Environment configured (.env)
- Vault structure ready
- All Python dependencies installed

## What You Need To Do

### Step 1: Get credentials.json from Google Cloud Console

**This is the ONLY missing piece.**

#### Option A: Quick Setup (5 minutes)

1. **Go to Google Cloud Console**
   - Visit: https://console.cloud.google.com/

2. **Create Project** (if you don't have one)
   - Click "Select a project" → "NEW PROJECT"
   - Name: `AI-Employee-Gmail`
   - Click "CREATE"

3. **Enable Gmail API**
   - Go to: https://console.cloud.google.com/apis/library
   - Search: "Gmail API"
   - Click "ENABLE"

4. **Configure OAuth Consent Screen**
   - Go to: https://console.cloud.google.com/apis/credentials/consent
   - User Type: "External"
   - App name: `AI Employee Gmail Watcher`
   - User support email: (your email)
   - Developer contact: (your email)
   - Click "SAVE AND CONTINUE"

   **Scopes:**
   - Click "ADD OR REMOVE SCOPES"
   - Search: `gmail.modify`
   - Check: `https://www.googleapis.com/auth/gmail.modify`
   - Click "UPDATE" → "SAVE AND CONTINUE"

   **Test Users:**
   - Click "ADD USERS"
   - Enter your Gmail address
   - Click "ADD" → "SAVE AND CONTINUE"

5. **Create OAuth2 Credentials**
   - Go to: https://console.cloud.google.com/apis/credentials
   - Click "CREATE CREDENTIALS" → "OAuth client ID"
   - Application type: "Desktop app"
   - Name: `AI Employee Desktop Client`
   - Click "CREATE"

6. **Download credentials.json**
   - Click "DOWNLOAD JSON"
   - Save as `credentials.json`
   - Move to: `Personal_AI_Employee/credentials.json`

#### Option B: Detailed Setup

See `GMAIL_API_SETUP.md` for step-by-step screenshots and troubleshooting.

---

### Step 2: Place credentials.json in Project Root

```
Personal_AI_Employee/
├── credentials.json  ← Place downloaded file here
├── watchers/
│   └── gmail_watcher.py
├── vault/
│   └── Inbox/
└── .env
```

**Windows Command:**
```bash
# Move downloaded file to project directory
move "%USERPROFILE%\Downloads\credentials.json" "C:\Users\Tech Trends\Desktop\Building Autonomous FTEs\Personal_AI_Employee\credentials.json"
```

---

### Step 3: Verify Setup

```bash
cd "C:\Users\Tech Trends\Desktop\Building Autonomous FTEs\Personal_AI_Employee"
python setup_gmail.py
```

You should see: `STATUS: READY TO RUN`

---

### Step 4: Start Gmail Watcher

```bash
python watchers/gmail_watcher.py
```

**First Run:**
- A browser window will open automatically
- Sign in to your Google account
- Click "Advanced" → "Go to AI Employee Gmail Watcher (unsafe)" (it's safe - it's YOUR app)
- Click "Allow"
- Browser shows: "The authentication flow has completed"
- Close browser and return to terminal

**You'll see:**
```
Authentication successful!
Credentials saved to token.json
Gmail service initialized successfully
✓ Gmail authentication successful
Starting monitoring loop...
```

---

### Step 5: Test It

1. **Send yourself a test email** (from phone or another account)
   - To: (your Gmail)
   - Subject: "Test AI Employee"
   - Body: "Testing the Gmail Watcher"

2. **Wait 60 seconds** (poll interval)

3. **Check terminal output:**
   ```
   Found 1 unread email(s)
   Saved email to: 2026-02-13__test_ai_employee.md
   Marked email as read: [email_id]
   Successfully processed: Test AI Employee
   ```

4. **Check vault/Inbox:**
   ```bash
   dir vault\Inbox\
   ```

   You should see: `2026-02-13__test_ai_employee.md`

5. **View the markdown file:**
   ```bash
   type vault\Inbox\2026-02-13__test_ai_employee.md
   ```

---

## How It Works

```
Gmail → Gmail Watcher → Markdown Files → vault/Inbox/
         (every 60s)     (YYYY-MM-DD__subject.md)
```

**The watcher:**
1. Checks Gmail every 60 seconds
2. Fetches unread emails
3. Converts to markdown format
4. Saves to `vault/Inbox/`
5. Marks email as read
6. Logs action to `logs/actions.log`
7. Prevents duplicate processing

---

## Markdown Format

Each email is saved as:

```markdown
# Email: {{Subject}}

**From:** {{Sender}}
**Date:** {{Date}}
**Status:** New
**Source:** Gmail

---

## Content

{{Email Body}}

---

## AI Notes

(Leave blank for brain.py to process)
```

---

## Commands

**Start Gmail Watcher:**
```bash
python watchers/gmail_watcher.py
```

**Stop Gmail Watcher:**
- Press `Ctrl+C` in terminal

**Check Setup:**
```bash
python setup_gmail.py
```

**View Logs:**
```bash
type logs\gmail_watcher.log
type logs\actions.log
```

**Clear Processed Emails Tracking:**
```bash
del logs\processed_emails.txt
```

---

## Configuration (.env)

```bash
GMAIL_CREDENTIALS_FILE=credentials.json  # OAuth2 credentials
GMAIL_TOKEN_FILE=token.json              # Auto-generated after first auth
POLL_INTERVAL=60                         # Seconds between checks
```

**Change poll interval:**
- Edit `.env` file
- Change `POLL_INTERVAL=60` to desired seconds
- Restart watcher

---

## Troubleshooting

### "credentials.json not found"
- Download from Google Cloud Console (Step 1)
- Place in project root directory
- Verify filename is exactly `credentials.json`

### "Failed to refresh credentials"
- Delete `token.json`
- Run watcher again
- Complete OAuth2 flow in browser

### "Access blocked: This app's request is invalid"
- Add your email as test user in OAuth consent screen
- Verify scope: `gmail.modify`

### No emails being processed
- Check you have unread emails in Gmail
- Wait 60 seconds (poll interval)
- Check logs: `type logs\gmail_watcher.log`

### Browser doesn't open on first run
- Check firewall settings
- Manually visit the URL shown in terminal
- Complete authentication in browser

---

## Security Notes

**credentials.json:**
- Contains OAuth2 client secret
- Already in .gitignore
- Never commit to version control

**token.json:**
- Contains your access token
- Auto-generated on first run
- Already in .gitignore
- Never commit to version control

**Revoke access:**
- Visit: https://myaccount.google.com/permissions
- Find "AI Employee Gmail Watcher"
- Click "Remove Access"

---

## Next Steps After Gmail Watcher is Running

1. **Start File Watcher** (processes markdown files)
   ```bash
   python run.py
   ```

2. **Monitor both watchers:**
   - Terminal 1: Gmail Watcher (fetches emails)
   - Terminal 2: File Watcher (processes files)

3. **View Dashboard:**
   - Open `vault/Dashboard.md` in Obsidian or text editor

---

## API Limits (Free Tier)

- **Daily quota:** 1 billion units
- **Your usage:** ~1,440 checks/day (every 60s)
- **Well within limits** - no credit card needed

---

## Support

**Setup issues:** See `GMAIL_API_SETUP.md` for detailed instructions

**Code issues:** Check `logs/gmail_watcher.log` for errors

**Testing:** See `GMAIL_TESTING_GUIDE.md` for comprehensive tests

---

**Current Status:** Ready to run once you add `credentials.json`
