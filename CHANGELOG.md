# Changelog

All notable changes to Jules_Choice are documented here.

The format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).

## [0.2.0] - 2026-03-08

### Added
- **Security Hardening (Issue #5)**
  - `SECURITY.md` with vulnerability disclosure policy
  - `.github/dependabot.yml` for weekly dependency scanning
  - `.github/workflows/codeql.yml` for code scanning
  - `tools/security_scan.py` for local security scanning
  - `jules_policy.yaml` expanded with security + media rules

- **Real Tools (Issue #8)**
  - `tools/policy_checker.py` — policy compliance validator
  - `tools/repo_health.py` — health metrics with 0-100 scoring
  - `tools/sprint_reporter.py` — sprint summary generator
  - `tools/goal_tracker.py` — vision goal progress tracker
  - `tools/chart_generator.py` — SVG chart/badge generator
  - `tools/diagram_generator.py` — architecture diagram generator

- **Real Tests (Issue #11)**
  - `tests/conftest.py` — shared fixtures
  - `tests/test_base_agent.py` — 84 parametrized agent lifecycle tests
  - `tests/test_policy_checker.py` — policy checker tests
  - `tests/test_repo_health.py` — repo health tests
  - `tests/test_security_scan.py` — security scanner tests

- **Media Pipeline (Issue #9)**
  - `docs/gallery.md` — generated assets showcase
  - `docs/assets/generated/` directory structure

- **Documentation (Issue #12)**
  - `CONTRIBUTING.md` — contribution guidelines
  - `docs/architecture.md` — full architecture documentation
  - This CHANGELOG

- **Self-Improvement Loop (Issue #13)**
  - `jules_self_improvement.yaml` — improvement configuration
  - `tools/self_improve.py` — automated improvement engine
  - `tools/self_eval.py` — self-evaluation tool

## [0.1.0] - 2026-03-07

### Added
- **Vision & Goals (Issue #4)**
  - `jules_vision.yaml` with vision, goals, instincts, intentions

- **CI/CD Pipeline (Issue #6)**
  - `.github/workflows/ci.yml` with lint, test, security, gallery

- **Project Infrastructure (Issue #7)**
  - `pyproject.toml`, `Makefile`, PR templates, issue templates

- **Agent Classes (Issue #10)**
  - `agents/base_agent.py` — Abstract base class
  - 14 persona-based agent implementations

- **Decision Framework (Issue #3)**
  - `config/decision_matrix.yaml` with RICE scoring

- **SVG Infographics (PR #2)**
  - 5 SVG infographic assets
