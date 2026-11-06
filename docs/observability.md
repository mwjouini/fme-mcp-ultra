# Observability & Monitoring

`fme-mcp-ultra` integrates enterprise observability out-of-the-box, supporting OpenTelemetry standards, Prometheus metrics, structured JSON logs, and immutable audit trails.

## Metrics & Health Probes

When running in Streamable HTTP mode, the server exposes dedicated monitoring endpoints:

- `GET /healthz`: Liveness probe verifying the event loop is active.
- `GET /readyz`: Readiness probe testing FME Flow API or local FME Form engine connectivity.
- `GET /metrics`: Standard Prometheus-formatted scrape target.

### Prometheus Metrics Exposed

| Metric Name | Type | Description |
|---|---|---|
| `fme_mcp_requests_total` | Counter | Total JSON-RPC tool calls by tool name and status |
| `fme_mcp_request_duration_seconds` | Histogram | Latency distribution of tool execution |
| `fme_mcp_active_jobs` | Gauge | Number of concurrent active FME workspace runs |
| `fme_mcp_rate_limit_rejections_total` | Counter | Rejected requests due to token bucket depletion |
| `fme_mcp_security_violations_total` | Counter | SSRF, path traversal, or command injection blocks |

## Structured Logging

Logs are formatted in structured JSON conforming to the OpenTelemetry schema. Every log entry includes:
- `timestamp`: UTC ISO-8601 with microsecond precision.
- `level`: `INFO`, `WARNING`, `ERROR`, `CRITICAL`.
- `correlation_id`: Unique UUID per JSON-RPC request for distributed tracing across agent hops.
- `tool_name`: Invoked MCP tool identifier.
- `user_id` / `client_id`: Authenticated caller identity.

## Immutable Security Audit Trail

All data transformations, parameter bindings, and workspace executions are appended to an immutable append-only audit log:

```json
{
  "timestamp": "2026-11-06T10:45:00.123456Z",
  "event_type": "TOOL_INVOCATION",
  "tool": "fme_run_workspace",
  "principal": "agent-claude-3-7",
  "status": "SUCCESS",
  "duration_ms": 1420,
  "parameters_hash": "sha256:e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
  "client_ip": "10.244.1.42"
}
```

Audit records can be forwarded directly to SIEM solutions such as Splunk, Datadog, ElasticSearch, or Google Cloud Operations Suite.
