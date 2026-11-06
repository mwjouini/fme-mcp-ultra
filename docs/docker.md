# Docker Deployment Guide

`fme-mcp-ultra` is packaged as an OCI-compliant container image published on GitHub Container Registry:

```bash
docker pull ghcr.io/mwjouini/fme-mcp-ultra:latest
```

## Quick Start with Docker

### 1. Interactive Container Run

To run the containerised MCP server exposing Streamable HTTP on port `8000`:

```bash
docker run -d \
  --name fme-mcp-ultra \
  -p 8000:8000 \
  -e FME_MCP_TRANSPORT=streamable_http \
  -e FME_MCP_HOST=0.0.0.0 \
  -e FME_MCP_PORT=8000 \
  -e FME_MCP_API_KEY="your-strong-api-key" \
  -e FME_FLOW_URL="https://fme-flow.internal.acme.org" \
  -e FME_FLOW_TOKEN="fme-flow-api-token" \
  -v fme_data:/data \
  ghcr.io/mwjouini/fme-mcp-ultra:latest
```

### 2. Multi-Container Orchestration with Docker Compose

A standard `docker-compose.yml` is provided at the repository root:

```yaml
version: "3.8"

services:
  fme-mcp:
    image: ghcr.io/mwjouini/fme-mcp-ultra:latest
    container_name: fme-mcp-ultra
    restart: unless-stopped
    ports:
      - "8000:8000"
    environment:
      - FME_MCP_TRANSPORT=streamable_http
      - FME_MCP_HOST=0.0.0.0
      - FME_MCP_PORT=8000
      - FME_MCP_API_KEY=${FME_MCP_API_KEY:-dev-secret-key}
      - FME_FLOW_URL=${FME_FLOW_URL:-}
      - FME_FLOW_TOKEN=${FME_FLOW_TOKEN:-}
    volumes:
      - ./data:/data
      - ./audit:/var/log/fme_mcp
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/healthz"]
      interval: 30s
      timeout: 5s
      retries: 3
```

Start the stack with:

```bash
docker compose up -d
```

### 3. Hardened Security Compose Profile

For production and high-compliance environments, run with `docker-compose.security.yml` which applies:
- Read-only root filesystem (`read_only: true`).
- Dropped Linux capabilities (`cap_drop: ALL`).
- No privilege escalation (`no-new-privileges:true`).
- Non-root user `uid: 10001`.
- Ephemeral writable `/tmp` tmpfs.

```bash
docker compose -f docker-compose.yml -f docker-compose.security.yml up -d
```
