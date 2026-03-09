from .base_agent import BaseAgent, Action

class ConsolidatorAgent(BaseAgent):
    """ConsolidatorAgent based on the consolidator persona."""

    def perceive(self) -> dict:
        return {"context": "I am the consolidator"}

    def decide(self) -> Action:
        return Action()

    def act(self, action: Action):
        print(f"{self.__class__.__name__} is executing action...")

    def reflect(self) -> str:
        return "I acted as consolidator."
