"""Unit tests for enterprise security guards and access control."""

from pathlib import Path

import pytest

from fme_mcp_ultra.core.errors import (
    CommandInjectionError,
    PathTraversalError,
    SecurityError,
    SSRFError,
)
from fme_mcp_ultra.security.command_guard import command_guard
from fme_mcp_ultra.security.path_guard import PathGuard
from fme_mcp_ultra.security.rbac import RBACEngine, Role
from fme_mcp_ultra.security.redaction import redaction_engine
from fme_mcp_ultra.security.ssrf_guard import SSRFGuard


def test_path_guard_allows_valid_subpath(tmp_path: Path):
    guard = PathGuard(allowed_dirs=[str(tmp_path)])
    valid_file = tmp_path / "workspace.fmw"
    valid_file.write_text("dummy")

    resolved = guard.validate_path(str(valid_file), must_exist=True)
    assert resolved == valid_file.resolve()


def test_path_guard_blocks_traversal_escape(tmp_path: Path):
    guard = PathGuard(allowed_dirs=[str(tmp_path)])
    escape_target = str(tmp_path / ".." / "system.dll")

    with pytest.raises(PathTraversalError):
        guard.validate_path(escape_target)


def test_path_guard_rejects_null_byte():
    guard = PathGuard()
    with pytest.raises(PathTraversalError):
        guard.validate_path("/tmp/workspace\0.fmw")


def test_command_guard_allows_safe_binary():
    cmd = ["fme.exe", "workspace.fmw", "--PARAM", "value"]
    validated = command_guard.validate_command(cmd)
    assert validated == cmd


def test_command_guard_blocks_unauthorised_binary():
    cmd = ["powershell.exe", "-Command", "dir"]
    with pytest.raises(CommandInjectionError):
        command_guard.validate_command(cmd)


def test_command_guard_blocks_shell_metacharacters():
    cmd = ["fme.exe", "workspace.fmw; rm -rf /"]
    with pytest.raises(CommandInjectionError):
        command_guard.validate_command(cmd)


def test_ssrf_guard_blocks_loopback():
    guard = SSRFGuard()
    with pytest.raises(SSRFError):
        guard.validate_url("http://127.0.0.1:8080/admin")


def test_ssrf_guard_blocks_cloud_metadata():
    guard = SSRFGuard()
    with pytest.raises(SSRFError):
        guard.validate_url("http://169.254.169.254/latest/meta-data/")


def test_redaction_engine_masks_bearer_token():
    text = "Authorization: Bearer supersecrettoken1234567890"
    redacted = redaction_engine.redact_text(text)
    assert "supersecrettoken" not in redacted
    assert "[REDACTED_TOKEN]" in redacted


def test_redaction_engine_masks_email():
    text = "Contact the steward at jane.doe@example.co.uk for details."
    redacted = redaction_engine.redact_text(text)
    assert "jane.doe@example.co.uk" not in redacted
    assert "[REDACTED_EMAIL]" in redacted


def test_rbac_permits_admin():
    assert RBACEngine.check_permission({Role.PLATFORM_ADMIN}, "fme_run_workspace") is True
    assert RBACEngine.check_permission({Role.PLATFORM_ADMIN}, "gov_audit_trail") is True


def test_rbac_restricts_read_only_user():
    assert RBACEngine.check_permission({Role.READ_ONLY}, "fme_get_workspace") is True
    assert RBACEngine.check_permission({Role.READ_ONLY}, "fme_run_workspace") is False


def test_rbac_enforcement_raises_on_denial():
    with pytest.raises(SecurityError):
        RBACEngine.enforce_permission({Role.READ_ONLY}, "fme_run_workspace")
