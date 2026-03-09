"""
HLF Runner — Full-stack toolchain wrapper for Jules agents.

Provides a unified interface to the HLF v3.0 toolchain:
  - compile_hlf()       → Parse source through LALR(1) compiler
  - lint_hlf()          → Static analysis (gas, tokens, unused vars)
  - run_hlf()           → Execute via AST interpreter
  - bytecode_compile()  → Compile to .hlbc binary
  - decompile()         → Disassemble bytecode to human-readable trace
  - translate()         → InsAIts HLF ↔ English round-trip
  - correct()           → Auto-heal broken HLF source
  - generate()          → Programmatic HLF authoring via CodeGenerator
  - format_hlf()        → Canonical pretty-print

This is not a stub. Every function wraps real toolchain components from
the hlf/ package ported from Sovereign_Agentic_OS_with_HLF.
"""

from __future__ import annotations

import json
import sys
import traceback
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

# Add project root to path for hlf imports
_PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(_PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(_PROJECT_ROOT))


@dataclass
class HLFResult:
    """Structured result from any HLF operation."""
    success: bool
    operation: str
    output: Any = None
    errors: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "success": self.success,
            "operation": self.operation,
            "output": self.output,
            "errors": self.errors,
            "warnings": self.warnings,
            "metadata": self.metadata,
        }


def chaos_to_hlf(source: str, backend: str = "openrouter") -> str:
    """Compile chaotic natural language into valid HLF AST using an AI backend."""
    try:
        import asyncio
        from agents.gateway.ollama_dispatch import get_dispatcher, InferenceRequest
    except ImportError:
        raise RuntimeError("Cannot load dispatcher for chaos compilation.")

    prompt = f"Structure this chaos to HLF:\n\n{source}\n\nRespond ONLY with valid HLF source code starting with [HLF-v3] and ending with Ω."
    req = InferenceRequest(
        prompt=prompt,
        model="qwen:7b",
        system="You are an expert HLF compiler translating raw text into valid HLF syntax.",
        metadata={"provider": backend}
    )
    dispatcher = get_dispatcher()
    try:
        result = asyncio.run(dispatcher.generate(req))
        return result.text
    except Exception as e:
        raise RuntimeError(f"AI Compilation Failed: {e}")

def compile_hlf(source: str) -> HLFResult:
    """Compile HLF source through the full LALR(1) pipeline.

    Runs the 4-pass compiler:
      1. Syntax Analysis — validates structure + glyph modifiers
      2. Semantic Analysis — collects constant pools + variable scopes
      3. AST Transformation — flattens to linear instruction sequence
      4. Code Generation — produces compiled AST dict

    Args:
        source: HLF source text (must include [HLF-v2/v3/v4] header and Ω terminator)

    Returns:
        HLFResult with compiled AST in output, or errors if compilation failed.
    """
    try:
        # Handle chaos-to-HLF if missing standard header
        if not source.lstrip().startswith("[HLF-"):
            source = chaos_to_hlf(source)
        from hlf.hlfc import compile as hlfc_compile
        ast = hlfc_compile(source)
        node_count = len(ast.get("program", []))
        return HLFResult(
            success=True,
            operation="compile",
            output=ast,
            metadata={
                "node_count": node_count,
                "version": ast.get("version", "unknown"),
            },
        )
    except Exception as e:
        return HLFResult(
            success=False,
            operation="compile",
            errors=[str(e)],
            metadata={"traceback": traceback.format_exc()},
        )


def lint_hlf(source: str, max_gas: int | None = None) -> HLFResult:
    """Run static analysis on HLF source.

    Checks:
      - Token count (max 30 per intent)
      - Gas budget (AST node count vs limit)
      - Unused SET variables
      - Parse errors

    Args:
        source: HLF source text
        max_gas: Maximum allowed AST nodes (default: from env or 10)

    Returns:
        HLFResult with diagnostics list in output.
    """
    try:
        from hlf.hlflint import lint
        diagnostics = lint(source, max_gas=max_gas)
        return HLFResult(
            success=len(diagnostics) == 0,
            operation="lint",
            output=diagnostics,
            warnings=diagnostics,
            metadata={"diagnostic_count": len(diagnostics)},
        )
    except Exception as e:
        return HLFResult(
            success=False,
            operation="lint",
            errors=[str(e)],
        )


