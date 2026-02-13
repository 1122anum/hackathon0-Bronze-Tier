# LinkedIn Watcher → MCP Server Integration

## Architecture Overview

The LinkedIn Watcher is designed to integrate with an MCP (Model Context Protocol) server for actual LinkedIn posting. Here's how the complete system works:

---

## Current State (Silver Tier)

```
┌─────────────────────────────────────────────────────────────┐
│                    LinkedIn Watcher                          │
│                                                              │
│  1. Generate post content                                    │
│  2. Save to Pending_Approval/                               │
│  3. Wait for human approval                                  │
└──────────────────────┬──────────────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────────────┐
│                  Approval Engine                             │
│                                                              │
│  1. Detect STATUS: APPROVED                                  │
│  2. Execute approved actions                                 │
│  3. [FUTURE] Call MCP server to post                        │
└──────────────────────────────────────────────────────────────┘
```

**Current behavior:** Posts are approved but not automatically published. Manual copy-paste to LinkedIn required.

---

## Future State (Gold Tier with MCP)

```
┌─────────────────────────────────────────────────────────────┐
│                    LinkedIn Watcher                          │
│                                                              │
│  1. Generate post content                                    │
│  2. Save to Pending_Approval/                               │
│  3. Wait for human approval                                  │
└──────────────────────┬──────────────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────────────┐
│                  Approval Engine                             │
│                                                              │
│  1. Detect STATUS: APPROVED                                  │
│  2. Parse post content                                       │
│  3. Call LinkedIn MCP Server                                 │
└──────────────────────┬──────────────────────────────────────┘
                       │
                       ▼ HTTP POST
┌─────────────────────────────────────────────────────────────┐
│              LinkedIn MCP Server (Node.js)                   │
│                                                              │
│  Endpoint: POST /api/linkedin/post                          │
│                                                              │
│  Request Body:                                               │
│  {                                                           │
│    "content": "Post text...",                               │
│    "hashtags": ["#AI", "#Automation"],                      │
│    "visibility": "PUBLIC"                                    │
│  }                                                           │
└──────────────────────┬──────────────────────────────────────┘
                       │
                       ▼ LinkedIn API
┌─────────────────────────────────────────────────────────────┐
│                    LinkedIn API                              │
│                                                              │
│  POST /v2/ugcPosts                                          │
│  Authorization: Bearer {access_token}                        │
└──────────────────────┬──────────────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────────────┐
│                  LinkedIn Platform                           │
│                                                              │
│  ✅ Post published to your profile                          │
│  📊 Engagement metrics tracked                              │
└──────────────────────────────────────────────────────────────┘
```

---

## MCP Server Implementation (Future)

### File: `mcp_server/linkedin_mcp_server.js`

```javascript
/**
 * LinkedIn MCP Server
 * Handles LinkedIn post publishing via LinkedIn API
 */

const express = require('express');
const axios = require('axios');
const bodyParser = require('body-parser');
require('dotenv').config();

const app = express();
const PORT = process.env.LINKEDIN_MCP_PORT || 3001;

app.use(bodyParser.json());

// LinkedIn API configuration
const LINKEDIN_API_URL = 'https://api.linkedin.com/v2';
const ACCESS_TOKEN = process.env.LINKEDIN_ACCESS_TOKEN;

/**
 * POST /api/linkedin/post
 * Publish a post to LinkedIn
 */
app.post('/api/linkedin/post', async (req, res) => {
    try {
        const { content, hashtags, visibility = 'PUBLIC' } = req.body;

        // Validate input
        if (!content) {
            return res.status(400).json({
                success: false,
                error: 'Content is required'
            });
        }

        // Format post content with hashtags
        const fullContent = `${content}\n\n${hashtags.join(' ')}`;

        // Prepare LinkedIn API request
        const linkedInPost = {
            author: `urn:li:person:${process.env.LINKEDIN_PERSON_ID}`,
            lifecycleState: 'PUBLISHED',
            specificContent: {
                'com.linkedin.ugc.ShareContent': {
                    shareCommentary: {
                        text: fullContent
                    },
                    shareMediaCategory: 'NONE'
                }
            },
            visibility: {
                'com.linkedin.ugc.MemberNetworkVisibility': visibility
            }
        };

        // Post to LinkedIn API
        const response = await axios.post(
            `${LINKEDIN_API_URL}/ugcPosts`,
            linkedInPost,
            {
                headers: {
                    'Authorization': `Bearer ${ACCESS_TOKEN}`,
                    'Content-Type': 'application/json',
                    'X-Restli-Protocol-Version': '2.0.0'
                }
            }
        );

        // Log success
        console.log('✅ Post published to LinkedIn:', response.data.id);

        res.json({
            success: true,
            post_id: response.data.id,
            post_url: `https://www.linkedin.com/feed/update/${response.data.id}`,
            timestamp: new Date().toISOString()
        });

    } catch (error) {
        console.error('❌ LinkedIn posting error:', error.response?.data || error.message);

        res.status(500).json({
            success: false,
            error: error.response?.data?.message || error.message
        });
    }
});

