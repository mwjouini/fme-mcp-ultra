"""Utility Tools: Diagnostics, environment introspection, and low-level FME execution."""

from __future__ import annotations

from typing import Any

from fme_mcp_ultra import __version__
from fme_mcp_ultra.core.schema import MCPToolResponse
from fme_mcp_ultra.fme.fme_form_client import fme_form_client


def fme_info() -> dict[str, Any]:
    """Retrieve full FME Form installation, build, licensing, and runtime details."""
    info = fme_form_client.get_info()
    return MCPToolResponse(success=True, data=info).to_dict()


def fme_list_transformers(search: str | None = None) -> dict[str, Any]:
    """List transformers installed in FME Form with optional keyword filtering.

    Args:
        search: Optional search term (e.g. 'Buffer', 'Tester', 'Spatial').
    """
    tfs = fme_form_client.list_transformers(search=search)
    return MCPToolResponse(
        success=True,
        data={"count": len(tfs), "search": search, "transformers": tfs},
    ).to_dict()


def fme_list_packages() -> dict[str, Any]:
    """List official FME Hub packages installed on the local system."""
    pkgs = fme_form_client.list_packages()
    return MCPToolResponse(success=True, data={"count": len(pkgs), "packages": pkgs}).to_dict()


def fme_execute_python(code: str, timeout_seconds: int = 120) -> dict[str, Any]:
    """Execute arbitrary Python code inside FME Form's embedded Python runtime (with fmeobjects).

    Args:
        code: Python script content to run.
        timeout_seconds: Process execution timeout in seconds (default 120).
    """
    res = fme_form_client.execute_python(code, timeout_seconds=timeout_seconds)
    return MCPToolResponse(
        success=res["success"],
        duration_seconds=res.get("duration_seconds"),
        data=res,
    ).to_dict()


def util_ping() -> dict[str, Any]:
    """Health check ping verifying that fme-mcp-ultra server is active and responsive."""
    return MCPToolResponse(
        success=True, data={"status": "pong", "server": "fme-mcp-ultra"}
    ).to_dict()


def util_version() -> dict[str, Any]:
    """Retrieve current version and licensing metadata of fme-mcp-ultra."""
    return MCPToolResponse(
        success=True,
        data={
            "version": __version__,
            "license": "Apache-2.0",
            "vendor": "Safe Software Partner Community",
        },
    ).to_dict()


def util_validate_coordinates(latitude: float, longitude: float) -> dict[str, Any]:
    """Validate whether geographic coordinates fall within standard WGS84 ranges.

    Args:
        latitude: Latitude (-90.0 to 90.0).
        longitude: Longitude (-180.0 to 180.0).
    """
    valid_lat = -90.0 <= latitude <= 90.0
    valid_lon = -180.0 <= longitude <= 180.0
    return MCPToolResponse(
        success=valid_lat and valid_lon,
        data={
            "latitude": latitude,
            "longitude": longitude,
            "valid_latitude": valid_lat,
            "valid_longitude": valid_lon,
        },
    ).to_dict()
