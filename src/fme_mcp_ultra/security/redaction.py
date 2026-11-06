"""Redaction engine: Prevents sensitive secrets and PII from leaking to AI models."""

from __future__ import annotations

import re
from typing import Any


class RedactionEngine:
    """Detects and masks sensitive credentials and personal data."""

    PATTERNS = [
        # Bearer tokens & API Keys
        (re.compile(r"Bearer\s+([A-Za-z0-9_\-\.]{15,})", re.IGNORECASE), "Bearer [REDACTED_TOKEN]"),
        (
            re.compile(
                r"(api[_-]?key|secret|password|token)\s*[:=]\s*['\"]?([^'\"\s]+)['\"]?",
                re.IGNORECASE,
            ),
            r"\1=[REDACTED]",
        ),
        # Credit Card numbers (Luhn-like patterns)
        (re.compile(r"\b(?:\d{4}[-\s]?){3}\d{4}\b"), "[REDACTED_CREDIT_CARD]"),
        # Email addresses
        (re.compile(r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,7}\b"), "[REDACTED_EMAIL]"),
    ]

    @classmethod
    def redact_text(cls, text: str) -> str:
        """Mask secrets and PII inside a string."""
        if not text:
            return text
        redacted = text
        for pattern, replacement in cls.PATTERNS:
            redacted = pattern.sub(replacement, redacted)
        return redacted

    @classmethod
    def redact_data(cls, data: Any) -> Any:
        """Recursively redact strings within dicts, lists, and primitives."""
        if isinstance(data, str):
            return cls.redact_text(data)
        elif isinstance(data, dict):
            return {k: cls.redact_data(v) for k, v in data.items()}
        elif isinstance(data, list):
            return [cls.redact_data(item) for item in data]
        return data


redaction_engine = RedactionEngine()