def run_hlf(source: str, tools: dict[str, Any] | None = None) -> HLFResult:
    """Execute HLF source via the AST interpreter.

    Runs the program through hlfrun.py which handles:
      - Math logic (14 built-in functions)
      - Control flow (guarded loops, assertions, returns)
      - Tool dispatch (↦ τ operator)
      - Memory/Recall operations

    Args:
        source: HLF source text
        tools: Optional dict of registered tool functions

    Returns:
        HLFResult with execution output.
    """
    try:
        # Handle chaos-to-HLF if missing standard header
        if not source.lstrip().startswith("[HLF-"):
            source = chaos_to_hlf(source)
        from hlf.hlfc import compile as hlfc_compile
        from hlf.hlfrun import HLFInterpreter

        ast = hlfc_compile(source)
        interpreter = HLFInterpreter()

        # Register provided tools
        if tools:
            for name, func in tools.items():
                interpreter.register_tool(name, func)

        result = interpreter.execute(ast)
        return HLFResult(
            success=True,
            operation="run",
            output=result,
            metadata={
                "scope": dict(interpreter.scope) if hasattr(interpreter, "scope") else {},
            },
        )
    except Exception as e:
        return HLFResult(
            success=False,
            operation="run",
            errors=[str(e)],
            metadata={"traceback": traceback.format_exc()},
        )


def bytecode_compile(source: str) -> HLFResult:
    """Compile HLF source to bytecode (.hlbc binary format).

    Pipeline:
      1. Parse to AST via hlfc
      2. Flatten AST to linear instruction sequence
      3. Emit binary payload with header, constant pool, code segment
      4. Attach SHA-256 integrity checksum

    Args:
        source: HLF source text

    Returns:
        HLFResult with bytecode bytes in output.
    """
    try:
        # Handle chaos-to-HLF if missing standard header
        if not source.lstrip().startswith("[HLF-"):
            source = chaos_to_hlf(source)
        from hlf.bytecode import HLFBytecodeCompiler

        compiler = HLFBytecodeCompiler()
        bytecode = compiler.compile(source)
        return HLFResult(
            success=True,
            operation="bytecode_compile",
            output=bytecode,
            metadata={
                "size_bytes": len(bytecode) if isinstance(bytecode, (bytes, bytearray)) else 0,
            },
        )
    except Exception as e:
        return HLFResult(
            success=False,
            operation="bytecode_compile",
            errors=[str(e)],
            metadata={"traceback": traceback.format_exc()},
        )


def decompile(bytecode: bytes) -> HLFResult:
    """Disassemble bytecode to human-readable instruction trace.

    Produces output like:
      0001: PUSH_CONST "audit_context"
      0005: STORE_VAR  "context"
      0009: LOAD_TOOL   "security_scan"
      ...

    Args:
        bytecode: Compiled .hlbc binary data

    Returns:
        HLFResult with disassembly string in output.
    """
    try:
        from hlf.bytecode import HLFDisassembler

        disasm = HLFDisassembler()
        trace = disasm.disassemble(bytecode)
        return HLFResult(
            success=True,
            operation="decompile",
            output=trace,
            metadata={
                "input_size": len(bytecode),
                "line_count": len(trace.splitlines()) if isinstance(trace, str) else 0,
            },
        )
    except Exception as e:
        return HLFResult(
            success=False,
            operation="decompile",
            errors=[str(e)],
            metadata={"traceback": traceback.format_exc()},
        )


def translate(source: Any, direction: str = "hlf_to_english") -> HLFResult:
    """Translate between HLF and English via InsAIts V2.

    Supports:
      - hlf_to_english: Decompile AST to English prose
      - bytecode_to_english: Decompile binary to English

    Args:
        source: HLF source text (for hlf_to_english)
        direction: "hlf_to_english" (default) or "bytecode_to_english"

    Returns:
        HLFResult with English prose in output.
    """
    try:
        if direction == "bytecode_to_fluent":
            if isinstance(source, str):
                source_bytes = source.encode()
            else:
                source_bytes = source
            from hlf.insaits import fluent_decompile
            english = fluent_decompile(source_bytes)
        else:
            if isinstance(source, bytes):
                source_str = source.decode("utf-8")
            else:
                source_str = source
            from hlf.hlfc import compile as hlfc_compile
            from hlf.insaits import decompile as insaits_decompile
            ast = hlfc_compile(source_str)
            english = insaits_decompile(ast)
        return HLFResult(
            success=True,
            operation="translate",
            output=english,
            metadata={
                "direction": direction,
                "source_length": len(source),
                "output_length": len(english),
            },
        )
    except Exception as e:
        return HLFResult(
            success=False,
            operation="translate",
            errors=[str(e)],
            metadata={"traceback": traceback.format_exc()},
        )


