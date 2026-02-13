# Scheduler Setup - Silver Tier

This document provides instructions for setting up scheduled tasks for the Personal AI Employee system.

---

## Overview

The Silver Tier system includes several scheduled tasks:

1. **Daily LinkedIn Post** - 9:00 AM weekdays
2. **Monday Morning CEO Brief** - 9:00 AM Mondays
3. **Approval Monitoring** - Every 30 seconds
4. **Gmail Monitoring** - Every 60 seconds

---

## Option 1: Windows Task Scheduler

### Prerequisites
- Windows 10 or later
- Python 3.13+ installed
- Personal_AI_Employee system installed

### Setup Steps

#### 1. Create Batch Scripts

Create the following batch files in the `Personal_AI_Employee` directory:

**run_approval_engine.bat**
```batch
@echo off
cd /d "%~dp0"
call venv\Scripts\activate.bat
python -c "from agent.approval_engine import ApprovalEngine; from pathlib import Path; engine = ApprovalEngine(str(Path('vault'))); engine.start_monitoring()"
```

**run_linkedin_watcher.bat**
```batch
@echo off
cd /d "%~dp0"
call venv\Scripts\activate.bat
python -c "from watchers.linkedin_watcher import LinkedInWatcher; from pathlib import Path; watcher = LinkedInWatcher(str(Path('vault'))); watcher.start_monitoring()"
```

**run_gmail_watcher.bat**
```batch
@echo off
cd /d "%~dp0"
call venv\Scripts\activate.bat
python watchers\gmail_watcher.py
```

#### 2. Configure Task Scheduler

1. Open **Task Scheduler** (search in Start menu)
2. Click **Create Basic Task** in the right panel

##### Task 1: Approval Engine (Continuous)

- **Name:** AI Employee - Approval Engine
- **Description:** Monitors pending approvals and executes approved actions
- **Trigger:** At startup
- **Action:** Start a program
  - **Program:** `C:\path\to\Personal_AI_Employee\run_approval_engine.bat`
- **Settings:**
  - ✅ Run whether user is logged on or not
  - ✅ Run with highest privileges
  - ✅ If task fails, restart every 1 minute

##### Task 2: LinkedIn Watcher (Continuous)

- **Name:** AI Employee - LinkedIn Watcher
- **Description:** Monitors LinkedIn posting schedule
- **Trigger:** At startup
- **Action:** Start a program
  - **Program:** `C:\path\to\Personal_AI_Employee\run_linkedin_watcher.bat`
- **Settings:**
  - ✅ Run whether user is logged on or not
  - ✅ Run with highest privileges
  - ✅ If task fails, restart every 1 minute

##### Task 3: Gmail Watcher (Continuous)

- **Name:** AI Employee - Gmail Watcher
- **Description:** Monitors Gmail inbox for new emails
- **Trigger:** At startup
- **Action:** Start a program
  - **Program:** `C:\path\to\Personal_AI_Employee\run_gmail_watcher.bat`
- **Settings:**
  - ✅ Run whether user is logged on or not
  - ✅ Run with highest privileges
  - ✅ If task fails, restart every 1 minute

#### 3. Verify Tasks

1. Right-click each task and select **Run**
2. Check logs in `logs/` directory
3. Verify processes are running in Task Manager

---

## Option 2: Linux/Mac Cron

### Prerequisites
- Linux or macOS
- Python 3.13+ installed
- Personal_AI_Employee system installed

### Setup Steps

#### 1. Create Shell Scripts

Create the following scripts in the `Personal_AI_Employee` directory:

**run_approval_engine.sh**
```bash
#!/bin/bash
cd "$(dirname "$0")"
source venv/bin/activate
python -c "from agent.approval_engine import ApprovalEngine; from pathlib import Path; engine = ApprovalEngine(str(Path('vault'))); engine.start_monitoring()"
```

**run_linkedin_watcher.sh**
```bash
#!/bin/bash
cd "$(dirname "$0")"
source venv/bin/activate
python -c "from watchers.linkedin_watcher import LinkedInWatcher; from pathlib import Path; watcher = LinkedInWatcher(str(Path('vault'))); watcher.start_monitoring()"
```

