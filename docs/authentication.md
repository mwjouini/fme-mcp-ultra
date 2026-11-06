# Authentication & Authorisation

`fme-mcp-ultra` supports multiple enterprise authentication and authorisation mechanisms to ensure that all tool operations are properly governed.

---

## 1. Authentication Mechanisms

### A. Static API Key
Configured via `FME_MCP_AUTH_MODE=api_key` and `FME_MCP_API_KEY=<token>`.
In HTTP transport mode, clients must pass the token in the `Authorization` header:
```http
Authorization: Bearer <your-api-key>
```
Or via the `X-API-Key` header:
```http
X-API-Key: <your-api-key>
```

### B. OAuth 2.1 / OIDC
In enterprise environments, `fme-mcp-ultra` integrates with standard OAuth 2.1 identity providers (Keycloak, Okta, Microsoft Entra ID) using JWT Bearer tokens:
```http
Authorization: Bearer eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9...
```
Tokens are validated for expiration, audience, issuer, and cryptographic signature.

### C. FME Flow Token Forwarding
When communicating with FME Flow, the server forwards client-provided or environment-configured FME Flow tokens (`fmetoken token=...`) directly to the FME Flow REST endpoints.

---

## 2. Authorisation (RBAC & ABAC)

Access to tools is strictly governed by the Role-Based Access Control (`RBACEngine`) and Attribute-Based Access Control policy layer:

| Role | Authorised Tool Prefixes |
| :--- | :--- |
| `platform_admin` | `*` (All tools) |
| `tenant_admin` | `fme_`, `data_`, `gis_`, `raster_`, `cad_`, `quality_`, `catalog_`, `workflow_`, `mcp_`, `ai_`, `gov_`, `util_` |
| `workspace_operator` | `fme_run_`, `fme_get_`, `fme_list_`, `fme_search_`, `fme_stream_`, `data_`, `gis_`, `util_` |
| `spatial_analyst` | `gis_`, `raster_`, `cad_`, `data_read_`, `data_profile_`, `fme_get_`, `fme_list_`, `util_` |
| `data_analyst` | `data_`, `quality_`, `catalog_`, `fme_get_`, `fme_list_`, `util_` |
| `auditor` | `gov_audit_`, `gov_list_`, `catalog_get_`, `fme_get_job`, `quality_get_`, `util_` |
| `read_only` | `fme_get_`, `fme_list_`, `data_read_`, `catalog_get_`, `util_` |

Any request to invoke a tool outside the user's role raises a `SecurityError` with code `FORBIDDEN`.

