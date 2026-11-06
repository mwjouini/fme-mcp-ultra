"""Model Context Protocol (MCP) Server for Safe Software FME (2018.0 - 2026+).

Exposes enterprise FME Form & Flow operations as standardized MCP tools.
"""

from __future__ import annotations

from typing import Any

from mcp.server.mcpserver import MCPServer

from fme_mcp_ultra import __version__
from fme_mcp_ultra.tools.ai import ai_tools
from fme_mcp_ultra.tools.catalog import catalog_tools
from fme_mcp_ultra.tools.datasets import dataset_tools
from fme_mcp_ultra.tools.governance import governance_tools
from fme_mcp_ultra.tools.mcp_federation import federation_tools
from fme_mcp_ultra.tools.orchestration import workflow_tools
from fme_mcp_ultra.tools.quality import quality_tools
from fme_mcp_ultra.tools.spatial import spatial_tools
from fme_mcp_ultra.tools.utilities import util_tools
from fme_mcp_ultra.tools.workspaces import workspace_tools

# Initialise standard MCP Server
mcp_server = MCPServer(
    name="fme-mcp-ultra",
    version=__version__,
    instructions=(
        "Model Context Protocol (MCP) server for Safe Software FME (2018.0 - 2026+). "
        "Allows AI agents to discover, inspect, and execute spatial data transformation workspaces, "
        "reproject coordinates, validate geometries, enforce data contracts, and query audit trails."
    ),
)


# ==============================================================================
# WORKSPACE TOOLS
# ==============================================================================


@mcp_server.tool()
def fme_discover_workspaces(directory: str | None = None, recursive: bool = True) -> dict[str, Any]:
    """Discover all FME workspace files (.fmw) in an authorised directory."""
    return workspace_tools.fme_discover_workspaces(directory=directory, recursive=recursive)


@mcp_server.tool()
def fme_get_workspace(workspace_path: str) -> dict[str, Any]:
    """Retrieve detailed inspection metadata, published parameters, transformers, and readers/writers."""
    return workspace_tools.fme_get_workspace(workspace_path=workspace_path)


@mcp_server.tool()
def fme_get_workspace_parameters(workspace_path: str) -> dict[str, Any]:
    """Retrieve published parameters and default values for an FME workspace."""
    return workspace_tools.fme_get_workspace_parameters(workspace_path=workspace_path)


@mcp_server.tool()
def fme_run_workspace(
    workspace_path: str,
    parameters: dict[str, Any] | None = None,
    log_file: str | None = None,
    timeout_seconds: int | None = None,
) -> dict[str, Any]:
    """Execute an FME workspace synchronously with parameter overrides and execution log analysis."""
    return workspace_tools.fme_run_workspace(
        workspace_path=workspace_path,
        parameters=parameters,
        log_file=log_file,
        timeout_seconds=timeout_seconds,
    )


@mcp_server.tool()
def fme_compare_workspaces(workspace_a: str, workspace_b: str) -> dict[str, Any]:
    """Compare two FME workspaces to identify differences in parameters, transformers, and datasets."""
    return workspace_tools.fme_compare_workspaces(workspace_a=workspace_a, workspace_b=workspace_b)


@mcp_server.tool()
def fme_enrich_geolocalisation(
    source_csv: str | None = None,
    output_geoloc_xlsx: str | None = None,
    output_non_geoloc_xlsx: str | None = None,
    output_gpkg: str | None = None,
) -> dict[str, Any]:
    """Execute the enriched geolocalisation pipeline with automatic BAN geocoding and GeoPackage output."""
    return workspace_tools.fme_enrich_geolocalisation(
        source_csv=source_csv,
        output_geoloc_xlsx=output_geoloc_xlsx,
        output_non_geoloc_xlsx=output_non_geoloc_xlsx,
        output_gpkg=output_gpkg,
    )


@mcp_server.tool()
def fme_diagnose() -> dict[str, Any]:
    """Run comprehensive system diagnostic for FME Form & Flow."""
    return workspace_tools.fme_diagnose()


@mcp_server.tool()
def fme_open_in_workbench(workspace_path: str) -> dict[str, Any]:
    """Launch or bring to focus FME Workbench GUI with the specified workspace."""
    return workspace_tools.fme_open_in_workbench(workspace_path=workspace_path)


@mcp_server.tool()
def fme_open_in_inspector(dataset_path: str) -> dict[str, Any]:
    """Launch FME Data Inspector GUI with the specified dataset for visual feature/map inspection."""
    return workspace_tools.fme_open_in_inspector(dataset_path=dataset_path)


