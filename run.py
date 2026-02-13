"""
Launcher Script - Easy Start for AI Employee
============================================

This script provides a simple way to start the AI Employee system
from VS Code or command line.

Usage:
    python run.py
"""

import os
import sys
from pathlib import Path

# Fix Windows console encoding for emoji support
if sys.platform == 'win32':
    try:
        # Try to set UTF-8 encoding
        import codecs
        sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')
        sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer, 'strict')
    except:
        # If that fails, we'll use ASCII-safe output
        pass


def main():
    """Launch the AI Employee file watcher."""
    print("=" * 80)
    print("PERSONAL AI EMPLOYEE - BRONZE TIER")
    print("=" * 80)
    print()

    # Check Python version
    if sys.version_info < (3, 11):
        print("❌ Error: Python 3.11+ required")
        print(f"   Current version: {sys.version}")
        sys.exit(1)

    print("[OK] Python version check passed")

    # Check dependencies
    try:
        import watchdog
        print("[OK] Dependencies installed")
    except ImportError:
        print("[ERROR] Dependencies not installed")
        print("   Run: pip install -r requirements.txt")
        sys.exit(1)

    # Check vault structure
    vault_path = Path(__file__).parent / "vault"
    required_dirs = ["Inbox", "Needs_Action", "Done"]

    for dir_name in required_dirs:
        dir_path = vault_path / dir_name
        if not dir_path.exists():
            print(f"[ERROR] Missing directory: {dir_name}")
            sys.exit(1)

    print("[OK] Vault structure verified")
    print()

    # Launch watcher
    print("Starting AI Employee...")
    print("Press Ctrl+C to stop")
    print()

    # Import and run watcher
    sys.path.insert(0, str(Path(__file__).parent))
    from watchers.file_watcher import main as watcher_main

    try:
        watcher_main()
    except KeyboardInterrupt:
        print("\n\nAI Employee stopped. Goodbye!")
        sys.exit(0)


if __name__ == "__main__":
    main()
