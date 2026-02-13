# LinkedIn Watcher - Quick Start Guide

## Run in VS Code

### Option 1: Direct Python Command

Open a new terminal in VS Code (Ctrl+`) and run:

```bash
cd Personal_AI_Employee
python watchers/linkedin_watcher.py
```

### Option 2: With Virtual Environment

```bash
cd Personal_AI_Employee
venv\Scripts\activate  # Windows
# OR
source venv/bin/activate  # Linux/Mac

python watchers/linkedin_watcher.py
```

### Option 3: VS Code Task (Recommended)

Add to `.vscode/tasks.json`:

```json
{
    "label": "Start LinkedIn Watcher",
    "type": "shell",
    "command": "${command:python.interpreterPath}",
    "args": [
        "watchers/linkedin_watcher.py"
    ],
    "isBackground": true,
    "problemMatcher": [],
    "presentation": {
        "reveal": "always",
        "panel": "dedicated",
        "group": "watchers"
    }
}
```

Then: `Ctrl+Shift+P` → "Tasks: Run Task" → "Start LinkedIn Watcher"

---

## Expected Output

```
============================================================
LinkedIn Watcher Started
============================================================
Monitoring interval: 60 minutes
Vault path: C:\...\Personal_AI_Employee\vault
Press Ctrl+C to stop
============================================================
2026-02-13 18:30:15 - LinkedInWatcher - INFO - Generating initial post...
2026-02-13 18:30:15 - LinkedInWatcher - INFO - Generating LinkedIn post...
2026-02-13 18:30:15 - LinkedInWatcher - INFO - Generated post on topic: AI Automation in Business
2026-02-13 18:30:15 - LinkedInWatcher - INFO - Post saved to: vault\Needs_Action\2026-02-13__linkedin_post.md
2026-02-13 18:30:15 - LinkedInWatcher - INFO - Moved to Pending_Approval: 2026-02-13__linkedin_post.md
2026-02-13 18:30:15 - LinkedInWatcher - INFO - ✅ LinkedIn post generated and moved to Pending_Approval
2026-02-13 18:30:15 - LinkedInWatcher - INFO - Next check in 60 minutes...
```

---

## Stop the Watcher

Press `Ctrl+C` in the terminal. The watcher will shut down gracefully:

```
2026-02-13 18:35:20 - LinkedInWatcher - INFO - Shutdown signal received. Finishing current operation...
2026-02-13 18:35:20 - LinkedInWatcher - INFO - LinkedIn Watcher stopped gracefully
```

---

## Configuration

Edit `.env` to customize:

```env
POST_INTERVAL_MINUTES=60    # Change to 5 for testing (generates every 5 minutes)
LOG_LEVEL=INFO              # Change to DEBUG for verbose logging
VAULT_PATH=vault            # Change if vault is in different location
```

---

## Troubleshooting

**Issue: "ModuleNotFoundError: No module named 'dotenv'"**

Solution:
```bash
pip install python-dotenv
```

**Issue: "Permission denied" when creating directories**

Solution: Run VS Code as administrator or check folder permissions

**Issue: Post not generating**

Solution: Check logs at `logs/linkedin_watcher.log` for errors

---

*Last Updated: 2026-02-13*
