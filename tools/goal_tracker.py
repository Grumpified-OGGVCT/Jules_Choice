#!/usr/bin/env python3
"""Goal tracker for Jules_Choice."""

import os
import sys
import yaml
from dataclasses import dataclass


@dataclass
class GoalStatus:
    goal_id: str
    description: str
    priority: str
    success_criteria: str
    achieved: bool
    evidence: str = ""


def load_vision(path: str = "jules_vision.yaml") -> dict:
    if not os.path.exists(path):
        return {}
    with open(path, 'r', encoding='utf-8') as f:
        return yaml.safe_load(f) or {}


def check_goal_g001() -> GoalStatus:
    tools_dir = 'tools'
    real_tools = []
    if os.path.exists(tools_dir):
        for f in os.listdir(tools_dir):
            if f.endswith('.py') and f != '__init__.py':
                filepath = os.path.join(tools_dir, f)
                with open(filepath, 'r', encoding='utf-8') as fh:
                    content = fh.read()
                if len(content.splitlines()) > 10:
                    real_tools.append(f)
    return GoalStatus("G-001", "Create at least one real Python tool", "P0",
                      "Tool exists, has tests, runs without errors", len(real_tools) > 0,
                      f"Found {len(real_tools)} real tools: {', '.join(real_tools)}" if real_tools else "No real tools")


def check_goal_g002() -> GoalStatus:
    achieved = os.path.exists('.github/workflows/ci.yml')
    return GoalStatus("G-002", "Establish CI/CD pipeline", "P0",
                      "CI runs on push/PR", achieved,
                      "ci.yml exists" if achieved else "CI not found")


def check_goal_g003() -> GoalStatus:
    agents_dir = 'agents'
    real_agents = [f for f in os.listdir(agents_dir) if f.endswith('.py') and f not in ('__init__.py', 'base_agent.py')] if os.path.exists(agents_dir) else []
    return GoalStatus("G-003", "Build first real agent class", "P1",
                      "Agent inherits BaseAgent, implements lifecycle", len(real_agents) > 0,
                      f"Found {len(real_agents)} agents" if real_agents else "No agents")


def check_goal_g004() -> GoalStatus:
    gen_dir = 'docs/assets/generated'
    assets = [f for f in os.listdir(gen_dir) if not f.startswith('.')] if os.path.exists(gen_dir) else []
    return GoalStatus("G-004", "Generate at least one data visualization", "P1",
                      "At least one chart in docs/assets/generated/", len(assets) > 0,
                      f"Found {len(assets)} generated assets" if assets else "No visualizations yet")


def track_goals(vision_path: str = "jules_vision.yaml") -> list[GoalStatus]:
    return [check_goal_g001(), check_goal_g002(), check_goal_g003(), check_goal_g004()]


def main():
    print("Jules Goal Tracker")
    print("=" * 50)
    goals = track_goals()
    achieved = sum(1 for g in goals if g.achieved)
    print(f"\nGoals: {achieved}/{len(goals)} achieved")
    for g in goals:
        icon = 'OK' if g.achieved else 'MISSING'
        print(f"  [{icon}] [{g.priority}] {g.goal_id}: {g.description}")
        print(f"     Evidence: {g.evidence}")
    print(f"\nSprint Completion: {(achieved / len(goals) * 100):.0f}%")


if __name__ == '__main__':
    main()
