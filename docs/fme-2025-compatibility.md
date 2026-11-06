# FME 2025.2 Compatibility Strategy

Safe Software FME 2025.2 (FME Form Build 25810 and FME Flow 2025.2) lacks native out-of-the-box MCP server support. `fme-mcp-ultra` bridges this gap through coordinated local and remote adapters:

---

## 1. Local FME Form Execution
- **Subprocess CLI Runner**: Calls `C:\Program Files\FME\fme.exe` with structured `--MACRO_NAME value` arguments.
- **In-Memory C-Extension (`fmeobjects`)**: Loads `fmeobjects.cp310-win_amd64.pyd` dynamically via `os.add_dll_directory`, allowing sub-second querying of published parameters, labels, types, and defaults via `FMEWorkspaceRunner`.

---

## 2. Remote FME Flow REST Integration
- Authenticates via Bearer tokens (`fmetoken token=...`).
- Submits asynchronous jobs to `/fmerest/v3/transformations/submit`.
- Retrieves execution logs from `/fmerest/v3/transformations/jobs/id/{job_id}/log`.
- Polls job lifecycle status until completion.