/**
 * GET /api/linkedin/health
 * Health check endpoint
 */
app.get('/api/linkedin/health', (req, res) => {
    res.json({
        status: 'healthy',
        service: 'LinkedIn MCP Server',
        version: '1.0.0'
    });
});

app.listen(PORT, () => {
    console.log(`LinkedIn MCP Server running on port ${PORT}`);
});
```

---

## Integration Code (Future Enhancement)

### Update `agent/approval_engine.py`

Add this method to the `ApprovalEngine` class:

```python
def _post_to_linkedin_via_mcp(self, post_content: str, hashtags: str) -> Dict:
    """
    Post to LinkedIn via MCP server

    Args:
        post_content: The post text
        hashtags: Space-separated hashtags

    Returns:
        Result dictionary
    """
    try:
        import requests

        mcp_url = os.getenv('LINKEDIN_MCP_URL', 'http://localhost:3001')

        # Prepare request
        payload = {
            "content": post_content,
            "hashtags": hashtags.split(),
            "visibility": "PUBLIC"
        }

        # Call MCP server
        response = requests.post(
            f"{mcp_url}/api/linkedin/post",
            json=payload,
            timeout=30
        )

        if response.status_code == 200:
            result = response.json()
            self.logger.info(f"✅ Posted to LinkedIn: {result['post_url']}")
            return {
                "success": True,
                "post_id": result['post_id'],
                "post_url": result['post_url']
            }
        else:
            self.logger.error(f"LinkedIn posting failed: {response.text}")
            return {
                "success": False,
                "error": response.text
            }

    except Exception as e:
        self.logger.error(f"Error posting to LinkedIn: {e}", exc_info=True)
        return {
            "success": False,
            "error": str(e)
        }
```

### Update `_execute_action` method:

```python
def _execute_action(self, action: str) -> Dict:
    """Execute a single action"""

    action_lower = action.lower()

    try:
        # LinkedIn posting
        if "linkedin" in action_lower or "post" in action_lower:
            # Parse post content from plan
            post_content = self._extract_post_content_from_plan()
            hashtags = self._extract_hashtags_from_plan()

            # Post via MCP
            result = self._post_to_linkedin_via_mcp(post_content, hashtags)

            return {
                "success": result["success"],
                "action": action,
                "result": f"Posted to LinkedIn: {result.get('post_url', 'N/A')}",
                "timestamp": datetime.now().isoformat()
            }

        # ... other action types ...

    except Exception as e:
        return {
            "success": False,
            "action": action,
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }
```

---

## LinkedIn API Setup (Required for Production)

### Step 1: Create LinkedIn App

1. Go to https://www.linkedin.com/developers/apps
2. Click "Create app"
3. Fill in app details:
   - App name: "Personal AI Employee"
   - LinkedIn Page: Your company page
   - App logo: Upload logo
4. Click "Create app"

### Step 2: Configure Permissions

1. Go to "Products" tab
2. Request access to:
   - **Share on LinkedIn** (required for posting)
   - **Sign In with LinkedIn** (for authentication)
3. Wait for approval (usually instant for Share on LinkedIn)

### Step 3: Get OAuth Credentials

1. Go to "Auth" tab
2. Copy:
   - Client ID
   - Client Secret
3. Add redirect URL: `http://localhost:3001/auth/linkedin/callback`

