# FME Desktop Live Integration

`fme-mcp-ultra` includes an interactive loopback bridge (`127.0.0.1:9877`) that allows running FME Workbench desktop sessions to report live translation events directly to connected AI agents and MCP clients.

---

## ⚡ How it Works

When you run a translation in FME Workbench:
1. The **Startup Script** notifies `fme-mcp-ultra` that translation has begun.
2. The **Shutdown Script** notifies `fme-mcp-ultra` when the translation completes (including final status, features read, features written, and error messages if failed).
3. The bridge communicates over local loopback (`127.0.0.1:9877`) in sub-millisecond time. If `fme-mcp-ultra` is not running, the scripts catch connection exceptions and fail silently with zero impact on FME.

---

## 🛠️ Step-by-Step Setup in FME Workbench

### Option A: Per-Workspace Setup

1. Open your workspace (`.fmw`) in **FME Workbench**.
2. In the **Navigator** pane (left side), expand **Workspace Parameters** -> **Scripting**.
3. Double-click **Startup Python Script**, copy and paste the code from [`examples/fme-workbench/startup_script.py`](https://github.com/mwjouini/fme-mcp-ultra/blob/main/examples/fme-workbench/startup_script.py), and click **OK**.
4. Double-click **Shutdown Python Script**, copy and paste the code from [`examples/fme-workbench/shutdown_script.py`](https://github.com/mwjouini/fme-mcp-ultra/blob/main/examples/fme-workbench/shutdown_script.py), and click **OK**.
5. Save the workspace.

### Option B: Global Setup for All Workspaces

To enable this across all workspaces automatically on your workstation:
1. Locate your FME user plugins directory:
   - **Windows**: `Documents\FME\Plugins\Python`
   - **Linux**: `~/.fme/Plugins/Python`
2. Create an `fme_mcp_bridge.py` module containing the notification logic to hook into custom transformers or default runners.

---

## 🔍 Diagnostic Verification

To check if the desktop bridge is active and reachable:
```bash
fme-mcp-ultra doctor
```
Or call the `fme_diagnose` MCP tool from Claude Desktop or Cursor.
