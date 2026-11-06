"""Maps FME published parameters to strict JSON Schema specifications."""

from __future__ import annotations

from typing import Any, Dict


def map_fme_param_to_json_schema(
    param_name: str,
    param_type: str,
    default_value: Any = None,
    label: str = "",
    optional: bool = False,
) -> Dict[str, Any]:
    """Convert an FME published parameter into an OpenAPI/JSON Schema property."""
    fme_type = (param_type or "").upper()

    schema: Dict[str, Any] = {
        "title": label or param_name,
        "description": f"FME Published Parameter ({fme_type})" + (f": {label}" if label else ""),
    }

    if default_value is not None and default_value != "":
        schema["default"] = default_value

    if fme_type in ("INTEGER", "INT", "SMALLINT", "BIGINT"):
        schema["type"] = "integer"
    elif fme_type in ("FLOAT", "REAL", "DOUBLE", "NUMBER"):
        schema["type"] = "number"
    elif fme_type in ("BOOLEAN", "BOOL", "CHECKBOX"):
        schema["type"] = "boolean"
    elif fme_type in ("FILENAME", "DIRNAME", "FILE", "MULTIFILE"):
        schema["type"] = "string"
        schema["format"] = "uri-reference"
    elif fme_type in ("CHOICE", "LOOKUP", "ENUM"):
        schema["type"] = "string"
    else:
        schema["type"] = "string"

    return schema

