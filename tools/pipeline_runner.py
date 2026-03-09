"""
Pipeline Runner — End-to-end autonomous HLF execution pipeline.

Closes the loop: GitHub Issue → HLF Program → Compile → Execute → Agent Output

This is the entry point for autonomous operation. It:
  1. Takes an issue title + body (or a direct task description)
  2. Selects the appropriate HLF program based on task type
  3. Compiles the program via hlfc
  4. Seeds the runtime scope with task context
  5. Executes via hlfrun (which dispatches to real agents via host functions)
  6. Collects and returns structured results

Usage:
  # As a module
  from tools.pipeline_runner import run_pipeline
  result = run_pipeline("Fix security vulnerability in auth module")

  # CLI
  python -m tools.pipeline_runner "Fix security vulnerability in auth module"
  python -m tools.pipeline_runner --issue 42  # Fetch from GitHub API
  python -m tools.pipeline_runner --dry-run "Test the pipeline"
"""

from __future__ import annotations

import argparse
import json
import os
import sys
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

# Ensure project root is importable
_PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(_PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(_PROJECT_ROOT))


@dataclass
class PipelineResult:
    """Structured result from a full pipeline execution."""
    success: bool
    task: str
    program_used: str
    compile_ok: bool = False
    execute_ok: bool = False
    agent_dispatched: str = ""
    agent_output: Any = None
    security_gate: bool | None = None
    health_score: float | None = None
    policy_passed: bool | None = None
    execution_time_ms: float = 0.0
    trace: list[dict] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)

    def to_dict(self) -> dict:
        return {
            "success": self.success,
            "task": self.task,
            "program_used": self.program_used,
            "compile_ok": self.compile_ok,
            "execute_ok": self.execute_ok,
            "agent_dispatched": self.agent_dispatched,
            "agent_output": self.agent_output,
            "security_gate": self.security_gate,
            "health_score": self.health_score,
            "policy_passed": self.policy_passed,
            "execution_time_ms": self.execution_time_ms,
            "trace_length": len(self.trace),
            "errors": self.errors,
        }

    def to_json(self, indent: int = 2) -> str:
        return json.dumps(self.to_dict(), indent=indent, default=str)


# --------------------------------------------------------------------------- #
# Program Selection
# --------------------------------------------------------------------------- #

# Maps task keywords to HLF program files
_PROGRAM_MAP = {
    "agent_dispatch": {
        "keywords": ["dispatch", "route", "assign", "delegate"],
        "file": "hlf_programs/agent_dispatch.hlf",
    },
    "decision_matrix": {
        "keywords": ["decide", "plan", "strategy", "architecture", "design", "roadmap"],
        "file": "hlf_programs/decision_matrix.hlf",
    },
    "security_audit": {
        "keywords": ["security", "audit", "vulnerability", "scan", "secret", "credential"],
        "file": "hlf_programs/security_audit.hlf",
    },
    "health_check": {
        "keywords": ["health", "metrics", "monitor", "status", "check"],
        "file": "hlf_programs/health_check.hlf",
    },
    "sprint_report": {
        "keywords": ["report", "sprint", "summary", "changelog", "release"],
        "file": "hlf_programs/sprint_report.hlf",
    },
}


def select_program(task: str) -> str:
    """
    Select the most appropriate HLF program for a task.

    Uses keyword matching against the task description.
    Falls back to agent_dispatch.hlf as the general-purpose dispatcher.

    Returns:
        Relative path to the .hlf program file.
    """
    task_lower = task.lower()
    best_match = "hlf_programs/agent_dispatch.hlf"
    best_score = 0

    for program_name, info in _PROGRAM_MAP.items():
        score = sum(1 for kw in info["keywords"] if kw in task_lower)
        if score > best_score:
            best_score = score
            best_match = info["file"]

    return best_match


# --------------------------------------------------------------------------- #
# Pipeline Execution
# --------------------------------------------------------------------------- #


