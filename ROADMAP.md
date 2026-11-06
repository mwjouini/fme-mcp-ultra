# Project Roadmap

This document outlines the strategic evolution of **`fme-mcp-ultra`**.

---

## Phase 1: Foundation (v1.0.0) — :white_check_mark: Complete
- [x] Full support for **FME Form 2025.2** via local CLI and native `fmeobjects` Python bindings.
- [x] Streamable HTTP and stdio transports.
- [x] Complete security middleware (PathGuard, CommandGuard, SSRF Guard, PII Redaction).
- [x] Dynamic workspace-to-MCP engine with automated parameter inference.
- [x] Core tool catalogue covering spatial transformations, catalogue, quality, and jobs.
- [x] Ready-to-copy client configurations (Claude Desktop, Cursor, Antigravity, VS Code).

---

## Phase 2: Enterprise Flow & Streaming (v1.1.0)
- [ ] Direct Server-Sent Events (SSE) log streaming for FME Flow jobs.
- [ ] Automated webhook receivers for asynchronous notifications.
- [ ] OpenTelemetry distributed tracing across federated MCP calls.
- [ ] Extended CAD/BIM conversion profiles.

---

## Phase 3: Autonomous Spatial Agents (v1.2.0)
- [ ] Natural Language to FMW generation engine.
- [ ] Multi-agent collaborative GIS workflows with human-in-the-loop approvals.
- [ ] Dynamic spatial indexing for billion-row vector datasets.
