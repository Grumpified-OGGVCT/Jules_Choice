"""Shared test fixtures for Jules_Choice test suite."""

import os
import sys
import tempfile
import shutil
import pytest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))


@pytest.fixture
def project_root():
    return Path(__file__).parent.parent


@pytest.fixture
def temp_dir():
    tmpdir = tempfile.mkdtemp(prefix="jules_test_")
    yield tmpdir
    shutil.rmtree(tmpdir, ignore_errors=True)


@pytest.fixture
def mock_repo(temp_dir):
    dirs = ['agents', 'tools', 'tests', 'config', 'logs', 'docs/assets/generated', '.github/workflows']
    for d in dirs:
        os.makedirs(os.path.join(temp_dir, d), exist_ok=True)
    files = {
        'README.md': '# Test Repo\n',
        'jules_policy.yaml': 'safety_rules:\n  - Do not delete user data\nenforcement:\n  ci_pipeline_check: true\n  pre_commit_hooks: true\n  local_scan_tool: tools/security_scan.py\n  decision_log: logs/decisions.log\n  ethics_log: logs/ethics.log\n',
        'jules_vision.yaml': 'vision:\n  statement: "Test vision"\ngoals:\n  current_sprint:\n    - id: G-001\n      description: "Test goal"\n      priority: P0\n',
        '.github/workflows/ci.yml': 'name: CI\non: [push]\n',
        '.pre-commit-config.yaml': 'repos: []\n',
        'logs/decisions.log': '',
        'logs/ethics.log': '',
        'tools/security_scan.py': 'import os\n\ndef scan_directory(root="."):\n    return {"files_scanned": 0, "findings": []}\n\ndef main():\n    print("scanning...")\n\nif __name__ == "__main__":\n    main()\n',
    }
    for filepath, content in files.items():
        full_path = os.path.join(temp_dir, filepath)
        os.makedirs(os.path.dirname(full_path), exist_ok=True)
        with open(full_path, 'w', encoding='utf-8') as f:
            f.write(content)
    yield temp_dir
