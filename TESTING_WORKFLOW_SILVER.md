# Silver Tier Testing Workflow

Complete end-to-end testing guide for the Personal AI Employee Silver Tier system.

---

## Testing Overview

This document provides step-by-step testing procedures for all Silver Tier features:

1. Planning System
2. Approval Workflow
3. LinkedIn Auto-Posting
4. Email via MCP
5. Multi-Watcher Integration
6. Scheduling System

---

## Prerequisites

- All services running (see VSCODE_RUN_INSTRUCTIONS_SILVER.md)
- MCP server running on port 3000
- Gmail API configured
- Virtual environment activated

---

## Test 1: Planning System

### Objective
Verify that complex tasks trigger plan generation with proper risk assessment.

### Steps

1. **Create test task file:**

```bash
cat > vault/Inbox/test_email_task.txt << 'EOF'
Send an email to john.doe@example.com with subject "Project Status Update"

Body:
Hi John,

The project is progressing well. We've completed phase 1 and are moving into phase 2.
Expected completion date is next Friday.

Best regards
EOF
```

2. **Monitor logs:**

```bash
tail -f logs/watcher.log
```

3. **Expected behavior:**
   - File detected by watcher
   - Brain processes file
   - Task classified as "Request"
   - Priority assigned
   - Plan generated (because "email" keyword detected)
   - Plan moved to `vault/Pending_Approval/`

4. **Verify plan created:**

```bash
ls -la vault/Pending_Approval/
```

5. **Check plan content:**

Open the plan file and verify:
- ✅ Objective clearly stated
- ✅ Required skills listed (Send_Email_via_MCP)
- ✅ Execution steps numbered
- ✅ Risk assessment shows "High" or "Medium"
- ✅ Approval required = YES
- ✅ Approval instructions included

### Expected Result

✅ **PASS:** Plan generated and moved to Pending_Approval
❌ **FAIL:** If plan not created or missing sections

---

## Test 2: Approval Workflow

### Objective
Verify human-in-the-loop approval system works correctly.

### Steps

1. **Locate pending plan:**

```bash
ls vault/Pending_Approval/
```

2. **Open plan file in editor**

3. **Approve the plan:**

Add this line at the very top of the file:
```
STATUS: APPROVED
```

Save the file.

4. **Monitor approval engine logs:**

```bash
tail -f logs/approval_engine.log
```

5. **Expected behavior within 30 seconds:**
   - Approval engine detects status change
   - Logs show "Approval detected"
   - Actions executed (simulated for now)
   - Plan moved to `vault/Approved/`
   - Completion report created

6. **Verify plan moved:**

```bash
ls -la vault/Approved/
ls -la vault/Approved/*.completion.md
```

7. **Check completion report:**

Open the `.completion.md` file and verify:
- ✅ All actions listed
- ✅ Success status for each action
- ✅ Timestamp recorded

### Expected Result

✅ **PASS:** Plan approved and executed, moved to Approved folder
❌ **FAIL:** If plan not moved or execution failed

---

## Test 3: Rejection Workflow

### Objective
Verify rejection handling works correctly.

### Steps

1. **Create another test task:**

```bash
echo "Delete all customer data from the database" > vault/Inbox/test_dangerous_task.txt
```

2. **Wait for plan generation**

3. **Locate plan in Pending_Approval**

4. **Reject the plan:**

Add at the top of the file:
```
STATUS: REJECTED
REJECTION REASON: This action is too dangerous and requires manual review
```

Save the file.

5. **Monitor approval engine logs**

6. **Expected behavior:**
   - Rejection detected
   - Plan moved to `vault/Done/`
   - Rejection note created

7. **Verify rejection:**

```bash
ls -la vault/Done/
cat vault/Done/*.rejection.md
```

### Expected Result

✅ **PASS:** Plan rejected and moved to Done with rejection note
❌ **FAIL:** If plan not handled correctly

---

## Test 4: LinkedIn Post Generation

### Objective
Verify LinkedIn post generation and approval workflow.

### Steps

