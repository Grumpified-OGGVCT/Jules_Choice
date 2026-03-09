from .base_agent import BaseAgent, Action

class StrategistAgent(BaseAgent):
    """StrategistAgent based on the strategist persona."""

    def perceive(self) -> dict:
        return {"context": "I am the strategist"}

    def decide(self) -> Action:
        return Action()

    def act(self, action: Action):
        print(f"{self.__class__.__name__} is executing action...")

    def reflect(self) -> str:
        return "I acted as strategist."
