"""FME Workbench Interactive Bridge Hook.

Copy and paste this script into FME Workbench:
Navigator -> Workspace Parameters -> Scripting -> Startup / Shutdown Python Script.

This sends non-blocking notifications to the local `fme-mcp-ultra` bridge server
(127.0.0.1:9877) when you run translations in FME Workbench. If the bridge server
is not active, it fails silently and has zero effect on your translation.
"""

import json
import socket

BRIDGE_HOST = "127.0.0.1"
BRIDGE_PORT = 9877


def send_bridge_event(event_type: str, details: dict | None = None) -> None:
    """Send a lightweight JSON event to fme-mcp-ultra over local loopback socket."""
    payload = {
        "event": event_type,
        "details": details or {},
    }
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            sock.settimeout(0.5)  # Fast sub-second non-blocking timeout
            sock.connect((BRIDGE_HOST, BRIDGE_PORT))
            sock.sendall((json.dumps(payload) + "\n").encode("utf-8"))
    except (ConnectionRefusedError, socket.timeout, OSError):
        # Bridge server is not running or unreachable — proceed normally
        pass


# ==============================================================================
# 1. STARTUP HOOK (Paste into 'Startup Python Script')
# ==============================================================================
def on_workspace_startup() -> None:
    """Notify fme-mcp-ultra that an FME translation has started."""
    try:
        import fme  # Built-in FME Python module

        workspace_name = getattr(fme, "macroValues", {}).get("FME_WORKSPACE_NAME", "Unknown")
    except ImportError:
        workspace_name = "Unknown"

    send_bridge_event("translation_started", {"workspace": workspace_name})


# ==============================================================================
# 2. SHUTDOWN HOOK (Paste into 'Shutdown Python Script')
# ==============================================================================
def on_workspace_shutdown() -> None:
    """Notify fme-mcp-ultra of translation outcome and statistics."""
    details = {}
    try:
        import fme

        details["status"] = "SUCCESS" if getattr(fme, "status", True) else "FAILED"
        details["failure_message"] = getattr(fme, "failureMessage", "")
        details["features_read"] = getattr(fme, "featuresRead", 0)
        details["features_written"] = getattr(fme, "featuresWritten", 0)
        details["workspace"] = getattr(fme, "macroValues", {}).get("FME_WORKSPACE_NAME", "Unknown")
    except ImportError:
        details["status"] = "UNKNOWN"

    send_bridge_event("translation_finished", details)


if __name__ == "__main__":
    # If run directly as a test:
    send_bridge_event("ping", {"test": True})
    print("Bridge event sent (or ignored if server inactive).")