1. **Manually trigger post generation:**

```bash
python -c "from watchers.linkedin_watcher import LinkedInWatcher; from pathlib import Path; w = LinkedInWatcher(str(Path('vault'))); result = w._trigger_post_generation(); print(result)"
```

2. **Expected output:**

```json
{
  "success": true,
  "post_file": "LinkedIn_Post_20260213_143022.md",
  "post_path": "vault/Needs_Action/LinkedIn_Post_20260213_143022.md"
}
```

3. **Verify post created:**

```bash
ls -la vault/Needs_Action/LinkedIn_Post_*.md
```

4. **Open post file and verify:**
   - ✅ Professional business content
   - ✅ Engagement hook (first line)
   - ✅ Main content (3-5 paragraphs)
   - ✅ Call-to-action
   - ✅ Hashtags (3-5)
   - ✅ Approval instructions

5. **Approve the post:**

Add `STATUS: APPROVED` at the top and save.

6. **Monitor approval engine:**

The post should be processed (in production, this would trigger actual LinkedIn posting via API).

### Expected Result

✅ **PASS:** LinkedIn post generated with proper format and approval workflow
❌ **FAIL:** If post missing elements or approval fails

---

## Test 5: LinkedIn Scheduling

### Objective
Verify LinkedIn watcher respects posting schedule.

### Steps

1. **Check current schedule:**

```bash
python -c "from watchers.linkedin_watcher import LinkedInWatcher; from pathlib import Path; w = LinkedInWatcher(str(Path('vault'))); print(w.posting_schedule)"
```

2. **Check posting status:**

```bash
python -c "from watchers.linkedin_watcher import LinkedInWatcher; from pathlib import Path; w = LinkedInWatcher(str(Path('vault'))); result = w.check_posting_schedule(); print(result)"
```

3. **Expected output:**

```json
{
  "post_triggered": false,
  "reason": "Not time yet (scheduled: 09:00:00, current: 14:30:15)",
  "next_post_time": "2026-02-14 09:00"
}
```

4. **Verify state file:**

```bash
cat logs/linkedin_state.json
```

### Expected Result

✅ **PASS:** Watcher correctly calculates next post time and respects schedule
❌ **FAIL:** If scheduling logic incorrect

---

## Test 6: MCP Email Server

### Objective
Verify MCP server can send emails (or simulate sending).

### Steps

1. **Check MCP server is running:**

```bash
curl http://localhost:3000/health
```

Expected:
```json
{
  "status": "healthy",
  "service": "MCP Email Server",
  "version": "1.0.0"
}
```

2. **Test email sending (simulation):**

```bash
curl -X POST http://localhost:3000/send-email \
  -H "Content-Type: application/json" \
  -d '{
    "to": "test@example.com",
    "subject": "Test Email from MCP Server",
    "body": "This is a test email to verify the MCP server is working correctly."
  }'
```

3. **Expected response:**

```json
{
  "success": true,
  "message_id": "<unique-id>",
  "timestamp": "2026-02-13T14:35:22.123Z",
  "duration_ms": 245
}
```

4. **Check MCP server logs:**

```bash
tail -20 logs/mcp_server.log
```

Verify:
- ✅ Request logged
- ✅ Email parameters validated
- ✅ Send attempt logged
- ✅ Success/failure recorded

### Expected Result

✅ **PASS:** MCP server accepts requests and processes them correctly
❌ **FAIL:** If server errors or doesn't respond

---

## Test 7: Gmail Integration

### Objective
Verify Gmail watcher detects and processes emails.

### Steps

1. **Send test email to your configured Gmail:**

Subject: "Test Task from Gmail"
Body:
```
Please analyze the Q4 sales data and prepare a summary report.

This is urgent and needs to be completed by end of day.
```

2. **Monitor Gmail watcher logs:**

```bash
tail -f logs/gmail_watcher.log
```

3. **Expected behavior within 60 seconds:**
   - New email detected
   - Email fetched via Gmail API
   - Converted to markdown
   - Saved to `vault/Inbox/`
   - Brain triggered to process

