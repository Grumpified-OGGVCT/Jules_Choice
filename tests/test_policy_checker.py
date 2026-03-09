"""Tests for the policy compliance checker."""

import os
import pytest
from tools.policy_checker import (
    load_policy, check_log_files_exist, check_ci_pipeline_exists,
    check_pre_commit_hooks, check_security_scan_tool, run_policy_check,
)


class TestLoadPolicy:
    def test_loads_valid_yaml(self, mock_repo):
        result = load_policy(os.path.join(mock_repo, 'jules_policy.yaml'))
        assert isinstance(result, dict)
        assert 'safety_rules' in result

    def test_returns_empty_for_missing_file(self):
        assert load_policy('/nonexistent/path.yaml') == {}


class TestCheckLogFiles:
    def test_passes_when_logs_exist(self, mock_repo):
        policy = load_policy(os.path.join(mock_repo, 'jules_policy.yaml'))
        old_cwd = os.getcwd()
        os.chdir(mock_repo)
        try:
            assert len(check_log_files_exist(policy)) == 0
        finally:
            os.chdir(old_cwd)

    def test_fails_when_logs_missing(self, temp_dir):
        policy = {'enforcement': {'decision_log': 'logs/decisions.log', 'ethics_log': 'logs/ethics.log'}}
        old_cwd = os.getcwd()
        os.chdir(temp_dir)
        try:
            assert len(check_log_files_exist(policy)) == 2
        finally:
            os.chdir(old_cwd)


class TestCheckCIPipeline:
    def test_passes_when_ci_exists(self, mock_repo):
        old_cwd = os.getcwd()
        os.chdir(mock_repo)
        try:
            assert len(check_ci_pipeline_exists({'enforcement': {'ci_pipeline_check': True}})) == 0
        finally:
            os.chdir(old_cwd)

    def test_fails_when_ci_missing(self, temp_dir):
        old_cwd = os.getcwd()
        os.chdir(temp_dir)
        try:
            violations = check_ci_pipeline_exists({'enforcement': {'ci_pipeline_check': True}})
            assert len(violations) == 1 and violations[0].severity == 'HIGH'
        finally:
            os.chdir(old_cwd)


class TestRunPolicyCheck:
    def test_full_check_passes_on_complete_repo(self, mock_repo):
        old_cwd = os.getcwd()
        os.chdir(mock_repo)
        try:
            result = run_policy_check(os.path.join(mock_repo, 'jules_policy.yaml'))
            assert result.checks_run >= 3 and result.passed is True
        finally:
            os.chdir(old_cwd)
