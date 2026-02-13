"""
AI Brain - Autonomous Reasoning Engine
======================================

This module implements the core AI reasoning loop that processes tasks,
selects appropriate skills, and executes actions until completion.

Architecture Decision:
- Implements "Ralph Wiggum Stop Hook" pattern (loop until task complete)
- Skill-based architecture for modularity
- State machine for task lifecycle management
- Integration with Claude Code for reasoning (future: API integration)

Author: AI Employee System
Version: 1.0.0
"""

import os
import re
import json
import shutil
import logging
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, asdict


logger = logging.getLogger("AIBrain")


@dataclass
class TaskState:
    """Represents the current state of a task being processed."""
    file_path: str
    file_name: str
    content: str
    task_type: Optional[str] = None
    priority: Optional[str] = None
    confidence: float = 0.0
    current_skill: Optional[str] = None
    actions_taken: List[str] = None
    is_complete: bool = False
    error: Optional[str] = None

    def __post_init__(self):
        if self.actions_taken is None:
            self.actions_taken = []


class SkillRegistry:
    """
    Manages available skills and their definitions.

    Parses SKILLS.md and provides skill lookup and execution logic.
    """

    def __init__(self, skills_path: Path):
        """
        Initialize the skill registry.

        Args:
            skills_path: Path to SKILLS.md file
        """
        self.skills_path = skills_path
        self.skills = {}
        self._load_skills()

    def _load_skills(self):
        """Load and parse skills from SKILLS.md."""
        try:
            with open(self.skills_path, 'r', encoding='utf-8') as f:
                content = f.read()

            # Parse skill definitions (simplified parsing)
            # In production, this would be more robust
            skill_pattern = r'## Skill #\d+: (.+?)\n'
            matches = re.finditer(skill_pattern, content)

            for match in matches:
                skill_name = match.group(1).strip()
                self.skills[skill_name] = {
                    'name': skill_name,
                    'loaded': True
                }

            logger.info(f"Loaded {len(self.skills)} skills from registry")

        except Exception as e:
            logger.error(f"Failed to load skills: {str(e)}")
            # Fallback to basic skills
            self._load_fallback_skills()

    def _load_fallback_skills(self):
        """Load basic fallback skills if SKILLS.md parsing fails."""
        self.skills = {
            'Process_New_File': {'name': 'Process_New_File', 'loaded': True},
            'Classify_Task': {'name': 'Classify_Task', 'loaded': True},
            'Prioritize_Task': {'name': 'Prioritize_Task', 'loaded': True},
            'Move_To_Needs_Action': {'name': 'Move_To_Needs_Action', 'loaded': True},
            'Move_To_Done': {'name': 'Move_To_Done', 'loaded': True},
            'Update_Dashboard': {'name': 'Update_Dashboard', 'loaded': True},
        }

    def get_skill(self, skill_name: str) -> Optional[Dict]:
        """Get skill definition by name."""
        return self.skills.get(skill_name)

    def list_skills(self) -> List[str]:
        """List all available skill names."""
        return list(self.skills.keys())


