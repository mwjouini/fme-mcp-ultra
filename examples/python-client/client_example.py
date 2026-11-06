"""Demonstration Python client calling fme-mcp-ultra."""

import asyncio
from fme_mcp_ultra.server.mcp_server import mcp_server


async def main():
    print("Querying fme-mcp-ultra tools...")
    tools = await mcp_server.list_tools()
    print(f"Total tools discovered: {len(tools)}")

    # Ping health check
    ping_res = await mcp_server.call_tool("util_ping", {})
    print("Ping output:", ping_res.content[0].text)

    # Reproject coordinates
    rep_res = await mcp_server.call_tool(
        "gis_reproject",
        {"x": 2.3522, "y": 48.8566, "source_epsg": 4326, "target_epsg": 2154},
    )
    print("Reprojection output:", rep_res.content[0].text)


if __name__ == "__main__":
    asyncio.run(main())

