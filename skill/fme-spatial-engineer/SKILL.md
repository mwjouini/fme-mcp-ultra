---
name: fme-spatial-engineer
description: Professional spatial data engineering skill for Safe Software FME (2018.0 - 2026+), FME Form, FME Flow, and GIS ETL pipelines. Automates workspace discovery, parameter introspection, headless execution, CRS reprojection, geometry validation, and data quality scoring.
version: 1.1.0
author: Mohamed Wael JOUINI
homepage: https://github.com/mwjouini/fme-mcp-ultra
license: Apache-2.0
tags:
  - fme
  - safe-software
  - gis
  - geospatial
  - etl
  - data-engineering
  - spatial-analysis
  - mcp
---

# FME Spatial Data Engineer Skill

Expert AI agent skill to automate, inspect, and execute spatial data transformation pipelines using **Safe Software FME** (compatible with FME Form & FME Flow from 2018.0 through 2026+) via the `fme-mcp-ultra` Model Context Protocol (MCP) server.

---

## 🎯 When to Activate This Skill

Activate this skill whenever the user asks to:
1. **Discover or Inspect Workspaces**: Scan directories for `.fmw` files, inspect canvas connections, read published parameters, or list transformers.
2. **Execute Translations**: Run local FME Form workspaces (`fme.exe`) or submit enterprise jobs to remote FME Flow instances.
3. **Perform Geoprocessing**: Reproject coordinates between reference systems (e.g., WGS84, Web Mercator, Lambert-93), generate circular buffers, or validate polygon topologies.
4. **Audit Data Quality**: Profile tabular and geospatial datasets, detect null values, score completeness, or generate standard Data Contract YAML.
5. **Diagnose FME Environment**: Check installed FME version, licensing status, `fmeobjects` C-extension bindings, and running desktop processes.

---

## 🔌 Required MCP Server Connection

This skill connects to the `fme-mcp-ultra` MCP server.

### Client Configuration (Claude Desktop, Cursor, Antigravity, Copilot)

Add to your agent's MCP configuration:

```json
{
  "mcpServers": {
    "fme-mcp-ultra": {
      "command": "uvx",
      "args": ["fme-mcp-ultra", "serve", "--transport", "stdio"]
    }
  }
}
```

*(On Windows machines without `uvx`, replace `"command": "uvx"` with `"command": "py"` and `"args": ["-m", "fme_mcp_ultra.cli.main", "serve", "--transport", "stdio"]`)*.

---

## 🛠️ Step-by-Step Agent Workflows

### 1. Pre-Flight Diagnostic (Always Run First)
Before attempting workspace execution, verify that FME is available on the system:
1. Call `fme_diagnose` or `fme_info`.
2. Inspect the returned JSON:
   - Check `fme_installed: true`.
   - Verify `fme_version` and license status.
   - Note whether `fmeobjects_loaded` is `true` (in-memory mode) or `false` (CLI fallback mode).
3. If FME is missing, alert the user and guide them to set `FME_DIR` or use remote FME Flow.

### 2. Workspace Introspection Workflow
When a user asks about a workspace or pipeline:
1. **Discover**: Call `fme_discover_workspaces(directory="...")` to locate `.fmw` files.
2. **Inspect Canvas**: Call `fme_inspect_canvas(workspace_path="...")` to extract the visual canvas topology (transformers used, reader/writer feature types, port connections).
3. **Inspect Parameters**: Call `fme_get_workspace_parameters(workspace_path="...")` to retrieve published parameters, default values, and data types.
4. **Synthesize**: Present a structured summary to the user (pipeline objective, expected inputs, outputs, and configurable parameters).

### 3. Safe Workspace Execution Workflow
When executing a translation:
1. Validate required parameter values against `fme_get_workspace_parameters`.
2. Ensure input dataset paths exist and fall within authorized directories (`PathGuard`).
3. Call `fme_run_workspace(workspace_path="...", parameters={...})`.
4. Parse the execution summary:
   - Features read vs. features written.
   - Elapsed CPU/real time.
   - Errors or warnings in the translation log.
5. If the translation fails, analyze the fatal error message and propose actionable fixes (e.g., missing schema mapping, invalid source path, projection mismatch).

### 4. Direct Spatial Geoprocessing Workflow
When the user needs quick spatial operations without launching a full workspace:
- **Reprojection**: Use `gis_reproject(x, y, source_crs="EPSG:4326", target_crs="EPSG:2154")`.
- **Buffer**: Use `gis_buffer(geojson_geometry={...}, distance_meters=500.0)`.
- **Topology Check**: Use `gis_validate_geometry(geojson_geometry={...})` to verify closed rings and detect self-intersections.

### 5. Data Profiling & Quality Contracts
When evaluating datasets (CSV, Excel, GeoPackage, Shapefile):
1. Call `data_read_metadata(file_path="...")` to extract columns, types, and record count.
2. Call `data_profile(file_path="...")` to calculate null percentage and unique value distributions.
3. Call `quality_generate_data_contract(dataset_path="...", rules=[...])` to produce a verifiable YAML data contract.

---

## 💡 Best Practices for the AI Agent

- **Non-Destructive Execution**: Always confirm destination overwrite parameters before executing translations on production files.
- **Path Resolution**: Use absolute paths or forward slashes (`/`) for cross-platform compatibility across Windows and Linux.
- **Redaction Awareness**: Never echo sensitive credentials or FME Flow API tokens in conversational outputs (`fme-mcp-ultra` automatically masks Bearer tokens and private keys).
- **Graceful Fallbacks**: If `fmeobjects` is not compiled for the local Python version, `fme-mcp-ultra` seamlessly falls back to `fme.exe` subprocess execution. Continue normally.

---

## 💬 Example User Prompts

- *"Scan my GIS folder for FME workspaces and show me what parameters they accept."*
- *"Inspect geolocalisation.fmw and explain which transformers it uses."*
- *"Execute my geocoding workspace with the updated addresses Excel file."*
- *"Reproject these coordinates from WGS84 to Lambert-93 and validate the boundary polygon."*
- *"Generate a data quality contract for our land registry GeoPackage."*
