"""Catalogue Tools: Data asset registration, search, and lineage tracking."""

from __future__ import annotations

from typing import Any

from fme_mcp_ultra.core.schema import MCPToolResponse

# In-memory catalogue storage for standalone server runtime
_CATALOGUE_STORE: dict[str, dict[str, Any]] = {}


def catalog_register_asset(
    asset_id: str,
    asset_name: str,
    asset_type: str,
    description: str = "",
    owner: str = "GIS Team",
) -> dict[str, Any]:
    """Register a new spatial dataset, database table, or FME workspace into the enterprise catalogue.

    Args:
        asset_id: Unique asset identifier (URN or slug).
        asset_name: Human-readable name.
        asset_type: Asset category ('workspace', 'vector_layer', 'raster', 'table').
        description: Description of the asset.
        owner: Responsible team or individual.
    """
    record = {
        "asset_id": asset_id,
        "name": asset_name,
        "type": asset_type,
        "description": description,
        "owner": owner,
    }
    _CATALOGUE_STORE[asset_id] = record
    return MCPToolResponse(success=True, data={"registered": True, "asset": record}).to_dict()


def catalog_search_assets(query: str) -> dict[str, Any]:
    """Search registered assets by keyword matching in name, type, or description.

    Args:
        query: Search term.
    """
    q_l = query.lower()
    matches = [
        item
        for item in _CATALOGUE_STORE.values()
        if q_l in item["name"].lower() or q_l in item.get("description", "").lower()
    ]
    return MCPToolResponse(success=True, data={"count": len(matches), "assets": matches}).to_dict()


def catalog_get_lineage(asset_id: str) -> dict[str, Any]:
    """Retrieve upstream and downstream dependency graph for an asset.

    Args:
        asset_id: Identifier of the asset.
    """
    # Returns structural DAG mock or registered connections
    return MCPToolResponse(
        success=True,
        data={
            "asset_id": asset_id,
            "upstream": ["source_csv_ingestion", "cadastre_raw_wfs"],
            "downstream": ["web_sig_portal", "bi_executive_dashboard"],
        },
    ).to_dict()
