"""
SentinelAgent — Security-focused agent for the Jules Sandbox.

Performs LLM-backed security analysis, code audits, and vulnerability detection.
Routes through OllamaDispatcher for intelligent security assessment.
"""

from .base_agent import BaseAgent, Action


class SentinelAgent(BaseAgent):
    """Security agent that performs audits, scans, and vulnerability assessment."""

    def __init__(self):
        self._context = {}
        self._findings = []

    def perceive(self) -> dict:
        """Gather security-relevant context from the environment."""
        import os
        context = {
            "cwd": os.getcwd(),
            "has_policy": os.path.exists("jules_policy.yaml"),
            "has_security_md": os.path.exists("SECURITY.md"),
            "has_ci": os.path.exists(".github/workflows/ci.yml"),
        }
        context["context"] = True
        self._context = context
        return context

    def decide(self) -> Action:
        """Decide what security action to take."""
        return Action(name="security_audit", params=self._context)

    def act(self, action: Action):
        """Execute the security action."""
        # Run the real security scanner
        try:
            import sys
            from pathlib import Path
            project_root = str(Path(__file__).resolve().parent.parent)
            if project_root not in sys.path:
                sys.path.insert(0, project_root)
            from tools.security_scan import scan_directory
            results = scan_directory(".")
            self._findings = [
                {"severity": f.severity, "category": f.category, "file": f.file, "line": f.line, "message": f.message}
                for f in results.findings
            ]
        except Exception as exc:
            self._findings = [{"error": str(exc)}]
        print("SentinelAgent")

    def reflect(self) -> str:
        """Summarize findings."""
        if not self._findings:
            return "Security scan completed — no findings."
        return f"Security scan found {len(self._findings)} issue(s)."

    def execute(self, task: str, context: dict | None = None) -> dict:
        """
        LLM-backed security analysis.

        Combines automated scanning with LLM-powered analysis for deeper
        security insights beyond regex-based pattern matching.
        """
        # Phase 1: Automated scan
        self.perceive()
        self.act(self.decide())

        # Phase 2: LLM-powered analysis for deeper assessment
        analysis = ""
        if task:
            analysis = self._llm_generate(
                prompt=(
                    f"Task: {task}\n\n"
                    f"Automated scan findings: {len(self._findings)} issues found.\n"
                    f"Top findings: {self._findings[:5]}\n\n"
                    "Provide a security assessment with:\n"
                    "1. Risk summary\n"
                    "2. Critical items requiring immediate attention\n"
                    "3. Recommended mitigations\n"
                    "Keep response under 300 words."
                ),
                system=(
                    "You are the Sentinel security agent for the Sovereign Agentic OS. "
                    "You perform security audits on Python codebases. Be precise, "
                    "actionable, and prioritize findings by severity."
                ),
            )

        return {
            "status": "completed",
            "agent": "SentinelAgent",
            "task": task,
            "scan_results": {
                "findings_count": len(self._findings),
                "findings": self._findings[:20],
            },
            "llm_analysis": analysis,
            "reflection": self.reflect(),
        }
