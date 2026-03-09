from abc import ABC, abstractmethod

class Action:
    pass

class BaseAgent(ABC):
    @abstractmethod
    def perceive(self) -> dict:
        """Observe the environment"""
        pass

    @abstractmethod
    def decide(self) -> Action:
        """Choose what to do"""
        pass

    @abstractmethod
    def act(self, action: Action):
        """Execute the action"""
        pass

    @abstractmethod
    def reflect(self) -> str:
        """Log and learn"""
        pass
