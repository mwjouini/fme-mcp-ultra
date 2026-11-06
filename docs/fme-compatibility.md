# FME Version Compatibility (2018.0 – 2026+)

Safe Software introduced official MCP features in FME 2026 (`safe.mcp` / `MCPCaller` on FME Hub in 2026.1 and native Flow MCP Server in 2026.2). However, thousands of production GIS workflows run on **FME 2018.0 through 2025**.

`fme-mcp-ultra` was built to provide full, seamless MCP capabilities across **all FME versions from 2018.0 to 2026+**.

---

## Why all versions from 2018 to 2026+ work out-of-the-box

The architecture of `fme-mcp-ultra` targets two stable interfaces that Safe Software has maintained consistently for years:

### 1. FME Form (Desktop) — Consistent CLI & XML Format
- **Subprocess CLI Runner (`fme.exe`)**: The command-line invocation syntax (`fme.exe <workspace.fmw> --PARAMETER VALUE`) has remained backward-compatible across every FME release since FME 2018.0.
- **XML Canvas Schema**: The `.fmw` file structure uses a stable XML format (`#! <WORKSPACE ...>`), allowing `fme-mcp-ultra` to parse transformers, reader/writer feature types, port connections, and published parameters across any version.
- **In-Memory C-Extension (`fmeobjects`)**: Where available, `fmeobjects` is dynamically bound for fast in-process parameter introspection. If `fmeobjects` is not present, the server automatically falls back to XML parsing and CLI execution without failing.

### 2. FME Flow (Enterprise Server) — Standard REST API v3
- FME Server / Flow introduced the **REST API v3** in FME 2018.0 (`/fmerest/v3/`).
- `fme-mcp-ultra` uses standard v3 endpoints for repository discovery (`/repositories`), job submission (`/transformations/submit`), and log inspection (`/transformations/jobs/id/{id}/log`).
- Any FME Server or FME Flow instance from 2018.0 onwards works without requiring custom plugins or updates.

---

## Compatibility Summary

| FME Release | Local FME Form | Remote FME Flow | Support Level | Notes |
| :--- | :---: | :---: | :---: | :--- |
| **FME 2026+** | ✅ | ✅ | Full | Interoperable with native FME 2026 MCP endpoints, adds local `stdio` transport. |
| **FME 2025.x** | ✅ | ✅ | Full | Direct `fme.exe`, `fmeobjects` bindings, canvas XML parsing, Flow REST v3. |
| **FME 2021 – 2024** | ✅ | ✅ | Full | Same CLI, XML schema, and Flow REST v3 endpoints. |
| **FME 2018 – 2020** | ✅ | ✅ | Full | Standard Flow REST v3 and local CLI execution. |
| **FME 2015 – 2017** | ⚠️ CLI only | ❌ | Partial | Command-line `fme.exe` works; REST v2 is deprecated. |
