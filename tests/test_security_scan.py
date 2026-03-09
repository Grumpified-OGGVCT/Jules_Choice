"""Tests for the security scanner."""

import os
import pytest
from tools.security_scan import (
    scan_file_for_secrets, scan_file_for_unsafe_code,
    check_dependency_pinning, scan_directory,
    SecurityFinding, ScanResults,
)


class TestScanForSecrets:
    def test_detects_potential_credential(self, temp_dir):
        """Test that the scanner detects patterns matching secret heuristics."""
        filepath = os.path.join(temp_dir, 'bad_config.py')
        # Use a clearly-fake pattern that still matches the regex
        with open(filepath, 'w') as f:
            f.write('password = "thisissuperlongandfakepassword123"\n')
        findings = scan_file_for_secrets(filepath)
        assert len(findings) >= 1
        assert findings[0].severity == 'CRITICAL'

    def test_clean_file_no_findings(self, temp_dir):
        filepath = os.path.join(temp_dir, 'clean.py')
        with open(filepath, 'w') as f:
            f.write('import os\nprint("hello")\n')
        assert len(scan_file_for_secrets(filepath)) == 0


class TestScanForUnsafeCode:
    def test_detects_eval(self, temp_dir):
        filepath = os.path.join(temp_dir, 'unsafe.py')
        with open(filepath, 'w') as f:
            f.write('result = eval(user_input)\n')
        findings = scan_file_for_unsafe_code(filepath)
        assert len(findings) >= 1 and findings[0].severity == 'HIGH'

    def test_detects_os_system(self, temp_dir):
        filepath = os.path.join(temp_dir, 'shell.py')
        with open(filepath, 'w') as f:
            f.write('os.system("ls")\n')
        findings = scan_file_for_unsafe_code(filepath)
        assert len(findings) >= 1

    def test_safe_code_no_findings(self, temp_dir):
        filepath = os.path.join(temp_dir, 'safe.py')
        with open(filepath, 'w') as f:
            f.write('import json\ndata = json.loads(input_str)\n')
        assert len(scan_file_for_unsafe_code(filepath)) == 0


class TestScanDirectory:
    def test_scans_directory(self, mock_repo):
        results = scan_directory(mock_repo)
        assert isinstance(results, ScanResults) and results.files_scanned > 0

    def test_scan_results_properties(self):
        results = ScanResults()
        results.add(SecurityFinding('CRITICAL', 'test', 'f.py', 1, 'msg'))
        results.add(SecurityFinding('HIGH', 'test', 'f.py', 2, 'msg'))
        results.add(SecurityFinding('LOW', 'test', 'f.py', 3, 'msg'))
        assert results.critical_count == 1 and results.high_count == 1 and not results.passed
