# VS Code Setup and Run Instructions - Silver Tier

Complete guide for running the Personal AI Employee Silver Tier system in VS Code.

---

## Prerequisites

- VS Code installed
- Python 3.13+ installed
- Node.js v18+ installed
- Git installed
- Gmail API credentials configured (see GMAIL_API_SETUP.md)

---

## Initial Setup

### 1. Open Project in VS Code

```bash
cd Personal_AI_Employee
code .
```

### 2. Install Python Extension

1. Open Extensions (Ctrl+Shift+X)
2. Search for "Python"
3. Install the official Python extension by Microsoft

### 3. Create Virtual Environment

Open terminal in VS Code (Ctrl+`):

```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate

# Linux/Mac:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 4. Configure Environment Variables

Copy `.env.example` to `.env`:

```bash
# Windows
copy .env.example .env

# Linux/Mac
cp .env.example .env
```

Edit `.env` with your credentials:

```env
# Gmail API
GMAIL_CREDENTIALS_PATH=credentials.json
GMAIL_TOKEN_PATH=token.json
GMAIL_CHECK_INTERVAL=60

# SMTP Configuration (for MCP email server)
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_SECURE=false
SMTP_USER=your-email@gmail.com
SMTP_PASS=your-app-password

# MCP Server
MCP_PORT=3000
MCP_HOST=localhost

# LinkedIn Configuration
LINKEDIN_POST_TIME=09:00
LINKEDIN_POST_DAYS=Monday,Tuesday,Wednesday,Thursday,Friday

# Approval Engine
APPROVAL_CHECK_INTERVAL=30

# System Configuration
LOG_LEVEL=INFO
VAULT_PATH=vault
```

### 5. Install Node.js Dependencies

```bash
cd mcp_server
npm install
cd ..
```

---

## Running the System

### Option 1: Run All Components (Recommended)

Create a VS Code task to run all components simultaneously.

#### Create `.vscode/tasks.json`:

```json
{
    "version": "2.0.0",
    "tasks": [
        {
            "label": "Start MCP Server",
            "type": "shell",
            "command": "cd mcp_server && npm start",
            "isBackground": true,
            "problemMatcher": [],
            "presentation": {
                "reveal": "always",
                "panel": "dedicated",
                "group": "servers"
            }
        },
        {
            "label": "Start Approval Engine",
            "type": "shell",
            "command": "${command:python.interpreterPath}",
            "args": [
                "-c",
                "from agent.approval_engine import ApprovalEngine; from pathlib import Path; engine = ApprovalEngine(str(Path('vault'))); engine.start_monitoring()"
            ],
            "isBackground": true,
            "problemMatcher": [],
            "presentation": {
                "reveal": "always",
                "panel": "dedicated",
                "group": "watchers"
            }
        },
        {
            "label": "Start LinkedIn Watcher",
            "type": "shell",
            "command": "${command:python.interpreterPath}",
            "args": [
                "-c",
                "from watchers.linkedin_watcher import LinkedInWatcher; from pathlib import Path; watcher = LinkedInWatcher(str(Path('vault'))); watcher.start_monitoring()"
            ],
            "isBackground": true,
            "problemMatcher": [],
            "presentation": {
                "reveal": "always",
                "panel": "dedicated",
                "group": "watchers"
            }
        },
        {
            "label": "Start Gmail Watcher",
            "type": "shell",
            "command": "${command:python.interpreterPath}",
            "args": [
                "watchers/gmail_watcher.py"
            ],
            "isBackground": true,
            "problemMatcher": [],
            "presentation": {
                "reveal": "always",
                "panel": "dedicated",
                "group": "watchers"
            }
        },
        {
            "label": "Start File Watcher",
            "type": "shell",
            "command": "${command:python.interpreterPath}",
            "args": [
                "run.py"
            ],
            "isBackground": true,
            "problemMatcher": [],
            "presentation": {
                "reveal": "always",
                "panel": "dedicated",
                "group": "watchers"
            }
        },
        {
            "label": "Start All Silver Tier Services",
            "dependsOn": [
                "Start MCP Server",
                "Start Approval Engine",
                "Start LinkedIn Watcher",
                "Start Gmail Watcher",
                "Start File Watcher"
            ],
            "problemMatcher": []
        }
    ]
}
```

#### Run All Services:

1. Press `Ctrl+Shift+P`
2. Type "Tasks: Run Task"
3. Select "Start All Silver Tier Services"

All components will start in separate terminal panels.

---

### Option 2: Run Components Individually

#### Terminal 1: MCP Server

```bash
cd mcp_server
npm start
```

#### Terminal 2: Approval Engine

```bash
python -c "from agent.approval_engine import ApprovalEngine; from pathlib import Path; engine = ApprovalEngine(str(Path('vault'))); engine.start_monitoring()"
```

#### Terminal 3: LinkedIn Watcher

```bash
python -c "from watchers.linkedin_watcher import LinkedInWatcher; from pathlib import Path; watcher = LinkedInWatcher(str(Path('vault'))); watcher.start_monitoring()"
```

#### Terminal 4: Gmail Watcher

```bash
python watchers/gmail_watcher.py
```

#### Terminal 5: File Watcher

```bash
python run.py
```

---

## Testing the System

### 1. Test MCP Server

Open a new terminal:

```bash
# Test health endpoint
curl http://localhost:3000/health

# Expected output:
# {
#   "status": "healthy",
#   "service": "MCP Email Server",
#   "version": "1.0.0",
#   "timestamp": "2026-02-13T..."
# }
```

### 2. Test File Processing

Create a test file in `vault/Inbox/`:

```bash
echo "Please send an email to john@example.com about the project update" > vault/Inbox/test_task.txt
```

Watch the logs to see:
1. File detected by watcher
2. Brain processes the file
3. Plan generated
4. Plan moved to Pending_Approval

### 3. Test Approval Workflow

1. Open `vault/Pending_Approval/Plan_*.md`
2. Add `STATUS: APPROVED` at the top of the file
3. Save the file
4. Watch approval engine logs for execution

### 4. Test LinkedIn Post Generation

Manually trigger a LinkedIn post:

```bash
python -c "from watchers.linkedin_watcher import LinkedInWatcher; from pathlib import Path; w = LinkedInWatcher(str(Path('vault'))); result = w._trigger_post_generation(); print(result)"
```

Check `vault/Needs_Action/` for the generated post.

### 5. Test Gmail Integration

Send an email to your configured Gmail account and watch for:
1. Email detected by Gmail watcher
2. Email converted to markdown
3. File created in `vault/Inbox/`
4. Brain processes the email

---

## Debugging

### Enable Debug Logging

Edit `.env`:

```env
LOG_LEVEL=DEBUG
```

Restart all services.

### View Logs in VS Code

Install "Log File Highlighter" extension for better log viewing.

Open logs:
- `logs/approval_engine.log`
- `logs/linkedin_watcher.log`
- `logs/gmail_watcher.log`
- `logs/mcp_server.log`
- `logs/watcher.log`

### Common Issues

#### Issue: MCP Server Won't Start

**Solution:**
```bash
# Check if port 3000 is in use
netstat -ano | findstr :3000  # Windows
lsof -i :3000                 # Linux/Mac

# Kill the process or change MCP_PORT in .env
```

#### Issue: Gmail Watcher Authentication Failed

**Solution:**
1. Delete `token.json`
2. Run `python setup_gmail.py`
3. Complete OAuth flow
4. Restart Gmail watcher

#### Issue: Approval Engine Not Detecting Changes

**Solution:**
1. Check file permissions on `vault/Pending_Approval/`
2. Verify approval engine is running
3. Check logs for errors
4. Ensure file is saved properly

#### Issue: Python Module Not Found

**Solution:**
```bash
# Ensure virtual environment is activated
# Windows:
venv\Scripts\activate

# Linux/Mac:
source venv/bin/activate

# Reinstall dependencies
pip install -r requirements.txt
```

---

## Development Workflow

### 1. Make Changes

Edit files in VS Code with full IntelliSense support.

### 2. Test Changes

Stop affected service (Ctrl+C in terminal) and restart:

```bash
# Example: Testing changes to planner.py
python -c "from agent.planner import TaskPlanner; from pathlib import Path; p = TaskPlanner(str(Path('vault'))); print(p.generate_plan('Test task', 'Request', 'High'))"
```

### 3. View Dashboard

Open `vault/Dashboard.md` in VS Code preview (Ctrl+Shift+V) to see real-time updates.

### 4. Monitor System

Use VS Code's integrated terminal to monitor multiple logs:

```bash
# Terminal 1
tail -f logs/approval_engine.log

# Terminal 2
tail -f logs/linkedin_watcher.log

# Terminal 3
tail -f logs/watcher.log
```

---

## VS Code Extensions (Recommended)

Install these extensions for better development experience:

1. **Python** (ms-python.python)
   - IntelliSense, debugging, linting

2. **Pylance** (ms-python.vscode-pylance)
   - Fast Python language server

3. **Markdown All in One** (yzhang.markdown-all-in-one)
   - Better markdown editing

4. **Log File Highlighter** (emilast.LogFileHighlighter)
   - Syntax highlighting for logs

5. **REST Client** (humao.rest-client)
   - Test MCP server endpoints

6. **GitLens** (eamodio.gitlens)
   - Enhanced Git integration

7. **Todo Tree** (Gruntfuggly.todo-tree)
   - Track TODOs in code

---

## Keyboard Shortcuts

### Essential Shortcuts

- `Ctrl+` ` - Toggle terminal
- `Ctrl+Shift+` ` - New terminal
- `Ctrl+Shift+P` - Command palette
- `Ctrl+P` - Quick file open
- `Ctrl+Shift+F` - Search in files
- `F5` - Start debugging
- `Ctrl+Shift+V` - Markdown preview

### Custom Shortcuts (Optional)

Add to `keybindings.json`:

```json
[
    {
        "key": "ctrl+shift+s",
        "command": "workbench.action.tasks.runTask",
        "args": "Start All Silver Tier Services"
    }
]
```

---

## Debugging with VS Code

### Create `.vscode/launch.json`:

```json
{
    "version": "0.2.0",
    "configurations": [
        {
            "name": "Debug Brain",
            "type": "python",
            "request": "launch",
            "module": "agent.brain",
            "console": "integratedTerminal"
        },
        {
            "name": "Debug Planner",
            "type": "python",
            "request": "launch",
            "module": "agent.planner",
            "console": "integratedTerminal"
        },
        {
            "name": "Debug Approval Engine",
            "type": "python",
            "request": "launch",
            "program": "${workspaceFolder}/agent/approval_engine.py",
            "console": "integratedTerminal"
        },
        {
            "name": "Debug File Watcher",
            "type": "python",
            "request": "launch",
            "program": "${workspaceFolder}/run.py",
            "console": "integratedTerminal"
        }
    ]
}
```

### Set Breakpoints

1. Click left of line number to set breakpoint
2. Press F5 to start debugging
3. Use debug toolbar to step through code

---

## Performance Monitoring

### Monitor Resource Usage

```bash
# Check Python processes
ps aux | grep python

# Check memory usage
top -p $(pgrep -f "approval_engine")
```

### Optimize Performance

1. Adjust check intervals in `.env`
2. Monitor log file sizes
3. Archive old tasks regularly
4. Rotate logs weekly

---

## Stopping the System

### Stop All Services

Press `Ctrl+C` in each terminal running a service.

### Or Kill All Processes

**Windows:**
```batch
taskkill /F /IM python.exe
taskkill /F /IM node.exe
```

**Linux/Mac:**
```bash
pkill -f "approval_engine"
pkill -f "linkedin_watcher"
pkill -f "gmail_watcher"
pkill -f "email_mcp_server"
pkill -f "file_watcher"
```

---

## Next Steps

1. ✅ Verify all services start successfully
2. ✅ Test end-to-end workflow
3. ✅ Monitor logs for 24 hours
4. ✅ Adjust configuration as needed
5. ✅ Set up production scheduling (see SCHEDULER_SETUP.md)

---

*Last Updated: 2026-02-13*
