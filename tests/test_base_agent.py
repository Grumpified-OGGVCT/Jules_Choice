"""Tests for the base agent lifecycle and concrete agent implementations."""

import pytest
from agents.base_agent import BaseAgent, Action
from agents import (
    StewardAgent, ArbiterAgent, CoveAgent, SentinelAgent,
    WeaverAgent, ChroniclerAgent, HeraldAgent, PaletteAgent,
    ScribeAgent, ConsolidatorAgent, OracleAgent, CatalystAgent,
    StrategistAgent, ScoutAgent,
)


class TestBaseAgent:
    def test_base_agent_cannot_be_instantiated(self):
        with pytest.raises(TypeError):
            BaseAgent()

    def test_action_class_exists(self):
        action = Action()
        assert action is not None


ALL_AGENTS = [
    StewardAgent, ArbiterAgent, CoveAgent, SentinelAgent,
    WeaverAgent, ChroniclerAgent, HeraldAgent, PaletteAgent,
    ScribeAgent, ConsolidatorAgent, OracleAgent, CatalystAgent,
    StrategistAgent, ScoutAgent,
]


@pytest.mark.parametrize("agent_class", ALL_AGENTS, ids=[a.__name__ for a in ALL_AGENTS])
class TestAgentLifecycle:
    def test_instantiation(self, agent_class):
        agent = agent_class()
        assert isinstance(agent, BaseAgent)

    def test_perceive_returns_dict(self, agent_class):
        result = agent_class().perceive()
        assert isinstance(result, dict)
        assert 'context' in result

    def test_decide_returns_action(self, agent_class):
        action = agent_class().decide()
        assert isinstance(action, Action)

    def test_act_executes(self, agent_class, capsys):
        agent = agent_class()
        agent.act(agent.decide())
        assert agent_class.__name__ in capsys.readouterr().out

    def test_reflect_returns_string(self, agent_class):
        reflection = agent_class().reflect()
        assert isinstance(reflection, str) and len(reflection) > 0

    def test_full_lifecycle(self, agent_class, capsys):
        agent = agent_class()
        assert isinstance(agent.perceive(), dict)
        assert isinstance(agent.decide(), Action)
        agent.act(agent.decide())
        assert isinstance(agent.reflect(), str)
