# 🧪 Testing Guide - Personal AI Employee

This guide provides comprehensive testing steps to verify your AI Employee is working correctly.

---

## Pre-Flight Checklist

Before testing, verify:

- [ ] Python 3.13+ installed (`python --version`)
- [ ] Virtual environment created and activated
- [ ] Dependencies installed (`pip list | findstr watchdog`)
- [ ] All vault folders exist (Inbox, Needs_Action, Done)
- [ ] No files currently in Inbox (clean slate)

---

## Test Suite

### Test 1: Basic System Startup ✅

**Objective:** Verify the system starts without errors

**Steps:**
1. Open terminal in project root
2. Run: `python run.py`

**Expected Output:**
```
================================================================================
🤖 PERSONAL AI EMPLOYEE - BRONZE TIER
================================================================================

✅ Python version check passed
✅ Dependencies installed
✅ Vault structure verified

🚀 Starting AI Employee...
   Press Ctrl+C to stop

================================================================================
AI EMPLOYEE - FILE WATCHER SERVICE
================================================================================
Vault Path: ...\Personal_AI_Employee\vault
Start Time: 2026-02-12T...
================================================================================
🚀 File Watcher started successfully
📂 Monitoring: ...\vault\Inbox
⏳ Waiting for new files...
```

**Pass Criteria:** No errors, system shows "Waiting for new files..."

---

### Test 2: Simple Question Classification 📝

**Objective:** Test classification of a question-type task

**Steps:**
1. Keep watcher running
2. Create file: `vault/Inbox/test_question.txt`
3. Add content: `What is the best way to learn Python in 2026?`
4. Save and observe terminal output

**Expected Terminal Output:**
```
🆕 New file detected: test_question.txt
📄 Processing file: test_question.txt (45 chars)
🧠 Brain processing: test_question.txt
🔄 Reasoning iteration 1
💭 Reasoning: classify_task
⚡ Executing action: classify_task
📋 Classified as: Question (confidence: 0.80)
🔄 Reasoning iteration 2
💭 Reasoning: prioritize_task
⚡ Executing action: prioritize_task
⚖️ Priority assigned: Medium (score: 6)
🔄 Reasoning iteration 3
💭 Reasoning: move_to_needs_action
⚡ Executing action: move_to_needs_action
📁 Moved to Needs_Action: test_question.txt
🔄 Reasoning iteration 4
💭 Reasoning: update_dashboard
⚡ Executing action: update_dashboard
📊 Dashboard updated
✅ Task complete after 4 iterations
✅ Successfully processed: test_question.txt
   Task Type: Question
   Priority: Medium
   Action: Moved to Needs_Action
```

**Verification:**
- [ ] File moved from `Inbox/` to `Needs_Action/`
- [ ] Metadata file created: `test_question.meta.json`
- [ ] Dashboard.md updated with last action
- [ ] Entry in `logs/actions.log`

**Pass Criteria:** All verifications checked, no errors

---

### Test 3: Urgent Request Processing 🚨

**Objective:** Test priority detection for urgent tasks

**Steps:**
1. Create file: `vault/Inbox/urgent_task.txt`
2. Add content: `URGENT: Please fix the production database connection ASAP!!!`
3. Observe processing

**Expected Behavior:**
- Classified as: **Request**
- Priority: **High** (due to "URGENT" and "ASAP" markers)
- Moved to: **Needs_Action**

**Verification:**
```bash
# Check metadata
type "vault\Needs_Action\urgent_task.meta.json"
```

Should show:
```json
{
  "task_type": "Request",
  "priority": "High",
  "confidence": 0.7
}
```

**Pass Criteria:** Priority is "High", not "Medium" or "Low"

---

### Test 4: Data Processing Task 📊

**Objective:** Test classification of data-related tasks

**Steps:**
1. Create file: `vault/Inbox/data_analysis.txt`
2. Add content: `Please analyze the sales data from Q4 and calculate the growth rate`
3. Observe processing

**Expected Behavior:**
- Classified as: **Data_Processing**
- Priority: **Medium**
- Moved to: **Needs_Action**

**Pass Criteria:** Correctly classified as Data_Processing

---

### Test 5: Research Task 🔍

**Objective:** Test research task classification

**Steps:**
1. Create file: `vault/Inbox/research_request.txt`
2. Add content: `Research the latest trends in AI agents and find relevant papers`
3. Observe processing

