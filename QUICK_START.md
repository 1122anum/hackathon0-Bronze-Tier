# Quick Start Guide - Gmail Watcher

**Your Gmail watcher is ready to deploy! Follow these steps to get it running.**

---

## Current Status

✅ **Completed:**
- Gmail watcher code (`watchers/gmail_watcher.py`)
- Gmail API dependencies installed
- Environment configuration (`.env`)
- Complete documentation suite
- Integration with existing file watcher

⏳ **Pending (You need to do):**
- Download `credentials.json` from Google Cloud Console
- Complete first-time OAuth2 authentication
- Test with a real email

---

## Next Steps (15 minutes)

### Step 1: Get Gmail API Credentials (10 min)

Follow the detailed guide: **`GMAIL_API_SETUP.md`**

Quick summary:
1. Go to https://console.cloud.google.com/
2. Create new project: "AI-Employee-Gmail"
3. Enable Gmail API
4. Configure OAuth consent screen (External, add your email as test user)
5. Create OAuth2 credentials (Desktop app)
6. Download as `credentials.json`
7. Place in project root folder

### Step 2: First Run - Authentication (2 min)

```bash
# Navigate to project
cd "C:\Users\Tech Trends\Desktop\Building Autonomous FTEs\Personal_AI_Employee"

# Activate virtual environment (if using one)
# venv\Scripts\activate

# Start Gmail watcher
python watchers/gmail_watcher.py
```

**What happens:**
- Browser opens automatically
- Sign in with your Google account
- Grant permissions (click "Advanced" → "Go to AI Employee Gmail Watcher (unsafe)")
- Click "Allow"
- `token.json` is created automatically
- Watcher starts monitoring

### Step 3: Test with Real Email (3 min)

1. **Send test email** to your Gmail account:
   - Subject: `Test AI Employee`
   - Body: `This is a test email for the AI Employee system`

2. **Wait up to 60 seconds** (poll interval)

3. **Check results:**
   ```bash
   # Should see new markdown file
   dir vault\Inbox\*test_ai_employee*

   # View the file
   type vault\Inbox\2026-02-12__test_ai_employee.md
   ```

4. **Verify in Gmail:**
   - Email should be marked as read
   - No longer in unread count

---

## Running Both Watchers (Production Mode)

Once Gmail watcher is working, run both watchers together:

**Terminal 1 - Gmail Watcher:**
```bash
cd "C:\Users\Tech Trends\Desktop\Building Autonomous FTEs\Personal_AI_Employee"
python watchers/gmail_watcher.py
```

**Terminal 2 - File Watcher:**
```bash
cd "C:\Users\Tech Trends\Desktop\Building Autonomous FTEs\Personal_AI_Employee"
python run.py
```

**Workflow:**
```
Gmail → Gmail Watcher → vault/Inbox/ → File Watcher → AI Brain → vault/Needs_Action/
```

See **`VSCODE_RUN_INSTRUCTIONS.md`** for VS Code integration options.

---

## Documentation Reference

| File | Purpose |
|------|---------|
| **GMAIL_API_SETUP.md** | Complete 9-step setup guide for Google Cloud Console |
| **VSCODE_RUN_INSTRUCTIONS.md** | 4 ways to run watchers in VS Code (split terminal, tasks, debugging) |
| **GMAIL_TESTING_GUIDE.md** | 17 comprehensive test scenarios |
| **QUICK_START.md** | This file - fastest path to running system |

---

## Troubleshooting

### "credentials.json not found"
- Download from Google Cloud Console (Step 1 above)
- Place in project root (same folder as `run.py`)

### "Failed to refresh credentials"
- Delete `token.json`
- Run `python watchers/gmail_watcher.py` again
- Complete OAuth2 flow in browser

### "No emails being processed"
- Verify you have unread emails in Gmail
- Wait 60 seconds (poll interval)
- Check logs: `type logs\gmail_watcher.log`

### "Access blocked: This app's request is invalid"
- Go to OAuth consent screen in Google Cloud Console
- Add your email as test user
- Verify scope is `gmail.modify`

---

## Security Notes

🔒 **Keep these files secure (never commit to git):**
- `credentials.json` - OAuth2 client secret
- `token.json` - Access token
- `.env` - Configuration

✅ Already in `.gitignore`

---

## Success Checklist

- [ ] `credentials.json` downloaded and placed in project root
- [ ] Gmail watcher started successfully
- [ ] Browser authentication completed
- [ ] `token.json` created automatically
- [ ] Test email sent
- [ ] Markdown file created in `vault/Inbox/`
- [ ] Email marked as read in Gmail
- [ ] File watcher running in second terminal
- [ ] Email processed and moved to `vault/Needs_Action/`

**When all checked: Your Digital FTE is fully operational! 🎉**

---

## What Happens Next

Once both watchers are running:

1. **Emails arrive** → Gmail watcher fetches every 60s
2. **Converted to markdown** → Saved to `vault/Inbox/`
3. **File watcher detects** → Triggers AI brain
4. **AI classifies** → Determines type (Question, Request, etc.)
5. **AI prioritizes** → Assigns priority (1-10)
6. **Auto-organized** → Moved to `vault/Needs_Action/`
7. **Dashboard updated** → Real-time status in `vault/Dashboard.md`
8. **Logged** → Full audit trail in `logs/`

Your AI Employee is now autonomously managing your inbox!

---

## Need Help?

- **Setup issues:** See `GMAIL_API_SETUP.md` troubleshooting section
- **Testing:** Follow `GMAIL_TESTING_GUIDE.md` (17 test scenarios)
- **VS Code:** See `VSCODE_RUN_INSTRUCTIONS.md` for optimal workflow

**Estimated time to full operation: 15 minutes**
