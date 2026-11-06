"""Integration tests for MCP Server protocol execution."""

import pytest
from pathlib import Path
from fme_mcp_ultra.server.mcp_server import mcp_server


@pytest.mark.asyncio
async def test_mcp_server_lists_all_tools():
    tools = await mcp_server.list_tools()
    tool_names = [t.name for t in tools]

    # Verify key tools from all domains are exposed
    assert "fme_info" in tool_names
    assert "fme_discover_workspaces" in tool_names
    assert "fme_get_workspace" in tool_names
    assert "fme_run_workspace" in tool_names
    assert "gis_reproject" in tool_names
    assert "gis_buffer" in tool_names
    assert "data_read_metadata" in tool_names
    assert "quality_score_dataset" in tool_names
    assert "catalog_register_asset" in tool_names
    assert "workflow_create" in tool_names
    assert "mcp_register_server" in tool_names
    assert "gov_redact_pii" in tool_names
    assert "util_ping" in tool_names


@pytest.mark.asyncio
async def test_mcp_server_call_ping():
    res = await mcp_server.call_tool("util_ping", {})
    assert res is not None
    assert "pong" in res.content[0].text


@pytest.mark.asyncio
async def test_mcp_server_call_reproject():
    res = await mcp_server.call_tool(
        "gis_reproject",
        {"x": 2.3522, "y": 48.8566, "source_epsg": 4326, "target_epsg": 3857},
    )
    assert res is not None
    assert "target_epsg" in res.content[0].text


@pytest.mark.asyncio
async def test_mcp_server_inspect_geolocalisation_fmw():
    sample_fmw = Path("E:/fme_mcp/geolocalisation.fmw")
    if sample_fmw.exists():
        res = await mcp_server.call_tool("fme_get_workspace", {"workspace_path": str(sample_fmw)})
        assert res is not None
        assert "geolocalisation.fmw" in res.content[0].text
