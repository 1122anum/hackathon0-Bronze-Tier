"""
LinkedIn Watcher - Silver Tier
Monitors LinkedIn posting schedule and triggers content generation
"""

import os
import time
import json
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, Optional
import logging


class LinkedInWatcher:
    """Monitors LinkedIn posting schedule and triggers post generation"""

    def __init__(self, vault_path: str, check_interval: int = 300):
        self.vault_path = Path(vault_path)
        self.needs_action_dir = self.vault_path / "Needs_Action"
        self.check_interval = check_interval  # 5 minutes default

        # Posting schedule configuration
        self.posting_schedule = {
            "enabled": True,
            "time": "09:00",  # 9 AM daily
            "days": ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"]  # Weekdays only
        }

        # State file to track last post
        self.state_file = self.vault_path.parent / "logs" / "linkedin_state.json"
        self.state_file.parent.mkdir(exist_ok=True)

        # Setup logging
        log_dir = self.vault_path.parent / "logs"
        log_dir.mkdir(exist_ok=True)

        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(log_dir / "linkedin_watcher.log"),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger("LinkedInWatcher")

    def start_monitoring(self):
        """Start continuous monitoring of LinkedIn posting schedule"""
        self.logger.info("LinkedIn Watcher started")
        self.logger.info(f"Posting schedule: {self.posting_schedule['time']} on {', '.join(self.posting_schedule['days'])}")
        self.logger.info(f"Check interval: {self.check_interval} seconds")

        try:
            while True:
                result = self.check_posting_schedule()

                if result["post_triggered"]:
                    self.logger.info(f"✅ LinkedIn post triggered")

                time.sleep(self.check_interval)

        except KeyboardInterrupt:
            self.logger.info("LinkedIn Watcher stopped by user")
        except Exception as e:
            self.logger.error(f"LinkedIn Watcher error: {e}", exc_info=True)

    def check_posting_schedule(self) -> Dict:
        """
        Check if it's time to post on LinkedIn

        Returns:
            Dictionary with check results
        """
        try:
            if not self.posting_schedule["enabled"]:
                return {
                    "post_triggered": False,
                    "reason": "Posting disabled",
                    "next_post_time": None
                }

            # Get current time
            now = datetime.now()
            current_day = now.strftime("%A")
            current_time = now.strftime("%H:%M")

            # Check if today is a posting day
            if current_day not in self.posting_schedule["days"]:
                next_post = self._calculate_next_post_time(now)
                return {
                    "post_triggered": False,
                    "reason": f"Not a posting day (today is {current_day})",
                    "next_post_time": next_post
                }

            # Load last post state
            last_post_date = self._load_last_post_date()

            # Check if we already posted today
            if last_post_date and last_post_date.date() == now.date():
                next_post = self._calculate_next_post_time(now)
                return {
                    "post_triggered": False,
                    "reason": "Already posted today",
                    "next_post_time": next_post
                }

            # Check if it's time to post
            scheduled_time = datetime.strptime(self.posting_schedule["time"], "%H:%M").time()
            current_time_obj = now.time()

            # Post if we're past the scheduled time and haven't posted today
            if current_time_obj >= scheduled_time:
                self.logger.info(f"📅 Time to post! Scheduled: {scheduled_time}, Current: {current_time_obj}")

                # Trigger post generation
                post_result = self._trigger_post_generation()

                if post_result["success"]:
                    # Update last post date
                    self._save_last_post_date(now)

                    return {
                        "post_triggered": True,
                        "post_file": post_result["post_file"],
                        "next_post_time": self._calculate_next_post_time(now)
                    }
                else:
                    return {
                        "post_triggered": False,
                        "reason": f"Post generation failed: {post_result.get('error')}",
                        "next_post_time": self._calculate_next_post_time(now)
                    }

            # Not time yet
            next_post = self._calculate_next_post_time(now)
            return {
                "post_triggered": False,
                "reason": f"Not time yet (scheduled: {scheduled_time}, current: {current_time_obj})",
                "next_post_time": next_post
            }

        except Exception as e:
            self.logger.error(f"Error checking posting schedule: {e}", exc_info=True)
            return {
                "post_triggered": False,
                "error": str(e),
                "next_post_time": None
            }

    def _trigger_post_generation(self) -> Dict:
        """
        Trigger LinkedIn post generation

        Returns:
            Dictionary with generation results
        """
        try:
            # Generate post content
            post_content = self._generate_post_content()

            # Create post file
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"LinkedIn_Post_{timestamp}.md"
            post_path = self.needs_action_dir / filename

            # Write post to file
            with open(post_path, 'w', encoding='utf-8') as f:
                f.write(post_content)

            self.logger.info(f"✅ LinkedIn post created: {filename}")

            return {
                "success": True,
                "post_file": filename,
                "post_path": str(post_path)
            }

        except Exception as e:
            self.logger.error(f"Error generating post: {e}", exc_info=True)
            return {
                "success": False,
                "error": str(e)
            }

    def _generate_post_content(self) -> str:
        """
        Generate LinkedIn post content

        In production, this would call the Generate_LinkedIn_Post skill
        For now, generates a template post
        """
        topics = [
            "Building autonomous AI systems",
            "The future of digital employees",
            "Productivity through automation",
            "AI-powered business growth",
            "Scaling with intelligent agents"
        ]

        # Simple topic rotation based on day of year
        topic_index = datetime.now().timetuple().tm_yday % len(topics)
        topic = topics[topic_index]

        post = f"""# LinkedIn Post - {datetime.now().strftime("%Y-%m-%d")}

**Topic:** {topic}

**Status:** PENDING APPROVAL

---

## Post Content

🚀 {topic}

In today's fast-paced business environment, the companies that thrive are those that embrace intelligent automation.

Here's what I've learned about building effective AI systems:

✅ Start with clear objectives
✅ Build incrementally (Bronze → Silver → Gold)
✅ Keep humans in the loop for critical decisions
✅ Measure everything and iterate

The future isn't about replacing humans—it's about augmenting human capabilities with AI that handles routine tasks, freeing us to focus on strategic thinking and creativity.

What's your experience with AI automation? Drop a comment below! 👇

---

**Hashtags:** #AI #Automation #DigitalTransformation #BusinessGrowth #FutureOfWork

**Call-to-Action:** Share your thoughts in the comments

---

## Approval Instructions

To approve this post:
1. Review the content above
2. Make any edits if needed
3. Add the line `STATUS: APPROVED` at the top
4. Save the file

To reject:
1. Add the line `STATUS: REJECTED` at the top
2. Save the file

---

*Generated by LinkedIn Watcher - {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}*
"""

        return post

    def _load_last_post_date(self) -> Optional[datetime]:
        """Load the date of the last post from state file"""
        try:
            if self.state_file.exists():
                with open(self.state_file, 'r') as f:
                    state = json.load(f)
                    last_post_str = state.get("last_post_date")
                    if last_post_str:
                        return datetime.fromisoformat(last_post_str)
            return None
        except Exception as e:
            self.logger.warning(f"Could not load last post date: {e}")
            return None

    def _save_last_post_date(self, post_date: datetime):
        """Save the date of the last post to state file"""
        try:
            state = {
                "last_post_date": post_date.isoformat(),
                "last_post_day": post_date.strftime("%A")
            }
            with open(self.state_file, 'w') as f:
                json.dump(state, f, indent=2)
        except Exception as e:
            self.logger.error(f"Could not save last post date: {e}")

    def _calculate_next_post_time(self, current_time: datetime) -> str:
        """Calculate the next scheduled post time"""
        try:
            scheduled_time = datetime.strptime(self.posting_schedule["time"], "%H:%M").time()

            # Start with tomorrow
            next_date = current_time + timedelta(days=1)

            # Find next posting day
            while next_date.strftime("%A") not in self.posting_schedule["days"]:
                next_date += timedelta(days=1)

            # Combine date and time
            next_post = datetime.combine(next_date.date(), scheduled_time)

            return next_post.strftime("%Y-%m-%d %H:%M")

        except Exception as e:
            self.logger.error(f"Error calculating next post time: {e}")
            return "Unknown"


if __name__ == "__main__":
    # Test the LinkedIn watcher
    vault_path = Path(__file__).parent.parent / "vault"
    watcher = LinkedInWatcher(str(vault_path), check_interval=10)

    print("Starting LinkedIn Watcher...")
    print("Press Ctrl+C to stop")
    print()

    watcher.start_monitoring()
