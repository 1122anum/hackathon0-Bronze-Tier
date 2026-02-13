"""
Gmail Watcher Test Script
==========================

Run this after setting up credentials.json to verify everything works.
"""

import os
import sys
from pathlib import Path
from datetime import datetime

def test_gmail_watcher():
    """Test Gmail Watcher setup and functionality."""

    print("=" * 80)
    print("GMAIL WATCHER TEST SUITE")
    print("=" * 80)
    print()

    # Test 1: Import test
    print("[TEST 1/5] Testing imports...")
    try:
        sys.path.append(str(Path(__file__).parent))
        from watchers.gmail_watcher import GmailWatcher
        print("    PASS: GmailWatcher imported successfully")
    except Exception as e:
        print(f"    FAIL: {e}")
        return False
    print()

    # Test 2: Environment test
    print("[TEST 2/5] Testing environment configuration...")
    try:
        from dotenv import load_dotenv
        load_dotenv()

        vault_path = os.getenv('VAULT_PATH', './vault')
        creds_file = os.getenv('GMAIL_CREDENTIALS_FILE', 'credentials.json')
        token_file = os.getenv('GMAIL_TOKEN_FILE', 'token.json')
        poll_interval = os.getenv('POLL_INTERVAL', '60')

        print(f"    VAULT_PATH: {vault_path}")
        print(f"    GMAIL_CREDENTIALS_FILE: {creds_file}")
        print(f"    GMAIL_TOKEN_FILE: {token_file}")
        print(f"    POLL_INTERVAL: {poll_interval}s")
        print("    PASS: Environment loaded")
    except Exception as e:
        print(f"    FAIL: {e}")
        return False
    print()

    # Test 3: Credentials check
    print("[TEST 3/5] Checking credentials.json...")
    if Path(creds_file).exists():
        print(f"    PASS: {creds_file} found")
    else:
        print(f"    FAIL: {creds_file} not found")
        print("    ACTION: Download from Google Cloud Console")
        print("    See: GMAIL_API_SETUP.md")
        return False
    print()

    # Test 4: Vault structure
    print("[TEST 4/5] Checking vault structure...")
    try:
        vault = Path(vault_path)
        inbox = vault / "Inbox"

        if not vault.exists():
            print(f"    FAIL: {vault} does not exist")
            return False

        if not inbox.exists():
            print(f"    FAIL: {inbox} does not exist")
            return False

        print(f"    PASS: Vault structure valid")
        print(f"    - Vault: {vault}")
        print(f"    - Inbox: {inbox}")
    except Exception as e:
        print(f"    FAIL: {e}")
        return False
    print()

    # Test 5: Initialize watcher (without running)
    print("[TEST 5/5] Testing GmailWatcher initialization...")
    try:
        watcher = GmailWatcher(vault_path)
        print("    PASS: GmailWatcher initialized")
        print(f"    - Inbox path: {watcher.inbox_path}")
        print(f"    - Poll interval: {watcher.poll_interval}s")
        print(f"    - Credentials file: {watcher.credentials_file}")
    except Exception as e:
        print(f"    FAIL: {e}")
        return False
    print()

    # Summary
    print("=" * 80)
    print("TEST RESULTS")
    print("=" * 80)
    print("STATUS: ALL TESTS PASSED")
    print()
    print("Your Gmail Watcher is ready to run!")
    print()
    print("Next steps:")
    print("  1. Start the watcher:")
    print("     python watchers/gmail_watcher.py")
    print()
    print("  2. On first run, authenticate in browser")
    print()
    print("  3. Send yourself a test email")
    print()
    print("  4. Check vault/Inbox/ after 60 seconds")
    print()

    return True

if __name__ == "__main__":
    try:
        success = test_gmail_watcher()
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"\nERROR: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
