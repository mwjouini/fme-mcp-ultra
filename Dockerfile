# syntax=docker/dockerfile:1.4
# ==============================================================================
# FME-MCP-ULTRA CONTAINER IMAGE
# Multi-stage secure build with non-root unprivileged execution
# ==============================================================================

FROM python:3.11-slim-bookworm AS builder

WORKDIR /build

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

COPY pyproject.toml README.md ./
COPY src/ ./src/

RUN pip install --no-cache-dir --upgrade pip && \
    pip wheel --no-cache-dir --no-deps --wheel-dir /build/wheels .

# Final runtime image
FROM python:3.11-slim-bookworm AS runtime

LABEL org.opencontainers.image.title="fme-mcp-ultra" \
      org.opencontainers.image.description="Model Context Protocol (MCP) server for Safe Software FME (2018.0 - 2026+)" \
      org.opencontainers.image.authors="Mohamed Wael JOUINI <mohamed.wael.jouini@gmail.com>" \
      org.opencontainers.image.licenses="Apache-2.0" \
      org.opencontainers.image.source="https://github.com/mwjouini/fme-mcp-ultra"

WORKDIR /app

# Create unprivileged system user and group
RUN groupadd -g 10001 fme && \
    useradd -u 10001 -g fme -s /bin/bash -m fme

COPY --from=builder /build/wheels /wheels
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir /wheels/* && \
    rm -rf /wheels

# Setup directories with secure permissions
RUN mkdir -p /app/data /app/logs && \
    chown -R fme:fme /app

USER fme:fme

ENV PYTHONUNBUFFERED=1 \
    PYTHONIOENCODING=utf-8 \
    FME_MCP_HOST=0.0.0.0 \
    FME_MCP_PORT=8000 \
    FME_MCP_TRANSPORT=streamable-http

EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=5s --start-period=5s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://127.0.0.1:8000/health').read()" || exit 1

ENTRYPOINT ["fme-mcp-ultra"]
CMD ["serve", "--transport", "streamable-http", "--host", "0.0.0.0", "--port", "8000"]