**run_gmail_watcher.sh**
```bash
#!/bin/bash
cd "$(dirname "$0")"
source venv/bin/activate
python watchers/gmail_watcher.py
```

Make scripts executable:
```bash
chmod +x run_approval_engine.sh
chmod +x run_linkedin_watcher.sh
chmod +x run_gmail_watcher.sh
```

#### 2. Configure Cron

Edit crontab:
```bash
crontab -e
```

Add the following entries:
```cron
# AI Employee - Start watchers at boot
@reboot cd /path/to/Personal_AI_Employee && ./run_approval_engine.sh >> logs/approval_engine.log 2>&1 &
@reboot cd /path/to/Personal_AI_Employee && ./run_linkedin_watcher.sh >> logs/linkedin_watcher.log 2>&1 &
@reboot cd /path/to/Personal_AI_Employee && ./run_gmail_watcher.sh >> logs/gmail_watcher.log 2>&1 &

# Keep processes alive (check every 5 minutes)
*/5 * * * * pgrep -f "approval_engine" > /dev/null || (cd /path/to/Personal_AI_Employee && ./run_approval_engine.sh >> logs/approval_engine.log 2>&1 &)
*/5 * * * * pgrep -f "linkedin_watcher" > /dev/null || (cd /path/to/Personal_AI_Employee && ./run_linkedin_watcher.sh >> logs/linkedin_watcher.log 2>&1 &)
*/5 * * * * pgrep -f "gmail_watcher" > /dev/null || (cd /path/to/Personal_AI_Employee && ./run_gmail_watcher.sh >> logs/gmail_watcher.log 2>&1 &)
```

#### 3. Verify Cron Jobs

```bash
# List cron jobs
crontab -l

# Check if processes are running
ps aux | grep -E "approval_engine|linkedin_watcher|gmail_watcher"

# Check logs
tail -f logs/approval_engine.log
tail -f logs/linkedin_watcher.log
tail -f logs/gmail_watcher.log
```

---

## Option 3: systemd (Linux - Recommended)

### Prerequisites
- Linux with systemd
- Root or sudo access

### Setup Steps

#### 1. Create Service Files

Create `/etc/systemd/system/ai-employee-approval.service`:
```ini
[Unit]
Description=AI Employee Approval Engine
After=network.target

[Service]
Type=simple
User=your-username
WorkingDirectory=/path/to/Personal_AI_Employee
ExecStart=/path/to/Personal_AI_Employee/venv/bin/python -c "from agent.approval_engine import ApprovalEngine; from pathlib import Path; engine = ApprovalEngine(str(Path('vault'))); engine.start_monitoring()"
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

Create `/etc/systemd/system/ai-employee-linkedin.service`:
```ini
[Unit]
Description=AI Employee LinkedIn Watcher
After=network.target

[Service]
Type=simple
User=your-username
WorkingDirectory=/path/to/Personal_AI_Employee
ExecStart=/path/to/Personal_AI_Employee/venv/bin/python -c "from watchers.linkedin_watcher import LinkedInWatcher; from pathlib import Path; watcher = LinkedInWatcher(str(Path('vault'))); watcher.start_monitoring()"
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

Create `/etc/systemd/system/ai-employee-gmail.service`:
```ini
[Unit]
Description=AI Employee Gmail Watcher
After=network.target

[Service]
Type=simple
User=your-username
WorkingDirectory=/path/to/Personal_AI_Employee
ExecStart=/path/to/Personal_AI_Employee/venv/bin/python watchers/gmail_watcher.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

#### 2. Enable and Start Services

```bash
# Reload systemd
sudo systemctl daemon-reload

# Enable services (start at boot)
sudo systemctl enable ai-employee-approval.service
sudo systemctl enable ai-employee-linkedin.service
sudo systemctl enable ai-employee-gmail.service

# Start services now
sudo systemctl start ai-employee-approval.service
sudo systemctl start ai-employee-linkedin.service
sudo systemctl start ai-employee-gmail.service
```

#### 3. Manage Services

```bash
# Check status
sudo systemctl status ai-employee-approval.service
sudo systemctl status ai-employee-linkedin.service
sudo systemctl status ai-employee-gmail.service

