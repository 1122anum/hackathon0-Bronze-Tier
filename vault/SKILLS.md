# AI Employee Skills Registry

**Version:** 2.0
**Last Updated:** February 12, 2026
**Total Skills:** 10
**Status:** Production Ready

---

## Overview

This document defines all operational skills available to the AI Employee system. Each skill is a modular, reusable capability that can be triggered autonomously or chained together for complex workflows.

**Design Principles:**
- **Modular:** Each skill is self-contained and independent
- **Composable:** Skills can be chained together
- **Testable:** Clear inputs, outputs, and completion criteria
- **Auditable:** All executions are logged
- **Fail-Safe:** Graceful error handling built-in

---

## Skill Index

| # | Skill Name | Category | Trigger Type | Avg Duration |
|---|------------|----------|--------------|--------------|
| 1 | [Process_New_File](#skill-1-process_new_file) | Core | Event-Driven | 0.10s |
| 2 | [Classify_Task](#skill-2-classify_task) | Analysis | Invoked | 0.05s |
| 3 | [Prioritize_Task](#skill-3-prioritize_task) | Analysis | Invoked | 0.03s |
| 4 | [Move_To_Needs_Action](#skill-4-move_to_needs_action) | File Ops | Invoked | 0.15s |
| 5 | [Move_To_Done](#skill-5-move_to_done) | File Ops | Invoked | 0.12s |
| 6 | [Generate_Task_Summary](#skill-6-generate_task_summary) | Reporting | Invoked | 0.20s |
| 7 | [Update_Dashboard](#skill-7-update_dashboard) | Reporting | Invoked | 0.23s |
| 8 | [Log_Action](#skill-8-log_action) | System | Invoked | 0.01s |
| 9 | [Generate_CEO_Briefing](#skill-9-generate_ceo_briefing) | Reporting | Scheduled | 2.50s |
| 10 | [Archive_Old_Tasks](#skill-10-archive_old_tasks) | Maintenance | Scheduled | 1.00s |

---

## Skill #1: Process_New_File

### Purpose
Entry point for all new file processing. Orchestrates the complete workflow from detection to completion.

### Trigger
**Event-Driven:** Automatically triggered when file watcher detects new file in Inbox folder

**Conditions:**
- File is not hidden (doesn't start with `.` or `~`)
- File is not a temporary file
- File is not currently being processed
- File exists and is readable

### Inputs

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `file_path` | string | Yes | Absolute path to the new file |
| `file_name` | string | Yes | Name of the file (with extension) |
| `content` | string | Yes | Full text content of the file |

### Process Steps

1. **Initialize Task State**
   - Create TaskState object
   - Set initial values (file_path, file_name, content)
   - Initialize empty actions_taken list
   - Set is_complete = False

2. **Validate File Content**
   - Check if content is empty or whitespace-only
   - If empty: Call Move_To_Done with "empty file" reason
   - If valid: Continue to step 3

3. **Enter Reasoning Loop**
   - Set max_iterations = 10 (safety limit)
   - While not is_complete and iteration < max_iterations:
     - Call Classify_Task skill
     - Call Prioritize_Task skill
     - Call Move_To_Needs_Action skill
     - Call Update_Dashboard skill
     - Call Log_Action skill
     - Evaluate completion criteria

4. **Verify Completion**
   - Check all required actions completed
   - Verify file moved successfully
   - Confirm metadata created
   - Validate dashboard updated

5. **Return Result**
   - Format result dictionary
   - Include success status, task_type, priority, actions_taken
   - Return to file watcher

### Output

```python
{
    "success": bool,              # True if processing completed without errors
    "file_name": str,             # Name of processed file
    "task_type": str,             # Classified task type
    "priority": str,              # Assigned priority (High/Medium/Low)
    "confidence": float,          # Classification confidence (0.0-1.0)
    "actions_taken": list[str],   # List of actions executed
    "action": str,                # Summary of final action
    "reasoning": str,             # Explanation of decisions
    "error": str | None           # Error message if failed, None if success
}
```

### Completion Criteria

**Success Conditions (ALL must be true):**
- ✅ File successfully read and parsed
- ✅ Task classified with confidence score
- ✅ Priority assigned
- ✅ File moved to appropriate destination
- ✅ Metadata file created
- ✅ Dashboard updated
- ✅ Action logged
- ✅ No errors occurred

**Failure Conditions (ANY triggers failure):**
- ❌ File read error
- ❌ Classification failed
- ❌ File move failed
- ❌ Max iterations exceeded
- ❌ Unhandled exception

### Error Handling

| Error Type | Action | Retry |
|------------|--------|-------|
| File not found | Log warning, return error | No |
| Empty file | Move to Done with note | No |
| Read error | Log error, escalate | 3x |
| Processing timeout | Log error, escalate | No |
| Unexpected exception | Log with stack trace, escalate | No |

---

## Skill #2: Classify_Task

### Purpose
Analyze file content and determine the task type with confidence score.

### Trigger
**Invoked:** Called by Process_New_File skill during reasoning loop

### Inputs

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `content` | string | Yes | Full text content to classify |
| `file_name` | string | No | File name (may provide context) |
| `metadata` | dict | No | Additional context if available |

### Process Steps

1. **Normalize Content**
   - Convert to lowercase for analysis
   - Remove extra whitespace
   - Preserve original for logging

2. **Scan for Type Indicators**
   - **Question:** Check for `?`, interrogative words (what, why, how, when, where, who)
   - **Request:** Check for action verbs (create, send, update, fix, analyze), polite language (please, can you)
   - **Data_Processing:** Check for data keywords (analyze, calculate, process, data, CSV)
   - **Documentation:** Check for doc keywords (document, write, create doc, README)
   - **Research:** Check for research keywords (research, investigate, find, explore)

3. **Calculate Confidence Scores**
   - For each type, count matching indicators
   - Weight by indicator strength (strong vs weak signals)
   - Normalize scores to 0.0-1.0 range
   - Select type with highest score

4. **Apply Confidence Threshold**
   - If max_score >= 0.7: High confidence
   - If max_score >= 0.5: Medium confidence
   - If max_score < 0.5: Low confidence (flag for review)

5. **Generate Reasoning**
   - List matched indicators
   - Explain why this type was selected
   - Note any ambiguities or competing types

### Output

```python
{
    "task_type": str,           # Question, Request, Data_Processing, Documentation, Research, Other
    "confidence": float,        # 0.0 to 1.0
    "reasoning": str,           # Explanation of classification
    "indicators": list[str],    # Matched keywords/patterns
    "alternatives": dict        # Other types considered with scores
}
```

### Completion Criteria

**Success:**
- ✅ Task type assigned
- ✅ Confidence score calculated (0.0-1.0)
- ✅ Reasoning generated
- ✅ Result logged

**Quality Checks:**
- Confidence score is valid float between 0.0 and 1.0
- Task type is one of the defined categories
- Reasoning is non-empty and explains decision

### Classification Matrix

| Task Type | Primary Indicators | Secondary Indicators | Default Priority |
|-----------|-------------------|---------------------|------------------|
| Question | `?`, what, why, how | seeking info, clarification | Medium |
| Request | please, can you, action verbs | deadline, deliverable | Medium |
| Data_Processing | data, analyze, calculate | CSV, numbers, metrics | Medium |
| Documentation | document, write, README | guide, instructions | Low |
| Research | research, investigate, find | explore, study, trends | Low |
| Other | No clear match | Mixed signals | Medium |

---

## Skill #3: Prioritize_Task

### Purpose
Assign priority level (High/Medium/Low) based on urgency, importance, and task characteristics.

### Trigger
**Invoked:** Called by Process_New_File skill after classification

### Inputs

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `content` | string | Yes | Full text content |
| `task_type` | string | Yes | Classified task type |
| `confidence` | float | No | Classification confidence |

### Process Steps

1. **Initialize Base Score**
   - Start with score = 5 (Medium baseline)

2. **Scan for Urgency Markers**
   - **High Urgency (+3):** "URGENT", "ASAP", "EMERGENCY", "!!!", "CRITICAL"
   - **Medium Urgency (+2):** "IMPORTANT", "PRIORITY", "SOON"
   - **Low Urgency (-2):** "when possible", "eventually", "low priority", "no rush"

3. **Detect Deadlines**
   - Parse for time expressions: "today", "tomorrow", "by Friday", "within 24 hours"
   - **< 24 hours:** +3 points
   - **< 1 week:** +1 point
   - **> 1 month:** -1 point

4. **Adjust for Task Type**
   - **Question:** +1 (usually quick to resolve)
   - **Request:** +0 (baseline)
   - **Data_Processing:** +0 (baseline)
   - **Documentation:** -1 (important but rarely urgent)
   - **Research:** -1 (time-intensive, exploratory)

5. **Calculate Final Score**
   - Sum all adjustments
   - Clamp to range [1, 10]

6. **Map Score to Priority**
   - **8-10:** High Priority
   - **4-7:** Medium Priority
   - **1-3:** Low Priority

7. **Generate Reasoning**
   - List factors that influenced score
   - Explain final priority assignment

### Output

```python
{
    "priority": str,            # "High", "Medium", or "Low"
    "score": int,               # Numeric score (1-10)
    "reasoning": str,           # Explanation of priority
    "urgency_markers": list,    # Detected urgency indicators
    "deadline": str | None      # Detected deadline if any
}
```

### Completion Criteria

**Success:**
- ✅ Priority assigned (High/Medium/Low)
- ✅ Score calculated (1-10)
- ✅ Reasoning generated
- ✅ Factors documented

### Priority Decision Matrix

| Score | Priority | Typical Characteristics | Response Time SLA |
|-------|----------|------------------------|-------------------|
| 8-10 | High | Urgent markers, tight deadline, critical impact | < 6 seconds |
| 4-7 | Medium | Standard request, reasonable timeline | < 31 seconds |
| 1-3 | Low | No urgency, exploratory, long timeline | < 2 minutes |

---

## Skill #4: Move_To_Needs_Action

### Purpose
Move classified file from Inbox to Needs_Action folder with metadata.

### Trigger
**Invoked:** Called by Process_New_File skill after classification and prioritization

### Inputs

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `file_path` | string | Yes | Current file location (in Inbox) |
| `file_name` | string | Yes | Name of file to move |
| `task_type` | string | Yes | Classified task type |
| `priority` | string | Yes | Assigned priority |
| `confidence` | float | Yes | Classification confidence |
| `reasoning` | string | Yes | Classification reasoning |

### Process Steps

1. **Validate Source File**
   - Check file exists at source path
   - Verify file is readable
   - If not found: Log error and return failure

2. **Prepare Destination**
   - Construct destination path: `Needs_Action/{file_name}`
   - Check for naming conflicts
   - If conflict: Append timestamp to filename

3. **Move File**
   - Use atomic move operation (shutil.move)
   - Preserve file permissions
   - Verify move succeeded

4. **Create Metadata File**
   - Generate metadata dictionary with:
     - original_path
     - moved_at (ISO 8601 timestamp)
     - task_type
     - priority
     - confidence
     - reasoning
   - Write to `{file_name}.meta.json`
   - Validate JSON format

5. **Update State**
   - Add "moved_to:Needs_Action" to actions_taken
   - Update file_path in task state
   - Log successful move

### Output

```python
{
    "success": bool,            # True if moved successfully
    "new_path": str,            # New file location
    "metadata_path": str,       # Path to metadata file
    "timestamp": str            # ISO 8601 timestamp of move
}
```

### Completion Criteria

**Success:**
- ✅ File moved from Inbox to Needs_Action
- ✅ File no longer exists in Inbox
- ✅ File exists at new location
- ✅ Metadata file created
- ✅ Metadata is valid JSON
- ✅ Action logged

**Rollback on Failure:**
- If metadata creation fails after move: Log warning but continue
- If move fails: Leave file in Inbox, log error, escalate

### Error Handling

| Error | Action | Recovery |
|-------|--------|----------|
| Source file missing | Log error, return failure | No recovery |
| Destination exists | Append timestamp, retry | Auto-retry once |
| Move permission denied | Log error, escalate | Manual intervention |
| Metadata write failed | Log warning, continue | Non-critical |

---

## Skill #5: Move_To_Done

### Purpose
Move file from Inbox to Done folder for completed or invalid tasks.

### Trigger
**Invoked:** Called for empty files, test files, or completed tasks

### Inputs

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `file_path` | string | Yes | Current file location |
| `file_name` | string | Yes | Name of file to move |
| `reason` | string | Yes | Why file is being moved to Done |
| `outcome` | string | No | Summary of outcome |
| `duration` | float | No | Processing time in seconds |

### Process Steps

1. **Validate Source**
   - Check file exists
   - Verify readable

2. **Move to Done**
   - Construct destination: `Done/{file_name}`
   - Handle naming conflicts (append timestamp)
   - Execute atomic move

3. **Create Completion Note**
   - Generate markdown note with:
     - File name
     - Completion timestamp
     - Reason for completion
     - Outcome summary
     - Processing duration
   - Write to `{file_name}.note.md`

4. **Update Metrics**
   - Increment completed tasks counter
   - Update average processing time
   - Log completion

### Output

```python
{
    "success": bool,
    "new_path": str,
    "note_path": str,
    "archive_id": str,          # Unique ID for this completion
    "timestamp": str
}
```

### Completion Criteria

**Success:**
- ✅ File moved to Done folder
- ✅ Completion note created
- ✅ Metrics updated
- ✅ Action logged

---

## Skill #6: Generate_Task_Summary

### Purpose
Create a concise summary of a task or document.

### Trigger
**Invoked:** On-demand or as part of reporting workflows

### Inputs

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `content` | string | Yes | Full text to summarize |
| `max_length` | int | No | Max words (default: 100) |
| `format` | string | No | "bullet" or "paragraph" (default: "paragraph") |

### Process Steps

1. **Analyze Content**
   - Identify main topics
   - Extract key sentences
   - Detect action items

2. **Generate Summary**
   - If format="paragraph": Create 2-3 sentence summary
   - If format="bullet": Create 3-5 bullet points
   - Ensure under max_length

3. **Extract Key Points**
   - Identify 3-5 most important points
   - Format as list

4. **Validate Output**
   - Check length constraint
   - Verify readability
   - Ensure completeness

### Output

```python
{
    "summary": str,             # Generated summary
    "key_points": list[str],    # 3-5 main points
    "word_count": int,          # Length of summary
    "format": str               # Format used
}
```

### Completion Criteria

**Success:**
- ✅ Summary generated
- ✅ Under max_length
- ✅ Key points extracted
- ✅ Readable and coherent

---

## Skill #7: Update_Dashboard

### Purpose
Refresh Dashboard.md with current system state and recent actions.

### Trigger
**Invoked:** After each task completion, or every 60 seconds for metrics

### Inputs

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `section` | string | No | Specific section to update (default: "all") |
| `task_state` | dict | No | Current task state if updating from task |
| `metrics` | dict | No | Performance metrics to update |

### Process Steps

1. **Read Current Dashboard**
   - Load Dashboard.md
   - Parse markdown structure
   - Identify sections

2. **Update Timestamp**
   - Replace "Last Updated" with current timestamp
   - Format: YYYY-MM-DD HH:MM:SS

3. **Update Last Action Log**
   - If task_state provided:
     - Format action log entry
     - Include file name, task type, priority, actions, status
     - Replace previous log entry

4. **Update Metrics**
   - If metrics provided:
     - Update performance metrics section
     - Recalculate averages
     - Update skill utilization table

5. **Update Status Indicators**
   - Set system status (🟢 Active / 🔴 Down)
   - Update component health checks
   - Refresh timestamps

6. **Write Updated Dashboard**
   - Write back to Dashboard.md
   - Preserve formatting
   - Validate markdown syntax

### Output

```python
{
    "success": bool,
    "sections_updated": list[str],
    "timestamp": str,
    "errors": list[str]         # Any non-critical errors
}
```

### Completion Criteria

**Success:**
- ✅ Dashboard.md updated
- ✅ Timestamp current
- ✅ Sections properly formatted
- ✅ File written successfully

**Non-Critical Failures:**
- ⚠️ If dashboard update fails, log warning but don't fail task
- ⚠️ Dashboard is informational, not critical to task completion

---

## Skill #8: Log_Action

### Purpose
Write detailed action log entry to logs/actions.log.

### Trigger
**Invoked:** After every significant action or task completion

### Inputs

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `action_type` | string | Yes | Type of action (FILE_PROCESSED, ERROR, etc.) |
| `file_name` | string | Yes | File involved |
| `status` | string | Yes | SUCCESS, FAILURE, WARNING |
| `details` | dict | Yes | Action details (task_type, priority, etc.) |
| `reasoning` | string | No | Explanation of action |

### Process Steps

1. **Format Log Entry**
   - Create header with separator line
   - Add ISO 8601 timestamp
   - Include action type
   - Add all details in structured format

2. **Append to Log File**
   - Open logs/actions.log in append mode
   - Write formatted entry
   - Add separator line
   - Flush to disk

3. **Verify Write**
   - Confirm file written
   - Check file size (rotate if > 100MB)

### Output

```python
{
    "success": bool,
    "log_path": str,
    "entry_size": int           # Bytes written
}
```

### Completion Criteria

**Success:**
- ✅ Entry written to log file
- ✅ Proper format maintained
- ✅ Timestamp included

### Log Entry Format

```
================================================================================
[2026-02-12T16:35:38.418205] FILE_PROCESSED
================================================================================
File: urgent_request.txt
Status: SUCCESS
Task Type: Request (confidence: 0.70)
Priority: High (score: 8)
Actions: classified, prioritized, moved_to_needs_action, dashboard_updated
Duration: 0.56s
Reasoning: Urgency markers detected ("URGENT", "ASAP"). Action-oriented
          language ("analyze", "create"). Meets High priority threshold.
================================================================================
```

---

## Skill #9: Generate_CEO_Briefing

### Purpose
Create weekly executive summary of AI Employee operations and insights.

### Trigger
**Scheduled:** Runs every Monday at 09:00, or on-demand

### Inputs

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `start_date` | string | No | Start of reporting period (default: last Monday) |
| `end_date` | string | No | End of reporting period (default: yesterday) |
| `format` | string | No | "markdown" or "text" (default: "markdown") |

### Process Steps

1. **Gather Data**
   - Scan Done folder for completed tasks in date range
   - Parse metadata files
   - Aggregate metrics:
     - Total tasks processed
     - Task type distribution
     - Priority distribution
     - Average processing time
     - Success rate
     - Escalation count

2. **Analyze Trends**
   - Compare to previous week
   - Identify patterns:
     - Busiest days/times
     - Most common task types
     - Priority trends
   - Calculate growth rates

3. **Generate Insights**
   - Identify optimization opportunities
   - Flag anomalies or concerns
   - Recommend actions

4. **Format Briefing**
   - Create executive summary (3-5 bullet points)
   - Add key metrics table
   - Include insights section
   - Add recommended actions
   - Provide risk assessment

5. **Update Dashboard**
   - Replace CEO Briefing section in Dashboard.md
   - Add timestamp

### Output

```python
{
    "briefing": str,            # Formatted briefing content
    "metrics": dict,            # Raw metrics data
    "insights": list[str],      # Key insights
    "recommendations": list[str], # Recommended actions
    "file_path": str            # Where briefing was saved
}
```

### Completion Criteria

**Success:**
- ✅ Data collected for date range
- ✅ Metrics calculated
- ✅ Insights generated
- ✅ Briefing formatted
- ✅ Dashboard updated

### Briefing Template

```markdown
## 🎯 Monday Morning CEO Briefing

### Week of [Date]

**Executive Summary:**
- [Key metric 1]
- [Key metric 2]
- [Key metric 3]

**Key Insights:**
- [Insight 1]
- [Insight 2]

**Recommended Actions:**
- [Action 1]
- [Action 2]

**Risk Assessment:** [Low/Medium/High] - [Brief explanation]
```

---

## Skill #10: Archive_Old_Tasks

### Purpose
Move completed tasks older than 30 days to archive folder for long-term storage.

### Trigger
**Scheduled:** Runs daily at 00:00, or on-demand

### Inputs

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `age_threshold_days` | int | No | Archive tasks older than X days (default: 30) |
| `destination` | string | No | Archive folder path (default: Done/Archive/) |

### Process Steps

1. **Scan Done Folder**
   - List all files in Done/
   - Get file modification dates
   - Filter files older than threshold

2. **Create Archive Folder**
   - Generate dated folder: `Archive_YYYY-MM/`
   - Create if doesn't exist

3. **Move Old Files**
   - For each old file:
     - Move to archive folder
     - Move associated metadata
     - Preserve timestamps

4. **Generate Manifest**
   - Create archive_manifest.md
   - List all archived files
   - Include metadata summary

5. **Update Metrics**
   - Count archived files
   - Calculate space freed
   - Log archival action

### Output

```python
{
    "archived_count": int,      # Number of files archived
    "space_freed_bytes": int,   # Disk space freed
    "archive_path": str,        # Location of archive
    "manifest_path": str        # Path to manifest file
}
```

### Completion Criteria

**Success:**
- ✅ Old files identified
- ✅ Archive folder created
- ✅ Files moved successfully
- ✅ Manifest generated
- ✅ Metrics updated

---

## Skill Execution Framework

### Chaining Skills

Skills can be chained together for complex workflows:

```
Process_New_File
    ↓
Classify_Task
    ↓
Prioritize_Task
    ↓
Move_To_Needs_Action
    ↓
Update_Dashboard
    ↓
Log_Action
```

### Error Propagation

- If a skill fails, error is logged and propagated up
- Calling skill decides whether to continue or abort
- Critical skills (file operations) abort on failure
- Non-critical skills (dashboard update) log warning and continue

### Performance Monitoring

Each skill execution is tracked:
- Start timestamp
- End timestamp
- Duration
- Success/failure status
- Error details if failed

Metrics are aggregated in Dashboard.md.

---

## Adding New Skills

To add a new skill:

1. **Define Skill Specification**
   - Follow the standard format
   - Include all required sections
   - Document inputs, outputs, completion criteria

2. **Implement in brain.py**
   - Add method to AIBrain class
   - Follow naming convention: `_skill_name`
   - Include error handling

3. **Update Skills Registry**
   - Add to this document
   - Update skill index table
   - Increment version number

4. **Test Thoroughly**
   - Unit test the skill
   - Integration test with other skills
   - Test error conditions

5. **Document Usage**
   - Add examples
   - Document common patterns
   - Note any limitations

---

## Skill Usage Statistics

| Skill | Times Used | Success Rate | Avg Duration | Last Used |
|-------|------------|--------------|--------------|-----------|
| Process_New_File | 1 | 100% | 0.56s | 2026-02-12 16:35:38 |
| Classify_Task | 1 | 100% | 0.05s | 2026-02-12 16:35:38 |
| Prioritize_Task | 1 | 100% | 0.03s | 2026-02-12 16:35:38 |
| Move_To_Needs_Action | 1 | 100% | 0.15s | 2026-02-12 16:35:38 |
| Update_Dashboard | 1 | 100% | 0.23s | 2026-02-12 16:35:38 |
| Log_Action | 1 | 100% | 0.01s | 2026-02-12 16:35:38 |
| Move_To_Done | 0 | N/A | N/A | Never |
| Generate_Task_Summary | 0 | N/A | N/A | Never |
| Generate_CEO_Briefing | 0 | N/A | N/A | Never |
| Archive_Old_Tasks | 0 | N/A | N/A | Never |

*Statistics updated in real-time as skills are executed.*

---

**Version History:**
- **2.0** (2026-02-12): Production release with 10 core skills
- **1.0** (2026-02-10): Initial skill definitions

**Next Review:** 2026-03-12

*This skills registry is the authoritative source for all AI Employee capabilities.*