4. **Verify email file created:**

```bash
ls -la vault/Inbox/Email_*.md
```

5. **Check email content:**

Open the file and verify:
- ✅ From address
- ✅ Subject
- ✅ Date
- ✅ Body content
- ✅ Proper markdown formatting

6. **Verify processing:**

Check that brain processed the email:
- Classified as task type
- Priority assigned
- Moved to appropriate folder

### Expected Result

✅ **PASS:** Email detected, converted, and processed automatically
❌ **FAIL:** If email not detected or processing fails

---

## Test 8: Multi-File Processing

### Objective
Verify system can handle multiple tasks simultaneously.

### Steps

1. **Create multiple test files:**

```bash
echo "Research competitor pricing strategies" > vault/Inbox/task1.txt
echo "Send weekly report to team@company.com" > vault/Inbox/task2.txt
echo "Update project documentation" > vault/Inbox/task3.txt
echo "URGENT: Fix production bug in payment system" > vault/Inbox/task4.txt
```

2. **Monitor watcher logs:**

```bash
tail -f logs/watcher.log
```

3. **Expected behavior:**
   - All 4 files detected
   - Each processed independently
   - Different priorities assigned based on content
   - Plans generated for email task
   - Files moved to appropriate folders

4. **Verify processing:**

```bash
# Check Needs_Action
ls -la vault/Needs_Action/

# Check Pending_Approval
ls -la vault/Pending_Approval/

# Check logs for all 4 tasks
grep -E "task[1-4]\.txt" logs/watcher.log
```

### Expected Result

✅ **PASS:** All tasks processed correctly with appropriate handling
❌ **FAIL:** If any task missed or incorrectly processed

---

## Test 9: Dashboard Updates

### Objective
Verify dashboard updates in real-time.

### Steps

1. **Open dashboard in VS Code:**

```bash
code vault/Dashboard.md
```

Enable preview (Ctrl+Shift+V)

2. **Process a test task:**

```bash
echo "Test dashboard update" > vault/Inbox/dashboard_test.txt
```

3. **Watch dashboard file:**

```bash
watch -n 1 cat vault/Dashboard.md
```

4. **Verify updates:**
   - ✅ "Last Updated" timestamp changes
   - ✅ "Last AI Action Log" shows new task
   - ✅ Task details included (type, priority, actions)
   - ✅ Status shows success

### Expected Result

✅ **PASS:** Dashboard updates automatically with task information
❌ **FAIL:** If dashboard not updated or shows incorrect data

---

## Test 10: Error Handling

### Objective
Verify system handles errors gracefully.

### Steps

1. **Test with empty file:**

```bash
touch vault/Inbox/empty_file.txt
```

Expected: File moved to Done with "empty file" note

2. **Test with corrupted file:**

```bash
echo -e "\x00\x01\x02\x03" > vault/Inbox/corrupted.txt
```

Expected: Error logged, file handled gracefully

3. **Test with very large file:**

```bash
yes "This is a test line" | head -10000 > vault/Inbox/large_file.txt
```

Expected: File processed (may take longer)

4. **Check error logs:**

```bash
grep -i error logs/*.log
```

### Expected Result

✅ **PASS:** All error cases handled without crashing
❌ **FAIL:** If system crashes or hangs

---

## Test 11: End-to-End Workflow

### Objective
Complete workflow from email to approved action.

### Steps

1. **Send email with actionable request:**

To: your-gmail@gmail.com
Subject: "Action Required: Send Project Update"
Body:
```
Hi AI Assistant,

Please send an email to stakeholders@company.com with an update on Project Phoenix.

Subject: Project Phoenix - Weekly Update
Body: Project is on track. Phase 1 completed. Phase 2 starting next week.

Thanks!
```

2. **Monitor complete workflow:**

```bash
# Terminal 1: Gmail watcher
tail -f logs/gmail_watcher.log

# Terminal 2: File watcher
tail -f logs/watcher.log

# Terminal 3: Approval engine
tail -f logs/approval_engine.log
```

