# MCP Client Integration Guide

Step-by-step configuration for leading Model Context Protocol clients.

---

## 1. Claude Desktop

Locate your configuration file:
- **Windows**: `%APPDATA%\Claude\claude_desktop_config.json`
- **macOS**: `~/Library/Application Support/Claude/claude_desktop_config.json`
- **Linux**: `~/.config/Claude/claude_desktop_config.json`

Add the following block:
```json
{
  "mcpServers": {
    "fme-mcp-ultra": {
      "command": "uvx",
      "args": ["fme-mcp-ultra", "serve", "--transport", "stdio"],
      "env": {
        "FME_DIR": "C:\\Program Files\\FME",
        "FME_ALLOWED_DIRS": "C:\\Program Files\\FME;E:\\fme_mcp"
      }
    }
  }
}
```

---

## 2. Cursor IDE

In Cursor Settings (`Features -> MCP Servers`), add:
- **Name**: `fme-mcp-ultra`
- **Type**: `command`
- **Command**: `fme-mcp-ultra serve --transport stdio`

---

## 3. Antigravity

In your Antigravity agent configuration:
```json
{
  "mcpServers": {
    "fme-mcp-ultra": {
      "command": "E:/fme_mcp/.venv/Scripts/python.exe",
      "args": ["-m", "fme_mcp_ultra", "serve", "--transport", "stdio"]
    }
  }
}
```