**Expected Behavior:**
- Classified as: **Research**
- Priority: **Medium** or **Low** (research is time-intensive)
- Moved to: **Needs_Action**

**Pass Criteria:** Correctly classified as Research

---

### Test 6: Empty File Handling 🗑️

**Objective:** Test error handling for invalid files

**Steps:**
1. Create empty file: `type nul > vault/Inbox/empty_file.txt`
2. Observe processing

**Expected Terminal Output:**
```
🆕 New file detected: empty_file.txt
📄 Processing file: empty_file.txt (0 chars)
⚠️ Empty file detected: empty_file.txt
📦 Moved empty file to Done: empty_file.txt
```

**Verification:**
- [ ] File moved to `Done/` (not Needs_Action)
- [ ] Note file created: `empty_file.note.md`

**Pass Criteria:** Empty file handled gracefully, no crash

---

### Test 7: Multiple Files Simultaneously 🔄

**Objective:** Test concurrent file processing

**Steps:**
1. Create 3 files quickly:
   ```bash
   echo "Question 1: What is AI?" > vault/Inbox/q1.txt
   echo "Question 2: How does ML work?" > vault/Inbox/q2.txt
   echo "Question 3: What is deep learning?" > vault/Inbox/q3.txt
   ```
2. Observe processing

**Expected Behavior:**
- All 3 files processed sequentially
- Each gets classified and moved
- No files lost or skipped

**Verification:**
```bash
# Check all files moved
dir vault\Needs_Action\q*.txt
```

Should show all 3 files.

**Pass Criteria:** All files processed successfully, no errors

---

### Test 8: Dashboard Update Verification 📊

**Objective:** Verify dashboard reflects current state

**Steps:**
1. After processing several files, open `vault/Dashboard.md`
2. Check the following sections:

**Expected Content:**

```markdown
## 📝 Last AI Action Log

[2026-02-12 ...] Processed: [filename]
Task Type: [type]
Priority: [priority]
Actions: classified_as:..., prioritized_as:..., moved_to:Needs_Action, dashboard_updated
Status: ✅ Success
```

**Verification:**
- [ ] Timestamp is recent
- [ ] Last processed file is shown
- [ ] Task type and priority are correct
- [ ] Status shows success

**Pass Criteria:** Dashboard accurately reflects last action

---

### Test 9: Log File Verification 📝

**Objective:** Verify comprehensive logging

**Steps:**
1. After processing files, check logs:

```bash
# View watcher log
type logs\watcher.log

# View actions log
type logs\actions.log
```

**Expected in watcher.log:**
```
2026-02-12 ... - FileWatcher - INFO - 🆕 New file detected: ...
2026-02-12 ... - AIBrain - INFO - 🧠 Brain processing: ...
2026-02-12 ... - AIBrain - INFO - ✅ Task complete after X iterations
```

**Expected in actions.log:**
```
================================================================================
[2026-02-12T...] FILE PROCESSED
================================================================================
File: test_question.txt
Success: True
Task Type: Question
Priority: Medium
...
```

**Pass Criteria:** Both logs contain detailed entries for all processed files

---

### Test 10: Graceful Shutdown 🛑

**Objective:** Test clean system shutdown

**Steps:**
1. With watcher running, press `Ctrl+C`

**Expected Output:**
```
⏹️  Shutdown signal received
🛑 Stopping file watcher...
✅ File watcher stopped successfully
```

**Pass Criteria:** Clean shutdown, no errors or hanging processes

---

### Test 11: Restart and Resume ♻️

**Objective:** Verify system can restart cleanly

**Steps:**
1. Stop the watcher (Ctrl+C)
2. Restart: `python run.py`
3. Add a new file to Inbox
4. Verify processing continues normally

**Pass Criteria:** System restarts without issues, processes new files

---

### Test 12: Metadata File Validation 📋

**Objective:** Verify metadata files are created correctly

**Steps:**
1. After processing a file, check its metadata:

```bash
type "vault\Needs_Action\test_question.meta.json"
```

**Expected Structure:**
```json
{
  "original_path": "..\\vault\\Inbox\\test_question.txt",
  "moved_at": "2026-02-12T...",
  "task_type": "Question",
  "priority": "Medium",
  "confidence": 0.8,
  "reason": "Classified as Question with Medium priority"
}
```

