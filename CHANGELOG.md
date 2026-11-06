# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## [1.1.0] - 2026-11-06

### Added
- **Desktop Interactivity Suite (Inspired by `qgis-mcp`)**:
  - `fme_diagnose`: System and environment diagnostic for FME installation, build, licensing, active processes, and bridge readiness.
  - `fme_inspect_canvas`: Structured `.fmw` XML canvas topology extraction (transformers with coordinates, links, unconnected port warnings).
  - `fme_open_in_workbench`: Non-blocking detached launcher for FME Workbench GUI.
  - `fme_open_in_inspector`: Instant dataset opening in FME Data Inspector GUI.
  - `fme_preview_dataset`: Direct in-chat preview of GeoPackage, SQLite, CSV, and Excel tables and schemas.
  - `FMEBridgeServer` & `FMEBridgeClient`: Loopback TCP socket bridge on `127.0.0.1:9877`.

### Changed
- **Zero-Configuration Generalisation**: Path resolution dynamically adapts to user home (`~`) and working directories without requiring explicit environment variables.
- **Repository Streamlining**: Removed redundant Kubernetes and Helm charts to keep the Python package lightweight and focused on MCP core functionality.
- Expanded automated test coverage to 32 tests spanning security, desktop tools, and MCP server calls.

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

