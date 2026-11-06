"""Role-Based Access Control (RBAC) engine."""

from __future__ import annotations

from enum import Enum
from typing import Dict, Set
from fme_mcp_ultra.core.errors import SecurityError


class Role(str, Enum):
    """Authorisation roles for fme-mcp-ultra."""

    PLATFORM_ADMIN = "platform_admin"
    TENANT_ADMIN = "tenant_admin"
    WORKSPACE_OPERATOR = "workspace_operator"
    SPATIAL_ANALYST = "spatial_analyst"
    DATA_ANALYST = "data_analyst"
    AUDITOR = "auditor"
    READ_ONLY = "read_only"


# Map roles to permitted tool domain prefixes
ROLE_PERMISSIONS: Dict[Role, Set[str]] = {
    Role.PLATFORM_ADMIN: {"*"},
    Role.TENANT_ADMIN: {"fme_", "data_", "gis_", "raster_", "cad_", "quality_", "catalog_", "workflow_", "mcp_", "ai_", "gov_", "util_"},
    Role.WORKSPACE_OPERATOR: {"fme_run_", "fme_get_", "fme_list_", "fme_search_", "fme_stream_", "data_", "gis_", "util_"},
    Role.SPATIAL_ANALYST: {"gis_", "raster_", "cad_", "data_read_", "data_profile_", "fme_get_", "fme_list_", "util_"},
    Role.DATA_ANALYST: {"data_", "quality_", "catalog_", "fme_get_", "fme_list_", "util_"},
    Role.AUDITOR: {"gov_audit_", "gov_list_", "catalog_get_", "fme_get_job", "quality_get_", "util_"},
    Role.READ_ONLY: {"fme_get_", "fme_list_", "data_read_", "catalog_get_", "util_"},
}


class RBACEngine:
    """Evaluates whether a principal possesses authorisation for a tool."""

    @classmethod
    def check_permission(cls, user_roles: Set[Role], tool_name: str) -> bool:
        """Verify if any of the user roles permit executing the tool."""
        if not user_roles:
            return False

        for role in user_roles:
            allowed_prefixes = ROLE_PERMISSIONS.get(role, set())
            if "*" in allowed_prefixes:
                return True
            for prefix in allowed_prefixes:
                if tool_name.startswith(prefix) or tool_name == prefix:
                    return True

        return False

    @classmethod
    def enforce_permission(cls, user_roles: Set[Role], tool_name: str) -> None:
        """Enforce permission or raise SecurityError."""
        if not cls.check_permission(user_roles, tool_name):
            raise SecurityError(
                f"Authorisation failed: roles {[r.value for r in user_roles]} are not permitted to execute tool '{tool_name}'.",
                code="FORBIDDEN",
            )

