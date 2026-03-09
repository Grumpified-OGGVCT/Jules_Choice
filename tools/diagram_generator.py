#!/usr/bin/env python3
"""Diagram generator for Jules_Choice.

Generates architecture and flow diagrams as SVG files.
"""

import os


def generate_architecture_diagram(output_path: str = "docs/assets/generated/architecture.svg") -> str:
    """Generate the Jules_Choice architecture overview diagram."""
    svg = """<svg xmlns="http://www.w3.org/2000/svg" width="700" height="500" viewBox="0 0 700 500">
  <defs>
    <linearGradient id="g1" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="#3b82f6"/>
      <stop offset="100%" stop-color="#8b5cf6"/>
    </linearGradient>
    <linearGradient id="g2" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="#06b6d4"/>
      <stop offset="100%" stop-color="#10b981"/>
    </linearGradient>
    <linearGradient id="g3" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="#f59e0b"/>
      <stop offset="100%" stop-color="#ef4444"/>
    </linearGradient>
  </defs>
  <rect width="700" height="500" rx="12" fill="#0f172a"/>
  <text x="350" y="35" text-anchor="middle" font-size="18" font-weight="bold" fill="#f1f5f9" font-family="monospace">Jules_Choice Architecture</text>

  <!-- Governance Layer -->
  <rect x="30" y="55" width="640" height="70" rx="8" fill="url(#g1)" opacity="0.9"/>
  <text x="350" y="80" text-anchor="middle" font-size="14" font-weight="bold" fill="white" font-family="monospace">Governance Layer</text>
  <text x="100" y="105" text-anchor="middle" font-size="10" fill="#dbeafe" font-family="monospace">jules_policy.yaml</text>
  <text x="250" y="105" text-anchor="middle" font-size="10" fill="#dbeafe" font-family="monospace">jules_vision.yaml</text>
  <text x="430" y="105" text-anchor="middle" font-size="10" fill="#dbeafe" font-family="monospace">decision_matrix.yaml</text>
  <text x="600" y="105" text-anchor="middle" font-size="10" fill="#dbeafe" font-family="monospace">SECURITY.md</text>

  <!-- Agent Layer -->
  <rect x="30" y="140" width="640" height="100" rx="8" fill="url(#g2)" opacity="0.9"/>
  <text x="350" y="165" text-anchor="middle" font-size="14" font-weight="bold" fill="white" font-family="monospace">Agent Layer (14 personas)</text>
  <text x="100" y="190" text-anchor="middle" font-size="9" fill="#d1fae5" font-family="monospace">Steward</text>
  <text x="200" y="190" text-anchor="middle" font-size="9" fill="#d1fae5" font-family="monospace">Arbiter</text>
  <text x="300" y="190" text-anchor="middle" font-size="9" fill="#d1fae5" font-family="monospace">Cove</text>
  <text x="400" y="190" text-anchor="middle" font-size="9" fill="#d1fae5" font-family="monospace">Sentinel</text>
  <text x="500" y="190" text-anchor="middle" font-size="9" fill="#d1fae5" font-family="monospace">Weaver</text>
  <text x="600" y="190" text-anchor="middle" font-size="9" fill="#d1fae5" font-family="monospace">Chronicler</text>
  <text x="100" y="215" text-anchor="middle" font-size="9" fill="#d1fae5" font-family="monospace">Herald</text>
  <text x="200" y="215" text-anchor="middle" font-size="9" fill="#d1fae5" font-family="monospace">Palette</text>
  <text x="300" y="215" text-anchor="middle" font-size="9" fill="#d1fae5" font-family="monospace">Scribe</text>
  <text x="400" y="215" text-anchor="middle" font-size="9" fill="#d1fae5" font-family="monospace">Consolidator</text>
  <text x="500" y="215" text-anchor="middle" font-size="9" fill="#d1fae5" font-family="monospace">Oracle</text>
  <text x="600" y="215" text-anchor="middle" font-size="9" fill="#d1fae5" font-family="monospace">+3 more</text>

  <!-- Tool Layer -->
  <rect x="30" y="260" width="640" height="80" rx="8" fill="url(#g3)" opacity="0.9"/>
  <text x="350" y="285" text-anchor="middle" font-size="14" font-weight="bold" fill="white" font-family="monospace">Tool Layer</text>
  <text x="100" y="315" text-anchor="middle" font-size="9" fill="#fef3c7" font-family="monospace">security_scan</text>
  <text x="220" y="315" text-anchor="middle" font-size="9" fill="#fef3c7" font-family="monospace">policy_checker</text>
  <text x="340" y="315" text-anchor="middle" font-size="9" fill="#fef3c7" font-family="monospace">repo_health</text>
  <text x="450" y="315" text-anchor="middle" font-size="9" fill="#fef3c7" font-family="monospace">chart_gen</text>
  <text x="560" y="315" text-anchor="middle" font-size="9" fill="#fef3c7" font-family="monospace">goal_tracker</text>

  <!-- Infrastructure Layer -->
  <rect x="30" y="360" width="300" height="120" rx="8" fill="#1e293b" stroke="#334155" stroke-width="1"/>
  <text x="180" y="385" text-anchor="middle" font-size="12" font-weight="bold" fill="#94a3b8" font-family="monospace">Infrastructure</text>
  <text x="180" y="410" text-anchor="middle" font-size="10" fill="#64748b" font-family="monospace">CI/CD Pipeline</text>
  <text x="180" y="430" text-anchor="middle" font-size="10" fill="#64748b" font-family="monospace">CodeQL + Dependabot</text>
  <text x="180" y="450" text-anchor="middle" font-size="10" fill="#64748b" font-family="monospace">Pre-commit Hooks</text>
  <text x="180" y="470" text-anchor="middle" font-size="10" fill="#64748b" font-family="monospace">Pytest Suite (90+ tests)</text>

  <!-- Outputs -->
  <rect x="370" y="360" width="300" height="120" rx="8" fill="#1e293b" stroke="#334155" stroke-width="1"/>
  <text x="520" y="385" text-anchor="middle" font-size="12" font-weight="bold" fill="#94a3b8" font-family="monospace">Outputs</text>
  <text x="520" y="410" text-anchor="middle" font-size="10" fill="#64748b" font-family="monospace">SVG Infographics</text>
  <text x="520" y="430" text-anchor="middle" font-size="10" fill="#64748b" font-family="monospace">Health Badges</text>
  <text x="520" y="450" text-anchor="middle" font-size="10" fill="#64748b" font-family="monospace">Sprint Reports</text>
  <text x="520" y="470" text-anchor="middle" font-size="10" fill="#64748b" font-family="monospace">App Gallery</text>
</svg>"""

    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(svg)
    return output_path