**Verification:**
- [ ] Valid JSON format
- [ ] All required fields present
- [ ] Timestamp is ISO format
- [ ] Confidence is between 0.0 and 1.0

**Pass Criteria:** Metadata is well-formed and accurate

---

## Performance Tests

### Test 13: Processing Speed ⚡

**Objective:** Measure processing time

**Steps:**
1. Note the time
2. Create a test file
3. Observe how long until "Task complete" message

**Expected:** < 2 seconds for simple files

**Pass Criteria:** Processing completes in reasonable time

---

### Test 14: Large File Handling 📦

**Objective:** Test with larger content

**Steps:**
1. Create file with ~1000 words of content
2. Observe processing

**Expected:** Should process successfully, might take slightly longer

**Pass Criteria:** No timeout or memory errors

---

## Edge Case Tests

### Test 15: Special Characters in Filename 🔤

**Steps:**
1. Create file: `vault/Inbox/test-file_2026.txt`
2. Verify processing

**Pass Criteria:** Handles hyphens, underscores, numbers correctly

---

### Test 16: Hidden File Ignore 👻

**Steps:**
1. Create hidden file: `vault/Inbox/.hidden_file.txt`
2. Observe terminal

**Expected:** File is ignored (debug log shows "Ignoring temporary/hidden file")

**Pass Criteria:** Hidden files are not processed

---

### Test 17: Temporary File Ignore 📄

**Steps:**
1. Create temp file: `vault/Inbox/~temp.txt`
2. Observe terminal

**Expected:** File is ignored

**Pass Criteria:** Temp files are not processed

---

## Integration Tests

### Test 18: Full Workflow End-to-End 🔄

**Objective:** Test complete workflow from Inbox to Done

**Steps:**
1. Create file in Inbox
2. Verify it moves to Needs_Action
3. Manually move it to Done (simulating completion)
4. Verify metadata is preserved

**Pass Criteria:** File successfully moves through all stages

---

## Stress Tests (Optional)

### Test 19: Rapid File Creation 💨

**Steps:**
1. Create 10 files in quick succession:
```bash
for /L %i in (1,1,10) do echo Test %i > vault/Inbox/test_%i.txt
```
2. Verify all are processed

**Pass Criteria:** All files processed, none lost

---

## Test Results Template

Use this template to track your testing:

```
TEST RESULTS - Personal AI Employee
====================================
Date: ___________
Tester: ___________

[ ] Test 1: Basic System Startup
[ ] Test 2: Simple Question Classification
[ ] Test 3: Urgent Request Processing
[ ] Test 4: Data Processing Task
[ ] Test 5: Research Task
[ ] Test 6: Empty File Handling
[ ] Test 7: Multiple Files Simultaneously
[ ] Test 8: Dashboard Update Verification
[ ] Test 9: Log File Verification
[ ] Test 10: Graceful Shutdown
[ ] Test 11: Restart and Resume
[ ] Test 12: Metadata File Validation
[ ] Test 13: Processing Speed
[ ] Test 14: Large File Handling
[ ] Test 15: Special Characters in Filename
[ ] Test 16: Hidden File Ignore
[ ] Test 17: Temporary File Ignore
[ ] Test 18: Full Workflow End-to-End
[ ] Test 19: Rapid File Creation

OVERALL STATUS: [ ] PASS [ ] FAIL

Notes:
_________________________________
_________________________________
```

---

## Troubleshooting Common Issues

### Issue: Files not being detected

**Solution:**
- Verify watcher is running
- Check file is in correct Inbox folder
- Ensure file is not hidden (doesn't start with `.` or `~`)

### Issue: Classification seems wrong

**Solution:**
- This is expected in Bronze Tier (rule-based classification)
- Silver Tier will use Claude API for better accuracy
- You can adjust classification logic in `brain.py`

### Issue: Dashboard not updating

**Solution:**
- Check if Dashboard.md is open in another program
- Verify file permissions
- Check logs for errors

---

## Success Criteria Summary

Your AI Employee is working correctly if:

✅ System starts without errors
✅ Files are detected within 1 second
✅ Classification happens automatically
✅ Files move to correct folders
✅ Metadata files are created
✅ Dashboard updates in real-time
✅ All actions are logged
✅ System shuts down cleanly
✅ No crashes or hangs

---

**🎉 If all tests pass, your AI Employee is production-ready!**