### Step 4: Get Access Token

Run OAuth flow to get user access token:

```javascript
// oauth_flow.js
const express = require('express');
const axios = require('axios');

const app = express();

const CLIENT_ID = 'your_client_id';
const CLIENT_SECRET = 'your_client_secret';
const REDIRECT_URI = 'http://localhost:3001/auth/linkedin/callback';

// Step 1: Redirect to LinkedIn authorization
app.get('/auth/linkedin', (req, res) => {
    const authUrl = `https://www.linkedin.com/oauth/v2/authorization?` +
        `response_type=code&` +
        `client_id=${CLIENT_ID}&` +
        `redirect_uri=${encodeURIComponent(REDIRECT_URI)}&` +
        `scope=w_member_social`;

    res.redirect(authUrl);
});

// Step 2: Handle callback and exchange code for token
app.get('/auth/linkedin/callback', async (req, res) => {
    const { code } = req.query;

    try {
        const response = await axios.post(
            'https://www.linkedin.com/oauth/v2/accessToken',
            null,
            {
                params: {
                    grant_type: 'authorization_code',
                    code: code,
                    client_id: CLIENT_ID,
                    client_secret: CLIENT_SECRET,
                    redirect_uri: REDIRECT_URI
                }
            }
        );

        const accessToken = response.data.access_token;

        res.send(`
            <h1>Success!</h1>
            <p>Access Token:</p>
            <pre>${accessToken}</pre>
            <p>Add this to your .env file as LINKEDIN_ACCESS_TOKEN</p>
        `);

    } catch (error) {
        res.status(500).send('Error: ' + error.message);
    }
});

app.listen(3001, () => {
    console.log('OAuth flow server running on http://localhost:3001');
    console.log('Visit: http://localhost:3001/auth/linkedin');
});
```

Run:
```bash
node oauth_flow.js
# Visit http://localhost:3001/auth/linkedin
# Copy the access token to .env
```

### Step 5: Configure Environment

Add to `.env`:

```env
# LinkedIn MCP Configuration
LINKEDIN_MCP_URL=http://localhost:3001
LINKEDIN_MCP_PORT=3001
LINKEDIN_ACCESS_TOKEN=your_access_token_here
LINKEDIN_PERSON_ID=your_person_id_here
```

To get your Person ID:
```bash
curl -X GET 'https://api.linkedin.com/v2/me' \
  -H 'Authorization: Bearer YOUR_ACCESS_TOKEN'
```

---

## Testing MCP Integration

### Test 1: MCP Server Health Check

```bash
curl http://localhost:3001/api/linkedin/health
```

Expected:
```json
{
  "status": "healthy",
  "service": "LinkedIn MCP Server",
  "version": "1.0.0"
}
```

### Test 2: Manual Post via MCP

```bash
curl -X POST http://localhost:3001/api/linkedin/post \
  -H "Content-Type: application/json" \
  -d '{
    "content": "Test post from AI Employee system",
    "hashtags": ["#AI", "#Automation", "#Test"],
    "visibility": "PUBLIC"
  }'
