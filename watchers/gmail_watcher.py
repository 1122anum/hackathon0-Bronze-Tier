"""
Gmail Watcher - Autonomous Email Monitor
=========================================

This module monitors Gmail for unread emails, converts them to markdown,
and saves them to the vault/Inbox folder for AI Employee processing.

Architecture Decision:
- OAuth2 authentication for security
- Polling-based (60s interval) for reliability
- Local token storage (no cloud dependencies)
- Duplicate prevention via processed email tracking
- Integration with existing file_watcher.py

Author: AI Employee System
Version: 1.0.0
"""

import os
import sys
import time
import logging
import re
import base64
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Optional
from email.utils import parsedate_to_datetime

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Google API imports
try:
    from google.auth.transport.requests import Request
    from google.oauth2.credentials import Credentials
    from google_auth_oauthlib.flow import InstalledAppFlow
    from googleapiclient.discovery import build
    from googleapiclient.errors import HttpError
except ImportError:
    print("ERROR: Google API libraries not installed.")
    print("Run: pip install google-auth google-auth-oauthlib google-api-python-client")
    sys.exit(1)

from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Gmail API scopes - read and modify (to mark as read)
SCOPES = ['https://www.googleapis.com/auth/gmail.modify']

# Configure logging
LOG_DIR = Path(__file__).parent.parent / "logs"
LOG_DIR.mkdir(exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(LOG_DIR / "gmail_watcher.log"),
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger("GmailWatcher")


class GmailWatcher:
    """
    Monitors Gmail for unread emails and converts them to markdown files.

    This watcher runs continuously, checking for new emails every 60 seconds.
    Each email is converted to markdown and saved to vault/Inbox/ for
    processing by the AI Employee brain.
    """

    def __init__(self, vault_path: str):
        """
        Initialize the Gmail watcher.

        Args:
            vault_path: Path to the vault root directory
        """
        self.vault_path = Path(vault_path)
        self.inbox_path = self.vault_path / "Inbox"

        # Get configuration from environment
        self.credentials_file = os.getenv('GMAIL_CREDENTIALS_FILE', 'credentials.json')
        self.token_file = os.getenv('GMAIL_TOKEN_FILE', 'token.json')
        self.poll_interval = int(os.getenv('POLL_INTERVAL', '60'))

        # Validate paths
        if not self.vault_path.exists():
            raise ValueError(f"Vault path does not exist: {self.vault_path}")

        if not self.inbox_path.exists():
            raise ValueError(f"Inbox path does not exist: {self.inbox_path}")

        # Gmail service (initialized on first use)
        self.service = None

        # Track processed emails to avoid duplicates
        self.processed_emails = set()
        self._load_processed_emails()

        logger.info(f"GmailWatcher initialized for vault: {self.vault_path}")
        logger.info(f"Poll interval: {self.poll_interval} seconds")

    def _load_processed_emails(self):
        """
        Load list of already processed email IDs from tracking file.

        This prevents duplicate processing if the watcher restarts.
        """
        tracking_file = LOG_DIR / "processed_emails.txt"

        if tracking_file.exists():
            try:
                with open(tracking_file, 'r') as f:
                    self.processed_emails = set(line.strip() for line in f if line.strip())
                logger.info(f"Loaded {len(self.processed_emails)} processed email IDs")
            except Exception as e:
                logger.error(f"Failed to load processed emails: {str(e)}")
                self.processed_emails = set()

    def _save_processed_email(self, email_id: str):
        """
        Save email ID to tracking file to prevent duplicate processing.

        Args:
            email_id: Gmail message ID
        """
        tracking_file = LOG_DIR / "processed_emails.txt"

        try:
            with open(tracking_file, 'a') as f:
                f.write(f"{email_id}\n")
            self.processed_emails.add(email_id)
        except Exception as e:
            logger.error(f"Failed to save processed email ID: {str(e)}")

    def authenticate_gmail(self) -> bool:
        """
        Authenticate with Gmail using OAuth2.

        This method handles the OAuth2 flow:
        1. Check if token.json exists (previous authentication)
        2. If token exists and valid, use it
        3. If token expired, refresh it
        4. If no token, initiate OAuth2 flow (opens browser)

        Returns:
            True if authentication successful, False otherwise
        """
        creds = None

        # Check if we have a saved token
        if os.path.exists(self.token_file):
            try:
                creds = Credentials.from_authorized_user_file(self.token_file, SCOPES)
                logger.info("Loaded existing credentials from token file")
            except Exception as e:
                logger.error(f"Failed to load credentials: {str(e)}")

        # If credentials don't exist or are invalid, authenticate
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                try:
                    logger.info("Refreshing expired credentials...")
                    creds.refresh(Request())
                    logger.info("Credentials refreshed successfully")
                except Exception as e:
                    logger.error(f"Failed to refresh credentials: {str(e)}")
                    creds = None

            # If still no valid credentials, run OAuth2 flow
            if not creds:
                if not os.path.exists(self.credentials_file):
                    logger.error(f"Credentials file not found: {self.credentials_file}")
                    logger.error("Please download credentials.json from Google Cloud Console")
                    return False

                try:
                    logger.info("Starting OAuth2 authentication flow...")
                    logger.info("A browser window will open for authentication")

                    flow = InstalledAppFlow.from_client_secrets_file(
                        self.credentials_file, SCOPES
                    )
                    creds = flow.run_local_server(port=0)

                    logger.info("Authentication successful!")
                except Exception as e:
                    logger.error(f"OAuth2 flow failed: {str(e)}")
                    return False

            # Save credentials for future use
            try:
                with open(self.token_file, 'w') as token:
                    token.write(creds.to_json())
                logger.info(f"Credentials saved to {self.token_file}")
            except Exception as e:
                logger.error(f"Failed to save credentials: {str(e)}")

        # Build Gmail service
        try:
            self.service = build('gmail', 'v1', credentials=creds)
            logger.info("Gmail service initialized successfully")
            return True
        except Exception as e:
            logger.error(f"Failed to build Gmail service: {str(e)}")
            return False

    def fetch_unread_emails(self) -> List[Dict]:
        """
        Fetch all unread emails from Gmail.

        Returns:
            List of email dictionaries with metadata and content
        """
        if not self.service:
            logger.error("Gmail service not initialized")
            return []

        try:
            # Query for unread messages
            results = self.service.users().messages().list(
                userId='me',
                q='is:unread',
                maxResults=50  # Process up to 50 emails per cycle
            ).execute()

            messages = results.get('messages', [])

            if not messages:
                logger.debug("No unread emails found")
                return []

            logger.info(f"Found {len(messages)} unread email(s)")

            # Fetch full details for each message
            emails = []
            for message in messages:
                email_id = message['id']

                # Skip if already processed
                if email_id in self.processed_emails:
                    logger.debug(f"Skipping already processed email: {email_id}")
                    continue

                try:
                    email_data = self._fetch_email_details(email_id)
                    if email_data:
                        emails.append(email_data)
                except Exception as e:
                    logger.error(f"Failed to fetch email {email_id}: {str(e)}")
                    continue

            return emails

        except HttpError as e:
            logger.error(f"Gmail API error: {str(e)}")
            return []
        except Exception as e:
            logger.error(f"Unexpected error fetching emails: {str(e)}")
            return []

    def _fetch_email_details(self, email_id: str) -> Optional[Dict]:
        """
        Fetch full details for a specific email.

        Args:
            email_id: Gmail message ID

        Returns:
            Dictionary with email details or None if failed
        """
        try:
            message = self.service.users().messages().get(
                userId='me',
                id=email_id,
                format='full'
            ).execute()

            # Extract headers
            headers = message['payload']['headers']
            subject = self._get_header(headers, 'Subject') or '(No Subject)'
            sender = self._get_header(headers, 'From') or '(Unknown Sender)'
            date_str = self._get_header(headers, 'Date') or ''

            # Parse date
            try:
                date = parsedate_to_datetime(date_str)
            except:
                date = datetime.now()

            # Extract body
            body = self._extract_email_body(message['payload'])

            return {
                'id': email_id,
                'subject': subject,
                'sender': sender,
                'date': date,
                'body': body
            }

        except Exception as e:
            logger.error(f"Error fetching email details: {str(e)}")
            return None

    def _get_header(self, headers: List[Dict], name: str) -> Optional[str]:
        """
        Extract a specific header value from email headers.

        Args:
            headers: List of header dictionaries
            name: Header name to find

        Returns:
            Header value or None if not found
        """
        for header in headers:
            if header['name'].lower() == name.lower():
                return header['value']
        return None

    def _extract_email_body(self, payload: Dict) -> str:
        """
        Extract plain text body from email payload.

        Handles both simple and multipart messages.
        Prefers plain text over HTML.

        Args:
            payload: Email payload from Gmail API

        Returns:
            Plain text body content
        """
        body = ""

        # Check if payload has body data directly
        if 'body' in payload and 'data' in payload['body']:
            body = self._decode_body(payload['body']['data'])
            return body

        # Handle multipart messages
        if 'parts' in payload:
            for part in payload['parts']:
                mime_type = part.get('mimeType', '')

                # Prefer plain text
                if mime_type == 'text/plain':
                    if 'data' in part['body']:
                        body = self._decode_body(part['body']['data'])
                        return body

                # Fallback to HTML (will be converted to text)
                elif mime_type == 'text/html' and not body:
                    if 'data' in part['body']:
                        html_body = self._decode_body(part['body']['data'])
                        body = self._html_to_text(html_body)

                # Recursively check nested parts
                elif 'parts' in part:
                    nested_body = self._extract_email_body(part)
                    if nested_body:
                        body = nested_body
                        return body

        return body or "(No content)"

    def _decode_body(self, data: str) -> str:
        """
        Decode base64url encoded email body.

        Args:
            data: Base64url encoded string

        Returns:
            Decoded text
        """
        try:
            decoded_bytes = base64.urlsafe_b64decode(data)
            return decoded_bytes.decode('utf-8', errors='ignore')
        except Exception as e:
            logger.error(f"Failed to decode email body: {str(e)}")
            return "(Failed to decode content)"

    def _html_to_text(self, html: str) -> str:
        """
        Convert HTML email to plain text.

        Simple conversion - removes HTML tags and decodes entities.

        Args:
            html: HTML content

        Returns:
            Plain text content
        """
        # Remove HTML tags
        text = re.sub(r'<[^>]+>', '', html)

        # Decode common HTML entities
        text = text.replace('&nbsp;', ' ')
        text = text.replace('&amp;', '&')
        text = text.replace('&lt;', '<')
        text = text.replace('&gt;', '>')
        text = text.replace('&quot;', '"')
        text = text.replace('&#39;', "'")

        # Clean up whitespace
        text = re.sub(r'\n\s*\n', '\n\n', text)
        text = text.strip()

        return text

    def save_email_to_markdown(self, email: Dict) -> Optional[Path]:
        """
        Convert email to markdown and save to vault/Inbox/.

        Args:
            email: Email dictionary with metadata and content

        Returns:
            Path to saved file or None if failed
        """
        try:
            # Create filename: YYYY-MM-DD__Subject_Slug.md
            date_str = email['date'].strftime('%Y-%m-%d')
            subject_slug = self._slugify(email['subject'])
            filename = f"{date_str}__{subject_slug}.md"

            # Ensure filename is unique
            file_path = self.inbox_path / filename
            counter = 1
            while file_path.exists():
                filename = f"{date_str}__{subject_slug}_{counter}.md"
                file_path = self.inbox_path / filename
                counter += 1

            # Format email as markdown
            markdown_content = self._format_email_markdown(email)

            # Write to file
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(markdown_content)

            logger.info(f"Saved email to: {filename}")
            return file_path

        except Exception as e:
            logger.error(f"Failed to save email to markdown: {str(e)}")
            return None

    def _slugify(self, text: str, max_length: int = 50) -> str:
        """
        Convert text to URL-friendly slug.

        Args:
            text: Text to slugify
            max_length: Maximum length of slug

        Returns:
            Slugified text
        """
        # Convert to lowercase
        text = text.lower()

        # Remove special characters
        text = re.sub(r'[^\w\s-]', '', text)

        # Replace spaces with underscores
        text = re.sub(r'[\s_]+', '_', text)

        # Remove leading/trailing underscores
        text = text.strip('_')

        # Truncate to max length
        if len(text) > max_length:
            text = text[:max_length].rstrip('_')

        return text or 'email'

    def _format_email_markdown(self, email: Dict) -> str:
        """
        Format email as markdown document.

        Args:
            email: Email dictionary

        Returns:
            Markdown formatted string
        """
        date_formatted = email['date'].strftime('%Y-%m-%d %H:%M:%S')

        markdown = f"""# Email: {email['subject']}

**From:** {email['sender']}
**Date:** {date_formatted}
**Status:** New
**Source:** Gmail

---

## Content

{email['body']}

---

## AI Notes

(Leave blank for brain.py to process)
"""

        return markdown

    def mark_email_as_read(self, email_id: str) -> bool:
        """
        Mark email as read in Gmail.

        Args:
            email_id: Gmail message ID

        Returns:
            True if successful, False otherwise
        """
        if not self.service:
            logger.error("Gmail service not initialized")
            return False

        try:
            self.service.users().messages().modify(
                userId='me',
                id=email_id,
                body={'removeLabelIds': ['UNREAD']}
            ).execute()

            logger.info(f"Marked email as read: {email_id}")
            return True

        except HttpError as e:
            logger.error(f"Failed to mark email as read: {str(e)}")
            return False
        except Exception as e:
            logger.error(f"Unexpected error marking email as read: {str(e)}")
            return False

    def log_action(self, email: Dict, file_path: Path):
        """
        Log email processing action to actions.log.

        Args:
            email: Email dictionary
            file_path: Path where email was saved
        """
        try:
            actions_log = LOG_DIR / "actions.log"

            with open(actions_log, 'a', encoding='utf-8') as f:
                timestamp = datetime.now().isoformat()
                f.write(f"\n{'='*80}\n")
                f.write(f"[{timestamp}] EMAIL PROCESSED\n")
                f.write(f"{'='*80}\n")
                f.write(f"Subject: {email['subject']}\n")
                f.write(f"From: {email['sender']}\n")
                f.write(f"Date: {email['date'].strftime('%Y-%m-%d %H:%M:%S')}\n")
                f.write(f"Saved to: {file_path.name}\n")
                f.write(f"Status: Success\n")
                f.write(f"{'='*80}\n\n")

        except Exception as e:
            logger.error(f"Failed to write to actions.log: {str(e)}")

    def process_emails(self):
        """
        Main processing loop - fetch, save, and mark emails as read.

        This is called once per polling cycle.
        """
        try:
            # Fetch unread emails
            emails = self.fetch_unread_emails()

            if not emails:
                return

            logger.info(f"Processing {len(emails)} new email(s)...")

            # Process each email
            for email in emails:
                try:
                    # Save to markdown
                    file_path = self.save_email_to_markdown(email)

                    if file_path:
                        # Mark as read
                        if self.mark_email_as_read(email['id']):
                            # Log action
                            self.log_action(email, file_path)

                            # Track as processed
                            self._save_processed_email(email['id'])

                            logger.info(f"✅ Successfully processed: {email['subject']}")
                        else:
                            logger.warning(f"Email saved but failed to mark as read: {email['id']}")
                    else:
                        logger.error(f"Failed to save email: {email['subject']}")

                except Exception as e:
                    logger.error(f"Error processing email {email.get('id', 'unknown')}: {str(e)}")
                    continue

        except Exception as e:
            logger.error(f"Error in process_emails: {str(e)}")

    def run(self):
        """
        Main run loop - continuously monitor Gmail for new emails.

        Runs until interrupted (Ctrl+C).
        """
        logger.info("="*80)
        logger.info("GMAIL WATCHER - STARTING")
        logger.info("="*80)
        logger.info(f"Monitoring Gmail for unread emails...")
        logger.info(f"Poll interval: {self.poll_interval} seconds")
        logger.info(f"Saving to: {self.inbox_path}")
        logger.info("Press Ctrl+C to stop")
        logger.info("="*80)

        # Authenticate
        if not self.authenticate_gmail():
            logger.error("Failed to authenticate with Gmail")
            logger.error("Please check your credentials and try again")
            return

        logger.info("✅ Gmail authentication successful")
        logger.info("🔄 Starting monitoring loop...")

        try:
            while True:
                try:
                    # Process emails
                    self.process_emails()

                    # Wait for next cycle
                    logger.debug(f"Waiting {self.poll_interval} seconds until next check...")
                    time.sleep(self.poll_interval)

                except KeyboardInterrupt:
                    raise  # Re-raise to be caught by outer handler

                except Exception as e:
                    logger.error(f"Error in monitoring loop: {str(e)}")
                    logger.info(f"Continuing after error... (retry in {self.poll_interval}s)")
                    time.sleep(self.poll_interval)

        except KeyboardInterrupt:
            logger.info("\n⏹️  Shutdown signal received")
            logger.info("🛑 Stopping Gmail watcher...")
            logger.info("✅ Gmail watcher stopped successfully")


def main():
    """
    Main entry point for the Gmail watcher.
    """
    # Get vault path from environment or use default
    vault_path = os.getenv(
        'VAULT_PATH',
        os.path.join(os.path.dirname(os.path.dirname(__file__)), 'vault')
    )

    try:
        # Create and start watcher
        watcher = GmailWatcher(vault_path)
        watcher.run()

    except Exception as e:
        logger.error(f"Failed to start Gmail watcher: {str(e)}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()
