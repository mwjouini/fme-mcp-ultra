# MCP Client Integration Guide

Step-by-step configuration for leading Model Context Protocol clients.

`fme-mcp-ultra` features zero-configuration auto-detection for FME Form installations (`C:\Program Files\FME`, `/opt/fme`, or system `PATH`) and automatically grants access to the user's working and home directories.

---

## 1. Claude Desktop

Locate your configuration file:
- **Windows**: `%APPDATA%\Claude\claude_desktop_config.json`
- **macOS**: `~/Library/Application Support/Claude/claude_desktop_config.json`
- **Linux**: `~/.config/Claude/claude_desktop_config.json`

### Standard Setup (via `uvx` — Zero Configuration)
```json
{
  "mcpServers": {
    "fme-mcp-ultra": {
      "command": "uvx",
      "args": ["fme-mcp-ultra", "serve", "--transport", "stdio"]
    }
  }
}
```

### Advanced Setup (Custom Directories & FME Flow)
If FME is installed in a non-standard path, or if you wish to restrict/allow explicit directories or connect to FME Flow:
```json
{
  "mcpServers": {
    "fme-mcp-ultra": {
      "command": "uvx",
      "args": ["fme-mcp-ultra", "serve", "--transport", "stdio"],
      "env": {
        "FME_MCP_FME_DIR": "C:\\Program Files\\FME",
        "FME_MCP_ALLOWED_DIRS": "C:\\Workspaces;D:\\GIS_Data",
        "FME_MCP_FME_FLOW_URL": "https://fme-flow.yourcompany.org",
        "FME_MCP_FME_FLOW_TOKEN": "your-token-here"
      }
    }
  }
}
```

---

## 2. Cursor & Windsurf

In Cursor Settings (`Features -> MCP Servers`), add:
- **Name**: `fme-mcp-ultra`
- **Type**: `command`
- **Command**: `uvx fme-mcp-ultra serve --transport stdio`

*(Or if installed in your Python environment: `fme-mcp-ultra serve --transport stdio`)*

---

## 3. Antigravity & VS Code (Cline / Roo Code)

In your agent configuration file:
```json
{
  "mcpServers": {
    "fme-mcp-ultra": {
      "command": "fme-mcp-ultra",
      "args": ["serve", "--transport", "stdio"]
    }
  }
}
```

