# Contributing to Jules_Choice

Thank you for your interest in contributing to Jules_Choice! This document provides guidelines and processes for contributing.

## Code of Conduct

Be respectful, constructive, and collaborative. Jules_Choice is an autonomous creative experiment, and we welcome diverse perspectives.

## Getting Started

1. **Fork** the repository
2. **Clone** your fork locally
3. **Install** dependencies:
   ```bash
   pip install -e ".[dev]"
   pre-commit install
   ```
4. **Create a branch** for your changes:
   ```bash
   git checkout -b feat/your-feature-name
   ```

## Development Workflow

### Code Quality

We enforce:
- **ruff** for linting and formatting
- **mypy** for type checking
- **pytest** for testing
- **bandit** for security scanning

Run all checks:
```bash
make lint
make test
make security-scan
```

### Testing

- All new features **must** include tests
- Tests go in `tests/` with `test_` prefix
- Use fixtures from `tests/conftest.py`
- Run: `pytest -v`

### Pre-commit Hooks

Pre-commit hooks run automatically on `git commit`. To run manually:
```bash
pre-commit run --all-files
```

## Pull Request Process

1. Update documentation if needed
2. Add tests for new functionality
3. Ensure all checks pass (`make lint && make test`)
4. Use the PR template (`.github/PULL_REQUEST_TEMPLATE.md`)
5. PRs are reviewed using the **11-Hat Review Protocol**

### Non-Reductive Policy

> **Critical:** All contributions must be **additive**. Do not remove existing functionality without replacing it with something equal or better. This is a core principle of Jules_Choice.

## Issue Guidelines

- Use the appropriate issue template
- Tag with priority labels (P0, P1, P2)
- Reference related issues

## Architecture Overview

See [docs/architecture.md](docs/architecture.md) for full architecture documentation.

### Key Directories

| Directory | Purpose |
|-----------|----------|
| `agents/` | Persona-based agent implementations |
| `tools/` | Utility scripts (security, health, charts) |
| `tests/` | Pytest test suite |
| `config/` | Persona definitions, decision matrix |
| `docs/` | Documentation and generated assets |
| `.github/` | CI/CD, templates, Dependabot |
