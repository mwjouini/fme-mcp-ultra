# Deployment Overview

`fme-mcp-ultra` can be deployed across several topologies depending on your operational requirements:

1. **Local Desktop Stdio Mode**: Directly coupled with AI clients like Claude Desktop, Cursor, or Antigravity on a workstation with local FME Form installed.
2. **Containerised Streamable HTTP Server**: Deployed via Docker or Kubernetes adjacent to an enterprise FME Flow cluster or spatial database.
3. **Hybrid Gateway**: Operating in front of both local developer workstations and shared cloud FME Flow instances.

---

## Deployment Architectures

```mermaid
flowchart TD
    subgraph Workstation["Developer Workstation"]
        Client1["Claude Desktop / Cursor"] --> |stdio| LocalServer["fme-mcp-ultra (Local)"]
        LocalServer --> FMEForm["FME Form 2025.2 (fme.exe)"]
    end

    subgraph EnterpriseCloud["Enterprise Cloud / Kubernetes"]
        Client2["Enterprise AI Copilots"] --> |HTTPS / SSE| CloudServer["fme-mcp-ultra (Pod)"]
        CloudServer --> FMEFlow["FME Flow Engine Pool"]
        CloudServer --> PostGIS["PostGIS / Spatial DB"]
    end
```