```

Expected:
```json
{
  "success": true,
  "post_id": "urn:li:share:1234567890",
  "post_url": "https://www.linkedin.com/feed/update/urn:li:share:1234567890",
  "timestamp": "2026-02-13T18:45:30.123Z"
}
```

### Test 3: End-to-End Integration

1. Start LinkedIn MCP server:
   ```bash
   cd mcp_server
   node linkedin_mcp_server.js
   ```

2. Start LinkedIn Watcher:
   ```bash
   python watchers/linkedin_watcher.py
   ```

3. Start Approval Engine:
   ```bash
   python -c "from agent.approval_engine import ApprovalEngine; from pathlib import Path; engine = ApprovalEngine(str(Path('vault'))); engine.start_monitoring()"
   ```

4. Approve a post:
   ```bash
   # Add STATUS: APPROVED to pending post
   ```

5. Verify:
   - Check logs for MCP call
   - Check LinkedIn profile for new post
   - Verify post URL in completion report

---

## Security Considerations

### Access Token Management

1. **Never commit tokens to git**
   - Add `.env` to `.gitignore`
   - Use environment variables only

2. **Token Rotation**
   - LinkedIn tokens expire after 60 days
   - Implement refresh token flow
   - Monitor token expiration

3. **Rate Limiting**
   - LinkedIn API: 100 posts per day
   - Implement rate limit tracking
   - Queue posts if limit reached

### Error Handling

```python
def _post_to_linkedin_via_mcp(self, post_content: str, hashtags: str) -> Dict:
    """Post to LinkedIn with comprehensive error handling"""

    max_retries = 3
    retry_delay = 5  # seconds

    for attempt in range(max_retries):
        try:
            response = requests.post(
                f"{mcp_url}/api/linkedin/post",
                json=payload,
                timeout=30
            )

            if response.status_code == 200:
                return {"success": True, ...}
            elif response.status_code == 429:
                # Rate limit hit
                self.logger.warning("Rate limit hit, waiting...")
                time.sleep(60)
                continue
            elif response.status_code == 401:
                # Token expired
                self.logger.error("Access token expired")
                return {"success": False, "error": "Token expired"}
            else:
                # Other error
                if attempt < max_retries - 1:
                    time.sleep(retry_delay)
                    continue
                return {"success": False, "error": response.text}

        except requests.Timeout:
            if attempt < max_retries - 1:
                time.sleep(retry_delay)
                continue
            return {"success": False, "error": "Timeout"}
        except Exception as e:
            return {"success": False, "error": str(e)}
```

---

## Monitoring & Analytics

### Track Post Performance

```python
def track_post_metrics(self, post_id: str):
    """Track LinkedIn post engagement metrics"""

    # Call LinkedIn Analytics API
    response = requests.get(
        f"{LINKEDIN_API_URL}/socialActions/{post_id}",
        headers={"Authorization": f"Bearer {ACCESS_TOKEN}"}
    )

    metrics = response.json()

    # Log metrics
    self.log_action("LINKEDIN_POST_METRICS", {
        "post_id": post_id,
        "likes": metrics.get("likeCount", 0),
        "comments": metrics.get("commentCount", 0),
        "shares": metrics.get("shareCount", 0),
        "impressions": metrics.get("impressionCount", 0)
    })
```

---

## Current vs Future Comparison

| Feature | Current (Silver Tier) | Future (Gold Tier with MCP) |
|---------|----------------------|----------------------------|
| Post Generation | ✅ Automated | ✅ Automated |
| Content Quality | ✅ Business-focused | ✅ Business-focused |
| Approval Workflow | ✅ Human-in-loop | ✅ Human-in-loop |
| Publishing | ❌ Manual copy-paste | ✅ Automated via API |
| Metrics Tracking | ❌ Manual | ✅ Automated |
| Scheduling | ✅ Time-based | ✅ Time-based |
| Error Handling | ✅ Comprehensive | ✅ Comprehensive |
| Rate Limiting | ❌ N/A | ✅ Implemented |

---

## Migration Path

### Phase 1: Current State (Now)
- LinkedIn Watcher generates posts
- Manual approval and publishing
- Learn content patterns

### Phase 2: MCP Server Setup (Week 1)
- Set up LinkedIn Developer App
- Implement OAuth flow
- Get access tokens
- Test MCP server locally

### Phase 3: Integration (Week 2)
- Update approval engine
- Add MCP posting logic
- Test end-to-end flow
- Monitor for errors

### Phase 4: Production (Week 3)
- Deploy MCP server
- Enable automated posting
- Monitor metrics
- Iterate on content

---

*Last Updated: 2026-02-13*
