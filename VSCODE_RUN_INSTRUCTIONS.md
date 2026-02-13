# Running Gmail Watcher in VS Code

**Complete guide for running the Gmail watcher alongside the file watcher**

---

## Quick Start (Recommended)

### Option 1: Two Terminal Windows

**Terminal 1 - Gmail Watcher:**
```bash
# Navigate to project
cd "C:\Users\Tech Trends\Desktop\Building Autonomous FTEs\Personal_AI_Employee"

# Activate virtual environment
venv\Scripts\activate

# Start Gmail watcher
python watchers/gmail_watcher.py
```

**Terminal 2 - File Watcher:**
```bash
# Navigate to project
cd "C:\Users\Tech Trends\Desktop\Building Autonomous FTEs\Personal_AI_Employee"

# Activate virtual environment
venv\Scripts\activate

# Start file watcher
python run.py
```

**How it works:**
1. Gmail watcher fetches emails → saves as markdown to `vault/Inbox/`
2. File watcher detects new markdown files → processes them
3. AI brain classifies and organizes emails automatically

---

## Option 2: VS Code Split Terminal

1. **Open VS Code**
   ```bash
   code "C:\Users\Tech Trends\Desktop\Building Autonomous FTEs\Personal_AI_Employee"
   ```

2. **Open Integrated Terminal**
   - Press `Ctrl + `` (backtick) or
   - Menu: Terminal → New Terminal

3. **Split Terminal**
   - Click the split terminal icon (⊞) in terminal toolbar
   - Or press `Ctrl + Shift + 5`

4. **Left Terminal - Gmail Watcher**
   ```bash
   venv\Scripts\activate
   python watchers/gmail_watcher.py
   ```

5. **Right Terminal - File Watcher**
   ```bash
   venv\Scripts\activate
   python run.py
   ```

**Result:** Both watchers running side-by-side in VS Code

---

## Option 3: VS Code Tasks (One-Click Launch)

### Create Tasks Configuration

1. **Create .vscode folder** (if not exists)
   ```bash
   mkdir .vscode
   ```

2. **Create tasks.json**

   Create file: `.vscode/tasks.json`

   ```json
   {
       "version": "2.0.0",
       "tasks": [
           {
               "label": "Start Gmail Watcher",
               "type": "shell",
               "command": "${workspaceFolder}/venv/Scripts/python",
               "args": ["watchers/gmail_watcher.py"],
               "problemMatcher": [],
               "presentation": {
                   "reveal": "always",
                   "panel": "dedicated",
                   "group": "watchers"
               },
               "isBackground": true
           },
           {
               "label": "Start File Watcher",
               "type": "shell",
               "command": "${workspaceFolder}/venv/Scripts/python",
               "args": ["run.py"],
               "problemMatcher": [],
               "presentation": {
                   "reveal": "always",
                   "panel": "dedicated",
                   "group": "watchers"
               },
               "isBackground": true
           },
           {
               "label": "Start Both Watchers",
               "dependsOn": [
                   "Start Gmail Watcher",
                   "Start File Watcher"
               ],
               "problemMatcher": []
           }
       ]
   }
   ```

3. **Run Tasks**
   - Press `Ctrl + Shift + P`
   - Type: "Tasks: Run Task"
   - Select: "Start Both Watchers"
   - Both watchers will start in separate terminals

---

## Option 4: VS Code Launch Configuration (Debugging)

### Create Launch Configuration

1. **Create launch.json**

   Create file: `.vscode/launch.json`

   ```json
   {
       "version": "0.2.0",
       "configurations": [
           {
               "name": "Debug Gmail Watcher",
               "type": "python",
               "request": "launch",
               "program": "${workspaceFolder}/watchers/gmail_watcher.py",
               "console": "integratedTerminal",
               "justMyCode": true,
               "env": {
                   "PYTHONPATH": "${workspaceFolder}"
               }
           },
           {
               "name": "Debug File Watcher",
               "type": "python",
               "request": "launch",
               "program": "${workspaceFolder}/run.py",
               "console": "integratedTerminal",
               "justMyCode": true
           }
       ],
       "compounds": [
           {
               "name": "Debug Both Watchers",
               "configurations": [
                   "Debug Gmail Watcher",
                   "Debug File Watcher"
               ],
               "presentation": {
                   "hidden": false,
                   "group": "",
                   "order": 1
               }
           }
       ]
   }
   ```

2. **Start Debugging**
   - Press `F5` or
   - Click Run → Start Debugging
   - Select: "Debug Both Watchers"
   - Set breakpoints to debug issues

---

## Monitoring & Logs

### View Logs in VS Code

1. **Open Log Files**
   ```
   logs/gmail_watcher.log  - Gmail operations
   logs/watcher.log        - File processing
   logs/actions.log        - All actions
   ```

2. **Tail Logs in Terminal**
   ```bash
   # Watch Gmail watcher log
   Get-Content logs\gmail_watcher.log -Wait -Tail 20

   # Watch file watcher log
   Get-Content logs\watcher.log -Wait -Tail 20

   # Watch actions log
   Get-Content logs\actions.log -Wait -Tail 20
   ```

3. **VS Code Extension (Optional)**
   - Install: "Log File Highlighter"
   - Open log files for syntax highlighting

---

## Stopping the Watchers

### Graceful Shutdown

**In each terminal:**
- Press `Ctrl + C`
- Wait for "stopped successfully" message

**Expected output:**
```
⏹️  Shutdown signal received
🛑 Stopping Gmail watcher...
✅ Gmail watcher stopped successfully
```

### Force Stop (if needed)

**Windows:**
```bash
# Find Python processes
tasklist | findstr python

