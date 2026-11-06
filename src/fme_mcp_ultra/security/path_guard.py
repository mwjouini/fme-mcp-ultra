"""PathGuard: File system sandboxing and directory traversal protection."""

from __future__ import annotations

from pathlib import Path

from fme_mcp_ultra.core.config import settings
from fme_mcp_ultra.core.errors import PathTraversalError


class PathGuard:
    """Enforces strict path containment within allowed directories."""

    def __init__(self, allowed_dirs: list[str] | None = None) -> None:
        self.allowed_dirs = [
            Path(d).resolve() for d in (allowed_dirs or settings.allowed_dirs) if d
        ]

    def validate_path(self, target_path: str, must_exist: bool = False) -> Path:
        """Validate and canonicalise target path against allowlist.

        Args:
            target_path: Path string to validate.
            must_exist: Whether the path must already exist.

        Returns:
            Resolved canonical Path object.

        Raises:
            PathTraversalError: If path escapes allowed directories or contains illegal sequences.
        """
        if not target_path or "\0" in target_path:
            raise PathTraversalError("Path contains null byte or is empty")

        # Resolve path to canonical absolute representation
        try:
            resolved = Path(target_path).resolve()
        except Exception as e:
            raise PathTraversalError(f"Failed to resolve path: {e}") from e

        if must_exist and not resolved.exists():
            raise PathTraversalError(f"Target path does not exist: {resolved}")

        # Check containment within at least one allowed directory
        is_allowed = False
        for base in self.allowed_dirs:
            try:
                # relative_to raises ValueError if resolved is not inside base
                resolved.relative_to(base)
                is_allowed = True
                break
            except ValueError:
                continue

        if not is_allowed:
            raise PathTraversalError(
                f"Access denied: path '{resolved}' is outside allowed directories."
            )

        return resolved


# Global PathGuard singleton
path_guard = PathGuard()
