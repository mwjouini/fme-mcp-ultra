# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## [1.0.0] - 2026-11-06

### Added
- Initial public release of `fme-mcp-ultra`.
- Full compatibility with Safe Software FME 2025.2 (FME Form and FME Flow).
- Universal MCP transports: Standard I/O (`stdio`) and Streamable HTTP (`sse`).
- Dynamic workspace-to-MCP engine automatically converting `.fmw` workspaces into validated MCP tools.
- Enterprise security engine including:
  - `PathGuard` for directory sandboxing and path traversal prevention.
  - `CommandGuard` for secure subprocess execution without shell expansion.
  - `SSRF Guard` protecting internal networks and cloud metadata services.
  - PII redaction and secret scrubbing in logs and data outputs.
- Comprehensive tool catalogue spanning spatial analysis, data engineering, quality verification, and metadata.
- Pre-configured client settings for Claude Desktop, Cursor, Antigravity, and VS Code.
- Automated CI/CD pipelines for linting, security scanning, container builds, and documentation.

