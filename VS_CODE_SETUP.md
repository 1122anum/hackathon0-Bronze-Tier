# VS Code Run Instructions

## Quick Start (Recommended)

1. **Open project in VS Code**
   - File → Open Folder
   - Select `Personal_AI_Employee` folder

2. **Open integrated terminal**
   - Terminal → New Terminal (or Ctrl+`)

3. **Create and activate virtual environment**
   ```bash
   python -m venv venv
   venv\Scripts\activate
   ```

4. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

5. **Run the AI Employee**
   ```bash
   python run.py
   ```

## Alternative: Direct Watcher Launch

```bash
python watchers/file_watcher.py
```

## VS Code Tasks (Optional)

Create `.vscode/tasks.json` for one-click launch:

```json
{
    "version": "2.0.0",
    "tasks": [
        {
            "label": "Start AI Employee",
            "type": "shell",
            "command": "${workspaceFolder}/venv/Scripts/python",
            "args": ["run.py"],
            "problemMatcher": [],
            "presentation": {
                "reveal": "always",
                "panel": "new"
            }
        }
    ]
}
```

Then: Terminal → Run Task → Start AI Employee

## Debugging in VS Code

Create `.vscode/launch.json`:

```json
{
    "version": "0.2.0",
    "configurations": [
        {
            "name": "Debug AI Employee",
            "type": "python",
            "request": "launch",
            "program": "${workspaceFolder}/run.py",
            "console": "integratedTerminal",
            "justMyCode": true
        }
    ]
}
```

Then: F5 to start debugging
