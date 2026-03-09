#!/usr/bin/env python3
"""Repository health checker for Jules_Choice.

Computes health metrics across the codebase:
- File counts by type
- Test coverage estimate
- Documentation completeness
- Code vs stub ratio
- Agent implementation completeness
"""

import os
import sys
import ast
import json
from pathlib import Path
from dataclasses import dataclass


@dataclass
class HealthMetrics:
    total_files: int = 0
    python_files: int = 0
    test_files: int = 0
    doc_files: int = 0
    yaml_files: int = 0
    agent_count: int = 0
    tool_count: int = 0
    total_python_lines: int = 0
    total_test_lines: int = 0
    placeholder_files: int = 0
    real_code_files: int = 0
    has_ci: bool = False
    has_readme: bool = False
    has_contributing: bool = False
    has_changelog: bool = False
    has_security: bool = False
    has_vision: bool = False
    has_policy: bool = False

    @property
    def health_score(self) -> float:
        score = 0
        if self.has_ci: score += 5
        if self.has_readme: score += 5
        if self.has_contributing: score += 3
        if self.has_changelog: score += 3
        if self.has_security: score += 4
        if self.has_vision: score += 5
        if self.has_policy: score += 5
        if self.python_files > 0:
            real_ratio = self.real_code_files / self.python_files
            score += int(real_ratio * 20)
        if self.test_files > 0:
            score += min(20, self.test_files * 4)
        score += min(15, self.agent_count * 1)
        score += min(15, self.tool_count * 3)
        return min(100, score)

    def to_dict(self) -> dict:
        return {
            "total_files": self.total_files,
            "python_files": self.python_files,
            "test_files": self.test_files,
            "doc_files": self.doc_files,
            "agent_count": self.agent_count,
            "tool_count": self.tool_count,
            "total_python_lines": self.total_python_lines,
            "total_test_lines": self.total_test_lines,
            "placeholder_files": self.placeholder_files,
            "real_code_files": self.real_code_files,
            "health_score": self.health_score,
        }


def is_placeholder_python(filepath: str) -> bool:
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read().strip()
        if not content or content in ('pass', '# placeholder', '# TODO'):
            return True
        tree = ast.parse(content)
        for node in ast.walk(tree):
            if isinstance(node, ast.Assert):
                if isinstance(node.test, ast.Constant) and node.test.value is True:
                    return True
        return len(content.splitlines()) < 3
    except (SyntaxError, OSError):
        return True


def count_lines(filepath: str) -> int:
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        return sum(1 for line in lines if line.strip() and not line.strip().startswith('#'))
    except (OSError, UnicodeDecodeError):
        return 0


def compute_health(root: str = ".") -> HealthMetrics:
    metrics = HealthMetrics()
    skip_dirs = {'.git', '__pycache__', '.pytest_cache', 'node_modules', '.venv', 'venv', '.mypy_cache'}
    metrics.has_ci = os.path.exists(os.path.join(root, '.github/workflows/ci.yml'))
    metrics.has_readme = os.path.exists(os.path.join(root, 'README.md'))
    metrics.has_contributing = os.path.exists(os.path.join(root, 'CONTRIBUTING.md'))
    metrics.has_changelog = os.path.exists(os.path.join(root, 'CHANGELOG.md'))
    metrics.has_security = os.path.exists(os.path.join(root, 'SECURITY.md'))
    metrics.has_vision = os.path.exists(os.path.join(root, 'jules_vision.yaml'))
    metrics.has_policy = os.path.exists(os.path.join(root, 'jules_policy.yaml'))
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = [d for d in dirnames if d not in skip_dirs]
        for filename in filenames:
            filepath = os.path.join(dirpath, filename)
            metrics.total_files += 1
            ext = Path(filename).suffix
            if ext == '.py':
                metrics.python_files += 1
                lines = count_lines(filepath)
                metrics.total_python_lines += lines
                if 'tests/' in filepath or 'test_' in filename:
                    metrics.test_files += 1
                    metrics.total_test_lines += lines
                elif 'agents/' in filepath and filename not in ('__init__.py',):
                    metrics.agent_count += 1
                elif 'tools/' in filepath:
                    metrics.tool_count += 1
                if is_placeholder_python(filepath):
                    metrics.placeholder_files += 1
                else:
                    metrics.real_code_files += 1
            elif ext in ('.md', '.rst', '.txt'):
                metrics.doc_files += 1
            elif ext in ('.yaml', '.yml'):
                metrics.yaml_files += 1
    return metrics


def main():
    print("Jules Repository Health Check")
    print("=" * 50)
    root = sys.argv[1] if len(sys.argv) > 1 else "."
    metrics = compute_health(root)
    print(f"\nOverall Health Score: {metrics.health_score}/100")
    print(f"\nFiles: {metrics.total_files}")
    print(f"  Python: {metrics.python_files} ({metrics.real_code_files} real, {metrics.placeholder_files} placeholders)")
    print(f"  Tests: {metrics.test_files}")
    print(f"  Docs: {metrics.doc_files}")
    print(f"  Agents: {metrics.agent_count}")
    print(f"  Tools: {metrics.tool_count}")
    checks = {
        'CI Pipeline': metrics.has_ci, 'README': metrics.has_readme,
        'CONTRIBUTING': metrics.has_contributing, 'CHANGELOG': metrics.has_changelog,
        'SECURITY': metrics.has_security, 'Vision': metrics.has_vision, 'Policy': metrics.has_policy,
    }
    for name, status in checks.items():
        print(f"  {'OK' if status else 'MISSING'} {name}")
    if '--json' in sys.argv:
        print(f"\n{json.dumps(metrics.to_dict(), indent=2)}")


if __name__ == '__main__':
    main()