def correct(source: str) -> HLFResult:
    """Auto-heal broken HLF source via the ErrorCorrector.

    Applies heuristic corrections:
      - Missing [HLF-v2/v3/v4] header
      - Missing Ω terminator
      - Common tag typos (INTNET→INTENT, FUCNTION→FUNCTION, etc.)
      - Missing closing brackets

    Args:
        source: Potentially broken HLF source text

    Returns:
        HLFResult with CorrectionResult in output.
    """
    try:
        from hlf.error_corrector import HLFErrorCorrector

        corrector = HLFErrorCorrector()
        result = corrector.correct(source)
        return HLFResult(
            success=result.auto_corrected or not result.error_message,
            operation="correct",
            output={
                "diagnosis": result.diagnosis,
                "suggestions": result.suggestions,
                "auto_corrected": result.auto_corrected,
                "fixed_source": result.fixed_source,
                "has_fixed_ast": result.fixed_ast is not None,
            },
            metadata={
                "original_error": result.error_message,
            },
        )
    except Exception as e:
        return HLFResult(
            success=False,
            operation="correct",
            errors=[str(e)],
        )


def generate(steps: list[dict[str, Any]]) -> HLFResult:
    """Programmatically generate HLF source via CodeGenerator.

    Each step is a dict with "type" and type-specific params:
      {"type": "set", "name": "x", "value": "hello"}
      {"type": "intent", "action": "scan", "target": "/deploy"}
      {"type": "tool", "tool_name": "security_scan", "args": ["target"]}
      {"type": "memory", "entity": "log", "content": "...", "confidence": 0.9}
      {"type": "result", "code": 0, "message": "ok"}

    Args:
        steps: List of step dicts to build into an HLF program

    Returns:
        HLFResult with generated source text in output.
    """
    try:
        from hlf.codegen import HLFCodeGenerator

        gen = HLFCodeGenerator()

        for step in steps:
            step_type = step.get("type", "")
            if step_type == "set":
                gen.set(step["name"], step["value"])
            elif step_type == "intent":
                gen.intent(step["action"], step.get("target", ""))
            elif step_type == "constraint":
                gen.constraint(step["key"], step["value"])
            elif step_type == "thought":
                gen.thought(step["reasoning"])
            elif step_type == "tool":
                gen.tool(step["tool_name"], *step.get("args", []))
            elif step_type == "memory":
                gen.memory(step["entity"], step["content"], step.get("confidence", 0.5))
            elif step_type == "recall":
                gen.recall(step["entity"], step.get("top_k", 5))
            elif step_type == "assert":
                gen.assert_(step["condition"], step.get("error", ""))
            elif step_type == "delegate":
                gen.delegate(step["role"], step["intent"])
            elif step_type == "observation":
                gen.observation(step["data"])
            elif step_type == "result":
                gen.result(step.get("code", 0), step.get("message", "ok"))
            elif step_type == "raw":
                gen.raw(step["line"])
            else:
                return HLFResult(
                    success=False,
                    operation="generate",
                    errors=[f"Unknown step type: {step_type}"],
                )

        source = gen.build()
        return HLFResult(
            success=True,
            operation="generate",
            output=source,
            metadata={
                "step_count": len(steps),
                "source_length": len(source),
            },
        )
    except Exception as e:
        return HLFResult(
            success=False,
            operation="generate",
            errors=[str(e)],
        )


def format_source(source: str) -> HLFResult:
    """Canonically format HLF source text.

    Normalizes:
      - Uppercase tags
      - Single space after ]
      - Mandatory trailing Ω
      - No trailing whitespace

    Args:
        source: HLF source text

    Returns:
        HLFResult with formatted source in output.
    """
    try:
        from hlf.hlffmt import format_hlf
        formatted = format_hlf(source)
        return HLFResult(
            success=True,
            operation="format",
            output=formatted,
            metadata={"original_length": len(source), "formatted_length": len(formatted)},
        )
    except Exception as e:
        return HLFResult(
            success=False,
            operation="format",
            errors=[str(e)],
        )