# View logs
sudo journalctl -u ai-employee-approval.service -f
sudo journalctl -u ai-employee-linkedin.service -f
sudo journalctl -u ai-employee-gmail.service -f

# Stop services
sudo systemctl stop ai-employee-approval.service
sudo systemctl stop ai-employee-linkedin.service
sudo systemctl stop ai-employee-gmail.service

# Restart services
sudo systemctl restart ai-employee-approval.service
sudo systemctl restart ai-employee-linkedin.service
sudo systemctl restart ai-employee-gmail.service
```

---

## MCP Server Setup

The MCP email server runs separately and should be started before the Python components.

### Start MCP Server

**Windows:**
```batch
cd mcp_server
npm install
npm start
```

**Linux/Mac:**
```bash
cd mcp_server
npm install
npm start
```

### Run as Service (systemd)

Create `/etc/systemd/system/ai-employee-mcp.service`:
```ini
[Unit]
Description=AI Employee MCP Email Server
After=network.target

[Service]
Type=simple
User=your-username
WorkingDirectory=/path/to/Personal_AI_Employee/mcp_server
ExecStart=/usr/bin/node email_mcp_server.js
Restart=always
RestartSec=10
Environment=NODE_ENV=production

[Install]
WantedBy=multi-user.target
```

Enable and start:
```bash
sudo systemctl daemon-reload
sudo systemctl enable ai-employee-mcp.service
sudo systemctl start ai-employee-mcp.service
sudo systemctl status ai-employee-mcp.service
```

---

## Verification

### Check All Services Are Running

**Windows:**
```batch
tasklist | findstr python
tasklist | findstr node
```

**Linux/Mac:**
```bash
ps aux | grep -E "approval_engine|linkedin_watcher|gmail_watcher|email_mcp_server"
```

### Check Logs

```bash
# View all logs
tail -f logs/*.log

# View specific log
tail -f logs/approval_engine.log
```

### Test Functionality

1. **Test Approval Engine:**
   - Create a test plan in `vault/Pending_Approval/`
   - Add `STATUS: APPROVED` to the file
   - Check logs for execution

2. **Test LinkedIn Watcher:**
   - Check `logs/linkedin_watcher.log`
   - Verify next post time is calculated

3. **Test Gmail Watcher:**
   - Send a test email to your configured Gmail
   - Check `vault/Inbox/` for new file

4. **Test MCP Server:**
   ```bash
   curl http://localhost:3000/health
   ```

---

## Troubleshooting

### Services Not Starting

1. Check Python virtual environment is activated
2. Verify all dependencies are installed: `pip install -r requirements.txt`
3. Check file permissions
4. Review logs for error messages

### Services Crashing

1. Check logs for error messages
2. Verify `.env` configuration is correct
3. Ensure Gmail API credentials are valid
4. Check MCP server is running

### No Tasks Being Processed

1. Verify file watcher is running
2. Check `vault/Inbox/` has files
3. Review `logs/watcher.log` for errors
4. Ensure brain.py is being triggered

---

## Monitoring

### Log Rotation

Add to crontab for automatic log rotation:
```cron
# Rotate logs weekly
0 0 * * 0 cd /path/to/Personal_AI_Employee/logs && for f in *.log; do mv "$f" "$f.$(date +\%Y\%m\%d)"; done
```

### Health Checks

Create a monitoring script to check service health:
```bash
#!/bin/bash
# health_check.sh

services=("approval_engine" "linkedin_watcher" "gmail_watcher")

for service in "${services[@]}"; do
    if pgrep -f "$service" > /dev/null; then
        echo "✅ $service is running"
    else
        echo "❌ $service is NOT running"
    fi
done
```

---

## Next Steps

After setting up scheduling:

1. Monitor logs for first 24 hours
2. Verify LinkedIn posts are generated on schedule
3. Test approval workflow end-to-end
4. Adjust check intervals if needed
5. Set up alerts for service failures

---

*Last Updated: 2026-02-13*
