# FME 2026 Parity & Transcendence Strategy

Safe Software announced and released official Model Context Protocol (MCP) integrations starting with FME 2026:
1. **FME 2026.1**: `safe.mcp` / `MCPCaller` on FME Hub (Client mode, allowing FME to call external MCP tools).
2. **FME 2026.2**: FME Flow Native MCP Server (Server mode, exposing workspaces as MCP tools).

---

## ⚖️ Parity Matrix

`fme-mcp-ultra` implements both modes simultaneously in a single, unified runtime:

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
| **Support for FME 2025.2** | ❌ Requires 2026+ | ✅ Native 2025.2 support |

