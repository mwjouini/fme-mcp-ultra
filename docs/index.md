# Welcome to fme-mcp-ultra

**`fme-mcp-ultra`** is the universal, open-source Model Context Protocol (MCP) server for **Safe Software FME (FME Form & FME Flow 2018.0 through 2026+)**, geospatial data, enterprise data pipelines, and AI agents.

---

## 🎯 Key Capabilities

- **Universal FME Support (2018.0 to 2026+)**: Complete support for local FME Form via CLI and in-memory `fmeobjects` bindings, alongside remote FME Flow REST APIs (v3 & v4).
- **Desktop Interactivity & Loopback Bridge**: Inspired by `qgis-mcp`, offers live environment diagnostics, canvas topology extraction, detached GUI execution (`FME Workbench`, `FME Data Inspector`), and instant dataset preview.
- **Automated Workspace-to-Tool Generation**: Dynamically inspects `.fmw` workspaces, extracts published parameters, and exposes them as strongly validated MCP tools.
- **Enterprise DevSecOps**: Hardened by default with directory containment (`PathGuard`), command injection protection (`CommandGuard`), outbound network defense (`SSRF Guard`), and automated PII / credential scrubbing.
- **MCP Federation**: Native client capabilities emulating and expanding upon FME 2026's `MCPCaller`.
- **Geospatial Intelligence**: Built-in spatial vector algorithms (reprojection, buffering, geometry repair), dataset profiling, and data contracts.

---

## 🚀 Getting Started

Explore our guides to install, configure, and integrate `fme-mcp-ultra` with your favourite MCP client:

- [Installation Guide](installation.md)
- [Configuration](configuration.md)
- [MCP Client Setups](mcp-clients.md)
- [Security Model](security.md)
- [Tools Catalogue](tools.md)

