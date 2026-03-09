# Security Policy

## Supported Versions

| Version | Supported          |
|---------|--------------------||
| main    | ✅ Yes             |
| Other   | ❌ No              |

## Reporting a Vulnerability

If you discover a security vulnerability in Jules_Choice, please report it responsibly.

### How to Report

1. **Do NOT open a public GitHub issue** for security vulnerabilities
2. **Email:** Send details to the repository maintainers via the organization contact
3. **Include:**
   - Description of the vulnerability
   - Steps to reproduce
   - Potential impact assessment
   - Suggested fix (if any)

### Response Timeline

- **Acknowledgment:** Within 48 hours of report
- **Initial Assessment:** Within 5 business days
- **Fix Timeline:** Depends on severity
  - Critical: 24-48 hours
  - High: 1 week
  - Medium: 2 weeks
  - Low: Next sprint

### Disclosure Policy

- We follow **coordinated disclosure**
- Credit will be given to reporters (unless anonymity is requested)
- Fixes are applied to `main` and released immediately

## Security Measures in Place

- **Bandit** security scanning in CI pipeline
- **CodeQL** code scanning on pull requests
- **Dependabot** for dependency vulnerability alerts
- **Policy checker** (`tools/security_scan.py`) for local scanning
- **Pre-commit hooks** for code quality

## Security Rules (`jules_policy.yaml`)

- No hardcoded secrets or API keys in source code
- No external API calls without review
- No arbitrary code execution
- All inputs must be validated
- All dependencies must be pinned
- Media files restricted to safe formats (SVG, PNG, JPG, GIF, WebP, MP4)
- No AI-generated faces in media assets
- All media must include alt text