def run_pipeline(
    task: str,
    dry_run: bool = False,
    tier: str = "forge",
    program: str | None = None,
) -> PipelineResult:
    """
    Execute the full autonomous pipeline.

    Args:
        task: Natural language task description (from issue title/body)
        dry_run: If True, compile and validate but don't execute agent actions
        tier: Deployment tier (hearth/forge/sovereign)
        program: Override the auto-selected program with a specific .hlf file

    Returns:
        PipelineResult with full execution details.
    """
    start_time = time.time()
    result = PipelineResult(success=False, task=task, program_used="")

    # Step 1: Select program
    program_file = program or select_program(task)
    result.program_used = program_file
    program_path = _PROJECT_ROOT / program_file

    if not program_path.exists():
        result.errors.append(f"Program file not found: {program_path}")
        result.execution_time_ms = (time.time() - start_time) * 1000
        return result

    # Step 2: Read program source
    try:
        source = program_path.read_text(encoding="utf-8")
    except Exception as exc:
        result.errors.append(f"Failed to read program: {exc}")
        result.execution_time_ms = (time.time() - start_time) * 1000
        return result

    # Step 3: Compile via hlfc
    try:
        from hlf.hlfc import compile as hlf_compile
        ast = hlf_compile(source)
        result.compile_ok = True
    except Exception as exc:
        result.errors.append(f"Compilation failed: {exc}")
        result.execution_time_ms = (time.time() - start_time) * 1000
        return result

    if dry_run:
        result.success = True
        result.execution_time_ms = (time.time() - start_time) * 1000
        return result

    # Step 4: Seed runtime scope with task context
    scope = {
        "TASK": task,
        "TASK_TYPE": select_program(task).split("/")[-1].replace(".hlf", ""),
        "TIER": tier,
        "DRY_RUN": dry_run,
        "PROJECT_ROOT": str(_PROJECT_ROOT),
    }

    # Step 5: Execute via hlfrun
    try:
        from hlf.hlfrun import HLFInterpreter
        interpreter = HLFInterpreter(scope=scope, tier=tier, max_gas=50)
        exec_result = interpreter.execute(ast)
        result.execute_ok = exec_result.get("code", -1) == 0
        result.trace = exec_result.get("trace", [])

        # Extract agent dispatch results from scope
        final_scope = exec_result.get("scope", {})

        # Look for agent-related results in the final scope
        for key, value in final_scope.items():
            if "CLASSIFY" in key:
                result.agent_dispatched = str(value)
            if "AGENT" in key and isinstance(value, str):
                try:
                    result.agent_output = json.loads(value)
                except (json.JSONDecodeError, TypeError):
                    result.agent_output = value
            if "SECURITY" in key:
                try:
                    scan_data = json.loads(value) if isinstance(value, str) else value
                    result.security_gate = scan_data.get("passed", None) if isinstance(scan_data, dict) else None
                except (json.JSONDecodeError, TypeError):
                    pass
            if "HEALTH" in key:
                try:
                    health_data = json.loads(value) if isinstance(value, str) else value
                    result.health_score = health_data.get("health_score", None) if isinstance(health_data, dict) else None
                except (json.JSONDecodeError, TypeError):
                    pass
            if "POLICY" in key:
                try:
                    policy_data = json.loads(value) if isinstance(value, str) else value
                    result.policy_passed = policy_data.get("passed", None) if isinstance(policy_data, dict) else None
                except (json.JSONDecodeError, TypeError):
                    pass

        result.success = result.execute_ok
    except Exception as exc:
        result.errors.append(f"Execution failed: {exc}")

    result.execution_time_ms = (time.time() - start_time) * 1000
    return result


def run_pipeline_from_issue(
    issue_title: str,
    issue_body: str = "",
    labels: list[str] | None = None,
    dry_run: bool = False,
) -> PipelineResult:
    """
    Run the pipeline from a GitHub issue.

    Combines issue title and body into a task description,
    uses labels to help select the right HLF program.
    """
    task = issue_title
    if issue_body:
        task = f"{issue_title}\n\n{issue_body[:500]}"

    # Use labels to force program selection
    program = None
    if labels:
        label_str = " ".join(labels).lower()
        if "security" in label_str:
            program = "hlf_programs/security_audit.hlf"
        elif "health" in label_str:
            program = "hlf_programs/health_check.hlf"
        elif "report" in label_str or "sprint" in label_str:
            program = "hlf_programs/sprint_report.hlf"

    return run_pipeline(task, dry_run=dry_run, program=program)


# --------------------------------------------------------------------------- #
# CLI Interface
# --------------------------------------------------------------------------- #


def main():
    """CLI entry point for the pipeline runner."""
    parser = argparse.ArgumentParser(
        description="HLF Autonomous Pipeline Runner",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=(
            "Examples:\n"
            '  python -m tools.pipeline_runner "Fix auth vulnerability"\n'
            '  python -m tools.pipeline_runner --dry-run "Test pipeline"\n'
            '  python -m tools.pipeline_runner --program hlf_programs/security_audit.hlf "Audit codebase"\n'
        ),
    )
    parser.add_argument("task", nargs="?", default="", help="Task description")
    parser.add_argument("--dry-run", action="store_true", help="Compile and validate only")
    parser.add_argument("--tier", default="forge", choices=["hearth", "forge", "sovereign"], help="Deployment tier")
    parser.add_argument("--program", default=None, help="Override HLF program selection")
    parser.add_argument("--json", action="store_true", help="Output as JSON")

    args = parser.parse_args()

    if not args.task:
        parser.print_help()
        print("\nError: task description required")
        sys.exit(1)

    print("=" * 60)
    print("  HLF Autonomous Pipeline Runner")
    print("=" * 60)
    print(f"  Task: {args.task[:80]}")
    print(f"  Tier: {args.tier}")
    print(f"  Mode: {'DRY RUN' if args.dry_run else 'LIVE'}")

    result = run_pipeline(
        task=args.task,
        dry_run=args.dry_run,
        tier=args.tier,
        program=args.program,
    )

    if args.json:
        print(result.to_json())
    else:
        print(f"\n  Program: {result.program_used}")
        print(f"  Compiled: {'✓' if result.compile_ok else '✗'}")
        print(f"  Executed: {'✓' if result.execute_ok else '✗'}")
        if result.agent_dispatched:
            print(f"  Agent: {result.agent_dispatched}")
        if result.security_gate is not None:
            print(f"  Security: {'PASSED' if result.security_gate else 'FAILED'}")
        if result.health_score is not None:
            print(f"  Health: {result.health_score}/100")
        if result.policy_passed is not None:
            print(f"  Policy: {'PASSED' if result.policy_passed else 'FAILED'}")
        print(f"  Time: {result.execution_time_ms:.0f}ms")
        if result.errors:
            print(f"\n  Errors:")
            for err in result.errors:
                print(f"    • {err}")
        print(f"\n  {'SUCCESS' if result.success else 'FAILED'}")
    print("=" * 60)

    sys.exit(0 if result.success else 1)


if __name__ == "__main__":
    main()
