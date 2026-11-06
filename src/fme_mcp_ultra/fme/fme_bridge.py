"""FME Live Bridge: Loopback TCP socket bridge connecting FME Desktop and MCP clients.

Inspired by the qgis-mcp architecture (nkarasiak/qgis-mcp), this bridge allows
AI agents to interact with a running FME desktop session over a secure local
loopback socket (127.0.0.1:9877).
"""

from __future__ import annotations

import json
import socket
import threading
import time
from typing import Any, Callable, Dict, Optional

from fme_mcp_ultra.core.logging import get_logger
from fme_mcp_ultra.fme.fme_form_client import fme_form_client

logger = get_logger("fme-bridge")

DEFAULT_BRIDGE_HOST = "127.0.0.1"
DEFAULT_BRIDGE_PORT = 9877


class FMEBridgeServer:
    """Non-blocking TCP socket server handling JSON-RPC commands for FME."""

    def __init__(self, host: str = DEFAULT_BRIDGE_HOST, port: int = DEFAULT_BRIDGE_PORT) -> None:
        self.host = host
        self.port = port
        self.running = False
        self._server_sock: Optional[socket.socket] = None
        self._thread: Optional[threading.Thread] = None
        self._handlers: Dict[str, Callable[[Dict[str, Any]], Dict[str, Any]]] = {
            "ping": self._handle_ping,
            "diagnose": self._handle_diagnose,
            "inspect_canvas": self._handle_inspect_canvas,
            "open_workbench": self._handle_open_workbench,
            "open_inspector": self._handle_open_inspector,
            "preview_dataset": self._handle_preview_dataset,
            "execute_code": self._handle_execute_code,
        }

    def start(self) -> None:
        """Start listening on the loopback port."""
        if self.running:
            return

        self._server_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._server_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self._server_sock.bind((self.host, self.port))
        self._server_sock.listen(5)
        self.running = True

        self._thread = threading.Thread(target=self._accept_loop, daemon=True)
        self._thread.start()
        logger.info(f"FME Live Bridge server listening on {self.host}:{self.port}")

    def stop(self) -> None:
        """Stop the loopback server."""
        self.running = False
        if self._server_sock:
            try:
                self._server_sock.close()
            except Exception:
                pass
        logger.info("FME Live Bridge server stopped.")

    def _accept_loop(self) -> None:
        while self.running and self._server_sock:
            try:
                client_sock, addr = self._server_sock.accept()
                threading.Thread(target=self._handle_client, args=(client_sock,), daemon=True).start()
            except Exception:
                break

    def _handle_client(self, client_sock: socket.socket) -> None:
        with client_sock:
            try:
                raw_data = client_sock.recv(65536)
                if not raw_data:
                    return

                req = json.loads(raw_data.decode("utf-8"))
                cmd = req.get("command", "")
                params = req.get("params", {})

                handler = self._handlers.get(cmd)
                if handler:
                    resp_payload = handler(params)
                    response = {"status": "SUCCESS", "result": resp_payload}
                else:
                    response = {"status": "ERROR", "error": f"Unknown command: '{cmd}'"}

                client_sock.sendall(json.dumps(response).encode("utf-8"))
            except Exception as e:
                err_resp = {"status": "ERROR", "error": str(e)}
                try:
                    client_sock.sendall(json.dumps(err_resp).encode("utf-8"))
                except Exception:
                    pass

    def _handle_ping(self, params: Dict[str, Any]) -> Dict[str, Any]:
        return {"pong": True, "timestamp": time.time()}

    def _handle_diagnose(self, params: Dict[str, Any]) -> Dict[str, Any]:
        return fme_form_client.diagnose()

    def _handle_inspect_canvas(self, params: Dict[str, Any]) -> Dict[str, Any]:
        return fme_form_client.inspect_canvas(params.get("workspace_path", ""))

    def _handle_open_workbench(self, params: Dict[str, Any]) -> Dict[str, Any]:
        return fme_form_client.open_in_workbench(params.get("workspace_path", ""))

    def _handle_open_inspector(self, params: Dict[str, Any]) -> Dict[str, Any]:
        return fme_form_client.open_in_inspector(params.get("dataset_path", ""))

    def _handle_preview_dataset(self, params: Dict[str, Any]) -> Dict[str, Any]:
        return fme_form_client.preview_dataset(params.get("dataset_path", ""), params.get("limit", 10))

    def _handle_execute_code(self, params: Dict[str, Any]) -> Dict[str, Any]:
        return fme_form_client.execute_python(params.get("code", ""))


class FMEBridgeClient:
    """Client that sends JSON commands to a running FMEBridgeServer."""

    def __init__(self, host: str = DEFAULT_BRIDGE_HOST, port: int = DEFAULT_BRIDGE_PORT) -> None:
        self.host = host
        self.port = port

    def is_bridge_active(self, timeout: float = 0.5) -> bool:
        """Check if the local FME Bridge daemon is reachable."""
        try:
            with socket.create_connection((self.host, self.port), timeout=timeout):
                return True
        except Exception:
            return False

    def send_command(self, command: str, params: Optional[Dict[str, Any]] = None, timeout: float = 30.0) -> Dict[str, Any]:
        """Send command over loopback socket and return parsed response."""
        req = {"command": command, "params": params or {}}
        with socket.create_connection((self.host, self.port), timeout=timeout) as sock:
            sock.sendall(json.dumps(req).encode("utf-8"))
            data = sock.recv(65536)
            return json.loads(data.decode("utf-8"))


# Global singleton instances
fme_bridge_server = FMEBridgeServer()
fme_bridge_client = FMEBridgeClient()

