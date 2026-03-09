"""
Tests for HLF Runner — validates the full toolchain integration.

Tests the hlf_runner.py tool against real HLF source code,
verifying compile, lint, validate, generate, format, and correct operations.
"""

import sys
from pathlib import Path

import pytest

# Ensure project root is in path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from tools.hlf_runner import (
    HLFResult,
    compile_hlf,
    correct,
    format_source,
    generate,
    lint_hlf,
    translate,
    validate,
)

# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

MINIMAL_HLF = """\
[HLF-v2]
[INTENT] "test"
[RESULT] 0 "ok"
Ω
"""

ADVANCED_HLF = """\
[HLF-v3]
[SET] target = "/deploy/prod"
[INTENT] "deploy" "${target}"
[CONSTRAINT] "timeout" "30s"
[THOUGHT] "Deploying to production"
[OBSERVATION] "Deployment initiated"
[RESULT] 0 "deploy_complete"
Ω
"""

V4_MACRO_HLF = """\
[HLF-v4]
[SET] scope = "full"
Σ [DEFINE] health_check
  [INTENT] "check_health"
  [RESULT] 0 "healthy"
[CALL] health_check
Ω
"""

BROKEN_HLF_MISSING_HEADER = """\
[INTENT] "test"
[RESULT] 0 "ok"
Ω
"""

BROKEN_HLF_MISSING_TERMINATOR = """\
[HLF-v2]
[INTENT] "test"
[RESULT] 0 "ok"
"""

BROKEN_HLF_BAD_TAG = """\
[HLF-v2]
[INTNET] "typo in tag"
[RESULT] 0 "ok"
Ω
"""

# ---------------------------------------------------------------------------
# Compile Tests
# ---------------------------------------------------------------------------

class TestCompile:
    """Test HLF compilation through the LALR(1) pipeline."""

    def test_compile_minimal_program(self):
        result = compile_hlf(MINIMAL_HLF)
        assert result.success is True
        assert result.operation == "compile"
        assert result.output is not None
        assert "program" in result.output
        assert result.metadata["node_count"] > 0

    def test_compile_advanced_program(self):
        result = compile_hlf(ADVANCED_HLF)
        assert result.success is True
        assert result.metadata["node_count"] >= 5

    def test_compile_returns_ast_dict(self):
        result = compile_hlf(MINIMAL_HLF)
        assert isinstance(result.output, dict)
        assert isinstance(result.output.get("program"), list)

    def test_compile_failure_returns_errors(self):
        result = compile_hlf("this is not HLF at all")
        assert result.success is False
        assert len(result.errors) > 0

    def test_compile_empty_source(self):
        result = compile_hlf("")
        assert result.success is False


# ---------------------------------------------------------------------------
# Lint Tests
# ---------------------------------------------------------------------------

class TestLint:
    """Test HLF static analysis."""

    def test_lint_clean_program(self):
        result = lint_hlf(MINIMAL_HLF, max_gas=50)
        assert result.success is True
        assert result.operation == "lint"
        assert len(result.output) == 0

    def test_lint_detects_gas_overflow(self):
        result = lint_hlf(ADVANCED_HLF, max_gas=2)
        assert result.success is False
        assert any("GAS" in d for d in result.output)

    def test_lint_returns_diagnostics_list(self):
        result = lint_hlf(MINIMAL_HLF, max_gas=100)
        assert isinstance(result.output, list)


# ---------------------------------------------------------------------------
# Validate Tests
# ---------------------------------------------------------------------------

class TestValidate:
    """Test structural validation."""

    def test_validate_valid_program(self):
        result = validate(MINIMAL_HLF)
        assert result.success is True
        assert result.output["heuristic_valid"] is True

    def test_validate_missing_header(self):
        result = validate(BROKEN_HLF_MISSING_HEADER)
        assert result.output["heuristic_valid"] is False

    def test_validate_missing_terminator(self):
        result = validate(BROKEN_HLF_MISSING_TERMINATOR)
        assert result.output["heuristic_valid"] is False


# ---------------------------------------------------------------------------
# Generate Tests
# ---------------------------------------------------------------------------

