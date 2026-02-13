"""
Approval Engine - Silver Tier
Monitors Pending_Approval folder and executes approved actions
"""

import os
import time
import json
import shutil
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional
import logging


class ApprovalEngine:
    """Monitors approval status and executes approved actions"""

    def __init__(self, vault_path: str, check_interval: int = 30):
        self.vault_path = Path(vault_path)
        self.pending_approval_dir = self.vault_path / "Pending_Approval"
        self.approved_dir = self.vault_path / "Approved"
        self.done_dir = self.vault_path / "Done"
        self.check_interval = check_interval

        # Ensure directories exist
        self.pending_approval_dir.mkdir(exist_ok=True)
        self.approved_dir.mkdir(exist_ok=True)
        self.done_dir.mkdir(exist_ok=True)

        # Setup logging
        log_dir = self.vault_path.parent / "logs"
        log_dir.mkdir(exist_ok=True)

        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(log_dir / "approval_engine.log"),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger("ApprovalEngine")

    def start_monitoring(self):
        """Start continuous monitoring of Pending_Approval folder"""
        self.logger.info("Approval Engine started")
        self.logger.info(f"Monitoring: {self.pending_approval_dir}")
        self.logger.info(f"Check interval: {self.check_interval} seconds")

        try:
            while True:
                result = self.check_pending_approvals()

                if result["approvals_processed"] > 0 or result["rejections_processed"] > 0:
                    self.logger.info(
                        f"Processed: {result['approvals_processed']} approvals, "
                        f"{result['rejections_processed']} rejections"
                    )

                time.sleep(self.check_interval)

        except KeyboardInterrupt:
            self.logger.info("Approval Engine stopped by user")
        except Exception as e:
            self.logger.error(f"Approval Engine error: {e}", exc_info=True)

    def check_pending_approvals(self) -> Dict:
        """
        Check Pending_Approval folder for status changes

        Returns:
            Dictionary with processing results
        """
        approvals_processed = 0
        rejections_processed = 0
        executions_triggered = 0
        errors = []

        try:
            # Get all plan files in Pending_Approval
            plan_files = list(self.pending_approval_dir.glob("Plan_*.md"))

            for plan_file in plan_files:
                try:
                    # Read plan content
                    with open(plan_file, 'r', encoding='utf-8') as f:
                        content = f.read()

                    # Check for approval status
                    if "STATUS: APPROVED" in content:
                        self.logger.info(f"Approval detected: {plan_file.name}")

                        # Process approval
                        exec_result = self._process_approval(plan_file, content)

                        if exec_result["success"]:
                            approvals_processed += 1
                            executions_triggered += 1
                        else:
                            errors.append(f"Execution failed for {plan_file.name}: {exec_result.get('error')}")

                    elif "STATUS: REJECTED" in content:
                        self.logger.info(f"Rejection detected: {plan_file.name}")

                        # Process rejection
                        self._process_rejection(plan_file, content)
                        rejections_processed += 1

                except Exception as e:
                    error_msg = f"Error processing {plan_file.name}: {str(e)}"
                    self.logger.error(error_msg)
                    errors.append(error_msg)

            return {
                "success": True,
                "approvals_processed": approvals_processed,
                "rejections_processed": rejections_processed,
                "executions_triggered": executions_triggered,
                "errors": errors,
                "timestamp": datetime.now().isoformat()
            }

        except Exception as e:
            self.logger.error(f"Error checking pending approvals: {e}", exc_info=True)
            return {
                "success": False,
                "error": str(e),
                "approvals_processed": 0,
                "rejections_processed": 0,
                "executions_triggered": 0
            }

    def _process_approval(self, plan_file: Path, content: str) -> Dict:
        """
        Process an approved plan and execute actions

        Args:
            plan_file: Path to approved plan file
            content: Plan file content

        Returns:
            Execution result dictionary
        """
        try:
            # Parse plan to extract actions
            actions = self._parse_execution_steps(content)

            self.logger.info(f"Executing {len(actions)} actions from {plan_file.name}")

            # Execute actions
            execution_results = []
            for i, action in enumerate(actions, 1):
                self.logger.info(f"Executing step {i}/{len(actions)}: {action[:50]}...")

                # Simulate action execution (in real implementation, call appropriate skills)
                action_result = self._execute_action(action)
                execution_results.append(action_result)

            # Move plan to Approved folder
            approved_path = self.approved_dir / plan_file.name
            shutil.move(str(plan_file), str(approved_path))

            # Create completion report
            self._create_completion_report(approved_path, execution_results)

            # Log approval event
            self._log_approval_event(plan_file.name, "APPROVED", execution_results)

            return {
                "success": True,
                "plan_name": plan_file.name,
                "actions_completed": len([r for r in execution_results if r["success"]]),
                "actions_failed": len([r for r in execution_results if not r["success"]]),
                "approved_path": str(approved_path)
            }

        except Exception as e:
            self.logger.error(f"Error processing approval: {e}", exc_info=True)
            return {
                "success": False,
                "error": str(e)
            }

    def _process_rejection(self, plan_file: Path, content: str):
        """
        Process a rejected plan

        Args:
            plan_file: Path to rejected plan file
            content: Plan file content
        """
        try:
            # Extract rejection reason if provided
            rejection_reason = "No reason provided"
            for line in content.split('\n'):
                if line.startswith("REJECTION REASON:"):
                    rejection_reason = line.replace("REJECTION REASON:", "").strip()
                    break

            # Move to Done folder with rejection note
            done_path = self.done_dir / plan_file.name
            shutil.move(str(plan_file), str(done_path))

            # Create rejection note
            note_path = self.done_dir / f"{plan_file.stem}.rejection.md"
            with open(note_path, 'w', encoding='utf-8') as f:
                f.write(f"# Plan Rejected\n\n")
                f.write(f"**Plan:** {plan_file.name}\n")
                f.write(f"**Rejected:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                f.write(f"**Reason:** {rejection_reason}\n\n")
                f.write("---\n\n")
                f.write("This plan was rejected by human review and will not be executed.\n")

            # Log rejection event
            self._log_approval_event(plan_file.name, "REJECTED", [{"reason": rejection_reason}])

            self.logger.info(f"Plan rejected: {plan_file.name} - {rejection_reason}")

        except Exception as e:
            self.logger.error(f"Error processing rejection: {e}", exc_info=True)

    def _parse_execution_steps(self, content: str) -> List[str]:
        """Parse execution steps from plan content"""
        steps = []
        in_steps_section = False

        for line in content.split('\n'):
            if "## Execution Steps" in line:
                in_steps_section = True
                continue

            if in_steps_section:
                if line.startswith("##"):  # Next section
                    break

                # Extract numbered steps
                if line.strip() and line.strip()[0].isdigit():
                    # Remove number and period
                    step = line.strip().split('.', 1)
                    if len(step) > 1:
                        steps.append(step[1].strip())

        return steps

    def _execute_action(self, action: str) -> Dict:
        """
        Execute a single action (placeholder for actual implementation)

        In production, this would:
        - Parse action type
        - Call appropriate skill/function
        - Handle errors
        - Return detailed results

        Args:
            action: Action description

        Returns:
            Action result dictionary
        """
        # Placeholder implementation
        # In real system, this would route to appropriate skills

        action_lower = action.lower()

        try:
            # Simulate different action types
            if "email" in action_lower:
                # Would call Send_Email_via_MCP skill
                return {
                    "success": True,
                    "action": action,
                    "result": "Email sent successfully (simulated)",
                    "timestamp": datetime.now().isoformat()
                }

            elif "linkedin" in action_lower or "post" in action_lower:
                # Would call Generate_LinkedIn_Post skill
                return {
                    "success": True,
                    "action": action,
                    "result": "LinkedIn post created (simulated)",
                    "timestamp": datetime.now().isoformat()
                }

            else:
                # Generic action execution
                return {
                    "success": True,
                    "action": action,
                    "result": "Action completed (simulated)",
                    "timestamp": datetime.now().isoformat()
                }

        except Exception as e:
            return {
                "success": False,
                "action": action,
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }

    def _create_completion_report(self, plan_path: Path, execution_results: List[Dict]):
        """Create completion report for executed plan"""
        report_path = plan_path.parent / f"{plan_path.stem}.completion.md"

        with open(report_path, 'w', encoding='utf-8') as f:
            f.write(f"# Execution Completion Report\n\n")
            f.write(f"**Plan:** {plan_path.name}\n")
            f.write(f"**Executed:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"**Total Actions:** {len(execution_results)}\n")
            f.write(f"**Successful:** {len([r for r in execution_results if r['success']])}\n")
            f.write(f"**Failed:** {len([r for r in execution_results if not r['success']])}\n\n")
            f.write("---\n\n## Action Results\n\n")

            for i, result in enumerate(execution_results, 1):
                status = "✅ Success" if result["success"] else "❌ Failed"
                f.write(f"### Action {i}: {status}\n\n")
                f.write(f"**Action:** {result['action']}\n\n")

                if result["success"]:
                    f.write(f"**Result:** {result.get('result', 'Completed')}\n\n")
                else:
                    f.write(f"**Error:** {result.get('error', 'Unknown error')}\n\n")

                f.write("---\n\n")

            f.write("*This report was automatically generated by the Approval Engine.*\n")

    def _log_approval_event(self, plan_name: str, status: str, results: List[Dict]):
        """Log approval event to approval log"""
        log_file = self.vault_path.parent / "logs" / "approvals.log"

        with open(log_file, 'a', encoding='utf-8') as f:
            f.write("=" * 80 + "\n")
            f.write(f"[{datetime.now().isoformat()}] APPROVAL EVENT\n")
            f.write("=" * 80 + "\n")
            f.write(f"Plan: {plan_name}\n")
            f.write(f"Status: {status}\n")
            f.write(f"Actions: {len(results)}\n")

            if status == "APPROVED":
                successful = len([r for r in results if r.get("success", False)])
                f.write(f"Successful: {successful}/{len(results)}\n")

            f.write("=" * 80 + "\n\n")


if __name__ == "__main__":
    # Test the approval engine
    vault_path = Path(__file__).parent.parent / "vault"
    engine = ApprovalEngine(str(vault_path), check_interval=5)

    print("Starting Approval Engine...")
    print("Press Ctrl+C to stop")
    print()

    engine.start_monitoring()