3. **Expected flow:**
   - ✅ Email detected by Gmail watcher
   - ✅ Converted to markdown in Inbox
   - ✅ Brain processes email
   - ✅ Classified as "Request"
   - ✅ High priority (action required)
   - ✅ Plan generated
   - ✅ Plan moved to Pending_Approval
   - ✅ (Manual) Human approves plan
   - ✅ Approval engine executes actions
   - ✅ Plan moved to Approved
   - ✅ Dashboard updated

4. **Verify each step:**

Check folders at each stage:
```bash
ls -la vault/Inbox/
ls -la vault/Pending_Approval/
ls -la vault/Approved/
```

### Expected Result

✅ **PASS:** Complete workflow executes successfully
❌ **FAIL:** If any step fails or is skipped

---

## Performance Testing

### Test 12: Load Testing

1. **Create 50 test files:**

```bash
for i in {1..50}; do
  echo "Test task number $i - please process this request" > vault/Inbox/load_test_$i.txt
  sleep 0.1
done
```

2. **Monitor system performance:**

```bash
# Check CPU usage
top -p $(pgrep -f "python")

# Check memory
ps aux | grep python | awk '{print $6}'

# Check processing time
time ls vault/Inbox/ | wc -l
```

3. **Verify all processed:**

```bash
# Should be 0 after processing
ls vault/Inbox/ | wc -l

# Should be 50
ls vault/Needs_Action/ | wc -l
```

### Expected Result

✅ **PASS:** All 50 files processed within reasonable time (< 5 minutes)
❌ **FAIL:** If system slows significantly or crashes

---

## Troubleshooting Failed Tests

### If Test Fails

1. **Check logs for errors:**
   ```bash
   grep -i error logs/*.log
   tail -100 logs/watcher.log
   ```

2. **Verify services running:**
   ```bash
   ps aux | grep -E "python|node"
   ```

3. **Check file permissions:**
   ```bash
   ls -la vault/*/
   ```

4. **Verify configuration:**
   ```bash
   cat .env
   ```

5. **Restart services:**
   - Stop all (Ctrl+C)
   - Clear logs: `rm logs/*.log`
   - Restart all services
   - Re-run test

---

## Test Results Template

Use this template to document test results:

```markdown
# Silver Tier Test Results

**Date:** 2026-02-13
**Tester:** [Your Name]
**Environment:** [Windows/Linux/Mac]

## Test Results

| Test # | Test Name | Status | Notes |
|--------|-----------|--------|-------|
| 1 | Planning System | ✅ PASS | Plan generated correctly |
| 2 | Approval Workflow | ✅ PASS | Approved and executed |
| 3 | Rejection Workflow | ✅ PASS | Rejected properly |
| 4 | LinkedIn Post Gen | ✅ PASS | Post format correct |
| 5 | LinkedIn Scheduling | ✅ PASS | Schedule respected |
| 6 | MCP Email Server | ✅ PASS | Server responding |
| 7 | Gmail Integration | ✅ PASS | Email processed |
| 8 | Multi-File Processing | ✅ PASS | All files handled |
| 9 | Dashboard Updates | ✅ PASS | Real-time updates |
| 10 | Error Handling | ✅ PASS | Errors handled gracefully |
| 11 | End-to-End Workflow | ✅ PASS | Complete flow works |
| 12 | Load Testing | ✅ PASS | 50 files in 3m 45s |

## Overall Result

✅ **ALL TESTS PASSED** - System ready for production

## Issues Found

None

## Recommendations

1. Monitor performance under real workload
2. Adjust check intervals based on usage
3. Set up log rotation
```

---

## Next Steps After Testing

1. ✅ Document any issues found
2. ✅ Fix critical bugs
3. ✅ Optimize performance bottlenecks
4. ✅ Set up production scheduling
5. ✅ Configure monitoring and alerts
6. ✅ Train users on approval workflow
7. ✅ Deploy to production environment

---

*Last Updated: 2026-02-13*
