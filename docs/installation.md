# Installation

`fme-mcp-ultra` can be executed locally, installed via `pip`, run with `uvx`, or deployed as an enterprise container.

---

## 1. Using `uvx` (Fastest, No Install Required)

```bash
uvx fme-mcp-ultra serve --transport stdio
```

---

## 2. Using `pip`

```bash
pip install fme-mcp-ultra
```

Verify your installation and local FME Form environment:
```bash
fme-mcp-ultra doctor
```

---

## 3. Using Docker Container

Run in unprivileged non-root mode:

```bash
docker run -d \
  --name fme-mcp-ultra \
  -p 8000:8000 \
  -e FME_MCP_TRANSPORT=streamable-http \
  ghcr.io/mwjouini/fme-mcp-ultra:latest
```
