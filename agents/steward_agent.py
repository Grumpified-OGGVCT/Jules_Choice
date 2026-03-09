from .base_agent import BaseAgent, Action

class StewardAgent(BaseAgent):
    """StewardAgent based on the steward persona."""

    def perceive(self) -> dict:
        return {"context": "I am the steward"}

    def decide(self) -> Action:
        return Action()

    def act(self, action: Action):
        print(f"{self.__class__.__name__} is executing action...")

    def reflect(self) -> str:
        return "I acted as steward."
