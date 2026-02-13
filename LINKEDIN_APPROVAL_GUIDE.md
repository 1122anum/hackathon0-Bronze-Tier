# LinkedIn Post Approval - Simulation Guide

## How the Approval System Works

The LinkedIn Watcher generates posts and places them in `vault/Pending_Approval/` for human review. Here's how to approve or reject posts.

---

## Method 1: Manual Approval (Recommended)

### Step 1: Locate the Post

```bash
cd Personal_AI_Employee
ls vault/Pending_Approval/
```

You'll see: `2026-02-13__linkedin_post.md`

### Step 2: Open the Post

Open the file in VS Code or any text editor:

```bash
code vault/Pending_Approval/2026-02-13__linkedin_post.md
```

### Step 3: Review the Content

Read through:
- **Content** - The main post text
- **CTA** - Call to action
- **Hashtags** - Relevant hashtags

### Step 4: Approve the Post

Add this line **at the very top** of the file:

```markdown
STATUS: APPROVED

# LinkedIn Post Draft
...rest of file...
```

**Complete example:**
```markdown
STATUS: APPROVED

# LinkedIn Post Draft

**Status:** Draft
**Approval Required:** Yes
**Platform:** LinkedIn
**Topic:** AI Automation in Business
**Generated:** 2026-02-13 18:30:15

---

## Content

🚀 Most businesses are still doing manually what AI could automate in seconds.
...
```

### Step 5: Save the File

Save and close (Ctrl+S in VS Code)

### Step 6: Verify Approval

If you have the approval engine running (Silver Tier), it will:
1. Detect the `STATUS: APPROVED` marker
2. Execute the posting action
3. Move the file to `vault/Approved/`
4. Log the action

**Check logs:**
```bash
tail -f logs/approval_engine.log
```

---

## Method 2: Reject a Post

### Step 1: Open the Post

```bash
code vault/Pending_Approval/2026-02-13__linkedin_post.md
```

### Step 2: Add Rejection Status

Add at the top:

```markdown
STATUS: REJECTED
REJECTION REASON: Content doesn't align with brand voice

# LinkedIn Post Draft
...rest of file...
```

### Step 3: Save and Verify

The approval engine will:
1. Detect rejection
2. Move to `vault/Done/`
3. Create rejection note
4. Log the action

---

## Method 3: Edit Before Approval

### Step 1: Open the Post

```bash
code vault/Pending_Approval/2026-02-13__linkedin_post.md
```

### Step 2: Make Your Edits

Edit any section:

**Before:**
```markdown
## Content

🚀 Most businesses are still doing manually what AI could automate in seconds.
```

**After:**
```markdown
## Content

🚀 Most businesses are STILL doing manually what AI could automate in SECONDS.

Let me share what I've learned...
```

### Step 3: Approve After Editing

Add `STATUS: APPROVED` at the top and save.

---

## Method 4: Automated Approval (Testing Only)

For testing purposes, you can create a script to auto-approve:

### Create `auto_approve.py`:

```python
"""
Auto-approve LinkedIn posts (TESTING ONLY)
DO NOT USE IN PRODUCTION
"""

from pathlib import Path
import time

def auto_approve_posts():
    pending_dir = Path("vault/Pending_Approval")

    for post_file in pending_dir.glob("*__linkedin_post.md"):
        print(f"Auto-approving: {post_file.name}")

        # Read content
        with open(post_file, 'r', encoding='utf-8') as f:
            content = f.read()

        # Add approval status
        approved_content = "STATUS: APPROVED\n\n" + content

        # Write back
        with open(post_file, 'w', encoding='utf-8') as f:
            f.write(approved_content)

        print(f"✅ Approved: {post_file.name}")

if __name__ == "__main__":
    auto_approve_posts()
```

### Run:

```bash
python auto_approve.py
```

**⚠️ WARNING:** Only use for testing. In production, always review posts manually.

---

## Method 5: Batch Approval

If you have multiple posts to approve:

### Create `batch_approve.sh` (Linux/Mac):

```bash
#!/bin/bash
cd vault/Pending_Approval

for file in *__linkedin_post.md; do
    echo "Approving: $file"
    echo -e "STATUS: APPROVED\n\n$(cat $file)" > $file
done

echo "✅ All posts approved"
```

### Or `batch_approve.bat` (Windows):

```batch
@echo off
cd vault\Pending_Approval

for %%f in (*__linkedin_post.md) do (
    echo Approving: %%f
    echo STATUS: APPROVED > temp.txt
    echo. >> temp.txt
    type "%%f" >> temp.txt
    move /y temp.txt "%%f"
)

echo All posts approved
```

---

## Approval Workflow Diagram

```
┌─────────────────────────────────────────────────────────┐
│                  LinkedIn Watcher                        │
│                                                          │
│  1. Generate Post                                        │
│  2. Save to Needs_Action/                               │
│  3. Move to Pending_Approval/                           │
└────────────────────┬────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────┐
│              Pending_Approval Folder                     │
│                                                          │
│  📄 2026-02-13__linkedin_post.md                        │
│     Status: Draft                                        │
│     Awaiting human review...                            │
└────────────────────┬────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────┐
│                 Human Review                             │
│                                                          │
│  Option A: Add "STATUS: APPROVED"                       │
│  Option B: Add "STATUS: REJECTED"                       │
│  Option C: Edit content, then approve                   │
└────────────────────┬────────────────────────────────────┘
                     │
         ┌───────────┴───────────┐
         ▼                       ▼
┌─────────────────┐    ┌─────────────────┐
│   APPROVED      │    │    REJECTED     │
│                 │    │                 │
│ Approval Engine │    │ Approval Engine │
│ detects status  │    │ detects status  │
│                 │    │                 │
│ Executes post   │    │ Moves to Done/  │
│ (via MCP)       │    │ with note       │
│                 │    │                 │
│ Moves to        │    │                 │
│ Approved/       │    │                 │
└─────────────────┘    └─────────────────┘
```

---

## Verification Checklist

After approval, verify:

- [ ] File moved from Pending_Approval/ to Approved/
- [ ] Completion report created (*.completion.md)
- [ ] Action logged in logs/actions.log
- [ ] Approval logged in logs/approval_engine.log
- [ ] Dashboard updated (if integrated)

---

## Common Issues

### Issue: Approval not detected

**Cause:** Approval engine not running

**Solution:**
```bash
# Start approval engine
python -c "from agent.approval_engine import ApprovalEngine; from pathlib import Path; engine = ApprovalEngine(str(Path('vault'))); engine.start_monitoring()"
```

### Issue: File not moving after approval

**Cause:** Incorrect status format

**Solution:** Ensure `STATUS: APPROVED` is:
- At the very top of the file
- Exactly this text (case-sensitive)
- On its own line
- Followed by blank line

### Issue: Post approved but not published

**Cause:** MCP server not running or not configured

**Solution:** See MCP integration guide below

---

## Next Steps

After approval:
1. Post is ready for publishing
2. In production, MCP server would post to LinkedIn API
3. For now, manually copy content to LinkedIn
4. Track engagement metrics

---

*Last Updated: 2026-02-13*