def generate_lifecycle_diagram(output_path: str = "docs/assets/generated/agent_lifecycle.svg") -> str:
    """Generate the agent perceive-decide-act-reflect lifecycle diagram."""
    svg = """<svg xmlns="http://www.w3.org/2000/svg" width="500" height="300" viewBox="0 0 500 300">
  <rect width="500" height="300" rx="12" fill="#0f172a"/>
  <text x="250" y="30" text-anchor="middle" font-size="14" font-weight="bold" fill="#f1f5f9" font-family="monospace">Agent Lifecycle</text>

  <!-- Perceive -->
  <circle cx="100" cy="100" r="40" fill="#3b82f6" opacity="0.9"/>
  <text x="100" y="105" text-anchor="middle" font-size="11" fill="white" font-family="monospace">Perceive</text>

  <!-- Decide -->
  <circle cx="250" cy="100" r="40" fill="#8b5cf6" opacity="0.9"/>
  <text x="250" y="105" text-anchor="middle" font-size="11" fill="white" font-family="monospace">Decide</text>

  <!-- Act -->
  <circle cx="400" cy="100" r="40" fill="#10b981" opacity="0.9"/>
  <text x="400" y="105" text-anchor="middle" font-size="11" fill="white" font-family="monospace">Act</text>

  <!-- Reflect -->
  <circle cx="250" cy="220" r="40" fill="#f59e0b" opacity="0.9"/>
  <text x="250" y="225" text-anchor="middle" font-size="11" fill="white" font-family="monospace">Reflect</text>

  <!-- Arrows -->
  <line x1="140" y1="100" x2="200" y2="100" stroke="#64748b" stroke-width="2" marker-end="url(#arrow)"/>
  <line x1="290" y1="100" x2="350" y2="100" stroke="#64748b" stroke-width="2" marker-end="url(#arrow)"/>
  <line x1="400" y1="140" x2="290" y2="210" stroke="#64748b" stroke-width="2" marker-end="url(#arrow)"/>
  <line x1="210" y1="210" x2="100" y2="140" stroke="#64748b" stroke-width="2" marker-end="url(#arrow)"/>

  <defs>
    <marker id="arrow" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-auto">
      <path d="M 0 0 L 10 5 L 0 10 z" fill="#64748b"/>
    </marker>
  </defs>

  <text x="250" y="285" text-anchor="middle" font-size="10" fill="#475569" font-family="monospace">BaseAgent ABC enforces this lifecycle for all 14 agents</text>
</svg>"""

    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(svg)
    return output_path


def main():
    print("Diagram Generator")
    print("=" * 40)
    print(f"  Generated: {generate_architecture_diagram()}")
    print(f"  Generated: {generate_lifecycle_diagram()}")


if __name__ == '__main__':
    main()
