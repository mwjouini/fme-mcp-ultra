# Product Roadmap

This document outlines the strategic development milestones and feature releases planned for `fme-mcp-ultra`.

## Version 1.0.0 (Released — November 2026) ✅

- **Core MCP Server**: Streamable HTTP and stdio transports based on MCP specification 1.x.
- **Universal FME Engine (2018.0 - 2026+)**:
  - Direct local FME Form execution via `fme.exe` CLI and `fmeobjects` bindings.
  - FME Flow REST API client with full authentication and workspace discovery.
- **Security Engine**:
  - Path traversal guard with canonical directory allowlists.
  - Command injection guard rejecting shell metacharacters.
  - SSRF protection against private IPv4/IPv6 ranges and cloud metadata services.
  - Sensitive parameter masking and redaction.
  - Role-Based Access Control (RBAC).
- **Core Tool Suites**:
  - Workspaces & Jobs execution and inspection.
  - Spatial analysis, coordinate reprojection, and geometry buffer operations.
  - Data engineering, profiling, quality validation, and schema inference.
  - Base Adresse Nationale (BAN) address geocoding and automated enrichment.
- **Distribution**:
  - Open-source release under Apache 2.0.
  - Automated CI/CD GitHub Actions pipeline.
  - Published on GitHub Container Registry and GitHub Releases.

## Version 1.1.0 (Target: Q1 2027) 🔄

- **FME 2026 Parity**: Native emulation of Safe Software 2026 MCP server protocols and JSON-RPC endpoints.
- **Asynchronous Webhook Reception**: Inbuilt HTTP webhook receiver for real-time FME Flow notification callbacks.
- **Enhanced Vector Indexing**: Automatic semantic indexing of workspace documentation and custom transformers using local embeddings.
- **Extended Spatial Tools**: Advanced 3D city model and BIM/IFC inspection tools via FME Quick Translator bindings.

## Version 1.2.0 (Target: Q2 2027) 📋

- **Enterprise Governance Suite**: Automated lineage graphing across multi-workspace data pipelines.
- **Federated MCP Gateway**: Downstream routing and composition across external MCP servers (PostGIS, GeoServer, QGIS, ArcGIS Enterprise).
- **High-Throughput Batch Processing**: Celery and Redis distributed job queue integration for multi-worker FME clusters.

