"""
StrategistAgent — Planning and architecture agent for the Jules Sandbox.

Generates implementation plans, architecture decisions, and roadmaps
using LLM inference via OllamaDispatcher. Outputs structured plans
that can be consumed by the ScribeAgent for code generation.
"""

from .base_agent import BaseAgent, Action


class StrategistAgent(BaseAgent):
    """Planning agent that designs architecture and creates implementation plans."""

    def __init__(self):
        self._context = {}
        self._plan = ""

    def perceive(self) -> dict:
        """Gather architectural context from the environment."""
        import os
        context = {
            "cwd": os.getcwd(),
            "has_readme": os.path.exists("README.md"),
            "has_vision": os.path.exists("jules_vision.yaml"),
            "has_policy": os.path.exists("jules_policy.yaml"),
            "directories": [],
        }
        # Scan top-level directory structure
        try:
            for entry in os.listdir("."):
                if not entry.startswith(".") and os.path.isdir(entry):
                    context["directories"].append(entry)
        except OSError:
            pass
        context["context"] = True
        self._context = context
        return context

    def decide(self) -> Action:
        """Decide what planning action to take."""
        return Action(name="strategic_planning", params=self._context)

    def act(self, action: Action):
        """Execute the planning action (stub for base loop)."""
        self._plan = f"StrategistAgent planned {action.name}"
        print("StrategistAgent")

    def reflect(self) -> str:
        """Summarize the plan."""
        return self._plan if self._plan else "No plan generated."

    def execute(self, task: str, context: dict | None = None) -> dict:
        """
        LLM-backed strategic planning.

        Takes a task description and generates an implementation plan
        with architecture decisions, file changes, and risk assessment.
        """
        perception = self.perceive()
        dir_list = ", ".join(perception.get("directories", []))

        # Generate implementation plan via LLM
        plan = self._llm_generate(
            prompt=(
                f"Task: {task}\n\n"
                f"Project structure: {dir_list}\n"
                f"Has README: {perception.get('has_readme')}\n"
                f"Has Vision: {perception.get('has_vision')}\n\n"
                "Create a detailed implementation plan with:\n"
                "1. **Goal**: What this achieves\n"
                "2. **Components**: Which files/modules to create or modify\n"
                "3. **Dependencies**: What needs to be in place first\n"
                "4. **Implementation Steps**: Ordered, specific steps\n"
                "5. **Risks**: Potential issues and mitigations\n"
                "6. **Testing**: How to verify the implementation\n"
                "Keep response under 500 words."
            ),
            system=(
                "You are the Strategist agent for the Sovereign Agentic OS. "
                "You create detailed, actionable implementation plans for Python projects. "
                "Be specific about file paths, function signatures, and integration points. "
                "Follow the VGII (Vision, Goals, Instincts, Intentions) framework."
            ),
        )

        # Generate RICE score for prioritization
        rice = self._llm_generate(
            prompt=(
                f"Task: {task}\n\n"
                "Score this task using the RICE framework (1-10 each):\n"
                "- Reach: How many components/users does this affect?\n"
                "- Impact: How significant is the change?\n"
                "- Confidence: How certain are we about the approach?\n"
                "- Effort: How much work is required? (lower = better)\n"
                "Respond in format: R:X I:X C:X E:X Total:XX"
            ),
            system="You are a project prioritization system. Be concise.",
            temperature=0.2,
        )

        return {
            "status": "completed",
            "agent": "StrategistAgent",
            "task": task,
            "plan": plan,
            "rice_score": rice,
            "project_context": {
                "directories": perception.get("directories", []),
            },
            "reflection": f"Created implementation plan for: {task[:80]}",
        }
