# Jules_Choice Architecture

## Overview

Jules_Choice is a sandboxed autonomous AI co-creation environment featuring a multi-agent system managed by a deterministic governance framework.

## Layer Architecture

```
+--------------------------------------------------+
|              Governance Layer                      |
|  jules_policy.yaml | jules_vision.yaml            |
|  decision_matrix.yaml | SECURITY.md               |
+--------------------------------------------------+
|              Agent Layer (14 Personas)             |
|  Steward | Arbiter | Cove | Sentinel | Weaver     |
|  Chronicler | Herald | Palette | Scribe            |
|  Consolidator | Oracle | Catalyst | Strategist     |
|  Scout                                             |
+--------------------------------------------------+
|              Tool Layer                            |
|  security_scan | policy_checker | repo_health      |
|  chart_generator | diagram_generator               |
|  goal_tracker | sprint_reporter                    |
|  build_app_gallery                                 |
+--------------------------------------------------+
|              Infrastructure Layer                  |
|  CI/CD | CodeQL | Dependabot | Pre-commit          |
|  Pytest (90+ test cases)                           |
+--------------------------------------------------+
|              Output Layer                          |
|  SVG Infographics | Health Badges                  |
|  Sprint Reports | App Gallery                      |
+--------------------------------------------------+
```

## Agent System

### BaseAgent (ABC)

All agents inherit from `BaseAgent` and implement the lifecycle:

1. **perceive()** -> dict: Gather context about the current state
2. **decide()** -> Action: Choose the next action based on perception
3. **act(action)**: Execute the chosen action
4. **reflect()** -> str: Evaluate the outcome and learn

### Agent Roster

| Agent | Role | Responsibility |
|-------|------|----------------|
| Steward | System Orchestrator | Overall coordination and resource management |
| Arbiter | Conflict Resolver | Decision-making and policy enforcement |
| Cove | Safe Harbor | Protected evaluation space for sensitive operations |
| Sentinel | Security Guard | Security monitoring and threat detection |
| Weaver | Integration Specialist | Cross-system integration and workflow chaining |
| Chronicler | Record Keeper | Audit logging an state documentation |
| Herald | Communication | Status reporting and notification management |
| Palette | Creative Director | UI/UX, visualization, and presentation output |
| Scribe | Documentation Writer | Content creation and documentation management |
| Consolidator | Cleanup Specialist | Debt reduction and code consolidation |
| Oracle | Forecasting | Predictive analysis and trend identification |
| Catalyst | Innovation Driver | New feature ideation and prototyping |
| Strategist | Planning | Long-term roadmap and strategic planning |
| Scout | Research | Technology scouting and competitive analysis |

## Decision Framework (RICE)

All decisions go through the RICE scoring matrix:
- **Reach:** How many components does it affect?
- **Impact:** How significant is the change? (1-3)
- **Confidence:** How certain are we? (0.0-1.0)
- **Effort:** How many sprints? (1-5)

Score = (Reach x Impact x Confidence) / Effort

## Tool System

| Tool | Purpose | Output |
|------|---------|--------|
| `security_scan.py` | Detect secrets, unsafe code | Exit 0/1 |
| `policy_checker.py` | Validate policy compliance | Exit 0/1 |
| `repo_health.py` | Compute health score | Score 0-100 |
| `chart_generator.py` | Generate SVG charts | SVG files |
| `diagram_generator.py` | Generate arch diagrams | SVG files |
| `goal_tracker.py` | Track vision goals | Progress % |
| `sprint_reporter.py` | Generate sprint reports | Markdown |
| `build_app_gallery.py` | Build app gallery page | HTML |

## CI/CD Pipeline

```
push/PR -> lint (ruff) -> type check (mypy) -> test (pytest)
                                                    |
                                              security (bandit)
                                                    |
                                              gallery build
```

Additional scanning:
- **CodeQL** on push to main, PRs, and weekly schedule
- **Dependabot** weekly for pip and GitHub Actions

## File Structure

```
Jules_Choice/
  agents/             # 14 persona-based agent implementations
  config/
    personas/          # 14 persona YAML specifications
    decision_matrix.yaml
  docs/
    assets/generated/  # Auto-generated SVG charts and diagrams
    gallery.md         # Asset showcase
    architecture.md    # This file
    roadmap.md         # Sprint roadmap
  tools/               # 8 functional Python tools
  tests/               # 5 test files, 90+ test cases
  .github/
    workflows/         # CI + CodeQL
    dependabot.yml
    PULL_REQUEST_TEMPLATE.md
    ISSUE_TEMPLATE/
  jules_policy.yaml    # Safety + security + media rules
  jules_vision.yaml    # Vision, goals, instincts
  SECURITY.md          # Vulnerability disclosure
  CONTRIBUTING.md      # Contribution guide
  CHANGELOG.md         # Release history
  pyproject.toml       # Project configuration
  Makefile             # Developer shortcuts
```
