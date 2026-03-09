from .base_agent import BaseAgent, Action

class CoveAgent(BaseAgent):
    """CoveAgent based on the cove persona."""

    def perceive(self) -> dict:
        return {"context": "I am the cove"}

    def decide(self) -> Action:
        return Action()

    def act(self, action: Action):
        print(f"{self.__class__.__name__} is executing action...")

    def reflect(self) -> str:
        return "I acted as cove."
