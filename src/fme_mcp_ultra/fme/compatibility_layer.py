"""Compatibility Layer: Bridges FME Form 2025.2, FME Flow, and future 2026.x runtimes."""

from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, Optional
from fme_mcp_ultra.fme.fme_flow_client import fme_flow_client
from fme_mcp_ultra.fme.fme_form_client import fme_form_client


class FMECompatibilityLayer:
    """Intelligently routes workspace runs and queries to Form or Flow."""

    @classmethod
    def get_unified_info(cls) -> Dict[str, Any]:
        """Aggregate installation and capability detection from both Form and Flow."""
        form_info = fme_form_client.get_info()
        return {
            "form": form_info,
            "flow_configured": fme_flow_client.is_configured,
            "primary_backend": "form" if form_info.get("installed") else ("flow" if fme_flow_client.is_configured else "emulated"),
        }

    @classmethod
    def inspect(cls, target: str) -> Dict[str, Any]:
        """Inspect a workspace file or repository item."""
        p = Path(target)
        if p.suffix.lower() in (".fmw", ".fmwt") or p.exists():
            return fme_form_client.inspect_workspace(str(p))
        return {"error": f"Target '{target}' cannot be located as a local workspace"}

    @classmethod
    def run(
        cls,
        target: str,
        parameters: Optional[Dict[str, Any]] = None,
        log_file: Optional[str] = None,
        timeout_seconds: Optional[int] = None,
    ) -> Dict[str, Any]:
        """Execute a workspace via the optimal available backend."""
        p = Path(target)
        if p.exists() or p.suffix.lower() == ".fmw":
            return fme_form_client.run_workspace(
                workspace_path=str(p),
                parameters=parameters,
                log_file=log_file,
                timeout_seconds=timeout_seconds,
            )
        raise FileNotFoundError(f"Local workspace '{target}' not found")


compatibility_layer = FMECompatibilityLayer()

