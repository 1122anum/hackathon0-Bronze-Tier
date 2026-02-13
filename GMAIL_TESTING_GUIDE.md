# Gmail Watcher Testing Guide

**Comprehensive testing procedures for the Gmail watcher system**

---

## Pre-Testing Checklist

Before running tests, ensure:

- [ ] Gmail API setup completed (credentials.json exists)
- [ ] OAuth2 authentication completed (token.json exists)
- [ ] Virtual environment activated
- [ ] Dependencies installed (`pip install -r requirements.txt`)
- [ ] .env file configured
- [ ] vault/Inbox/ folder exists

---

## Test Suite Overview

| Test Type | Purpose | Duration |
|-----------|---------|----------|
| Unit Tests | Test individual functions | 2 min |
| Integration Tests | Test Gmail API connection | 5 min |
| End-to-End Tests | Test full email workflow | 10 min |
| Edge Case Tests | Test unusual scenarios | 15 min |
| Performance Tests | Test under load | 10 min |
| Error Handling Tests | Test failure scenarios | 10 min |

**Total Testing Time:** ~50 minutes

---

## Test 1: Authentication Test

**Objective:** Verify Gmail API authentication works

### Steps

1. **Delete existing token** (to test fresh auth)
   ```bash
   del token.json
   ```

2. **Start Gmail watcher**
   ```bash
   python watchers/gmail_watcher.py
   ```

3. **Complete OAuth2 flow**
   - Browser should open automatically
   - Sign in with your Google account
   - Grant permissions
   - Return to terminal

### Expected Results

```
Starting OAuth2 authentication flow...
A browser window will open for authentication
Authentication successful!
Credentials saved to token.json
Gmail service initialized successfully
✅ Gmail authentication successful
```

### Pass Criteria

- ✅ Browser opened automatically
- ✅ Authentication completed without errors
- ✅ token.json file created
- ✅ Gmail service initialized
- ✅ No error messages in logs

---

## Test 2: Simple Email Processing

**Objective:** Test basic email fetch and conversion

### Steps

1. **Ensure Gmail watcher is running**
   ```bash
   python watchers/gmail_watcher.py
   ```

2. **Send test email**
   - From: Another email account
   - To: Your Gmail account
   - Subject: `Test Email 001`
   - Body: `This is a simple test email for the AI Employee system.`

3. **Wait for processing** (max 60 seconds)

4. **Check terminal output**

5. **Verify markdown file created**
   ```bash
   dir vault\Inbox\*test_email_001*
   ```

6. **View markdown content**
   ```bash
   type vault\Inbox\2026-02-12__test_email_001.md
   ```

### Expected Results

**Terminal output:**
```
Found 1 unread email(s)
Processing 1 new email(s)...
Saved email to: 2026-02-12__test_email_001.md
Marked email as read: [email_id]
✅ Successfully processed: Test Email 001
```

**Markdown file:**
```markdown
# Email: Test Email 001

**From:** sender@example.com
**Date:** 2026-02-12 17:30:00
**Status:** New
**Source:** Gmail

---

## Content

This is a simple test email for the AI Employee system.

---

## AI Notes

(Leave blank for brain.py to process)
```

**Gmail:**
- Email marked as read
- No longer in unread count

### Pass Criteria

- ✅ Email detected within 60 seconds
- ✅ Markdown file created in vault/Inbox/
- ✅ Filename format correct: YYYY-MM-DD__subject_slug.md
- ✅ Markdown content properly formatted
- ✅ Email marked as read in Gmail
- ✅ Logged in logs/actions.log

---

## Test 3: HTML Email Processing

**Objective:** Test HTML email conversion to plain text

### Steps

