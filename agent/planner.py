"""
Planner Module - Silver Tier
Generates structured execution plans for complex tasks
"""

import os
import json
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple


class TaskPlanner:
    """Generates and manages execution plans for tasks"""

    def __init__(self, vault_path: str):
        self.vault_path = Path(vault_path)
        self.plans_dir = self.vault_path / "Plans"
        self.pending_approval_dir = self.vault_path / "Pending_Approval"
        self.approved_dir = self.vault_path / "Approved"

        # Ensure directories exist
        self.plans_dir.mkdir(exist_ok=True)
        self.pending_approval_dir.mkdir(exist_ok=True)
        self.approved_dir.mkdir(exist_ok=True)

    def generate_plan(
        self,
        task_content: str,
        task_type: str,
        priority: str,
        context: Optional[Dict] = None
    ) -> Dict:
        """
        Generate structured execution plan for a task

        Args:
            task_content: Full task description
            task_type: Classified task type
            priority: Task priority (High/Medium/Low)
            context: Additional context

        Returns:
            Dictionary with plan details
        """
        try:
            # Analyze task requirements
            objective = self._extract_objective(task_content)
            required_skills = self._identify_required_skills(task_content, task_type)
            execution_steps = self._generate_execution_steps(task_content, task_type, required_skills)
            risk_assessment = self._assess_risk(execution_steps, task_type)
            approval_required = risk_assessment["requires_approval"]
            estimated_outcome = self._estimate_outcome(task_content, execution_steps)

            # Generate task name for filename
            task_name = self._generate_task_name(task_content)
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"Plan_{timestamp}_{task_name}.md"

            # Create plan content
            plan_content = self._format_plan(
                task_name=task_name,
                objective=objective,
                required_skills=required_skills,
                execution_steps=execution_steps,
                risk_assessment=risk_assessment,
                approval_required=approval_required,
                estimated_outcome=estimated_outcome,
                priority=priority,
                task_type=task_type
            )

            # Save plan
            plan_path = self.plans_dir / filename
            with open(plan_path, 'w', encoding='utf-8') as f:
                f.write(plan_content)

            return {
                "success": True,
                "plan_path": str(plan_path),
                "filename": filename,
                "approval_required": approval_required,
                "risk_level": risk_assessment["risk_level"],
                "estimated_steps": len(execution_steps),
                "task_name": task_name
            }

        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "plan_path": None
            }

    def _extract_objective(self, task_content: str) -> str:
        """Extract main objective from task content"""
        # Take first sentence or first 200 characters
        lines = task_content.strip().split('\n')
        first_line = lines[0] if lines else task_content

        if len(first_line) > 200:
            return first_line[:197] + "..."
        return first_line

    def _identify_required_skills(self, task_content: str, task_type: str) -> List[str]:
        """Identify which skills are needed for this task"""
        skills = []
        content_lower = task_content.lower()

        # Check for email-related tasks
        if any(word in content_lower for word in ["email", "send", "reply", "message"]):
            skills.append("Send_Email_via_MCP")

        # Check for LinkedIn tasks
        if any(word in content_lower for word in ["linkedin", "post", "social media", "share"]):
            skills.append("Generate_LinkedIn_Post")

        # Check for research tasks
        if any(word in content_lower for word in ["research", "investigate", "find", "analyze"]):
            skills.append("Generate_Task_Summary")

        # Check for reporting tasks
        if any(word in content_lower for word in ["report", "summary", "briefing", "overview"]):
            skills.append("Generate_CEO_Briefing")

        # Always include core skills
        skills.extend(["Classify_Task", "Prioritize_Task", "Log_Action"])

        return list(set(skills))  # Remove duplicates

    def _generate_execution_steps(
        self,
        task_content: str,
        task_type: str,
        required_skills: List[str]
    ) -> List[str]:
        """Generate step-by-step execution plan"""
        steps = []
        content_lower = task_content.lower()

        # Step 1: Always analyze the task
        steps.append("Analyze task requirements and validate inputs")

        # Add task-specific steps
        if "Send_Email_via_MCP" in required_skills:
            steps.append("Draft email content with subject and body")
            steps.append("Validate recipient email address")
            steps.append("Send email via MCP server")
            steps.append("Verify email delivery confirmation")

        if "Generate_LinkedIn_Post" in required_skills:
            steps.append("Generate LinkedIn post content with engagement hook")
            steps.append("Add relevant hashtags and call-to-action")
            steps.append("Save draft to Needs_Action folder")
            steps.append("Request approval for posting")

        if task_type == "Research":
            steps.append("Gather relevant information from available sources")
            steps.append("Analyze and synthesize findings")
            steps.append("Generate summary report")

        if task_type == "Data_Processing":
            steps.append("Load and validate data")
            steps.append("Process data according to requirements")
            steps.append("Generate output report")

        # Final steps
        steps.append("Update dashboard with task completion")
        steps.append("Log all actions taken")
        steps.append("Move task to Done folder")

        return steps

    def _assess_risk(self, execution_steps: List[str], task_type: str) -> Dict:
        """Assess risk level of planned actions"""
        risk_score = 0
        risk_factors = []

        # High-risk actions
        high_risk_keywords = [
            "send email", "post", "publish", "delete", "remove",
            "financial", "payment", "transfer", "api call"
        ]

        # Medium-risk actions
        medium_risk_keywords = [
            "modify", "update", "change", "external"
        ]

        steps_text = " ".join(execution_steps).lower()

        for keyword in high_risk_keywords:
            if keyword in steps_text:
                risk_score += 3
                risk_factors.append(f"High-risk action: {keyword}")

        for keyword in medium_risk_keywords:
            if keyword in steps_text:
                risk_score += 1
                risk_factors.append(f"Medium-risk action: {keyword}")

        # Determine risk level
        if risk_score >= 3:
            risk_level = "High"
            requires_approval = True
        elif risk_score >= 1:
            risk_level = "Medium"
            requires_approval = True
        else:
            risk_level = "Low"
            requires_approval = False

        return {
            "risk_level": risk_level,
            "risk_score": risk_score,
            "requires_approval": requires_approval,
            "risk_factors": risk_factors if risk_factors else ["No significant risk factors identified"]
        }

    def _estimate_outcome(self, task_content: str, execution_steps: List[str]) -> str:
        """Estimate expected outcome of task execution"""
        step_count = len(execution_steps)

        if step_count <= 3:
            complexity = "simple"
        elif step_count <= 6:
            complexity = "moderate"
        else:
            complexity = "complex"

        return f"Task will be completed through {step_count} steps ({complexity} complexity). Expected outcome: successful execution of all planned actions with full audit trail."

    def _generate_task_name(self, task_content: str) -> str:
        """Generate short task name from content"""
        # Take first few words, clean them up
        words = task_content.split()[:5]
        name = "_".join(words)

        # Remove special characters
        name = "".join(c if c.isalnum() or c == "_" else "_" for c in name)

        # Limit length
        if len(name) > 50:
            name = name[:50]

        return name

    def _format_plan(
        self,
        task_name: str,
        objective: str,
        required_skills: List[str],
        execution_steps: List[str],
        risk_assessment: Dict,
        approval_required: bool,
        estimated_outcome: str,
        priority: str,
        task_type: str
    ) -> str:
        """Format plan as markdown"""

        plan = f"""# Plan: {task_name}

**Created:** {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
**Priority:** {priority}
**Task Type:** {task_type}
**Status:** Pending Approval

---

## Objective

{objective}

---

## Required Skills

"""

        for skill in required_skills:
            plan += f"- {skill}\n"

        plan += "\n---\n\n## Execution Steps\n\n"

        for i, step in enumerate(execution_steps, 1):
            plan += f"{i}. {step}\n"

        plan += f"\n---\n\n## Risk Assessment\n\n"
        plan += f"**Risk Level:** {risk_assessment['risk_level']}\n"
        plan += f"**Risk Score:** {risk_assessment['risk_score']}/10\n\n"
        plan += "**Risk Factors:**\n"

        for factor in risk_assessment['risk_factors']:
            plan += f"- {factor}\n"

        plan += f"\n---\n\n## Approval Required\n\n"
        plan += f"**{'YES' if approval_required else 'NO'}**\n\n"

        if approval_required:
            plan += """**To approve this plan:**
1. Review all execution steps carefully
2. Verify risk assessment is acceptable
3. Add the line `STATUS: APPROVED` at the top of this file
4. Save the file

**To reject this plan:**
1. Add the line `STATUS: REJECTED` at the top of this file
2. Optionally add rejection reason
3. Save the file

"""

        plan += f"---\n\n## Estimated Outcome\n\n{estimated_outcome}\n\n"
        plan += "---\n\n*This plan was automatically generated by the AI Employee system.*\n"

        return plan


if __name__ == "__main__":
    # Test the planner
    vault_path = Path(__file__).parent.parent / "vault"
    planner = TaskPlanner(str(vault_path))

    test_task = """Send an email to john@example.com with subject "Project Update"
    and let him know the project is on track and will be completed by Friday."""

    result = planner.generate_plan(
        task_content=test_task,
        task_type="Request",
        priority="High"
    )

    print(json.dumps(result, indent=2))