def validate(source: str) -> HLFResult:
    """Quick structural validation without full compilation.

    Uses the regex-based heuristic validator from hlf.__init__:
      - Checks for [HLF-v2/v3/v4] header
      - Checks for Ω terminator
      - Validates each line structurally

    Args:
        source: HLF source text

    Returns:
        HLFResult with validation status.
    """
    try:
        from hlf import validate_hlf, validate_hlf_heuristic

        heuristic_ok = validate_hlf_heuristic(source)
        lines = source.strip().splitlines()
        invalid_lines = []
        for i, line in enumerate(lines, 1):
            if not validate_hlf(line):
                invalid_lines.append({"line": i, "content": line.strip()})

        return HLFResult(
            success=heuristic_ok and len(invalid_lines) == 0,
            operation="validate",
            output={
                "heuristic_valid": heuristic_ok,
                "invalid_lines": invalid_lines,
                "total_lines": len(lines),
            },
            warnings=[f"Line {il['line']}: {il['content']}" for il in invalid_lines[:5]],
        )
    except Exception as e:
        return HLFResult(
            success=False,
            operation="validate",
            errors=[str(e)],
        )


def run_program_file(filepath: str | Path, tools: dict[str, Any] | None = None) -> HLFResult:
    """Load and run an HLF program from a file.

    Convenience wrapper that reads a .hlf file and runs it through
    the full pipeline: validate → lint → compile → execute.

    Args:
        filepath: Path to .hlf file
        tools: Optional tool registry

    Returns:
        HLFResult with execution output and full pipeline metadata.
    """
    path = Path(filepath)
    if not path.exists():
        return HLFResult(
            success=False,
            operation="run_program_file",
            errors=[f"File not found: {filepath}"],
        )

    source = path.read_text(encoding="utf-8")

    # Pipeline: validate → lint → compile → run
    val_result = validate(source)
    lint_result = lint_hlf(source, max_gas=100)
    compile_result = compile_hlf(source)

    if not compile_result.success:
        return HLFResult(
            success=False,
            operation="run_program_file",
            errors=compile_result.errors,
            warnings=lint_result.warnings,
            metadata={
                "file": str(path),
                "validation": val_result.to_dict(),
                "lint": lint_result.to_dict(),
                "compile": compile_result.to_dict(),
            },
        )

    run_result = run_hlf(source, tools=tools)
    return HLFResult(
        success=run_result.success,
        operation="run_program_file",
        output=run_result.output,
        errors=run_result.errors,
        warnings=lint_result.warnings,
        metadata={
            "file": str(path),
            "pipeline": {
                "validation": val_result.success,
                "lint_clean": lint_result.success,
                "compiled": compile_result.success,
                "executed": run_result.success,
            },
        },
    )


# ---------------------------------------------------------------------------
# CLI Interface
# ---------------------------------------------------------------------------
def main() -> None:
    """CLI entry point for hlf_runner.

    Usage:
        python tools/hlf_runner.py compile <file.hlf>
        python tools/hlf_runner.py lint <file.hlf>
        python tools/hlf_runner.py run <file.hlf>
        python tools/hlf_runner.py translate <file.hlf>
        python tools/hlf_runner.py validate <file.hlf>
        python tools/hlf_runner.py format <file.hlf>
        python tools/hlf_runner.py correct <file.hlf>
    """
    if len(sys.argv) < 3:
        print("Usage: python tools/hlf_runner.py <command> <file.hlf>")
        print("Commands: compile, lint, run, translate, validate, format, correct")
        sys.exit(1)

    command = sys.argv[1]
    filepath = Path(sys.argv[2])

    if not filepath.exists():
        print(f"Error: File not found: {filepath}", file=sys.stderr)
        sys.exit(1)

    direction = "bytecode_to_fluent" if command == "translate" and str(filepath).endswith(".bc") else "hlf_to_english"
    if command in ["translate", "decompile"] and str(filepath).endswith(".bc"):
        source = filepath.read_bytes()
    else:
        source = filepath.read_text(encoding="utf-8")

    dispatch = {
        "compile": lambda: compile_hlf(source),
        "lint": lambda: lint_hlf(source),
        "run": lambda: run_hlf(source),
        "translate": lambda: translate(source, direction=direction),
        "validate": lambda: validate(source),
        "format": lambda: format_source(source),
        "correct": lambda: correct(source),
    }

    handler = dispatch.get(command)
    if not handler:
        print(f"Unknown command: {command}", file=sys.stderr)
        sys.exit(1)

    result = handler()
    print(json.dumps(result.to_dict(), indent=2, default=str))
    sys.exit(0 if result.success else 1)


if __name__ == "__main__":
    main()