class TestGenerate:
    """Test programmatic HLF code generation."""

    def test_generate_simple_program(self):
        steps = [
            {"type": "set", "name": "x", "value": "hello"},
            {"type": "intent", "action": "greet", "target": "${x}"},
            {"type": "result", "code": 0, "message": "done"},
        ]
        result = generate(steps)
        assert result.success is True
        assert "[HLF-v2]" in result.output
        assert "Ω" in result.output
        assert "[SET]" in result.output
        assert "[INTENT]" in result.output

    def test_generate_with_tools(self):
        steps = [
            {"type": "intent", "action": "scan"},
            {"type": "tool", "tool_name": "security_scan", "args": ["target"]},
            {"type": "result", "code": 0, "message": "scanned"},
        ]
        result = generate(steps)
        assert result.success is True
        assert "τ(security_scan)" in result.output

    def test_generate_with_memory(self):
        steps = [
            {"type": "memory", "entity": "log", "content": "test entry", "confidence": 0.9},
            {"type": "recall", "entity": "log", "top_k": 3},
            {"type": "result", "code": 0, "message": "ok"},
        ]
        result = generate(steps)
        assert result.success is True
        assert "[MEMORY]" in result.output
        assert "[RECALL]" in result.output

    def test_generate_with_delegation(self):
        steps = [
            {"type": "delegate", "role": "sentinel", "intent": "audit"},
            {"type": "result", "code": 0, "message": "delegated"},
        ]
        result = generate(steps)
        assert result.success is True
        assert "[DELEGATE]" in result.output

    def test_generate_unknown_type_fails(self):
        steps = [{"type": "nonexistent_type"}]
        result = generate(steps)
        assert result.success is False

    def test_generate_empty_steps(self):
        result = generate([])
        assert result.success is True
        assert "[HLF-v2]" in result.output
        assert "Ω" in result.output


# ---------------------------------------------------------------------------
# Format Tests
# ---------------------------------------------------------------------------

class TestFormat:
    """Test canonical formatting."""

    def test_format_preserves_structure(self):
        result = format_source(MINIMAL_HLF)
        assert result.success is True
        assert "Ω" in result.output

    def test_format_normalizes_output(self):
        result = format_source(MINIMAL_HLF)
        assert result.output.endswith("\n")


# ---------------------------------------------------------------------------
# Correct Tests
# ---------------------------------------------------------------------------

class TestCorrect:
    """Test error correction and auto-healing."""

    def test_correct_valid_program(self):
        result = correct(MINIMAL_HLF)
        assert result.success is True
        assert result.output["diagnosis"] is not None

    def test_correct_missing_header(self):
        result = correct(BROKEN_HLF_MISSING_HEADER)
        assert result.output is not None
        assert "diagnosis" in result.output

    def test_correct_missing_terminator(self):
        result = correct(BROKEN_HLF_MISSING_TERMINATOR)
        assert result.output is not None
        assert "diagnosis" in result.output


# ---------------------------------------------------------------------------
# Translate Tests
# ---------------------------------------------------------------------------

class TestTranslate:
    """Test InsAIts HLF ↔ English translation."""

    def test_translate_to_english(self):
        result = translate(MINIMAL_HLF)
        assert result.success is True
        assert isinstance(result.output, str)
        assert len(result.output) > 0

    def test_translate_advanced_program(self):
        result = translate(ADVANCED_HLF)
        assert result.success is True
        assert result.metadata["direction"] == "hlf_to_english"


# ---------------------------------------------------------------------------
# HLFResult Tests
# ---------------------------------------------------------------------------

class TestHLFResult:
    """Test the structured result dataclass."""

    def test_result_to_dict(self):
        result = HLFResult(success=True, operation="test", output="data")
        d = result.to_dict()
        assert d["success"] is True
        assert d["operation"] == "test"
        assert d["output"] == "data"

    def test_result_default_fields(self):
        result = HLFResult(success=False, operation="fail")
        assert result.errors == []
        assert result.warnings == []
        assert result.metadata == {}


# ---------------------------------------------------------------------------
# Program File Tests
# ---------------------------------------------------------------------------

class TestProgramFiles:
    """Test that all HLF program files in hlf_programs/ are valid."""

    @pytest.fixture
    def hlf_programs_dir(self):
        return PROJECT_ROOT / "hlf_programs"

    def test_programs_directory_exists(self, hlf_programs_dir):
        assert hlf_programs_dir.exists(), "hlf_programs/ directory must exist"

    def test_all_programs_compile(self, hlf_programs_dir):
        if not hlf_programs_dir.exists():
            pytest.skip("hlf_programs/ not found")
        for hlf_file in hlf_programs_dir.glob("*.hlf"):
            source = hlf_file.read_text(encoding="utf-8")
            result = compile_hlf(source)
            assert result.success, f"{hlf_file.name} failed to compile: {result.errors}"

    def test_all_programs_validate(self, hlf_programs_dir):
        if not hlf_programs_dir.exists():
            pytest.skip("hlf_programs/ not found")
        for hlf_file in hlf_programs_dir.glob("*.hlf"):
            source = hlf_file.read_text(encoding="utf-8")
            result = validate(source)
            assert result.output["heuristic_valid"], f"{hlf_file.name} failed validation"
