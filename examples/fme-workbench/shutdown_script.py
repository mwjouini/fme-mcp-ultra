# ==============================================================================
# FME Workbench Shutdown Python Script
# ==============================================================================
# Paste this entire script into FME Workbench:
# Navigator -> Workspace Parameters -> Scripting -> Shutdown Python Script
#
# Notifies fme-mcp-ultra when translation finishes (status, features read/written).
# If fme-mcp-ultra is not running, it fails silently with 0 overhead.
# ==============================================================================

import json
import socket
import time

try:
    import fme

    _status = "SUCCESS" if getattr(fme, "status", True) else "FAILED"
    _failure_msg = getattr(fme, "failureMessage", "")
    _features_read = getattr(fme, "featuresRead", 0)
    _features_written = getattr(fme, "featuresWritten", 0)
    _workspace_name = getattr(fme, "macroValues", {}).get("FME_WORKSPACE_NAME", "Unknown Workspace")
except ImportError:
    _status = "UNKNOWN"
    _failure_msg = ""
    _features_read = 0
    _features_written = 0
    _workspace_name = "Unknown Workspace"

_payload = {
    "event": "translation_finished",
    "timestamp": time.time(),
    "workspace": _workspace_name,
    "status": _status,
    "features_read": _features_read,
    "features_written": _features_written,
    "failure_message": _failure_msg,
}

try:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as _sock:
        _sock.settimeout(0.3)
        _sock.connect(("127.0.0.1", 9877))
        _sock.sendall((json.dumps(_payload) + "\n").encode("utf-8"))
except Exception:
    pass  # Fail silently if bridge server is not active
