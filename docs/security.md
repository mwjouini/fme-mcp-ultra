# Security Architecture & Threat Model

`fme-mcp-ultra` applies an enterprise **Default-Deny** security posture.

---

## 🛡️ Core Defenses

### 1. PathGuard (Directory Sandboxing)
- Resolves all file paths to their absolute canonical representation (`os.path.realpath`).
- Enforces strict containment within `FME_ALLOWED_DIRS`.
- Immediately raises `PathTraversalError` upon detecting `..` directory traversal or null byte injection (`\0`).

### 2. CommandGuard (Subprocess Sandboxing)
- Forbids invocation of shells (`shell=False` is enforced across all subprocess executions).
- Whitelists executable binaries (`fme.exe`, `fme`, `python.exe`).
- Disallows shell metacharacters (`|`, `;`, `&`, `$`, `>`, `<`).

### 3. SSRF Guard (Network Defense)
- Pre-resolves outbound DNS hostnames.
- Blocks calls to loopback (`127.0.0.1`), private networks (`10.0.0.0/8`, `192.168.0.0/16`, `172.16.0.0/12`), link-local IPs (`169.254.169.254`), and non-whitelisted domains.

### 4. RedactionEngine (PII & Secret Scrubbing)
- Proactively scans stdout, stderr, and structured outputs for Bearer tokens, API credentials, email addresses, and payment card numbers, replacing them with redaction tokens before response delivery.

### 5. Role-Based Access Control (RBAC)
- Strict separation of duties:
  - `platform_admin`: Full access.
  - `workspace_operator`: Permitted to inspect and execute workspaces.
  - `spatial_analyst`: Vector and raster GIS operations.
  - `auditor`: Compliance and audit logs only.
  - `read_only`: Inspection and queries only.
