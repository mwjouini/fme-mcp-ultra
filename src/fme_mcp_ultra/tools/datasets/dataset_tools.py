"""Dataset Tools: Metadata extraction, profiling, and schema inference."""

from __future__ import annotations

import csv
import json
from typing import Any

from fme_mcp_ultra.core.schema import MCPToolResponse
from fme_mcp_ultra.security.path_guard import path_guard


def data_read_metadata(dataset_path: str) -> dict[str, Any]:
    """Extract metadata, file size, line counts, and format characteristics of a dataset.

    Args:
        dataset_path: Path to dataset file (CSV, GeoJSON, JSON, etc.).
    """
    path = path_guard.validate_path(dataset_path, must_exist=True)
    stat = path.stat()

    ext = path.suffix.lower()
    meta: dict[str, Any] = {
        "file_name": path.name,
        "extension": ext,
        "size_bytes": stat.st_size,
        "last_modified": stat.st_mtime,
    }

    if ext in (".csv", ".tsv"):
        with open(path, encoding="utf-8", errors="replace") as f:
            reader = csv.reader(f)
            header = next(reader, None)
            meta["columns"] = header or []
            line_count = 1 + sum(1 for _ in f)
            meta["estimated_records"] = line_count - 1
    elif ext == ".geojson":
        with open(path, encoding="utf-8", errors="replace") as f:
            try:
                data = json.load(f)
                meta["geojson_type"] = data.get("type")
                features = data.get("features", [])
                meta["feature_count"] = len(features)
                if features:
                    meta["sample_properties"] = list(features[0].get("properties", {}).keys())
            except Exception as e:
                meta["json_error"] = str(e)

    return MCPToolResponse(success=True, data=meta).to_dict()


def data_profile(dataset_path: str, max_rows: int = 1000) -> dict[str, Any]:
    """Profile tabular data (completeness, null counts, distinct values) up to max_rows.

    Args:
        dataset_path: Path to CSV or tabular file.
        max_rows: Sample row ceiling for statistical computation.
    """
    path = path_guard.validate_path(dataset_path, must_exist=True)
    if path.suffix.lower() not in (".csv", ".tsv"):
        return MCPToolResponse(
            success=False,
            error={
                "code": "UNSUPPORTED_FORMAT",
                "message": "Only CSV/TSV profiling currently supported natively",
            },
        ).to_dict()

    with open(path, encoding="utf-8", errors="replace") as f:
        reader = csv.DictReader(f)
        if not reader.fieldnames:
            return MCPToolResponse(success=True, data={"columns": []}).to_dict()

        total_counts = {col: 0 for col in reader.fieldnames}
        null_counts = {col: 0 for col in reader.fieldnames}
        unique_vals: dict[str, set[str]] = {col: set() for col in reader.fieldnames}
        row_count = 0
        for row in reader:
            row_count += 1
            for k, v in row.items():
                if k in total_counts:
                    total_counts[k] += 1
                    if v is None or v.strip() == "":
                        null_counts[k] += 1
                    else:
                        if len(unique_vals[k]) < 100:
                            unique_vals[k].add(v)
            if row_count >= max_rows:
                break

    profile_summary = {}
    for col in total_counts:
        tot = total_counts[col]
        nul = null_counts[col]
        profile_summary[col] = {
            "sampled_records": tot,
            "null_count": nul,
            "completeness_pct": round((tot - nul) / tot * 100, 2) if tot else 0.0,
            "approx_distinct_count": len(unique_vals[col]),
        }

    return MCPToolResponse(
        success=True,
        data={"rows_analysed": row_count, "columns": profile_summary},
    ).to_dict()
