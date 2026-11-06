# Configuration Reference

All settings can be configured via environment variables (prefixed with `FME_MCP_`), a `.env` file, or command-line parameters.

| Variable | Default | Description |
| :--- | :--- | :--- |
| `FME_MCP_HOST` | `0.0.0.0` | Host address to bind HTTP/SSE server |
| `FME_MCP_PORT` | `8000` | Port for HTTP/SSE transport |
| `FME_MCP_TRANSPORT` | `stdio` | Transport mechanism (`stdio` or `streamable-http`) |
| `FME_MCP_LOG_LEVEL` | `INFO` | Logging verbosity (`DEBUG`, `INFO`, `WARNING`, `ERROR`) |
| `FME_ALLOWED_DIRS` | Current working directory | Semicolon-separated file-system allowlist for PathGuard |
| `FME_ALLOWED_OUTBOUND_DOMAINS` | `safe.com,github.com` | Whitelist for outbound federation calls (SSRF Guard) |
| `FME_DIR` | Auto-detected | Local FME Form installation directory |
| `FME_TIMEOUT_SECONDS` | `600` | Maximum execution timeout for workspaces |
| `FME_FLOW_URL` | None | Base URL of enterprise FME Flow instance |
| `FME_FLOW_TOKEN` | None | Bearer token for FME Flow REST authentication |

