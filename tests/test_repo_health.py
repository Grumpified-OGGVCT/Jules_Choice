"""Tests for the repository health checker."""

import os
from tools.repo_health import compute_health, count_lines, is_placeholder_python, HealthMetrics


class TestCountLines:
    def test_counts_non_empty_lines(self, temp_dir):
        filepath = os.path.join(temp_dir, 'test.py')
        with open(filepath, 'w') as f:
            f.write('import os\n\n# comment\ndef foo():\n    pass\n')
        assert count_lines(filepath) == 3

    def test_returns_zero_for_missing_file(self):
        assert count_lines('/nonexistent/file.py') == 0


class TestIsPlaceholder:
    def test_detects_empty_file(self, temp_dir):
        filepath = os.path.join(temp_dir, 'empty.py')
        with open(filepath, 'w') as f:
            f.write('')
        assert is_placeholder_python(filepath) is True

    def test_real_code_not_placeholder(self, temp_dir):
        filepath = os.path.join(temp_dir, 'real.py')
        with open(filepath, 'w') as f:
            f.write('import os\nimport sys\n\ndef main():\n    print("hello")\n    return 0\n\nif __name__ == "__main__":\n    main()\n')
        assert is_placeholder_python(filepath) is False


class TestComputeHealth:
    def test_computes_metrics_on_mock_repo(self, mock_repo):
        metrics = compute_health(mock_repo)
        assert isinstance(metrics, HealthMetrics)
        assert metrics.has_ci and metrics.has_readme and metrics.has_policy

    def test_health_score_range(self, mock_repo):
        assert 0 <= compute_health(mock_repo).health_score <= 100

    def test_to_dict(self, mock_repo):
        d = compute_health(mock_repo).to_dict()
        assert isinstance(d, dict) and 'health_score' in d