class AIBrain:
    """
    Core AI reasoning engine that processes tasks autonomously.

    Implements the reasoning loop:
    1. Reason - Analyze current state and decide next action
    2. Act - Execute the selected skill
    3. Evaluate - Check if task is complete
    4. Continue - Loop until task complete or error
    """

    def __init__(self, vault_path: Path):
        """
        Initialize the AI brain.

        Args:
            vault_path: Path to the vault root directory
        """
        self.vault_path = vault_path
        self.inbox_path = vault_path / "Inbox"
        self.needs_action_path = vault_path / "Needs_Action"
        self.done_path = vault_path / "Done"
        self.dashboard_path = vault_path / "Dashboard.md"
        self.handbook_path = vault_path / "Company_Handbook.md"
        self.skills_path = vault_path / "SKILLS.md"

        # Load skill registry
        self.skills = SkillRegistry(self.skills_path)

        # Load handbook for decision-making context
        self.handbook = self._load_handbook()

        logger.info("AI Brain initialized successfully")

    def _load_handbook(self) -> str:
        """Load company handbook for context."""
        try:
            with open(self.handbook_path, 'r', encoding='utf-8') as f:
                return f.read()
        except Exception as e:
            logger.warning(f"Could not load handbook: {str(e)}")
            return ""

    def process_new_file(self, file_path: str, file_name: str, content: str) -> Dict:
        """
        Main entry point for processing a new file.

        Implements the autonomous reasoning loop until task completion.

        Args:
            file_path: Full path to the file
            file_name: Name of the file
            content: File content

        Returns:
            Dictionary with processing results
        """
        logger.info(f"🧠 Brain processing: {file_name}")

        # Initialize task state
        state = TaskState(
            file_path=file_path,
            file_name=file_name,
            content=content
        )

        # Reasoning loop - continue until task complete
        max_iterations = 10  # Safety limit
        iteration = 0

        while not state.is_complete and iteration < max_iterations:
            iteration += 1
            logger.info(f"🔄 Reasoning iteration {iteration}")

            try:
                # REASON: Decide what to do next
                next_action = self._reason(state)
                logger.info(f"💭 Reasoning: {next_action}")

                # ACT: Execute the action
                self._act(state, next_action)

                # EVALUATE: Check if we're done
                state.is_complete = self._evaluate(state)

                if state.is_complete:
                    logger.info(f"✅ Task complete after {iteration} iterations")
                    break

            except Exception as e:
                logger.error(f"Error in reasoning loop: {str(e)}", exc_info=True)
                state.error = str(e)
                state.is_complete = True  # Stop on error

        # Return results
        return self._format_result(state)

    def _reason(self, state: TaskState) -> str:
        """
        Reasoning step: Analyze current state and decide next action.

        This is where the AI "thinks" about what to do next.

        Args:
            state: Current task state

        Returns:
            Next action to take
        """
        # If we haven't classified yet, classify first
        if state.task_type is None:
            return "classify_task"

        # If we haven't prioritized yet, prioritize
        if state.priority is None:
            return "prioritize_task"

        # If we've classified and prioritized, move to appropriate folder
        if "moved_to" not in [a.split(':')[0] for a in state.actions_taken]:
            # Decide where to move based on task type
            if state.task_type in ["Question", "Request", "Data_Processing"]:
                return "move_to_needs_action"
            else:
                return "move_to_needs_action"  # Default to needs action

        # If we've moved the file, update dashboard
        if "dashboard_updated" not in state.actions_taken:
            return "update_dashboard"

        # All done
        return "complete"

    def _act(self, state: TaskState, action: str):
        """
        Action step: Execute the decided action.

        Args:
            state: Current task state
            action: Action to execute
        """
        logger.info(f"⚡ Executing action: {action}")

        if action == "classify_task":
            self._classify_task(state)

        elif action == "prioritize_task":
            self._prioritize_task(state)

        elif action == "move_to_needs_action":
            self._move_to_needs_action(state)

        elif action == "move_to_done":
            self._move_to_done(state)

        elif action == "update_dashboard":
            self._update_dashboard(state)

        elif action == "complete":
            state.is_complete = True

        else:
            logger.warning(f"Unknown action: {action}")

    def _evaluate(self, state: TaskState) -> bool:
        """
        Evaluation step: Check if task is complete.

        Args:
            state: Current task state

        Returns:
            True if task is complete, False otherwise
        """
        # Task is complete if:
        # 1. File has been moved
        # 2. Dashboard has been updated
        # 3. No errors occurred

        has_moved = any(a.startswith("moved_to") for a in state.actions_taken)
        has_updated_dashboard = "dashboard_updated" in state.actions_taken
        no_errors = state.error is None

        return has_moved and has_updated_dashboard and no_errors

    def _classify_task(self, state: TaskState):
        """
        Classify the task based on content analysis.

        Implements Skill #2: Classify_Task
        """
        content_lower = state.content.lower()

        # Simple keyword-based classification
        # In production, this would use Claude API for better classification
        if '?' in state.content or any(word in content_lower for word in ['how', 'what', 'why', 'when', 'where']):
            task_type = "Question"
            confidence = 0.8

        elif any(word in content_lower for word in ['please', 'can you', 'need', 'request']):
            task_type = "Request"
            confidence = 0.7

        elif any(word in content_lower for word in ['data', 'analyze', 'process', 'calculate']):
            task_type = "Data_Processing"
            confidence = 0.75

        elif any(word in content_lower for word in ['document', 'write', 'create doc', 'report']):
            task_type = "Documentation"
            confidence = 0.7

        elif any(word in content_lower for word in ['research', 'find', 'investigate', 'study']):
            task_type = "Research"
            confidence = 0.7

        else:
            task_type = "Other"
            confidence = 0.5

        state.task_type = task_type
        state.confidence = confidence
        state.actions_taken.append(f"classified_as:{task_type}")

        logger.info(f"📋 Classified as: {task_type} (confidence: {confidence:.2f})")

    def _prioritize_task(self, state: TaskState):
        """
        Assign priority to the task.

        Implements Skill #8: Prioritize_Task
        """
        content_lower = state.content.lower()
        score = 5  # Base score

        # Check for urgency markers
        if any(marker in content_lower for marker in ['urgent', 'asap', '!!!', 'emergency']):
            score += 3

        if any(marker in content_lower for marker in ['important', 'priority', 'critical']):
            score += 2

        if any(marker in content_lower for marker in ['when possible', 'eventually', 'low priority']):
            score -= 2

        # Adjust based on task type
        if state.task_type == "Question":
            score += 1  # Quick to resolve

        elif state.task_type == "Research":
            score -= 1  # Time-intensive

        # Map score to priority
        if score >= 8:
            priority = "High"
        elif score >= 4:
            priority = "Medium"
        else:
            priority = "Low"

        state.priority = priority
        state.actions_taken.append(f"prioritized_as:{priority}")

        logger.info(f"⚖️ Priority assigned: {priority} (score: {score})")

    def _move_to_needs_action(self, state: TaskState):
        """
        Move file to Needs_Action folder.

        Implements Skill #3: Move_To_Needs_Action
        """
        try:
            source = Path(state.file_path)
            destination = self.needs_action_path / state.file_name

            # Check if file still exists
            if not source.exists():
                logger.warning(f"Source file no longer exists: {state.file_name}")
                return

            # Move file
            shutil.move(str(source), str(destination))

            # Create metadata file
            metadata = {
                'original_path': state.file_path,
                'moved_at': datetime.now().isoformat(),
                'task_type': state.task_type,
                'priority': state.priority,
                'confidence': state.confidence,
                'reason': f"Classified as {state.task_type} with {state.priority} priority"
            }

            metadata_path = destination.with_suffix('.meta.json')
            with open(metadata_path, 'w', encoding='utf-8') as f:
                json.dump(metadata, f, indent=2)

            state.actions_taken.append(f"moved_to:Needs_Action")
            logger.info(f"📁 Moved to Needs_Action: {state.file_name}")

        except Exception as e:
            logger.error(f"Failed to move file: {str(e)}")
            state.error = f"Move failed: {str(e)}"

    def _move_to_done(self, state: TaskState):
        """
        Move file to Done folder.

        Implements Skill #4: Move_To_Done
        """
        try:
            source = Path(state.file_path)
            destination = self.done_path / state.file_name

            # Move file
            shutil.move(str(source), str(destination))

            # Create completion metadata
            metadata = {
                'completed_at': datetime.now().isoformat(),
                'task_type': state.task_type,
                'priority': state.priority,
                'actions_taken': state.actions_taken,
                'outcome': 'Successfully processed'
            }

            metadata_path = destination.with_suffix('.meta.json')
            with open(metadata_path, 'w', encoding='utf-8') as f:
                json.dump(metadata, f, indent=2)

            state.actions_taken.append(f"moved_to:Done")
            logger.info(f"✅ Moved to Done: {state.file_name}")

        except Exception as e:
            logger.error(f"Failed to move file: {str(e)}")
            state.error = f"Move failed: {str(e)}"

    def _update_dashboard(self, state: TaskState):
        """
        Update Dashboard.md with current task information.

        Implements Skill #6: Update_Dashboard
        """
        try:
            # Read current dashboard
            with open(self.dashboard_path, 'r', encoding='utf-8') as f:
                dashboard = f.read()

            # Update timestamp
            dashboard = re.sub(
                r'\*\*Last Updated:\*\* .+',
                f'**Last Updated:** {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}',
                dashboard
            )

            # Update last action log
            action_log = f"""```
[{datetime.now().strftime("%Y-%m-%d %H:%M:%S")}] Processed: {state.file_name}
Task Type: {state.task_type}
Priority: {state.priority}
Actions: {', '.join(state.actions_taken)}
Status: {'✅ Success' if not state.error else '❌ Error'}
```"""

            dashboard = re.sub(
                r'## 📝 Last AI Action Log\n\n```[\s\S]*?```',
                f'## 📝 Last AI Action Log\n\n{action_log}',
                dashboard
            )

            # Write updated dashboard
            with open(self.dashboard_path, 'w', encoding='utf-8') as f:
                f.write(dashboard)

            state.actions_taken.append("dashboard_updated")
            logger.info(f"📊 Dashboard updated")

        except Exception as e:
            logger.error(f"Failed to update dashboard: {str(e)}")
            # Don't fail the whole task if dashboard update fails

    def _format_result(self, state: TaskState) -> Dict:
        """
        Format the final result for return.

        Args:
            state: Final task state

        Returns:
            Dictionary with processing results
        """
        return {
            'success': state.error is None,
            'file_name': state.file_name,
            'task_type': state.task_type,
            'priority': state.priority,
            'confidence': state.confidence,
            'actions_taken': state.actions_taken,
            'action': f"Moved to {'Needs_Action' if 'moved_to:Needs_Action' in state.actions_taken else 'Done'}",
            'reasoning': f"Classified as {state.task_type} with {state.priority} priority (confidence: {state.confidence:.2f})",
            'error': state.error
        }
