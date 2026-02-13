# LinkedIn Watcher - Complete Testing Guide

## Test 1: Basic Functionality Test (2 minutes)

### Step 1: Start the Watcher

```bash
cd Personal_AI_Employee
python watchers/linkedin_watcher.py
```

### Step 2: Verify Initial Post Generation

**Expected behavior:**
- Post generates immediately on startup
- File created: `vault/Pending_Approval/2026-02-13__linkedin_post.md`
- Log shows: "✅ LinkedIn post generated and moved to Pending_Approval"

**Verify:**
```bash
# Check file exists
ls vault/Pending_Approval/

# View the post
cat vault/Pending_Approval/2026-02-13__linkedin_post.md
```

**Expected file content:**
```markdown
# LinkedIn Post Draft

**Status:** Draft
**Approval Required:** Yes
**Platform:** LinkedIn
**Topic:** AI Automation in Business
**Generated:** 2026-02-13 18:30:15

---

## Content

🚀 Most businesses are still doing manually what AI could automate in seconds.

Here's what I've learned building autonomous systems:
...
```

### Step 3: Check Logs

```bash
# View watcher log
tail -20 logs/linkedin_watcher.log

# View action log
tail -20 logs/actions.log
```

**Expected in actions.log:**
```
================================================================================
[2026-02-13T18:30:15.123456] LINKEDIN_POST_GENERATED
================================================================================
filename: 2026-02-13__linkedin_post.md
topic: AI Automation in Business
status: Pending Approval
word_count: 156
hashtags: #AI #Automation #BusinessGrowth #Productivity #DigitalTransformation
================================================================================
```

---

## Test 2: Duplicate Prevention Test (1 minute)

### Step 1: Try to Generate Again

Stop the watcher (Ctrl+C) and restart:

```bash
python watchers/linkedin_watcher.py
```

### Step 2: Verify Duplicate Detection

**Expected behavior:**
- Watcher detects existing post for today
- Log shows: "Skipping: Post already generated today"
- No new file created

**Verify:**
```bash
# Should still be only one file for today
ls vault/Pending_Approval/ | grep $(date +%Y-%m-%d)
```

---

## Test 3: Multiple Day Simulation (3 minutes)

### Step 1: Manually Change Date in Filename

```bash
# Rename today's post to yesterday
cd vault/Pending_Approval
mv 2026-02-13__linkedin_post.md 2026-02-12__linkedin_post.md
cd ../..
```

### Step 2: Restart Watcher

```bash
python watchers/linkedin_watcher.py
```

### Step 3: Verify New Post Generated

**Expected behavior:**
- New post generated for today (2026-02-13)
- Yesterday's post (2026-02-12) still exists
- Both posts have different topics (template rotation)

**Verify:**
```bash
ls -la vault/Pending_Approval/
# Should see both:
# 2026-02-12__linkedin_post.md
# 2026-02-13__linkedin_post.md
```

---

## Test 4: Content Quality Test (2 minutes)

### Step 1: Review Generated Post

Open `vault/Pending_Approval/2026-02-13__linkedin_post.md`

### Step 2: Verify Content Requirements

**Checklist:**
- ✅ Hook in first line (engaging opening)
- ✅ Business growth focused
- ✅ Authority tone
- ✅ Value-driven body (actionable insights)
- ✅ Clear CTA (call to action)
- ✅ 3-5 hashtags
- ✅ 150-300 words
- ✅ Professional formatting

### Step 3: Check Word Count

```bash
# Count words in content section
grep -A 20 "## Content" vault/Pending_Approval/2026-02-13__linkedin_post.md | wc -w
```

**Expected:** Between 150-300 words

---

## Test 5: Template Rotation Test (5 minutes)

### Step 1: Generate Multiple Posts

```bash
# Generate 7 posts (one for each template)
for i in {1..7}; do
    # Change date to force new generation
    date_str=$(date -d "$i days ago" +%Y-%m-%d 2>/dev/null || date -v-${i}d +%Y-%m-%d)

    # Remove existing post for that date
    rm -f vault/Pending_Approval/${date_str}__linkedin_post.md

    # Temporarily modify date check (or manually test)
    python watchers/linkedin_watcher.py &
    PID=$!
    sleep 3
    kill $PID
done
```

### Step 2: Verify Different Topics

```bash
# List all generated posts with topics
grep "Topic:" vault/Pending_Approval/*.md
```

**Expected output:**
```
vault/Pending_Approval/2026-02-13__linkedin_post.md:**Topic:** AI Automation in Business
vault/Pending_Approval/2026-02-12__linkedin_post.md:**Topic:** Building vs Buying Software
vault/Pending_Approval/2026-02-11__linkedin_post.md:**Topic:** Productivity Through Systems
...
```