@mcp_server.tool()
def fme_inspect_canvas(workspace_path: str) -> dict[str, Any]:
    """Extract structured visual canvas graph from an FME workspace (.fmw)."""
    return workspace_tools.fme_inspect_canvas(workspace_path=workspace_path)


@mcp_server.tool()
def fme_preview_dataset(dataset_path: str, limit: int = 10) -> dict[str, Any]:
    """Preview features and schema from any dataset produced or consumed by FME (.gpkg, .xlsx, .csv)."""
    return workspace_tools.fme_preview_dataset(dataset_path=dataset_path, limit=limit)


# ==============================================================================
# SPATIAL TOOLS
# ==============================================================================


@mcp_server.tool()
def gis_reproject(
    x: float,
    y: float,
    source_epsg: int = 4326,
    target_epsg: int = 2154,
) -> dict[str, Any]:
    """Reproject 2D coordinates between common CRS (EPSG:4326 WGS84, EPSG:2154 Lambert-93, EPSG:3857 Web Mercator)."""
    return spatial_tools.gis_reproject(x=x, y=y, source_epsg=source_epsg, target_epsg=target_epsg)


@mcp_server.tool()
def gis_buffer(
    center_lon: float,
    center_lat: float,
    radius_metres: float,
    num_points: int = 32,
) -> dict[str, Any]:
    """Generate a geographic circular buffer polygon as a standard GeoJSON geometry."""
    return spatial_tools.gis_buffer(
        center_lon=center_lon,
        center_lat=center_lat,
        radius_metres=radius_metres,
        num_points=num_points,
    )


@mcp_server.tool()
def gis_validate_geometry(geojson_geometry: dict[str, Any]) -> dict[str, Any]:
    """Validate a GeoJSON geometry for structural completeness and closed rings."""
    return spatial_tools.gis_validate_geometry(geojson_geometry=geojson_geometry)


# ==============================================================================
# DATASET TOOLS
# ==============================================================================


@mcp_server.tool()
def data_read_metadata(dataset_path: str) -> dict[str, Any]:
    """Extract metadata, file size, line counts, and format characteristics of a dataset."""
    return dataset_tools.data_read_metadata(dataset_path=dataset_path)


@mcp_server.tool()
def data_profile(dataset_path: str, max_rows: int = 1000) -> dict[str, Any]:
    """Profile tabular data (completeness, null counts, distinct values) up to max_rows."""
    return dataset_tools.data_profile(dataset_path=dataset_path, max_rows=max_rows)


# ==============================================================================
# QUALITY TOOLS
# ==============================================================================


@mcp_server.tool()
def quality_score_dataset(dataset_path: str) -> dict[str, Any]:
    """Calculate an overall data quality index (0-100) based on attribute completeness."""
    return quality_tools.quality_score_dataset(dataset_path=dataset_path)


@mcp_server.tool()
def quality_generate_data_contract(
    dataset_name: str, schema_columns: dict[str, str]
) -> dict[str, Any]:
    """Generate a machine-readable Data Contract YAML specification."""
    return quality_tools.quality_generate_data_contract(
        dataset_name=dataset_name, schema_columns=schema_columns
    )


# ==============================================================================
# CATALOGUE & LINEAGE TOOLS
# ==============================================================================


@mcp_server.tool()
def catalog_register_asset(
    asset_id: str,
    asset_name: str,
    asset_type: str,
    description: str = "",
    owner: str = "GIS Team",
) -> dict[str, Any]:
    """Register a new spatial dataset, database table, or FME workspace into the enterprise catalogue."""
    return catalog_tools.catalog_register_asset(
        asset_id=asset_id,
        asset_name=asset_name,
        asset_type=asset_type,
        description=description,
        owner=owner,
    )


@mcp_server.tool()
def catalog_search_assets(query: str) -> dict[str, Any]:
    """Search registered assets by keyword matching in name, type, or description."""
    return catalog_tools.catalog_search_assets(query=query)


@mcp_server.tool()
def catalog_get_lineage(asset_id: str) -> dict[str, Any]:
    """Retrieve upstream and downstream dependency graph for an asset."""
    return catalog_tools.catalog_get_lineage(asset_id=asset_id)


# ==============================================================================
# WORKFLOW ORCHESTRATION TOOLS
# ==============================================================================


@mcp_server.tool()
def workflow_create(
    name: str, steps: list[dict[str, Any]], description: str = ""
) -> dict[str, Any]:
    """Define a multi-step execution workflow DAG chaining FME workspaces and validation checks."""
    return workflow_tools.workflow_create(name=name, steps=steps, description=description)