# Kill specific process
taskkill /PID <process_id> /F
```

---

## Workflow Diagram

```
┌─────────────────────┐
│   Gmail Account     │
│  (Unread Emails)    │
└──────────┬──────────┘
           │
           │ Every 60s
           ▼
┌─────────────────────┐
│  Gmail Watcher      │
│  (gmail_watcher.py) │
└──────────┬──────────┘
           │
           │ Saves as markdown
           ▼
┌─────────────────────┐
│   vault/Inbox/      │
│  (Markdown Files)   │
└──────────┬──────────┘
           │
           │ Detects new files
           ▼
┌─────────────────────┐
│   File Watcher      │
│     (run.py)        │
└──────────┬──────────┘
           │
           │ Processes
           ▼
┌─────────────────────┐
│      AI Brain       │
│    (brain.py)       │
└──────────┬──────────┘
           │
           │ Classifies & Organizes
           ▼
┌─────────────────────┐
│ vault/Needs_Action/ │
│   (Organized)       │
└─────────────────────┘
```

---

## Recommended VS Code Extensions

1. **Python** (Microsoft)
   - Syntax highlighting
   - IntelliSense
   - Debugging

2. **Pylance** (Microsoft)
   - Type checking
   - Auto-completion

3. **Python Docstring Generator**
   - Auto-generate docstrings

4. **Log File Highlighter**
   - Colorize log files

5. **Markdown All in One**
   - Preview markdown files from vault

---

## Keyboard Shortcuts

| Action | Shortcut |
|--------|----------|
| New Terminal | `Ctrl + Shift + `` |
| Split Terminal | `Ctrl + Shift + 5` |
| Toggle Terminal | `Ctrl + `` |
| Run Task | `Ctrl + Shift + P` → "Tasks: Run Task" |
| Start Debugging | `F5` |
| Stop Debugging | `Shift + F5` |
| Open File | `Ctrl + P` |
| Command Palette | `Ctrl + Shift + P` |

---

## Troubleshooting

### Issue: "venv\Scripts\activate" not recognized

**Solution:**
```bash
# Use full path
C:\Users\Tech Trends\Desktop\Building Autonomous FTEs\Personal_AI_Employee\venv\Scripts\activate

# Or navigate first
cd "C:\Users\Tech Trends\Desktop\Building Autonomous FTEs\Personal_AI_Employee"
venv\Scripts\activate
```

### Issue: Python not found in VS Code

**Solution:**
1. Press `Ctrl + Shift + P`
2. Type: "Python: Select Interpreter"
3. Choose: `.\venv\Scripts\python.exe`

### Issue: Tasks not appearing

**Solution:**
- Verify `.vscode/tasks.json` exists
- Reload VS Code: `Ctrl + Shift + P` → "Reload Window"

### Issue: Both watchers in same terminal

**Solution:**
- Use split terminal or tasks.json
- Each watcher needs its own terminal (they run continuously)

---

## Best Practices

1. **Always activate virtual environment first**
   ```bash
   venv\Scripts\activate
   ```

2. **Check logs if something seems wrong**
   ```bash
   type logs\gmail_watcher.log
   ```

3. **Test with one email first**
   - Send test email
   - Verify it appears in vault/Inbox/
   - Verify it gets processed

4. **Monitor both terminals**
   - Gmail watcher: Shows email fetching
   - File watcher: Shows file processing

5. **Use VS Code tasks for convenience**
   - One-click launch
   - Consistent environment

---

## Production Deployment

### Running as Background Service (Optional)

**Windows Task Scheduler:**

1. Open Task Scheduler
2. Create Basic Task
3. Name: "AI Employee Gmail Watcher"
4. Trigger: At startup
5. Action: Start a program
6. Program: `C:\Users\Tech Trends\Desktop\Building Autonomous FTEs\Personal_AI_Employee\venv\Scripts\python.exe`
7. Arguments: `watchers\gmail_watcher.py`
8. Start in: `C:\Users\Tech Trends\Desktop\Building Autonomous FTEs\Personal_AI_Employee`

**Repeat for file watcher (run.py)**

---

## Success Checklist

- [ ] VS Code opened in project folder
- [ ] Virtual environment activated
- [ ] Gmail watcher running in terminal 1
- [ ] File watcher running in terminal 2
- [ ] Both showing "Waiting for..." messages
- [ ] Test email sent
- [ ] Email appears in vault/Inbox/ as markdown
- [ ] File watcher processes the markdown file
- [ ] Email moved to vault/Needs_Action/
- [ ] Logs show successful processing

**If all checked: Your system is fully operational! 🎉**
