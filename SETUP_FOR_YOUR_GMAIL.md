# Gmail Watcher Setup for anumbabar84@gmail.com
# ================================================

## Quick Setup Steps

### 1. Create Google Cloud Project

1. Go to: https://console.cloud.google.com/
2. Sign in with: anumbabar84@gmail.com
3. Click "Select a project" → "NEW PROJECT"
4. Project name: AI-Employee-Gmail
5. Click "CREATE"

### 2. Enable Gmail API

1. Go to: https://console.cloud.google.com/apis/library
2. Search: "Gmail API"
3. Click on "Gmail API"
4. Click "ENABLE"

### 3. Configure OAuth Consent Screen

1. Go to: https://console.cloud.google.com/apis/credentials/consent
2. User Type: Select "External"
3. Click "CREATE"

**App Information:**
- App name: AI Employee Gmail Watcher
- User support email: anumbabar84@gmail.com
- Developer contact: anumbabar84@gmail.com
- Click "SAVE AND CONTINUE"

**Scopes:**
- Click "ADD OR REMOVE SCOPES"
- Search: gmail.modify
- Check: https://www.googleapis.com/auth/gmail.modify
- Click "UPDATE"
- Click "SAVE AND CONTINUE"

**Test Users:**
- Click "ADD USERS"
- Enter: anumbabar84@gmail.com
- Click "ADD"
- Click "SAVE AND CONTINUE"
- Click "BACK TO DASHBOARD"

### 4. Create OAuth2 Credentials

1. Go to: https://console.cloud.google.com/apis/credentials
2. Click "CREATE CREDENTIALS"
3. Select "OAuth client ID"
4. Application type: "Desktop app"
5. Name: AI Employee Desktop Client
6. Click "CREATE"

### 5. Download credentials.json

1. A popup appears with Client ID and Secret
2. Click "DOWNLOAD JSON"
3. Save the file

### 6. Move credentials.json to Project

**Windows Command:**
```cmd
move "%USERPROFILE%\Downloads\client_secret_*.json" "C:\Users\Tech Trends\Desktop\Building Autonomous FTEs\Personal_AI_Employee\credentials.json"
```

Or manually:
- Rename downloaded file to: credentials.json
- Move to: C:\Users\Tech Trends\Desktop\Building Autonomous FTEs\Personal_AI_Employee\

### 7. Verify Setup

```cmd
cd "C:\Users\Tech Trends\Desktop\Building Autonomous FTEs\Personal_AI_Employee"
python setup_gmail.py
```

Should show: STATUS: READY TO RUN

### 8. Start Gmail Watcher

```cmd
python watchers/gmail_watcher.py
```

**First Run:**
- Browser opens automatically
- Sign in with: anumbabar84@gmail.com
- Click "Advanced" → "Go to AI Employee Gmail Watcher (unsafe)"
- Click "Allow"
- Browser shows: "The authentication flow has completed"
- Return to terminal

**Terminal shows:**
```
Authentication successful!
Gmail service initialized successfully
✓ Gmail authentication successful
Starting monitoring loop...
```

### 9. Test

1. Send email to: anumbabar84@gmail.com (from another account or phone)
2. Subject: "Test AI Employee"
3. Wait 60 seconds
4. Check: vault\Inbox\

You'll see: 2026-02-13__test_ai_employee.md

---

## Important Notes

- The watcher automatically uses whichever Gmail account you authenticate with
- No need to hardcode your email anywhere
- credentials.json is specific to your Google Cloud project
- token.json will be auto-generated after first authentication
- Both files are already in .gitignore (secure)

---

## Commands

**Start watcher:**
```cmd
python watchers/gmail_watcher.py
```

**Stop watcher:**
Press Ctrl+C

**Check status:**
```cmd
python setup_gmail.py
```

**View logs:**
```cmd
type logs\gmail_watcher.log
```

---

## Troubleshooting

**"credentials.json not found"**
- Make sure you downloaded it from Google Cloud Console
- Rename to exactly: credentials.json
- Place in project root (same folder as run.py)

**"Access blocked"**
- Make sure you added anumbabar84@gmail.com as test user
- Check OAuth consent screen configuration

**Browser doesn't open**
- Copy the URL from terminal
- Paste in browser manually
- Complete authentication

---

**Your Gmail account (anumbabar84@gmail.com) will be automatically detected during OAuth2 authentication.**
