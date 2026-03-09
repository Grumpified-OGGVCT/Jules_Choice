#!/usr/bin/env python3
"""Policy compliance checker for Jules_Choice.

Reads jules_policy.yaml and validates the current repo state
against defined safety and security rules.
"""

import os
import sys
import yaml
from dataclasses import dataclass, field


@dataclass
class PolicyViolation:
    rule: str
    description: str
    severity: str = "WARNING"


@dataclass
class PolicyCheckResult:
    violations: list = field(default_factory=list)
    checks_run: int = 0
    passed: bool = True

    def add_violation(self, violation: PolicyViolation):
        self.violations.append(violation)
        self.passed = False


def load_policy(path: str = "jules_policy.yaml") -> dict:
    """Load the policy configuration."""
    if not os.path.exists(path):
        return {}
    with open(path, 'r', encoding='utf-8') as f:
        return yaml.safe_load(f) or {}


def check_log_files_exist(policy: dict) -> list[PolicyViolation]:
    """Check that required log files exist."""
    violations = []
    enforcement = policy.get('enforcement', {})
    for key in ['decision_log', 'ethics_log']:
        log_path = enforcement.get(key)
        if log_path and not os.path.exists(log_path):
            violations.append(PolicyViolation(
                rule=key,
                description=f"Required log file missing: {log_path}",
                severity="MEDIUM"
            ))
    return violations


def check_ci_pipeline_exists(policy: dict) -> list[PolicyViolation]:
    """Verify CI pipeline is configured."""
    violations = []
    if policy.get('enforcement', {}).get('ci_pipeline_check', False):
        if not os.path.exists('.github/workflows/ci.yml'):
            violations.append(PolicyViolation(
                rule='ci_pipeline_check',
                description="CI pipeline required but .github/workflows/ci.yml not found",
                severity="HIGH"
            ))
    return violations


def check_pre_commit_hooks(policy: dict) -> list[PolicyViolation]:
    """Verify pre-commit hooks are configured."""
    violations = []
    if policy.get('enforcement', {}).get('pre_commit_hooks', False):
        if not os.path.exists('.pre-commit-config.yaml'):
            violations.append(PolicyViolation(
                rule='pre_commit_hooks',
                description="Pre-commit required but .pre-commit-config.yaml not found",
                severity="MEDIUM"
            ))
    return violations


def check_security_scan_tool(policy: dict) -> list[PolicyViolation]:
    """Verify the security scan tool exists."""
    violations = []
    scan_tool = policy.get('enforcement', {}).get('local_scan_tool')
    if scan_tool and not os.path.exists(scan_tool):
        violations.append(PolicyViolation(
            rule='local_scan_tool',
            description=f"Security scan tool missing: {scan_tool}",
            severity="HIGH"
        ))
    return violations


def run_policy_check(policy_path: str = "jules_policy.yaml") -> PolicyCheckResult:
    """Run all policy checks."""
    result = PolicyCheckResult()
    policy = load_policy(policy_path)
    if not policy:
        return result
    checkers = [
        check_log_files_exist,
        check_ci_pipeline_exists,
        check_pre_commit_hooks,
        check_security_scan_tool,
    ]
    for checker in checkers:
        result.checks_run += 1
        for violation in checker(policy):
            result.add_violation(violation)
    return result


def main():
    """Run policy check and print results."""
    print("Jules Policy Checker")
    print("=" * 50)
    policy_path = sys.argv[1] if len(sys.argv) > 1 else "jules_policy.yaml"
    result = run_policy_check(policy_path)
    print(f"\nChecks run: {result.checks_run}")
    print(f"Violations: {len(result.violations)}")
    if result.violations:
        for v in result.violations:
            print(f"  [{v.severity}] {v.rule}: {v.description}")
    if result.passed:
        print("\nPASSED -- All policy checks satisfied.")
    else:
        print("\nFAILED -- Policy violations detected.")
        sys.exit(1)


if __name__ == "__main__":
    main()
