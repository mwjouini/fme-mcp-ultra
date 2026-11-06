"""Workspace Tools: Workspace discovery, inspection, and execution."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, List, Optional
from fme_mcp_ultra.core.schema import MCPToolResponse
from fme_mcp_ultra.fme.fme_form_client import fme_form_client
from fme_mcp_ultra.security.path_guard import path_guard
from fme_mcp_ultra.security.audit_log import audit_logger


def fme_discover_workspaces(directory: Optional[str] = None, recursive: bool = True) -> Dict[str, Any]:
    """Discover all FME workspace files (.fmw) in an authorised directory.

    Args:
        directory: Directory to search (defaults to current working directory).
        recursive: Whether to scan subdirectories recursively.
    """
    search_dir = path_guard.validate_path(directory or ".", must_exist=True)
    pattern = "**/*.fmw" if recursive else "*.fmw"

    workspaces = []
    for f in search_dir.glob(pattern):
        try:
            stat = f.stat()
            workspaces.append(
                {
                    "name": f.name,
                    "path": str(f.resolve()),
                    "size_bytes": stat.st_size,
                    "last_modified": stat.st_mtime,
                }
            )
        except OSError:
            continue

    audit_logger.record_event("DISCOVER_WORKSPACES", "mcp-user", "fme_discover_workspaces")
    return MCPToolResponse(
        success=True,
        data={"count": len(workspaces), "directory": str(search_dir), "workspaces": workspaces},
    ).to_dict()


def fme_get_workspace(workspace_path: str) -> Dict[str, Any]:
    """Retrieve detailed inspection metadata for a local workspace (.fmw).

    Args:
        workspace_path: Path to the .fmw workspace file.
    """
    inspection = fme_form_client.inspect_workspace(workspace_path)
    audit_logger.record_event("INSPECT_WORKSPACE", "mcp-user", "fme_get_workspace", {"path": workspace_path})
    return MCPToolResponse(success=True, data=inspection).to_dict()


def fme_get_workspace_parameters(workspace_path: str) -> Dict[str, Any]:
    """Retrieve published parameters and default values for an FME workspace.

    Args:
        workspace_path: Path to the .fmw workspace file.
    """
    inspection = fme_form_client.inspect_workspace(workspace_path)
    params = inspection.get("published_parameters", [])
    return MCPToolResponse(
        success=True,
        data={"workspace_path": workspace_path, "parameters": params},
    ).to_dict()


def fme_run_workspace(
    workspace_path: str,
    parameters: Optional[Dict[str, Any]] = None,
    log_file: Optional[str] = None,
    timeout_seconds: Optional[int] = None,
) -> Dict[str, Any]:
    """Execute an FME workspace synchronously with user-provided parameters.

    Args:
        workspace_path: Path to the .fmw workspace file.
        parameters: Key-value dictionary of published parameter overrides.
        log_file: Optional path to save the execution log file.
        timeout_seconds: Maximum execution time before aborting (default 600s).
    """
    audit_logger.record_event(
        "RUN_WORKSPACE", "mcp-user", "fme_run_workspace", {"path": workspace_path, "params": parameters}
    )
    result = fme_form_client.run_workspace(
        workspace_path=workspace_path,
        parameters=parameters,
        log_file=log_file,
        timeout_seconds=timeout_seconds,
    )
    return MCPToolResponse(
        success=result["success"],
        duration_seconds=result.get("duration_seconds"),
        data=result,
    ).to_dict()


def fme_compare_workspaces(workspace_a: str, workspace_b: str) -> Dict[str, Any]:
    """Compare two FME workspaces to identify differences in parameters, transformers, and readers/writers.

    Args:
        workspace_a: Path to the first .fmw workspace.
        workspace_b: Path to the second .fmw workspace.
    """
    info_a = fme_form_client.inspect_workspace(workspace_a)
    info_b = fme_form_client.inspect_workspace(workspace_b)

    tf_a = {t["name"]: t["count"] for t in info_a.get("transformers", [])}
    tf_b = {t["name"]: t["count"] for t in info_b.get("transformers", [])}

    all_tfs = set(tf_a.keys()).union(set(tf_b.keys()))
    tf_diffs = []
    for tf in sorted(all_tfs):
        count_a = tf_a.get(tf, 0)
        count_b = tf_b.get(tf, 0)
        if count_a != count_b:
            tf_diffs.append({"transformer": tf, "workspace_a_count": count_a, "workspace_b_count": count_b})

    return MCPToolResponse(
        success=True,
        data={
            "workspace_a": workspace_a,
            "workspace_b": workspace_b,
            "transformer_differences": tf_diffs,
            "readers_a": info_a.get("readers"),
            "readers_b": info_b.get("readers"),
            "writers_a": info_a.get("writers"),
            "writers_b": info_b.get("writers"),
        },
    ).to_dict()


def fme_enrich_geolocalisation(
    source_csv: Optional[str] = None,
    output_geoloc_xlsx: Optional[str] = None,
    output_non_geoloc_xlsx: Optional[str] = None,
    output_gpkg: Optional[str] = None,
) -> Dict[str, Any]:
    """Execute the enriched geolocalisation pipeline with automatic BAN geocoding and GeoPackage output.

    Cleans coordinate typos (trailing commas, non-numeric strings), geocodes un-located controls
    via the French National Base Adresse Nationale (BAN) API, and exports to Excel and GeoPackage.

    Args:
        source_csv: Path to input CSV file (defaults to configured SMAS control tracking CSV).
        output_geoloc_xlsx: Target path for geolocalised controls Excel workbook.
        output_non_geoloc_xlsx: Target path for non-geolocalised controls Excel workbook.
        output_gpkg: Target path for OGC GeoPackage point layer in EPSG:2154 (Lambert-93).
    """
    import subprocess
    import sys
    from pathlib import Path

    script_path = Path(r"E:\fme_mcp\run_geolocalisation_ultra.py")
    if not script_path.exists():
        return MCPToolResponse(success=False, error={"code": "SCRIPT_NOT_FOUND", "message": "Enrichment script not found"}).to_dict()

    python_exe = sys.executable
    cmd = [python_exe, str(script_path)]

    audit_logger.record_event("ENRICH_GEOLOCALISATION", "mcp-user", "fme_enrich_geolocalisation")
    res = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8", errors="replace")

    return MCPToolResponse(
        success=res.returncode == 0,
        data={
            "stdout": res.stdout,
            "stderr": res.stderr if res.returncode != 0 else None,
            "geoloc_xlsx": str(output_geoloc_xlsx or r"E:\fme_mcp\geolocalisé.xlsx"),
            "non_geoloc_xlsx": str(output_non_geoloc_xlsx or r"E:\fme_mcp\non_geolocalisé.xlsx"),
            "gpkg": str(output_gpkg or r"E:\fme_mcp\geolocalisé.gpkg"),
        },
    ).to_dict()


