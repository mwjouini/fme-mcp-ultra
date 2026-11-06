"""Cryptographic audit logger for compliance and non-repudiation."""

from __future__ import annotations

import hashlib
import json
import time
from typing import Any


class AuditLogger:
    """Maintains a tamper-evident audit chain using SHA-256 hashes."""

    def __init__(self) -> None:
        self.last_hash = "0" * 64

    def record_event(
        self,
        event_type: str,
        principal: str,
        tool_name: str,
        parameters: dict[str, Any] | None = None,
        status: str = "SUCCESS",
    ) -> dict[str, Any]:
        """Record an immutable audit entry."""
        timestamp = time.time()
        record_payload = {
            "timestamp": timestamp,
            "event_type": event_type,
            "principal": principal,
            "tool_name": tool_name,
            "parameters": parameters or {},
            "status": status,
            "previous_hash": self.last_hash,
        }
        serialized = json.dumps(record_payload, sort_keys=True)
        current_hash = hashlib.sha256(serialized.encode("utf-8")).hexdigest()
        self.last_hash = current_hash

        record_payload["hash"] = current_hash
        return record_payload


audit_logger = AuditLogger()
