from __future__ import annotations
from typing import Dict, Any
from .base_agent import BaseAgent

class DebuggerAgent(BaseAgent):
    def __init__(self, ai_client=None):
        super().__init__(name="DebuggerAgent", role_key="debugger", ai_client=ai_client)

    def _create_planning_prompt(self, task: Dict[str, Any], context: Dict[str, Any], retrieved):
        return (
            "You are a debugger. Apply fixes to address the issues.\n"
            f"Task: {task.get('title')}\n"
            f"Details: {task.get('description')}\n"
            f"Relevant files (paths,score): {retrieved}\n"
            "Outline a short execution plan."
        )

    def _create_execution_prompt(self, task: Dict[str, Any], context: Dict[str, Any], plan_text: str, retrieved):
        return (
            f"Plan:\n{plan_text}\n"
            "Now produce the concrete deliverable for this role. "
            "If code, include full file content or unified diff when appropriate."
        )
