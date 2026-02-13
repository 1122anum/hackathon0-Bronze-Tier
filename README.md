# 🤖 Personal AI Employee - Bronze Tier

**Version:** 1.0.0 (Minimum Viable Autonomous Agent)
**Status:** Production-Ready
**Architecture:** Local-First, Event-Driven

---

## 📋 Overview

This is a production-ready **Digital FTE (Full-Time Employee)** that operates autonomously inside VS Code. It monitors your Obsidian vault, processes incoming tasks, and takes action without manual prompting.

### What It Does

- 🔍 **Monitors** `vault/Inbox/` for new files
- 🧠 **Classifies** tasks using AI reasoning
- ⚖️ **Prioritizes** work automatically
- 📁 **Organizes** files into appropriate folders
- 📊 **Updates** dashboard in real-time
- 📝 **Logs** every action for transparency

### Architecture

```
Personal_AI_Employee/
│
├── vault/                    # Obsidian markdown vault
│   ├── Dashboard.md         # Real-time system status
│   ├── Company_Handbook.md  # AI operating rules
│   ├── SKILLS.md            # Modular capabilities
│   ├── Inbox/               # Drop files here
│   ├── Needs_Action/        # Pending tasks
│   └── Done/                # Completed work
│
├── watchers/
│   └── file_watcher.py      # Event-driven file monitor
│
├── agent/
│   └── brain.py             # Autonomous reasoning engine
│
├── mcp/                     # Future: MCP servers
├── logs/                    # Action logs
│
├── .env.example             # Configuration template
├── requirements.txt         # Python dependencies
└── README.md               # This file
```

---

## 🚀 Quick Start

### Prerequisites

- **Python 3.13+** installed
- **VS Code** with terminal access
- **Obsidian** (optional, for vault visualization)
- **Git** (for version control)

### Installation

1. **Clone or navigate to project directory**

```bash
cd "C:\Users\Tech Trends\Desktop\Building Autonomous FTEs\Personal_AI_Employee"
```

2. **Create virtual environment**

```bash
python -m venv venv
```

3. **Activate virtual environment**

Windows:
```bash
venv\Scripts\activate
```

Mac/Linux:
```bash
source venv/bin/activate
```

4. **Install dependencies**

```bash
pip install -r requirements.txt
```

5. **Configure environment (optional)**

```bash
copy .env.example .env
# Edit .env with your preferences
```

6. **Verify installation**

```bash
python -c "import watchdog; print('✅ Dependencies installed successfully')"
```

---

## 🎯 Usage

### Starting the AI Employee

Open VS Code terminal and run:

```bash
python watchers/file_watcher.py
```

You should see:

```
================================================================================
AI EMPLOYEE - FILE WATCHER SERVICE
================================================================================
Vault Path: C:\Users\Tech Trends\Desktop\...\vault
Start Time: 2026-02-12T...
================================================================================
🚀 File Watcher started successfully
📂 Monitoring: ...\vault\Inbox
⏳ Waiting for new files...
```

### Testing the System

1. **Create a test file** in `vault/Inbox/`:

```bash
echo "Please research the latest AI trends in 2026" > vault/Inbox/test_task.txt
```

2. **Watch the magic happen**:
   - File is detected instantly
   - AI brain classifies it as "Research"
   - Priority is assigned (e.g., "Medium")
   - File moves to `Needs_Action/`
   - Dashboard updates automatically
   - Action logged in `logs/actions.log`

3. **Check the results**:
   - Open `vault/Dashboard.md` to see updated status
   - Check `vault/Needs_Action/` for the moved file
   - Review `logs/actions.log` for detailed log

### Stopping the System

Press `Ctrl+C` in the terminal:

```
⏹️  Shutdown signal received
🛑 Stopping file watcher...
✅ File watcher stopped successfully
```

---

## 📚 How It Works

### The Reasoning Loop

The AI Brain implements a continuous reasoning loop:

```python
while not task_complete:
    # 1. REASON: Analyze current state
    next_action = brain.reason(state)

    # 2. ACT: Execute the action
    brain.act(state, next_action)

    # 3. EVALUATE: Check if done
    task_complete = brain.evaluate(state)

    # 4. CONTINUE: Loop until complete
```

This is the **"Ralph Wiggum Stop Hook"** pattern - the agent keeps going until the task is truly complete.

### Skill-Based Architecture

Every capability is defined as a modular skill in `SKILLS.md`:

- **Process_New_File** - Initial file handling
- **Classify_Task** - Determine task type
- **Prioritize_Task** - Assign priority level
- **Move_To_Needs_Action** - Organize pending work
- **Move_To_Done** - Archive completed tasks
- **Update_Dashboard** - Refresh status display

Skills have clear:
- **Inputs** - What data they need
- **Outputs** - What they produce
- **Steps** - How they execute
- **Error Handling** - What to do when things fail

### Decision-Making Authority

The AI operates within defined boundaries (see `Company_Handbook.md`):

**✅ Can Do Autonomously:**
- Classify and prioritize tasks
- Move files between folders
- Update dashboard
- Generate summaries
- Log actions

**⚠️ Must Escalate:**
- Ambiguous requirements
- External API calls (not yet configured)
- Destructive operations
- Security concerns

---

## 🔧 Configuration

### Environment Variables

Edit `.env` to customize behavior:

