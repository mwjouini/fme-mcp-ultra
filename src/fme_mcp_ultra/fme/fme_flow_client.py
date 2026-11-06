"""FME Flow REST API Client (v3/v4) for enterprise orchestration."""

from __future__ import annotations

from typing import Any

import httpx

from fme_mcp_ultra.core.config import settings
from fme_mcp_ultra.core.errors import FMEMCPError
from fme_mcp_ultra.core.logging import get_logger
from fme_mcp_ultra.security.ssrf_guard import ssrf_guard

logger = get_logger("fme-flow-client")


class FMEFlowClient:
    """Interacts with FME Flow (formerly FME Server) REST API."""

    def __init__(
        self,
        base_url: str | None = None,
        token: str | None = None,
        verify_ssl: bool = True,
    ) -> None:
        self.base_url = (base_url or settings.fme_flow_url or "").rstrip("/")
        self.token = token or settings.fme_flow_token
        self.verify_ssl = verify_ssl if verify_ssl is not None else settings.fme_flow_verify_ssl
        self.is_configured = bool(self.base_url and self.token)

    def _headers(self) -> dict[str, str]:
        return {
            "Authorization": f"fmetoken token={self.token}",
            "Accept": "application/json",
            "User-Agent": "fme-mcp-ultra/1.0.0",
        }

    async def get_health(self) -> dict[str, Any]:
        """Check FME Flow health status."""
        if not self.is_configured:
            return {"configured": False, "status": "NOT_CONFIGURED"}

        url = ssrf_guard.validate_url(f"{self.base_url}/fmerest/v3/healthcheck")
        async with httpx.AsyncClient(verify=self.verify_ssl) as client:
            resp = await client.get(url, headers=self._headers(), timeout=10.0)
            return {
                "status_code": resp.status_code,
                "data": resp.json() if resp.status_code == 200 else resp.text,
            }

    async def list_repositories(self) -> list[dict[str, Any]]:
        """List all accessible repositories on FME Flow."""
        if not self.is_configured:
            return []

        url = ssrf_guard.validate_url(f"{self.base_url}/fmerest/v3/repositories")
        async with httpx.AsyncClient(verify=self.verify_ssl) as client:
            resp = await client.get(url, headers=self._headers(), timeout=15.0)
            if resp.status_code == 200:
                return resp.json().get("items", [])
            return []

    async def list_workspaces(self, repository: str) -> list[dict[str, Any]]:
        """List workspaces inside a specific repository."""
        if not self.is_configured:
            return []

        url = ssrf_guard.validate_url(f"{self.base_url}/fmerest/v3/repositories/{repository}/items")
        async with httpx.AsyncClient(verify=self.verify_ssl) as client:
            resp = await client.get(url, headers=self._headers(), timeout=15.0)
            if resp.status_code == 200:
                return resp.json().get("items", [])
            return []

    async def submit_job(
        self,
        repository: str,
        workspace: str,
        parameters: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """Submit an asynchronous job to FME Flow."""
        if not self.is_configured:
            raise FMEMCPError(
                "FME Flow is not configured with valid URL and token.", code="FLOW_NOT_CONFIGURED"
            )

        url = ssrf_guard.validate_url(
            f"{self.base_url}/fmerest/v3/transformations/submit/{repository}/{workspace}"
        )
        payload = {
            "publishedParameters": [{"name": k, "value": v} for k, v in (parameters or {}).items()]
        }
        async with httpx.AsyncClient(verify=self.verify_ssl) as client:
            resp = await client.post(url, headers=self._headers(), json=payload, timeout=20.0)
            if resp.status_code in (200, 201):
                return resp.json()
            raise FMEMCPError(
                f"Failed to submit job to FME Flow: {resp.text}",
                code="FLOW_SUBMIT_FAILED",
                details={"status_code": resp.status_code},
            )

    async def get_job_status(self, job_id: int) -> dict[str, Any]:
        """Query execution status of an active or historical job."""
        if not self.is_configured:
            raise FMEMCPError("FME Flow is not configured.", code="FLOW_NOT_CONFIGURED")

        url = ssrf_guard.validate_url(
            f"{self.base_url}/fmerest/v3/transformations/jobs/id/{job_id}"
        )
        async with httpx.AsyncClient(verify=self.verify_ssl) as client:
            resp = await client.get(url, headers=self._headers(), timeout=15.0)
            if resp.status_code == 200:
                return resp.json()
            raise FMEMCPError(f"Job {job_id} not found on FME Flow", code="JOB_NOT_FOUND")

    async def get_job_log(self, job_id: int) -> str:
        """Download complete text log for an executed job."""
        if not self.is_configured:
            raise FMEMCPError("FME Flow is not configured.", code="FLOW_NOT_CONFIGURED")

        url = ssrf_guard.validate_url(
            f"{self.base_url}/fmerest/v3/transformations/jobs/id/{job_id}/log"
        )
        async with httpx.AsyncClient(verify=self.verify_ssl) as client:
            resp = await client.get(url, headers=self._headers(), timeout=30.0)
            if resp.status_code == 200:
                return resp.text
            raise FMEMCPError(f"Could not retrieve log for job {job_id}", code="LOG_NOT_FOUND")


# Global singleton client
fme_flow_client = FMEFlowClient()
