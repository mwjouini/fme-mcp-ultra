"""CommandGuard: Subprocess security preventing shell and argument injection."""

from __future__ import annotations

import re
from collections.abc import Sequence
from pathlib import Path

from fme_mcp_ultra.core.errors import CommandInjectionError


class CommandGuard:
    """Validates executable binaries and sanitises argument vectors."""

    ALLOWED_BINARY_NAMES = {"fme.exe", "fme", "python.exe", "python", "python3"}
    FORBIDDEN_CHARS = re.compile(r"[;&|`$><\r\n]")

    @classmethod
    def validate_command(cls, cmd: Sequence[str]) -> list[str]:
        """Validate command list before subprocess execution.

        Args:
            cmd: Command sequence where cmd[0] is the binary executable.

        Returns:
            Validated list of string arguments.

        Raises:
            CommandInjectionError: If binary is unauthorised or arguments contain injection vectors.
        """
        if not cmd:
            raise CommandInjectionError("Command sequence cannot be empty")

        binary_path = Path(cmd[0])
        binary_name = binary_path.name.lower()

        if binary_name not in cls.ALLOWED_BINARY_NAMES:
            raise CommandInjectionError(
                f"Binary '{binary_name}' is not in the authorised execution allowlist."
            )

        sanitised: list[str] = []
        for arg in cmd:
            if not isinstance(arg, str):
                arg = str(arg)
            if "\0" in arg:
                raise CommandInjectionError("Argument contains illegal null byte")
            if cls.FORBIDDEN_CHARS.search(arg):
                raise CommandInjectionError(
                    f"Argument '{arg}' contains shell metacharacters which are strictly forbidden"
                )
            sanitised.append(arg)

        return sanitised


command_guard = CommandGuard()