@mcp_server.tool()
def workflow_get(workflow_id: str) -> dict[str, Any]:
    """Retrieve details and step graph of a defined workflow."""
    return workflow_tools.workflow_get(workflow_id=workflow_id)


@mcp_server.tool()
def workflow_run(workflow_id: str) -> dict[str, Any]:
    """Trigger execution of an orchestrated workflow DAG."""
    return workflow_tools.workflow_run(workflow_id=workflow_id)


# ==============================================================================
# MCP FEDERATION TOOLS
# ==============================================================================


@mcp_server.tool()
def mcp_register_server(
    server_id: str,
    server_url: str,
    transport: str = "http",
    auth_token: str | None = None,
) -> dict[str, Any]:
    """Register a remote federated MCP server."""
    return federation_tools.mcp_register_server(
        server_id=server_id,
        server_url=server_url,
        transport=transport,
        auth_token=auth_token,
    )


@mcp_server.tool()
def mcp_list_servers() -> dict[str, Any]:
    """List all connected federated MCP servers."""
    return federation_tools.mcp_list_servers()


# ==============================================================================
# AI ASSISTANCE TOOLS
# ==============================================================================


@mcp_server.tool()
def ai_explain_workspace(workspace_path: str) -> dict[str, Any]:
    """Generate an architectural summary of what an FME workspace does."""
    return ai_tools.ai_explain_workspace(workspace_path=workspace_path)


@mcp_server.tool()
def ai_suggest_transformations(
    source_format: str, destination_format: str, objective: str
) -> dict[str, Any]:
    """Recommend optimal FME transformers and geometric operations for a data pipeline objective."""
    return ai_tools.ai_suggest_transformations(
        source_format=source_format,
        destination_format=destination_format,
        objective=objective,
    )


# ==============================================================================
# GOVERNANCE & REDACTION TOOLS
# ==============================================================================


@mcp_server.tool()
def gov_get_tenant_config() -> dict[str, Any]:
    """Retrieve security configuration, active guards, and quotas for the current tenant."""
    return governance_tools.gov_get_tenant_config()


@mcp_server.tool()
def gov_redact_pii(text: str) -> dict[str, Any]:
    """Scan and scrub sensitive personal data (emails, credit cards) and authentication secrets."""
    return governance_tools.gov_redact_pii(text=text)


@mcp_server.tool()
def gov_classify_dataset(
    dataset_name: str, contains_pii: bool = False, is_internal_only: bool = True
) -> dict[str, Any]:
    """Assign data governance classification tags (PUBLIC, INTERNAL, CONFIDENTIAL, RESTRICTED)."""
    return governance_tools.gov_classify_dataset(
        dataset_name=dataset_name,
        contains_pii=contains_pii,
        is_internal_only=is_internal_only,
    )


# ==============================================================================
# UTILITY TOOLS
# ==============================================================================


@mcp_server.tool()
def fme_info() -> dict[str, Any]:
    """Retrieve full FME Form installation, build, licensing, and runtime details."""
    return util_tools.fme_info()


@mcp_server.tool()
def fme_list_transformers(search: str | None = None) -> dict[str, Any]:
    """List transformers installed in FME Form with optional keyword filtering."""
    return util_tools.fme_list_transformers(search=search)


@mcp_server.tool()
def fme_list_packages() -> dict[str, Any]:
    """List official FME Hub packages installed on the local system."""
    return util_tools.fme_list_packages()


@mcp_server.tool()
def fme_execute_python(code: str, timeout_seconds: int = 120) -> dict[str, Any]:
    """Execute arbitrary Python code inside FME Form's embedded Python runtime (with fmeobjects)."""
    return util_tools.fme_execute_python(code=code, timeout_seconds=timeout_seconds)


@mcp_server.tool()
def util_ping() -> dict[str, Any]:
    """Health check ping verifying that fme-mcp-ultra server is active and responsive."""
    return util_tools.util_ping()


@mcp_server.tool()
def util_version() -> dict[str, Any]:
    """Retrieve current version and licensing metadata of fme-mcp-ultra."""
    return util_tools.util_version()


@mcp_server.tool()
def util_validate_coordinates(latitude: float, longitude: float) -> dict[str, Any]:
    """Validate whether geographic coordinates fall within standard WGS84 ranges."""
    return util_tools.util_validate_coordinates(latitude=latitude, longitude=longitude)
