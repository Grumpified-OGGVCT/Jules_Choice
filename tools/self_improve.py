#!/usr/bin/env python3
"""Self-improvement engine for Jules_Choice.

Reads jules_self_improvement.yaml and evaluates improvement triggers,
then logs actions and recommendations.
"""

import os
import sys
import json
import yaml
from datetime import datetime
from pathlib import Path


def load_config(path: str = "jules_self_improvement.yaml") -> dict:
    """Load the self-improvement configuration."""
    if not os.path.exists(path):
        return {}
    with open(path, 'r', encoding='utf-8') as f:
        return yaml.safe_load(f) or {}


def get_current_metrics() -> dict:
    """Collect current metrics from the repo."""
    metrics = {}
    try:
        from tools.repo_health import compute_health
        health = compute_health('.')
        metrics['health_score'] = health.health_score
        metrics['test_count'] = health.test_files
        metrics['tool_count'] = health.tool_count
        metrics['agent_count'] = health.agent_count
        metrics['placeholder_ratio'] = (
            health.placeholder_files / health.python_files
            if health.python_files > 0 else 0
        )
        metrics['real_code_files'] = health.real_code_files
    except ImportError:
        metrics['health_score'] = 0
        metrics['placeholder_ratio'] = 1.0

    try:
        from tools.goal_tracker import track_goals
        goals = track_goals()
        achieved = sum(1 for g in goals if g.achieved)
        metrics['goal_completion'] = achieved / len(goals) if goals else 0
    except ImportError:
        metrics['goal_completion'] = 0

    return metrics


def evaluate_triggers(config: dict, metrics: dict) -> list[dict]:
    """Evaluate improvement triggers against current metrics."""
    triggered = []
    for action_def in config.get('improvement_actions', []):
        trigger = action_def.get('trigger', '')
        # Simple trigger evaluation
        if 'health_score < 50' in trigger and metrics.get('health_score', 0) < 50:
            triggered.append(action_def)
        elif 'placeholder_ratio > 0.2' in trigger and metrics.get('placeholder_ratio', 0) > 0.2:
            triggered.append(action_def)
        elif 'test_count_delta < 5' in trigger and metrics.get('test_count', 0) < 5:
            triggered.append(action_def)
        elif 'goal_completion < 50%' in trigger and metrics.get('goal_completion', 0) < 0.5:
            triggered.append(action_def)
    return triggered


def log_improvement(metrics: dict, triggered_actions: list, log_path: str = "logs/self_improvement.log"):
    """Log improvement evaluation results."""
    os.makedirs(os.path.dirname(log_path), exist_ok=True)
    timestamp = datetime.now().isoformat()
    with open(log_path, 'a', encoding='utf-8') as f:
        f.write(f"\n{'=' * 60}\n")
        f.write(f"Self-Improvement Evaluation: {timestamp}\n")
        f.write(f"{'=' * 60}\n")
        for key, value in metrics.items():
            f.write(f"  {key}: {value}\n")
        if triggered_actions:
            f.write(f"\nTriggered Actions:\n")
            for action in triggered_actions:
                f.write(f"  [{action.get('priority', '?')}] {action.get('action', '?')}\n")
        else:
            f.write(f"\nNo improvement actions triggered. All metrics within targets.\n")


def main():
    """Run self-improvement evaluation."""
    print("Jules Self-Improvement Engine")
    print("=" * 50)

    config = load_config()
    if not config:
        print("No self-improvement config found.")
        sys.exit(1)

    metrics = get_current_metrics()
    print(f"\nCurrent Metrics:")
    for key, value in metrics.items():
        if isinstance(value, float):
            print(f"  {key}: {value:.2f}")
        else:
            print(f"  {key}: {value}")

    triggered = evaluate_triggers(config, metrics)
    if triggered:
        print(f"\nTriggered Actions ({len(triggered)}):")
        for action in triggered:
            print(f"  [{action.get('priority', '?')}] {action.get('action', '?')}")
    else:
        print(f"\nAll metrics within targets. No actions needed.")

    log_improvement(metrics, triggered)
    print(f"\nLogged to logs/self_improvement.log")


if __name__ == '__main__':
    main()
