# ==============================================================================
# FME Workbench Startup Python Script
# ==============================================================================
# Paste this entire script into FME Workbench:
# Navigator -> Workspace Parameters -> Scripting -> Startup Python Script
#
# This sends an interactive event to the local fme-mcp-ultra bridge (127.0.0.1:9877).
# If fme-mcp-ultra is not running, it fails silently with 0 overhead.
# ==============================================================================

import json
import socket
import time

try:
    import fme

    _workspace_name = getattr(fme, "macroValues", {}).get("FME_WORKSPACE_NAME", "Unknown Workspace")
except ImportError:
    _workspace_name = "Unknown Workspace"

_payload = {
    "event": "translation_started",
    "timestamp": time.time(),
    "workspace": _workspace_name,
}

try:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as _sock:
        _sock.settimeout(0.3)
        _sock.connect(("127.0.0.1", 9877))
        _sock.sendall((json.dumps(_payload) + "\n").encode("utf-8"))
except Exception:
    pass  # Fail silently if bridge server is not active
