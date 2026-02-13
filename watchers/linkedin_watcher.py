"""
LinkedIn Watcher - Autonomous Post Generation
==============================================

Continuously monitors posting schedule and generates business-focused
LinkedIn content for approval and publishing.

Author: AI Employee System
Version: 2.0.0
"""

import os
import time
import logging
from pathlib import Path
from datetime import datetime, date
from typing import Dict, Optional, List
from dotenv import load_dotenv
import signal
import sys

# Load environment variables
load_dotenv()

# Configuration
POST_INTERVAL_MINUTES = int(os.getenv('POST_INTERVAL_MINUTES', 60))
LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
VAULT_PATH = Path(os.getenv('VAULT_PATH', 'vault'))

# Setup logging
log_dir = Path('logs')
log_dir.mkdir(exist_ok=True)

logging.basicConfig(
    level=getattr(logging, LOG_LEVEL),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(log_dir / 'linkedin_watcher.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger('LinkedInWatcher')

# Global flag for graceful shutdown
shutdown_requested = False


def signal_handler(signum, frame):
    """Handle shutdown signals gracefully"""
    global shutdown_requested
    logger.info("Shutdown signal received. Finishing current operation...")
    shutdown_requested = True


# Register signal handlers
signal.signal(signal.SIGINT, signal_handler)
signal.signal(signal.SIGTERM, signal_handler)


class LinkedInPostGenerator:
    """Generates business-focused LinkedIn content"""

    def __init__(self):
        self.post_templates = self._load_templates()
        self.template_index = 0

    def _load_templates(self) -> List[Dict]:
        """Load post templates with different topics"""
        return [
            {
                "topic": "AI Automation in Business",
                "hook": "🚀 Most businesses are still doing manually what AI could automate in seconds.",
                "body": """Here's what I've learned building autonomous systems:

The gap isn't technology—it's implementation.

Companies that win aren't using the most advanced AI.
They're using practical automation that solves real problems.

Three principles that matter:
→ Start with high-volume, low-complexity tasks
→ Keep humans in the loop for critical decisions
→ Measure impact in hours saved, not features built

The future isn't about replacing people.
It's about freeing them to do work that actually matters.""",
                "cta": "What's one task you wish you could automate? Drop it in the comments.",
                "hashtags": ["#AI", "#Automation", "#BusinessGrowth", "#Productivity", "#DigitalTransformation"]
            },
            {
                "topic": "Building vs Buying Software",
                "hook": "💡 Spent $50K on software that solved 60% of our problem.",
                "body": """Then spent $5K building the missing 40% ourselves.

Here's what nobody tells you about SaaS:

Off-the-shelf software is built for everyone.
Which means it's perfect for no one.

The real ROI comes from:
→ Custom workflows that match YOUR process
→ Integrations that connect YOUR tools
→ Automation that solves YOUR bottlenecks

Don't get me wrong—buy when you can.
But know when to build.

The companies winning in 2026 aren't using more tools.
They're using the RIGHT tools, customized to their needs.""",
                "cta": "Build or buy? What's your approach? Let's discuss below.",
                "hashtags": ["#SaaS", "#BusinessStrategy", "#TechLeadership", "#Innovation", "#Entrepreneurship"]
            },
            {
                "topic": "Productivity Through Systems",
                "hook": "⚡ Working harder isn't the answer. Working smarter is overrated too.",
                "body": """The real answer? Working systematically.

I used to pride myself on being busy.
Inbox zero. Back-to-back meetings. Always available.

Then I realized: busy ≠ productive.

What changed everything:
→ Documented every repeating task
→ Automated what could be automated
→ Delegated what couldn't (including to AI)
→ Protected deep work time like it was sacred

Result?
Same output. Half the hours. Zero burnout.

The secret isn't doing more.
It's building systems that do the work for you.""",
                "cta": "What's your biggest productivity bottleneck? Share below—I might have a solution.",
                "hashtags": ["#Productivity", "#TimeManagement", "#WorkSmart", "#Efficiency", "#Leadership"]
            },
            {
                "topic": "AI Implementation Reality",
                "hook": "🎯 Everyone's talking about AI. Few are actually using it effectively.",
                "body": """Here's the gap I see:

Companies are either:
→ Waiting for the "perfect" AI solution
→ Or throwing AI at everything hoping something sticks

Both approaches fail.

What works:
Start with one painful, repetitive process.
Build a simple automation.
Measure the impact.
Then scale.

We automated email triage last month.
Saved 10 hours per week.
Cost? $0 in software. 2 days to build.

The AI revolution isn't coming.
It's here. But only for those who start small and iterate fast.""",
                "cta": "What's one process you could automate this week? Let me know—happy to share ideas.",
                "hashtags": ["#ArtificialIntelligence", "#BusinessAutomation", "#Innovation", "#TechTrends", "#DigitalStrategy"]
            },
            {
                "topic": "Remote Work Efficiency",
                "hook": "📊 Remote work isn't the problem. Unstructured remote work is.",
                "body": """Three years of remote work taught me this:

Location doesn't matter.
Systems do.

What separates high-performing remote teams:

→ Async communication by default
→ Clear documentation (not tribal knowledge)
→ Automated status updates (not daily standups)
→ Results measured by output, not activity

The teams struggling with remote work?
They're trying to replicate the office online.

The teams thriving?
They've built systems that work anywhere.

Remote work isn't a compromise.
Done right, it's a competitive advantage.""",
                "cta": "Remote, hybrid, or office? What's working for your team? Share your experience.",
                "hashtags": ["#RemoteWork", "#FutureOfWork", "#TeamProductivity", "#WorkCulture", "#Leadership"]
            },
            {
                "topic": "Decision Making Framework",
                "hook": "🧠 The best decision I made last year? Deciding how to decide.",
                "body": """Sounds meta, but hear me out.

Most businesses waste time on decisions that don't matter.
And rush through decisions that do.

I built a simple framework:

Type 1: Reversible decisions → Decide fast, iterate
Type 2: Irreversible decisions → Slow down, gather data
Type 3: No decision needed → Automate or delegate

Example:
→ Hiring? Type 2. Take your time.
→ Email response? Type 3. Template it.
→ New tool trial? Type 1. Test for a week.

Since implementing this:
→ 60% fewer meetings
→ Faster execution
→ Better outcomes

Stop treating every decision like it's life or death.""",
                "cta": "How do you approach decision-making? Drop your framework below.",
                "hashtags": ["#DecisionMaking", "#Leadership", "#BusinessStrategy", "#Productivity", "#Management"]
            },
            {
                "topic": "Learning in Public",
                "hook": "📚 Sharing what you learn isn't just generous. It's strategic.",
                "body": """Here's why I document everything publicly:

1. Teaching forces clarity
   Can't explain it? Don't understand it.

2. Feedback accelerates learning
   Share early. Get corrected. Improve fast.

3. Network effects compound
   Help 100 people → 10 reach out → 1 becomes a client/partner

4. Future you will thank present you
   Your documented learnings become your knowledge base.

I've shared:
→ Failed experiments (most valuable)
→ System designs (with diagrams)
→ Automation scripts (open source)
→ Lessons learned (the hard way)

Result? Opportunities I never could have predicted.

Your knowledge isn't valuable locked in your head.
It's valuable when it helps others.""",
                "cta": "What's something you learned recently that others should know? Share it below.",
                "hashtags": ["#LearningInPublic", "#KnowledgeSharing", "#ProfessionalDevelopment", "#Growth", "#Community"]
            }
        ]

    def generate_post(self) -> Dict[str, str]:
        """
        Generate a LinkedIn post using template rotation

        Returns:
            Dictionary with post content, CTA, and hashtags
        """
        # Get current template and rotate
        template = self.post_templates[self.template_index]
        self.template_index = (self.template_index + 1) % len(self.post_templates)

        # Format the post
        post_content = f"{template['hook']}\n\n{template['body']}"

        # Word count validation (150-300 words)
        word_count = len(post_content.split())
        logger.debug(f"Generated post with {word_count} words")

        return {
            "topic": template["topic"],
            "content": post_content,
            "cta": template["cta"],
            "hashtags": " ".join(template["hashtags"][:5])  # Max 5 hashtags
        }


class LinkedInWatcher:
    """Main watcher class for LinkedIn post generation"""

    def __init__(self):
        self.vault_path = VAULT_PATH
        self.needs_action_dir = self.vault_path / "Needs_Action"
        self.pending_approval_dir = self.vault_path / "Pending_Approval"
        self.generator = LinkedInPostGenerator()

        # Ensure directories exist
        self.needs_action_dir.mkdir(parents=True, exist_ok=True)
        self.pending_approval_dir.mkdir(parents=True, exist_ok=True)

        logger.info("LinkedIn Watcher initialized")
        logger.info(f"Post interval: {POST_INTERVAL_MINUTES} minutes")

    def check_duplicate_today(self) -> bool:
        """
        Check if a post was already generated today

        Returns:
            True if post exists for today, False otherwise
        """
        today = date.today().strftime("%Y-%m-%d")
        pattern = f"{today}__linkedin_post.md"

        # Check in Needs_Action
        if (self.needs_action_dir / pattern).exists():
            logger.info(f"Post already exists in Needs_Action: {pattern}")
            return True

        # Check in Pending_Approval
        if (self.pending_approval_dir / pattern).exists():
            logger.info(f"Post already exists in Pending_Approval: {pattern}")
            return True

        return False

    def generate_linkedin_post(self) -> Optional[Dict[str, str]]:
        """
        Generate LinkedIn post content

        Returns:
            Dictionary with post data or None if generation fails
        """
        try:
            logger.info("Generating LinkedIn post...")
            post_data = self.generator.generate_post()
            logger.info(f"Generated post on topic: {post_data['topic']}")
            return post_data
        except Exception as e:
            logger.error(f"Failed to generate post: {e}", exc_info=True)
            return None

    def save_post_to_markdown(self, post_data: Dict[str, str]) -> Optional[Path]:
        """
        Save post to markdown file in Needs_Action

        Args:
            post_data: Dictionary with post content

        Returns:
            Path to saved file or None if save fails
        """
        try:
            # Generate filename with today's date
            today = date.today().strftime("%Y-%m-%d")
            filename = f"{today}__linkedin_post.md"
            filepath = self.needs_action_dir / filename

            # Create markdown content
            markdown_content = f"""# LinkedIn Post Draft

**Status:** Draft
**Approval Required:** Yes
**Platform:** LinkedIn
**Topic:** {post_data['topic']}
**Generated:** {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}

---

## Content

{post_data['content']}

---

## CTA

{post_data['cta']}

---

## Hashtags

{post_data['hashtags']}

---

## Approval Instructions

To approve this post:
1. Review the content above
2. Make any edits if needed
3. Add the line `STATUS: APPROVED` at the top of this file
4. Save the file

To reject this post:
1. Add the line `STATUS: REJECTED` at the top of this file
2. Optionally add a rejection reason
3. Save the file

---

*Generated by LinkedIn Watcher - {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}*
"""

            # Write to file
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(markdown_content)

            logger.info(f"Post saved to: {filepath}")
            return filepath

        except Exception as e:
            logger.error(f"Failed to save post: {e}", exc_info=True)
            return None

    def move_to_pending_approval(self, filepath: Path) -> bool:
        """
        Move post from Needs_Action to Pending_Approval

        Args:
            filepath: Path to the file to move

        Returns:
            True if move successful, False otherwise
        """
        try:
            destination = self.pending_approval_dir / filepath.name

            # Move file
            filepath.rename(destination)

            logger.info(f"Moved to Pending_Approval: {filepath.name}")
            return True

        except Exception as e:
            logger.error(f"Failed to move file: {e}", exc_info=True)
            return False

    def log_action(self, action: str, details: Dict):
        """
        Log action to actions.log

        Args:
            action: Action type
            details: Action details
        """
        try:
            log_file = Path('logs') / 'actions.log'

            with open(log_file, 'a', encoding='utf-8') as f:
                f.write("=" * 80 + "\n")
                f.write(f"[{datetime.now().isoformat()}] {action}\n")
                f.write("=" * 80 + "\n")
                for key, value in details.items():
                    f.write(f"{key}: {value}\n")
                f.write("=" * 80 + "\n\n")

            logger.debug(f"Action logged: {action}")

        except Exception as e:
            logger.error(f"Failed to log action: {e}", exc_info=True)

    def process_post_generation(self):
        """Main process for generating and saving a post"""
        try:
            # Check for duplicate
            if self.check_duplicate_today():
                logger.info("Skipping: Post already generated today")
                return

            # Generate post
            post_data = self.generate_linkedin_post()
            if not post_data:
                logger.error("Post generation failed")
                return

            # Save to markdown
            filepath = self.save_post_to_markdown(post_data)
            if not filepath:
                logger.error("Failed to save post")
                return

            # Move to Pending_Approval
            if self.move_to_pending_approval(filepath):
                # Log success
                self.log_action("LINKEDIN_POST_GENERATED", {
                    "filename": filepath.name,
                    "topic": post_data['topic'],
                    "status": "Pending Approval",
                    "word_count": len(post_data['content'].split()),
                    "hashtags": post_data['hashtags']
                })
                logger.info("✅ LinkedIn post generated and moved to Pending_Approval")
            else:
                logger.error("Failed to move post to Pending_Approval")

        except Exception as e:
            logger.error(f"Error in post generation process: {e}", exc_info=True)
            self.log_action("LINKEDIN_POST_ERROR", {
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            })

    def main_loop(self):
        """Main monitoring loop"""
        logger.info("=" * 60)
        logger.info("LinkedIn Watcher Started")
        logger.info("=" * 60)
        logger.info(f"Monitoring interval: {POST_INTERVAL_MINUTES} minutes")
        logger.info(f"Vault path: {self.vault_path.absolute()}")
        logger.info("Press Ctrl+C to stop")
        logger.info("=" * 60)

        # Generate first post immediately
        logger.info("Generating initial post...")
        self.process_post_generation()

        # Main loop
        while not shutdown_requested:
            try:
                # Wait for interval
                logger.info(f"Next check in {POST_INTERVAL_MINUTES} minutes...")

                # Sleep in small increments to allow graceful shutdown
                for _ in range(POST_INTERVAL_MINUTES * 60):
                    if shutdown_requested:
                        break
                    time.sleep(1)

                if shutdown_requested:
                    break

                # Generate post
                self.process_post_generation()

            except Exception as e:
                logger.error(f"Error in main loop: {e}", exc_info=True)
                time.sleep(60)  # Wait 1 minute before retrying

        logger.info("LinkedIn Watcher stopped gracefully")


def main():
    """Entry point"""
    try:
        watcher = LinkedInWatcher()
        watcher.main_loop()
    except KeyboardInterrupt:
        logger.info("Interrupted by user")
    except Exception as e:
        logger.error(f"Fatal error: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()
