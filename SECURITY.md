# Security Policy

## Supported Versions

We provide security patches and vulnerability remediations for the following releases:

| Version | Supported |
| :--- | :--- |
| **1.0.x** | :white_check_mark: Active security support |
| < 1.0.0 | :x: Unsupported |

---

## Reporting a Vulnerability

**Please do not report security vulnerabilities through public GitHub issues.**

If you discover a security vulnerability in `fme-mcp-ultra`, please report it privately via GitHub Private Vulnerability Reporting or by emailing the project maintainer:

- **Security Contact**: Mohamed Wael JOUINI (`mohamed.wael.jouini@gmail.com`)
- **PGP Key**: Available on request.

Please include:
1. A description of the vulnerability, potential impact, and affected components.
2. Step-by-step reproduction instructions or a minimal Proof of Concept (PoC).
3. Any suggested remediations or mitigations.

### Response Timelines
- **Acknowledgement**: Within 48 hours.
- **Triage & Assessment**: Within 5 working days.
- **Fix & Advisory Release**: Coordinated with the reporter, typically within 30 days.

---

## Security Architecture Highlights

`fme-mcp-ultra` implements enterprise-grade DevSecOps controls:
- **Default Deny**: All tool invocations require explicit authentication and authorisation.
- **PathGuard**: Strict sandboxing preventing directory traversal attacks (`..`).
- **CommandGuard**: Zero shell invocations (`shell=False`) protecting against command injection.
- **SSRF Guard**: Automated DNS verification disallowing private/loopback IP addressing.
- **Secret Redaction**: Proactive scrubbing of API tokens and PII before response delivery.

