"""MCP Federation Tools: Outbound MCP client allowing FME to call external MCP servers."""

from __future__ import annotations

from typing import Any, Dict, List, Optional
from fme_mcp_ultra.core.schema import MCPToolResponse
from fme_mcp_ultra.security.ssrf_guard import ssrf_guard

_FEDERATED_SERVERS: Dict[str, Dict[str, Any]] = {}


def mcp_register_server(
    server_id: str,
    server_url: str,
    transport: str = "http",
    auth_token: Optional[str] = None,
) -> Dict[str, Any]:
    """Register a remote federated MCP server.

    Args:
        server_id: Unique handle for the remote server.
        server_url: URL for Streamable HTTP or endpoint.
        transport: Transport mechanism ('http' or 'stdio').
        auth_token: Optional bearer token for authentication.
    """
    if transport == "http":
        ssrf_guard.validate_url(server_url)

    _FEDERATED_SERVERS[server_id] = {
        "server_id": server_id,
        "url": server_url,
        "transport": transport,
        "active": True,
    }
    return MCPToolResponse(
        success=True,
        data={"server_id": server_id, "registered": True, "transport": transport},
    ).to_dict()


def mcp_list_servers() -> Dict[str, Any]:
    """List all connected federated MCP servers."""
    return MCPToolResponse(
        success=True,
        data={"count": len(_FEDERATED_SERVERS), "servers": list(_FEDERATED_SERVERS.values())},
    ).to_dict()