**Verify:** All 7 topics are different (template rotation working)

---

## Test 6: Error Handling Test (3 minutes)

### Test 6.1: Invalid Vault Path

```bash
# Set invalid path
export VAULT_PATH=/invalid/path
python watchers/linkedin_watcher.py
```

**Expected behavior:**
- Watcher creates directories if they don't exist
- OR logs error and exits gracefully

### Test 6.2: Permission Denied

```bash
# Make Pending_Approval read-only
chmod 444 vault/Pending_Approval
python watchers/linkedin_watcher.py
```

**Expected behavior:**
- Error logged: "Failed to move file"
- Watcher continues running
- Post remains in Needs_Action

**Cleanup:**
```bash
chmod 755 vault/Pending_Approval
```

### Test 6.3: Disk Full Simulation

```bash
# Create large file to fill disk (careful!)
# Skip this test unless you have a test environment
```

---

## Test 7: Graceful Shutdown Test (1 minute)

### Step 1: Start Watcher

```bash
python watchers/linkedin_watcher.py
```

### Step 2: Send Interrupt Signal

Press `Ctrl+C`

### Step 3: Verify Graceful Shutdown

**Expected output:**
```
2026-02-13 18:45:30 - LinkedInWatcher - INFO - Shutdown signal received. Finishing current operation...
2026-02-13 18:45:30 - LinkedInWatcher - INFO - LinkedIn Watcher stopped gracefully
```

**Verify:**
- No error messages
- No corrupted files
- Logs properly closed

---

## Test 8: Continuous Operation Test (10 minutes)

### Step 1: Set Short Interval for Testing

Edit `.env`:
```env
POST_INTERVAL_MINUTES=2  # 2 minutes for testing
```

### Step 2: Start Watcher

```bash
python watchers/linkedin_watcher.py
```

### Step 3: Monitor for 10 Minutes

**Expected behavior:**
- First post generated immediately
- Subsequent checks every 2 minutes
- Duplicate detection working (no new posts after first)
- Logs show: "Next check in 2 minutes..."

### Step 4: Verify Stability

**Check:**
- No memory leaks (monitor with `top` or Task Manager)
- No excessive CPU usage
- Logs not growing excessively
- No error messages

---

## Test 9: Log Rotation Test (2 minutes)

### Step 1: Check Log File Size

```bash
ls -lh logs/linkedin_watcher.log
ls -lh logs/actions.log
```

### Step 2: Generate Multiple Posts

Run watcher multiple times to generate log entries

### Step 3: Verify Logs Are Readable

```bash
tail -50 logs/linkedin_watcher.log
tail -50 logs/actions.log
```

**Expected:**
- Logs properly formatted
- Timestamps accurate
- No garbled text
- All actions recorded

---

## Test 10: Integration Test (5 minutes)

### Step 1: Start All Components

```bash
# Terminal 1: LinkedIn Watcher
python watchers/linkedin_watcher.py

# Terminal 2: File Watcher (if you have it)
python run.py

# Terminal 3: Monitor logs
tail -f logs/*.log
```

### Step 2: Verify Integration

**Check:**
- LinkedIn post appears in Pending_Approval
- File watcher doesn't interfere
- All logs writing correctly
- No conflicts between watchers

---

## Test Results Template

Use this template to document your test results:

```markdown
# LinkedIn Watcher Test Results

**Date:** 2026-02-13
**Tester:** [Your Name]
**Environment:** Windows 10 / Python 3.13

## Test Results

| Test # | Test Name | Status | Notes |
|--------|-----------|--------|-------|
| 1 | Basic Functionality | ✅ PASS | Post generated successfully |
| 2 | Duplicate Prevention | ✅ PASS | Correctly skipped duplicate |
| 3 | Multiple Day Simulation | ✅ PASS | Different posts for different days |
| 4 | Content Quality | ✅ PASS | All requirements met |
| 5 | Template Rotation | ✅ PASS | 7 different topics |
| 6 | Error Handling | ✅ PASS | Graceful error handling |
| 7 | Graceful Shutdown | ✅ PASS | Clean shutdown |
| 8 | Continuous Operation | ✅ PASS | Stable for 10+ minutes |
| 9 | Log Rotation | ✅ PASS | Logs properly formatted |
| 10 | Integration | ✅ PASS | Works with other components |

## Issues Found

None

## Recommendations

1. System is production-ready
2. Consider adding more post templates
3. Monitor log file sizes in production
```

---

## Quick Test (30 seconds)

If you just want to verify it works:

```bash
cd Personal_AI_Employee
python watchers/linkedin_watcher.py
# Wait 3 seconds
# Press Ctrl+C
# Check: ls vault/Pending_Approval/
# Should see: 2026-02-13__linkedin_post.md
```

---

*Last Updated: 2026-02-13*
