"""AI Tools: Intelligent diagnostics, transformer suggestions, and workspace planning."""

from __future__ import annotations

from typing import Any, Dict, List, Optional
from fme_mcp_ultra.core.schema import MCPToolResponse
from fme_mcp_ultra.fme.fme_form_client import fme_form_client


def ai_explain_workspace(workspace_path: str) -> Dict[str, Any]:
    """Generate an architectural summary of what an FME workspace does based on its readers, writers, and transformers.

    Args:
        workspace_path: Path to the .fmw workspace file.
    """
    inspection = fme_form_client.inspect_workspace(workspace_path)
    transformers = [t["name"] for t in inspection.get("transformers", [])]
    readers = inspection.get("readers", [])
    writers = inspection.get("writers", [])

    summary = (
        f"Workspace '{inspection['file_name']}' reads data from {readers or ['unspecified']} sources, "
        f"processes features through {len(transformers)} unique transformer types ({', '.join(transformers[:8])}...), "
        f"and outputs results to {writers or ['unspecified']} formats."
    )

    return MCPToolResponse(
        success=True,
        data={
            "workspace_path": workspace_path,
            "executive_summary": summary,
            "reader_formats": readers,
            "writer_formats": writers,
            "transformer_pipeline": transformers,
        },
    ).to_dict()


def ai_suggest_transformations(source_format: str, destination_format: str, objective: str) -> Dict[str, Any]:
    """Recommend optimal FME transformers and geometric operations for a data pipeline objective.

    Args:
        source_format: Origin format (e.g. 'CSV', 'SHP', 'DWG').
        destination_format: Target format (e.g. 'GeoJSON', 'PostGIS', 'GPKG').
        objective: Natural language task description (e.g. 'Geocode addresses, calculate 500m buffers, and filter active zones').
    """
    suggestions = []
    obj_l = objective.lower()

    if "buffer" in obj_l:
        suggestions.append({"transformer": "Bufferer", "role": "Calculates geometric buffer zones around points/lines/polygons."})
    if "reproject" in obj_l or "coordinate" in obj_l:
        suggestions.append({"transformer": "CsmapReprojector", "role": "Reprojects coordinates between national and global CRS."})
    if "filter" in obj_l or "test" in obj_l:
        suggestions.append({"transformer": "Tester", "role": "Filters features based on attribute values and relational comparisons."})
    if "join" in obj_l or "merge" in obj_l:
        suggestions.append({"transformer": "FeatureJoiner", "role": "Performs relational joins on shared attribute keys."})
    if "spatial" in obj_l or "intersect" in obj_l:
        suggestions.append({"transformer": "SpatialFilter", "role": "Performs geometric spatial queries (within, intersects, contains)."})

    if not suggestions:
        suggestions.append({"transformer": "AttributeManager", "role": "Manages, renames, creates, and strips dataset attributes."})

    return MCPToolResponse(
        success=True,
        data={
            "source_format": source_format,
            "destination_format": destination_format,
            "recommended_transformers": suggestions,
        },
    ).to_dict()