```bash
# Vault location
VAULT_PATH=./vault

# Logging detail
LOG_LEVEL=INFO  # DEBUG, INFO, WARNING, ERROR

# Performance
MAX_ITERATIONS=10  # Safety limit for reasoning loop
PROCESSING_TIMEOUT=300  # Max seconds per task
```

### Customizing Skills

Edit `vault/SKILLS.md` to:
- Add new skills
- Modify existing behavior
- Define custom workflows

### Customizing Rules

Edit `vault/Company_Handbook.md` to:
- Change decision-making authority
- Adjust priority criteria
- Define escalation rules

---

## 📊 Monitoring & Logs

### Dashboard

Open `vault/Dashboard.md` in Obsidian or any markdown viewer to see:
- System status (🟢 Active / 🔴 Down)
- Active tasks being processed
- Pending items in Needs_Action
- Recently completed work
- Last AI action with details
- Performance metrics

### Log Files

**`logs/watcher.log`** - File watcher events
```
2026-02-12 10:30:15 - FileWatcher - INFO - 🆕 New file detected: task.txt
2026-02-12 10:30:15 - AIBrain - INFO - 🧠 Brain processing: task.txt
```

**`logs/actions.log`** - Detailed action history
```
================================================================================
[2026-02-12T10:30:15] FILE PROCESSED
================================================================================
File: task.txt
Success: True
Task Type: Research
Priority: Medium
Action: Moved to Needs_Action
Reasoning: Classified as Research with Medium priority (confidence: 0.70)
================================================================================
```

---

## 🧪 Testing

### Manual Testing

1. **Test Classification**

Create files with different content types:

```bash
# Question
echo "What is the capital of France?" > vault/Inbox/question.txt

# Request
echo "Please create a report on Q4 sales" > vault/Inbox/request.txt

# Urgent task
echo "URGENT: Fix production bug ASAP!!!" > vault/Inbox/urgent.txt
```

Watch how each is classified and prioritized differently.

2. **Test Error Handling**

```bash
# Empty file
type nul > vault/Inbox/empty.txt

# Large file (if you want to test limits)
# Create a file > 10MB
```

3. **Test Dashboard Updates**

After processing files, check `vault/Dashboard.md` to verify:
- Last action log is updated
- Pending items section shows new files
- Timestamp is current

### Automated Testing (Future)

```bash
# When tests are added
pytest tests/
```

---

## 🛠️ Troubleshooting

### Watcher Not Starting

**Error:** `ValueError: Vault path does not exist`

**Solution:** Verify vault path is correct
```bash
# Check if vault exists
dir vault
```

### Files Not Being Processed

**Check:**
1. Is watcher running? (Look for "⏳ Waiting for new files...")
2. Are files in correct location? (`vault/Inbox/`)
3. Are files hidden or temporary? (Starting with `.` or `~`)

**Debug:**
```bash
# Enable debug logging
set LOG_LEVEL=DEBUG
python watchers/file_watcher.py
```

### Import Errors

**Error:** `ModuleNotFoundError: No module named 'watchdog'`

**Solution:** Reinstall dependencies
```bash
pip install -r requirements.txt
```

### Permission Errors

**Error:** `PermissionError: [WinError 32]`

**Solution:** File might be open in another program. Close it and try again.

---

## 🚀 Next Steps (Silver/Gold Tiers)

This is the **Bronze Tier** - a minimum viable autonomous agent. Future enhancements:

### Silver Tier
- ✨ Claude API integration for advanced reasoning
- 🔌 MCP server implementation
- 📧 Email monitoring and processing
- 🔔 Slack/Discord notifications
- 📅 Calendar integration

### Gold Tier
- 🤖 Multi-agent collaboration
- 🧠 Long-term memory system
- 📈 Advanced analytics and insights
- 🔄 Workflow automation builder
- 🌐 Web research capabilities

---

## 📝 Development

### Project Structure

```
watchers/
  file_watcher.py    # Event-driven file monitor
                     # - Uses watchdog library
                     # - Triggers brain on new files
                     # - Handles errors gracefully

agent/
  brain.py           # Autonomous reasoning engine
                     # - Implements reasoning loop
                     # - Manages task state
                     # - Executes skills
                     # - Updates dashboard

vault/
  *.md               # Markdown-based memory
                     # - Human-readable
                     # - Version-controllable
                     # - Obsidian-compatible
```

### Adding New Features

1. **Define skill** in `vault/SKILLS.md`
2. **Implement logic** in `agent/brain.py`
3. **Update handbook** if needed
4. **Test thoroughly**
5. **Update version number**

### Code Style

- Follow PEP 8 for Python
- Use type hints where possible
- Document with docstrings
- Log important actions
- Handle errors gracefully

---

## 🤝 Contributing

This is a personal AI employee system, but feel free to:
- Fork and customize for your needs
- Share improvements and ideas
- Report bugs or issues

---

## 📄 License

MIT License - Use freely, modify as needed

---

## 🙏 Acknowledgments

Built with:
- **Claude Code** - Reasoning engine
- **Obsidian** - Knowledge management
- **Python Watchdog** - File system monitoring
- **VS Code** - Development environment

---

## 📞 Support

For issues or questions:
1. Check `logs/` for error details
2. Review `vault/Company_Handbook.md` for rules
3. Verify configuration in `.env`
4. Test with simple files first

---

**🎉 Congratulations! You now have a working autonomous AI employee.**

Drop a file in `vault/Inbox/` and watch it work its magic. 🚀
