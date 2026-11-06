"""Standard schema models and envelopes for tool responses."""

from __future__ import annotations

import datetime
import uuid
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class MCPToolResponse(BaseModel):
    """Standardised envelope for all MCP tool outputs."""

    success: bool = Field(description="Indicates whether the tool operation succeeded")
    timestamp: str = Field(
        default_factory=lambda: datetime.datetime.now(datetime.timezone.utc).isoformat(),
        description="ISO 8601 UTC timestamp of execution",
    )
    duration_seconds: Optional[float] = Field(default=None, description="Execution duration in seconds")
    data: Any = Field(default=None, description="Primary result payload")
    warnings: List[str] = Field(default_factory=list, description="Non-fatal warnings encountered")
    audit_id: str = Field(
        default_factory=lambda: str(uuid.uuid4()),
        description="Cryptographic trace identifier for audit logs",
    )
    error: Optional[Dict[str, Any]] = Field(default=None, description="Error information if success is false")

    def to_dict(self) -> Dict[str, Any]:
        """Convert response to dictionary with strict typing."""
        return self.model_dump()

