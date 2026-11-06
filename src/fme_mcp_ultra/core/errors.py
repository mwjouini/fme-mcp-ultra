"""Standard error definitions with stable, machine-readable codes."""

from __future__ import annotations

from typing import Any


class FMEMCPError(Exception):
    """Base exception for all fme-mcp-ultra errors."""

    def __init__(
        self,
        message: str,
        code: str = "INTERNAL_ERROR",
        details: dict[str, Any] | None = None,
    ) -> None:
        super().__init__(message)
        self.message = message
        self.code = code
        self.details = details or {}

    def to_dict(self) -> dict[str, Any]:
        """Convert exception to structured dictionary format."""
        return {
            "code": self.code,
            "message": self.message,
            "details": self.details,
        }


class SecurityError(FMEMCPError):
    """Raised when a security guard or authorisation check fails."""

    def __init__(
        self, message: str, code: str = "SECURITY_VIOLATION", details: dict[str, Any] | None = None
    ):
        super().__init__(message, code=code, details=details)


class PathTraversalError(SecurityError):
    """Raised when an unauthorised directory escape is attempted."""

    def __init__(self, message: str = "Path traversal attempted outside allowed directories"):
        super().__init__(message, code="PATH_TRAVERSAL_DETECTED")


class SSRFError(SecurityError):
    """Raised when an outbound request targets a private or forbidden IP address."""

    def __init__(self, message: str = "Outbound request to target host is blocked by SSRF Guard"):
        super().__init__(message, code="SSRF_PREVENTED")


class CommandInjectionError(SecurityError):
    """Raised when an unsafe executable invocation is detected."""

    def __init__(self, message: str = "Execution blocked due to unsafe command arguments"):
        super().__init__(message, code="COMMAND_INJECTION_PREVENTED")


class WorkspaceNotFoundError(FMEMCPError):
    """Raised when an FME workspace cannot be found."""

    def __init__(self, workspace_path: str):
        super().__init__(
            f"Workspace not found: {workspace_path}",
            code="WORKSPACE_NOT_FOUND",
            details={"path": workspace_path},
        )


class WorkspaceExecutionError(FMEMCPError):
    """Raised when an FME workspace execution fails."""

    def __init__(self, message: str, exit_code: int = 1, log_summary: dict[str, Any] | None = None):
        super().__init__(
            message,
            code="WORKSPACE_EXECUTION_FAILED",
            details={"exit_code": exit_code, "log_summary": log_summary},
        )
