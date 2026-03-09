"""
ScribeAgent — Code generation agent for the Jules Sandbox.

The primary coding agent: takes task descriptions and generates Python code,
refactors existing code, and creates implementation plans using LLM inference
via OllamaDispatcher.
"""

from .base_agent import BaseAgent, Action


class ScribeAgent(BaseAgent):
    """Code generation agent that writes, refactors, and fixes code via LLM."""

    def __init__(self):
        self._context = {}
        self._output = ""

    def perceive(self) -> dict:
        """Gather code-relevant context from the environment."""
        import os
        context = {
            "cwd": os.getcwd(),
            "python_files": [],
        }
        # Quick scan for relevant files
        for root, dirs, files in os.walk(".", topdown=True):
            dirs[:] = [d for d in dirs if d not in {".git", "__pycache__", ".venv", "node_modules"}]
            for f in files:
                if f.endswith(".py"):
                    context["python_files"].append(os.path.join(root, f))
            if len(context["python_files"]) > 50:
                break
        self._context = context
        return context

    def decide(self) -> Action:
        """Decide what code action to take."""
        return Action(name="code_generation", params=self._context)

    def act(self, action: Action):
        """Execute the code action (stub for base loop)."""
        self._output = f"ScribeAgent executed {action.name}"

    def reflect(self) -> str:
        """Summarize what was generated."""
        return self._output if self._output else "No code generated."

    def execute(self, task: str, context: dict | None = None) -> dict:
        """
        LLM-backed code generation.

        Takes a task description and generates code using the configured
        LLM via OllamaDispatcher. Returns structured output with the
        generated code and implementation notes.
        """
        # Gather context
        perception = self.perceive()
        file_list = "\n".join(perception.get("python_files", [])[:20])

        # Generate code via LLM
        code_output = self._llm_generate(
            prompt=(
                f"Task: {task}\n\n"
                f"Project files (first 20):\n{file_list}\n\n"
                "Generate the Python code to accomplish this task. Include:\n"
                "1. Complete, runnable Python code\n"
                "2. Docstrings and type hints\n"
                "3. Any necessary imports\n"
                "Format your response as a single Python code block."
            ),
            system=(
                "You are the Scribe agent for the Sovereign Agentic OS. "
                "You write clean, production-quality Python code following "
                "the project's conventions: type hints, docstrings, dataclasses, "
                "and structured error handling. Never use placeholder stubs."
            ),
        )

        # Generate implementation notes
        notes = self._llm_generate(
            prompt=(
                f"Task: {task}\n\n"
                f"Generated code summary (first 200 chars): {code_output[:200]}\n\n"
                "Provide a brief (3-5 bullet points) implementation summary:\n"
                "- What was created/modified\n"
                "- Key design decisions\n"
                "- Testing recommendations"
            ),
            system="You are a code reviewer providing concise implementation notes.",
            temperature=0.2,
        )

        return {
            "status": "completed",
            "agent": "ScribeAgent",
            "task": task,
            "code": code_output,
            "notes": notes,
            "files_context": len(perception.get("python_files", [])),
            "reflection": f"Generated code for: {task[:80]}",
        }
