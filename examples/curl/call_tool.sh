#!/usr/bin/env bash
# Example cURL request invoking fme-mcp-ultra HTTP/SSE endpoint

curl -X POST "http://localhost:8000/tools/call" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "gis_reproject",
    "arguments": {
      "x": 2.3522,
      "y": 48.8566,
      "source_epsg": 4326,
      "target_epsg": 2154
    }
  }'

