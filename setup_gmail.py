"""
Gmail Watcher Setup Verification Script
========================================

This script checks if your Gmail Watcher is ready to run.
"""

import os
import sys
from pathlib import Path

def check_setup():
    """Check if Gmail Watcher is properly configured."""

    print("=" * 80)
    print("GMAIL WATCHER SETUP VERIFICATION")
    print("=" * 80)
    print()

    issues = []
    warnings = []

    # Check 1: Python version
    print("[1/7] Checking Python version...")
    if sys.version_info >= (3, 11):
        print(f"    OK: Python {sys.version_info.major}.{sys.version_info.minor}")
    else:
        issues.append("Python 3.11+ required")
        print(f"    ERROR: Python {sys.version_info.major}.{sys.version_info.minor} (need 3.11+)")
    print()

    # Check 2: Gmail API libraries
    print("[2/7] Checking Gmail API libraries...")
    try:
        import google.auth
        from googleapiclient.discovery import build
        print("    OK: All Gmail API libraries installed")
    except ImportError as e:
        issues.append(f"Missing library: {e}")
        print(f"    ERROR: {e}")
    print()

    # Check 3: .env file
    print("[3/7] Checking .env configuration...")
    if Path('.env').exists():
        print("    OK: .env file exists")
        from dotenv import load_dotenv
        load_dotenv()

        gmail_creds = os.getenv('GMAIL_CREDENTIALS_FILE')
        gmail_token = os.getenv('GMAIL_TOKEN_FILE')
        poll_interval = os.getenv('POLL_INTERVAL')

        print(f"    - GMAIL_CREDENTIALS_FILE: {gmail_creds}")
        print(f"    - GMAIL_TOKEN_FILE: {gmail_token}")
        print(f"    - POLL_INTERVAL: {poll_interval}s")
    else:
        issues.append(".env file not found")
        print("    ERROR: .env file not found")
    print()

    # Check 4: credentials.json
    print("[4/7] Checking credentials.json...")
    creds_file = os.getenv('GMAIL_CREDENTIALS_FILE', 'credentials.json')
    if Path(creds_file).exists():
        print(f"    OK: {creds_file} found")
    else:
        issues.append(f"{creds_file} not found - download from Google Cloud Console")
        print(f"    ERROR: {creds_file} not found")
        print("    ACTION REQUIRED: Download OAuth2 credentials from Google Cloud Console")
        print("    See: GMAIL_API_SETUP.md for instructions")
    print()

    # Check 5: token.json
    print("[5/7] Checking token.json...")
    token_file = os.getenv('GMAIL_TOKEN_FILE', 'token.json')
    if Path(token_file).exists():
        print(f"    OK: {token_file} found (already authenticated)")
    else:
        warnings.append(f"{token_file} not found - will be created on first run")
        print(f"    INFO: {token_file} not found (will be created on first authentication)")
    print()

    # Check 6: vault/Inbox directory
    print("[6/7] Checking vault/Inbox directory...")
    inbox_path = Path('vault/Inbox')
    if inbox_path.exists() and inbox_path.is_dir():
        print(f"    OK: {inbox_path} exists")
        file_count = len(list(inbox_path.glob('*.md')))
        print(f"    - Current files: {file_count}")
    else:
        issues.append("vault/Inbox directory not found")
        print(f"    ERROR: {inbox_path} not found")
    print()

    # Check 7: logs directory
    print("[7/7] Checking logs directory...")
    logs_path = Path('logs')
    if logs_path.exists() and logs_path.is_dir():
        print(f"    OK: {logs_path} exists")
    else:
        warnings.append("logs directory not found - will be created automatically")
        print(f"    INFO: {logs_path} not found (will be created automatically)")
    print()

    # Summary
    print("=" * 80)
    print("SUMMARY")
    print("=" * 80)

    if not issues:
        print("STATUS: READY TO RUN")
        print()
        print("Your Gmail Watcher is fully configured!")
        print()
        print("To start monitoring Gmail:")
        print("  python watchers/gmail_watcher.py")
        print()
        if warnings:
            print("Notes:")
            for warning in warnings:
                print(f"  - {warning}")
        return True
    else:
        print("STATUS: SETUP INCOMPLETE")
        print()
        print("Issues found:")
        for issue in issues:
            print(f"  - {issue}")
        print()
        print("Please fix the issues above before running the Gmail Watcher.")
        print()
        print("Setup guide: GMAIL_API_SETUP.md")
        return False

if __name__ == "__main__":
    try:
        success = check_setup()
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"\nERROR: {e}")
        sys.exit(1)
