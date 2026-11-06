# Comparison with FME 2026 Native MCP

Safe Software introduced Model Context Protocol (MCP) support in FME 2026:
1. **FME 2026.1**: `safe.mcp` / `MCPCaller` on FME Hub (Client mode, allowing FME workspaces to call external MCP tools).
2. **FME 2026.2**: FME Flow Native MCP Server (Server mode, exposing hosted workspaces as MCP tools).

---

## Feature Comparison

`fme-mcp-ultra` supports both server and client capabilities in a single runtime, while also adding desktop client support and backward compatibility:

| Capability | FME 2026 Official | `fme-mcp-ultra` |
| :--- | :---: | :---: |
| **Server Mode (Expose Workspaces)** | ✅ Flow Only (2026.2+) | ✅ Form (Local) & Flow (Remote) |
| **Client Mode (MCP Caller)** | ✅ Via Hub Package | ✅ Built-in Federation Client |
| **Streamable HTTP Transport** | ✅ Yes | ✅ Yes (FastAPI/Starlette) |
| **Standard I/O (stdio) Transport** | ❌ Flow is HTTP only | ✅ Yes (Local desktop clients) |
| **Directory Sandboxing (`PathGuard`)** | ⚠️ Basic permissions | ✅ Strict PathGuard & Canonicalisation |
| **Command Injection Guard** | ⚠️ Standard OS | ✅ Strict Binary Whitelisting |
| **SSRF Network Protection** | ❌ Not included | ✅ Pre-DNS IP Resolution Check |
| **PII & Credential Redaction** | ❌ Not included | ✅ Automated Real-Time Masking |
| **Built-in Vector GIS Tools** | ❌ None (must create FMW) | ✅ Built-in spatial intelligence |
| **Data Contracts & Scoring** | ❌ None | ✅ YAML Data Contracts & Profiling |
| **Support for Older Versions (2018.0 - 2025.x)** | ❌ Requires FME 2026+ | ✅ Full support for FME 2018.0 through 2026+ |
