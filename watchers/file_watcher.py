"""
File Watcher - Autonomous Inbox Monitor
========================================

This module continuously monitors the vault/Inbox folder for new files.
When a new file is detected, it triggers the AI agent brain to process it.

Architecture Decision:
- Uses watchdog library for efficient file system event monitoring
- Event-driven architecture (not polling) for better performance
- Integrates with brain.py for AI decision-making
- Implements graceful error handling and recovery

Author: AI Employee System
Version: 1.0.0
"""

import os
import sys
import time
import logging
from pathlib import Path
from datetime import datetime
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from agent.brain import AIBrain


# Configure logging
LOG_DIR = Path(__file__).parent.parent / "logs"
LOG_DIR.mkdir(exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(LOG_DIR / "watcher.log"),
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger("FileWatcher")


class InboxHandler(FileSystemEventHandler):
    """
    Handles file system events in the Inbox folder.

    This handler responds to file creation events and triggers
    the AI brain to process new files autonomously.
    """

    def __init__(self, vault_path: Path):
        """
        Initialize the inbox handler.

        Args:
            vault_path: Path to the vault root directory
        """
        super().__init__()
        self.vault_path = vault_path
        self.inbox_path = vault_path / "Inbox"
        self.brain = AIBrain(vault_path)
        self.processing = set()  # Track files currently being processed

        logger.info(f"InboxHandler initialized. Monitoring: {self.inbox_path}")

    def on_created(self, event):
        """
        Called when a file or directory is created.

        Args:
            event: FileSystemEvent object containing event details
        """
        # Ignore directory creation events
        if event.is_directory:
            return

        file_path = Path(event.src_path)

        # Ignore temporary files and hidden files
        if file_path.name.startswith('.') or file_path.name.startswith('~'):
            logger.debug(f"Ignoring temporary/hidden file: {file_path.name}")
            return

        # Ignore files we're currently processing (avoid duplicate processing)
        if str(file_path) in self.processing:
            logger.debug(f"File already being processed: {file_path.name}")
            return

        logger.info(f"🆕 New file detected: {file_path.name}")

        # Small delay to ensure file is fully written
        time.sleep(0.5)

        # Process the file
        self._process_file(file_path)

    def _process_file(self, file_path: Path):
        """
        Process a new file using the AI brain.

        Args:
            file_path: Path to the file to process
        """
        try:
            # Mark as processing
            self.processing.add(str(file_path))

            # Check if file still exists (might have been moved/deleted)
            if not file_path.exists():
                logger.warning(f"File disappeared before processing: {file_path.name}")
                return

            # Read file content
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
            except UnicodeDecodeError:
                # Try with different encoding
                with open(file_path, 'r', encoding='latin-1') as f:
                    content = f.read()

            # Validate content
            if not content.strip():
                logger.warning(f"Empty file detected: {file_path.name}")
                self._handle_empty_file(file_path)
                return

            logger.info(f"📄 Processing file: {file_path.name} ({len(content)} chars)")

            # Trigger AI brain to process
            result = self.brain.process_new_file(
                file_path=str(file_path),
                file_name=file_path.name,
                content=content
            )

            # Log result
            if result.get('success'):
                logger.info(f"✅ Successfully processed: {file_path.name}")
                logger.info(f"   Task Type: {result.get('task_type')}")
                logger.info(f"   Priority: {result.get('priority')}")
                logger.info(f"   Action: {result.get('action')}")
            else:
                logger.error(f"❌ Failed to process: {file_path.name}")
                logger.error(f"   Error: {result.get('error')}")

            # Log to actions.log
            self._log_action(file_path.name, result)

        except Exception as e:
            logger.error(f"❌ Error processing {file_path.name}: {str(e)}", exc_info=True)
            self._log_error(file_path.name, str(e))

        finally:
            # Remove from processing set
            self.processing.discard(str(file_path))

    def _handle_empty_file(self, file_path: Path):
        """
        Handle empty files by moving them to Done with a note.

        Args:
            file_path: Path to the empty file
        """
        try:
            done_path = self.vault_path / "Done" / file_path.name

            # Move to Done
            file_path.rename(done_path)

            # Create note
            note_path = done_path.with_suffix('.note.md')
            with open(note_path, 'w', encoding='utf-8') as f:
                f.write(f"# Processing Note\n\n")
                f.write(f"**File:** {file_path.name}\n")
                f.write(f"**Status:** Invalid (Empty File)\n")
                f.write(f"**Timestamp:** {datetime.now().isoformat()}\n\n")
                f.write(f"This file was empty and automatically archived.\n")

            logger.info(f"📦 Moved empty file to Done: {file_path.name}")

        except Exception as e:
            logger.error(f"Failed to handle empty file: {str(e)}")

    def _log_action(self, file_name: str, result: dict):
        """
        Log action to actions.log file.

        Args:
            file_name: Name of the processed file
            result: Processing result dictionary
        """
        try:
            actions_log = LOG_DIR / "actions.log"

            with open(actions_log, 'a', encoding='utf-8') as f:
                timestamp = datetime.now().isoformat()
                f.write(f"\n{'='*80}\n")
                f.write(f"[{timestamp}] FILE PROCESSED\n")
                f.write(f"{'='*80}\n")
                f.write(f"File: {file_name}\n")
                f.write(f"Success: {result.get('success', False)}\n")
                f.write(f"Task Type: {result.get('task_type', 'Unknown')}\n")
                f.write(f"Priority: {result.get('priority', 'Unknown')}\n")
                f.write(f"Action: {result.get('action', 'Unknown')}\n")
                f.write(f"Reasoning: {result.get('reasoning', 'N/A')}\n")
                f.write(f"{'='*80}\n\n")

        except Exception as e:
            logger.error(f"Failed to write to actions.log: {str(e)}")

    def _log_error(self, file_name: str, error: str):
        """
        Log error to actions.log file.

        Args:
            file_name: Name of the file that caused error
            error: Error message
        """
        try:
            actions_log = LOG_DIR / "actions.log"

            with open(actions_log, 'a', encoding='utf-8') as f:
                timestamp = datetime.now().isoformat()
                f.write(f"\n{'='*80}\n")
                f.write(f"[{timestamp}] ERROR\n")
                f.write(f"{'='*80}\n")
                f.write(f"File: {file_name}\n")
                f.write(f"Error: {error}\n")
                f.write(f"{'='*80}\n\n")

        except Exception as e:
            logger.error(f"Failed to write error to actions.log: {str(e)}")


class FileWatcher:
    """
    Main file watcher service that monitors the Inbox folder.

    This is the entry point for the autonomous monitoring system.
    It runs continuously and triggers processing when new files appear.
    """

    def __init__(self, vault_path: str):
        """
        Initialize the file watcher.

        Args:
            vault_path: Path to the vault root directory
        """
        self.vault_path = Path(vault_path)
        self.inbox_path = self.vault_path / "Inbox"

        # Validate paths
        if not self.vault_path.exists():
            raise ValueError(f"Vault path does not exist: {self.vault_path}")

        if not self.inbox_path.exists():
            raise ValueError(f"Inbox path does not exist: {self.inbox_path}")

        # Create observer and handler
        self.observer = Observer()
        self.handler = InboxHandler(self.vault_path)

        logger.info(f"FileWatcher initialized for vault: {self.vault_path}")

    def start(self):
        """
        Start the file watcher service.

        This method runs continuously until interrupted.
        """
        try:
            # Schedule the observer
            self.observer.schedule(
                self.handler,
                str(self.inbox_path),
                recursive=False
            )

            # Start observing
            self.observer.start()
            logger.info("🚀 File Watcher started successfully")
            logger.info(f"📂 Monitoring: {self.inbox_path}")
            logger.info("⏳ Waiting for new files...")

            # Keep running
            while True:
                time.sleep(1)

        except KeyboardInterrupt:
            logger.info("⏹️  Shutdown signal received")
            self.stop()

        except Exception as e:
            logger.error(f"❌ Fatal error in file watcher: {str(e)}", exc_info=True)
            self.stop()
            raise

    def stop(self):
        """
        Stop the file watcher service gracefully.
        """
        logger.info("🛑 Stopping file watcher...")
        self.observer.stop()
        self.observer.join()
        logger.info("✅ File watcher stopped successfully")


def main():
    """
    Main entry point for the file watcher service.
    """
    # Get vault path from environment or use default
    vault_path = os.getenv(
        'VAULT_PATH',
        os.path.join(os.path.dirname(os.path.dirname(__file__)), 'vault')
    )

    logger.info("="*80)
    logger.info("AI EMPLOYEE - FILE WATCHER SERVICE")
    logger.info("="*80)
    logger.info(f"Vault Path: {vault_path}")
    logger.info(f"Start Time: {datetime.now().isoformat()}")
    logger.info("="*80)

    try:
        # Create and start watcher
        watcher = FileWatcher(vault_path)
        watcher.start()

    except Exception as e:
        logger.error(f"Failed to start file watcher: {str(e)}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()
