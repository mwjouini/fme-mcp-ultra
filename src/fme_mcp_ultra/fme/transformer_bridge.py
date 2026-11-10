"""FME Custom Transformer Bridge Implementation.

Designed to be executed directly inside FME Workbench via a PythonCaller
or embedded Custom Transformer (.fmx) using FME's built-in Python runtime.
Zero external dependencies required.
"""

from __future__ import annotations

import contextlib
import json
import socket
import subprocess
import sys
import time
from typing import Any

DEFAULT_HOST = "127.0.0.1"
DEFAULT_PORT = 9877


def is_bridge_running(host: str = DEFAULT_HOST, port: int = DEFAULT_PORT) -> bool:
    """Check if loopback bridge socket is listening."""
    try:
        with socket.create_connection((host, port), timeout=0.5):
            return True
    except OSError:
        return False


def ensure_bridge_started(host: str = DEFAULT_HOST, port: int = DEFAULT_PORT) -> bool:
    """Ensure the fme-mcp-ultra server is active; launch if offline."""
    if is_bridge_running(host, port):
        return True

    # Attempt to auto-start using FME's internal Python interpreter
    try:
        cmd = [sys.executable, "-m", "fme_mcp_ultra.cli.main", "serve", "--transport", "stdio"]
        subprocess.Popen(
            cmd,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            stdin=subprocess.DEVNULL,
            start_new_session=True,
        )
        # Wait up to 3 seconds for socket bind
        for _ in range(6):
            time.sleep(0.5)
            if is_bridge_running(host, port):
                return True
    except Exception:
        pass
    return is_bridge_running(host, port)


class MCPAgentBridgeTransformer:
    """FME PythonCaller Transformer class for AI Agent & MCP integration."""

    def __init__(self) -> None:
        self.host = DEFAULT_HOST
        self.port = DEFAULT_PORT
        self.connected = False
        self.sock: socket.socket | None = None
        self._setup_connection()

    def _setup_connection(self) -> None:
        """Connect to the local loopback bridge."""
        if ensure_bridge_started(self.host, self.port):
            try:
                self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                self.sock.settimeout(3.0)
                self.sock.connect((self.host, self.port))
                self.connected = True
            except Exception:
                self.connected = False
                self.sock = None

    def input(self, feature: Any) -> None:
        """Process an incoming FME feature.

        Compatible with both live fmeobjects.FMEFeature and test mock objects.
        """
        # 1. Read parameters or attributes
        action = feature.getAttribute("_ai_action") or "INSPECT"
        feature_type = (
            feature.getFeatureType()
            if hasattr(feature, "getFeatureType")
            else str(feature.getAttribute("fme_feature_type") or "Feature")
        )

        # 2. Collect user attributes
        attrs: dict[str, Any] = {}
        if hasattr(feature, "getAllAttributeNames"):
            for name in feature.getAllAttributeNames():
                if not name.startswith("fme_") and not name.startswith("_mcp_"):
                    attrs[name] = feature.getAttribute(name)

        payload = {
            "jsonrpc": "2.0",
            "method": "bridge_event",
            "params": {
                "event": "feature_process",
                "action": action,
                "feature_type": feature_type,
                "attributes": attrs,
                "timestamp": time.time(),
            },
        }

        # 3. Transmit through loopback bridge
        response_text = ""
        status = "OFFLINE"
        if self.connected and self.sock:
            try:
                msg = (json.dumps(payload) + "\n").encode("utf-8")
                self.sock.sendall(msg)
                status = "CONNECTED"
                response_text = (
                    f"Feature '{feature_type}' streamed to AI Agent via port {self.port}"
                )
            except Exception as exc:
                status = f"ERROR: {exc}"
                self.connected = False
        else:
            status = "BRIDGE_STANDALONE"
            response_text = "FME processed feature locally (Bridge daemon offline)"

        # 4. Set enrichment attributes on feature
        feature.setAttribute("_mcp_status", status)
        feature.setAttribute("_mcp_bridge_port", self.port)
        feature.setAttribute("_ai_response", response_text)

        # Output feature to next transformer in pipeline
        if hasattr(self, "pyoutput"):
            self.pyoutput(feature)

    def close(self) -> None:
        """Close socket connection on translation termination."""
        if self.sock:
            with contextlib.suppress(Exception):
                self.sock.close()
            self.sock = None
            self.connected = False