1. **Send HTML email**
   - Use Gmail web interface
   - Format text with **bold**, *italic*, colors
   - Add a link: [Click here](https://example.com)
   - Subject: `Test HTML Email`

2. **Wait for processing**

3. **Check markdown file**
   ```bash
   type vault\Inbox\*test_html_email*
   ```

### Expected Results

- HTML tags removed
- Plain text extracted
- Links preserved (if possible)
- Formatting stripped

### Pass Criteria

- ✅ No HTML tags in markdown file
- ✅ Content readable as plain text
- ✅ No `<div>`, `<p>`, `<span>` tags visible

---

## Test 4: Special Characters in Subject

**Objective:** Test filename sanitization

### Test Cases

Send emails with these subjects:

1. `Test: Email with colon`
2. `Test/Email/With/Slashes`
3. `Test "Email" With Quotes`
4. `Test <Email> With Brackets`
5. `Test | Email | With | Pipes`
6. `Test Email with émojis 🎉🚀`

### Expected Results

All should create valid filenames:
```
2026-02-12__test_email_with_colon.md
2026-02-12__testemail_withslashes.md
2026-02-12__test_email_with_quotes.md
2026-02-12__test_email_with_brackets.md
2026-02-12__test_email_with_pipes.md
2026-02-12__test_email_with_emojis.md
```

### Pass Criteria

- ✅ All files created successfully
- ✅ No invalid filename characters
- ✅ Filenames are readable
- ✅ No file creation errors

---

## Test 5: Long Subject Line

**Objective:** Test subject truncation

### Steps

1. **Send email with very long subject**
   ```
   Subject: This is a very long email subject line that exceeds the normal length and should be truncated to prevent filesystem issues with maximum path lengths
   ```

2. **Check filename**
   ```bash
   dir vault\Inbox\*this_is_a_very_long*
   ```

### Expected Results

Filename truncated to ~50 characters:
```
2026-02-12__this_is_a_very_long_email_subject_line_that_exc.md
```

### Pass Criteria

- ✅ Filename created successfully
- ✅ Filename length reasonable (< 100 chars total)
- ✅ No path length errors

---

## Test 6: Multiple Emails Simultaneously

**Objective:** Test batch processing

### Steps

1. **Send 5 emails quickly**
   - Subject: `Batch Test 1`
   - Subject: `Batch Test 2`
   - Subject: `Batch Test 3`
   - Subject: `Batch Test 4`
   - Subject: `Batch Test 5`

2. **Wait for processing**

3. **Count markdown files**
   ```bash
   dir vault\Inbox\*batch_test* | find /c ".md"
   ```

### Expected Results

```
Found 5 unread email(s)
Processing 5 new email(s)...
✅ Successfully processed: Batch Test 1
✅ Successfully processed: Batch Test 2
✅ Successfully processed: Batch Test 3
✅ Successfully processed: Batch Test 4
✅ Successfully processed: Batch Test 5
```

### Pass Criteria

- ✅ All 5 emails processed
- ✅ 5 markdown files created
- ✅ All emails marked as read
- ✅ No duplicates
- ✅ No errors

---

## Test 7: Duplicate Prevention

**Objective:** Test that emails aren't processed twice

### Steps

1. **Process an email normally**
   - Send email: `Duplicate Test`
   - Wait for processing
   - Verify markdown file created

2. **Restart Gmail watcher**
   ```bash
   # Stop with Ctrl+C
   # Start again
   python watchers/gmail_watcher.py
   ```

3. **Wait 60 seconds**

4. **Check for duplicate files**
   ```bash
   dir vault\Inbox\*duplicate_test*
   ```

### Expected Results

- Only ONE markdown file exists
- Logs show: "Skipping already processed email"
- No duplicate processing

### Pass Criteria

- ✅ Only one markdown file created
- ✅ Email not reprocessed after restart
- ✅ processed_emails.txt contains email ID

---

## Test 8: Empty Email Body

**Objective:** Test handling of emails with no content

### Steps

1. **Send email with subject only**
   - Subject: `Empty Body Test`
   - Body: (leave completely empty)

2. **Check markdown file**

### Expected Results

```markdown
## Content

(No content)
```

### Pass Criteria

- ✅ File created successfully
- ✅ Shows "(No content)" placeholder
- ✅ No errors or crashes

---

## Test 9: Email with Attachments

**Objective:** Test handling of attachments (note: attachments are ignored)

### Steps

1. **Send email with attachment**
   - Subject: `Attachment Test`
   - Body: `This email has an attachment`
   - Attach: Any file (PDF, image, etc.)

2. **Check markdown file**

### Expected Results

- Email body extracted
- Attachment ignored (not downloaded)
- Markdown file created normally

### Pass Criteria

- ✅ Email processed successfully
- ✅ Body text extracted
- ✅ No attachment content in markdown
- ✅ No errors

---

## Test 10: Non-English Characters

**Objective:** Test Unicode support

### Steps

1. **Send emails with various languages**
   - Subject: `Test 中文 Chinese`
   - Subject: `Test العربية Arabic`
   - Subject: `Test Русский Russian`
   - Subject: `Test 日本語 Japanese`

2. **Check markdown files**

### Expected Results

- All characters preserved correctly
- UTF-8 encoding maintained
- Files readable

### Pass Criteria

- ✅ All files created
- ✅ Unicode characters preserved
- ✅ No encoding errors

---

## Test 11: Rate Limiting

**Objective:** Test behavior under Gmail API rate limits

### Steps

1. **Send 100 emails rapidly** (if possible)

2. **Monitor processing**

3. **Check for rate limit errors**

### Expected Results

- Emails processed in batches (50 per cycle)
- No rate limit errors (within free tier)
- All emails eventually processed

### Pass Criteria

- ✅ All emails processed
- ✅ No "quota exceeded" errors
- ✅ System continues operating

---

## Test 12: Network Interruption

**Objective:** Test error recovery

### Steps

1. **Start Gmail watcher**

2. **Disconnect internet** (disable WiFi)

3. **Wait for next poll cycle** (60 seconds)

4. **Check logs for error**

5. **Reconnect internet**

6. **Verify recovery**

### Expected Results

```
Error in monitoring loop: [network error]
Continuing after error... (retry in 60s)
```

After reconnection:
```
Found X unread email(s)
Processing continues normally...
```

### Pass Criteria

- ✅ Error logged but watcher doesn't crash
- ✅ Automatic recovery after reconnection
- ✅ No manual intervention needed

---

## Test 13: Invalid Credentials

**Objective:** Test handling of authentication failures

### Steps

1. **Corrupt token.json**
   ```bash
   echo "invalid" > token.json
   ```

2. **Start Gmail watcher**

3. **Observe behavior**

### Expected Results

```
Failed to load credentials: [error]
Starting OAuth2 authentication flow...
```

Browser opens for re-authentication.

### Pass Criteria

- ✅ Error detected
- ✅ Re-authentication triggered
- ✅ System recovers after re-auth

---

## Test 14: Integration with File Watcher

**Objective:** Test end-to-end workflow

### Steps

1. **Start Gmail watcher** (Terminal 1)
   ```bash
   python watchers/gmail_watcher.py
   ```

2. **Start File watcher** (Terminal 2)
   ```bash
   python run.py
   ```

3. **Send test email**
   - Subject: `Integration Test`
   - Body: `URGENT: This is a high priority task ASAP!!!`

4. **Monitor both terminals**

5. **Check final location**
   ```bash
   dir vault\Needs_Action\*integration_test*
   ```

### Expected Results

**Terminal 1 (Gmail watcher):**
```
Saved email to: 2026-02-12__integration_test.md
```

**Terminal 2 (File watcher):**
```
🆕 New file detected: 2026-02-12__integration_test.md
📋 Classified as: Request
⚖️ Priority assigned: High
📁 Moved to Needs_Action
```

**Final location:**
```
vault/Needs_Action/2026-02-12__integration_test.md
vault/Needs_Action/2026-02-12__integration_test.meta.json
```

### Pass Criteria

- ✅ Email fetched by Gmail watcher
- ✅ Markdown created in Inbox
- ✅ File watcher detected new file
- ✅ Email classified correctly
- ✅ Priority assigned (High due to URGENT/ASAP)
- ✅ Moved to Needs_Action
- ✅ Metadata created

---

## Test 15: Performance Test

**Objective:** Measure processing speed

### Steps

1. **Send 10 emails**

2. **Time the processing**

3. **Calculate metrics**

### Expected Results

- Detection time: < 60 seconds (poll interval)
- Processing time per email: < 2 seconds
- Total time for 10 emails: < 80 seconds

### Pass Criteria

- ✅ All emails processed within reasonable time
- ✅ No performance degradation
- ✅ Memory usage stable

---

## Test 16: Log File Verification

**Objective:** Verify comprehensive logging

### Steps

1. **Process several emails**

2. **Check log files**
   ```bash
   type logs\gmail_watcher.log
   type logs\actions.log
   type logs\processed_emails.txt
   ```

### Expected Results

**gmail_watcher.log:**
- Timestamps for all operations
- Authentication events
- Email processing events
- Error messages (if any)

**actions.log:**
- Detailed email processing records
- Subject, sender, date
- File paths

**processed_emails.txt:**
- List of processed email IDs
- One per line

### Pass Criteria

- ✅ All logs exist
- ✅ Logs contain expected information
- ✅ Timestamps are accurate
- ✅ No sensitive data (tokens) in logs

---

## Test 17: Graceful Shutdown

**Objective:** Test clean shutdown

### Steps

1. **Start Gmail watcher**

2. **Press Ctrl+C**

3. **Observe shutdown**

### Expected Results

```
⏹️  Shutdown signal received
🛑 Stopping Gmail watcher...
✅ Gmail watcher stopped successfully
```

### Pass Criteria

- ✅ Clean shutdown message
- ✅ No error messages
- ✅ No orphaned processes
- ✅ Logs properly closed

---

## Automated Test Script (Optional)

Create `test_gmail_watcher.py`:

```python
"""
Automated tests for Gmail watcher
Run with: pytest test_gmail_watcher.py
"""

import pytest
from pathlib import Path
from watchers.gmail_watcher import GmailWatcher

def test_slugify():
    """Test filename slugification"""
    watcher = GmailWatcher("./vault")

    assert watcher._slugify("Test Email") == "test_email"
    assert watcher._slugify("Test: Email") == "test_email"
    assert watcher._slugify("Test/Email") == "testemail"
    assert len(watcher._slugify("A" * 100)) <= 50

def test_html_to_text():
    """Test HTML conversion"""
    watcher = GmailWatcher("./vault")

    html = "<p>Hello <b>World</b></p>"
    text = watcher._html_to_text(html)

    assert "<p>" not in text
    assert "<b>" not in text
    assert "Hello" in text
    assert "World" in text

# Add more tests as needed
```

Run with:
```bash
pip install pytest
pytest test_gmail_watcher.py -v
```

---

## Test Results Template

Use this template to track your testing:

```
GMAIL WATCHER TEST RESULTS
==========================
Date: ___________
Tester: ___________

[ ] Test 1: Authentication
[ ] Test 2: Simple Email Processing
[ ] Test 3: HTML Email Processing
[ ] Test 4: Special Characters in Subject
[ ] Test 5: Long Subject Line
[ ] Test 6: Multiple Emails Simultaneously
[ ] Test 7: Duplicate Prevention
[ ] Test 8: Empty Email Body
[ ] Test 9: Email with Attachments
[ ] Test 10: Non-English Characters
[ ] Test 11: Rate Limiting
[ ] Test 12: Network Interruption
[ ] Test 13: Invalid Credentials
[ ] Test 14: Integration with File Watcher
[ ] Test 15: Performance Test
[ ] Test 16: Log File Verification
[ ] Test 17: Graceful Shutdown

OVERALL STATUS: [ ] PASS [ ] FAIL

Issues Found:
_________________________________
_________________________________

Notes:
_________________________________
_________________________________
```

---

## Success Criteria Summary

Your Gmail watcher is production-ready if:

✅ All authentication tests pass
✅ Emails converted to markdown correctly
✅ Special characters handled properly
✅ Duplicate prevention works
✅ Error recovery functions
✅ Integration with file watcher works
✅ Logs are comprehensive
✅ Performance is acceptable
✅ No data loss or corruption

**If all tests pass: Your Gmail watcher is ready for production! 🎉**
