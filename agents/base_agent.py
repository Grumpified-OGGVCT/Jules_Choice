from abc import ABC, abstractmethod
from typing import Any


class Action:
    """Represents an agent action to be executed."""
    def __init__(self, name: str = "", params: dict | None = None):
        self.name = name
        self.params = params or {}


class BaseAgent(ABC):
    """
    Base class for all Jules Sandbox agents.

    Implements the Perceive → Decide → Act → Reflect loop.
    Subclasses can override individual methods or use the high-level
    execute() method which chains them together with LLM integration.
    """

    @abstractmethod
    def perceive(self) -> dict:
        """Observe the environment and return context."""
        pass

    @abstractmethod
    def decide(self) -> Action:
        """Choose what action to take based on perception."""
        pass

    @abstractmethod
    def act(self, action: Action):
        """Execute the chosen action."""
        pass

    @abstractmethod
    def reflect(self) -> str:
        """Log and learn from the action taken."""
        pass

    def execute(self, task: str, context: dict | None = None) -> dict:
        """
        High-level execution method that chains the agent loop with LLM integration.

        Override this in subclasses for agent-specific LLM-backed logic.
        Default implementation runs perceive → decide → act → reflect.

        Args:
            task: Natural language task description
            context: Optional additional context (issue body, file contents, etc.)

        Returns:
            Dict with execution results including status, output, and reflection.
        """
        perception = self.perceive()
        action = self.decide()
        self.act(action)
        reflection = self.reflect()
        return {
            "status": "completed",
            "agent": self.__class__.__name__,
            "task": task,
            "perception": perception,
            "action": action.name if hasattr(action, "name") else str(action),
            "reflection": reflection,
        }

    def _llm_generate(self, prompt: str, system: str = "", temperature: float = 0.3) -> str:
        """
        Call the OllamaDispatcher to generate an LLM response.

        Falls back to a placeholder when the LLM is unavailable.
        """
        try:
            from agents.gateway.ollama_dispatch import OllamaDispatcher, InferenceRequest

            dispatcher = OllamaDispatcher()
            result = dispatcher.generate(InferenceRequest(
                prompt=prompt,
                system=system,
                temperature=temperature,
                max_tokens=4096,
            ))
            return result.text.strip()
        except Exception:
            return f"[LLM_UNAVAILABLE] Prompt was: {prompt[:200]}"
