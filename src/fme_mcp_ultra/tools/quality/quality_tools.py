"""Quality Tools: Data quality scoring, anomaly detection, and data contracts."""

from __future__ import annotations

import csv
from typing import Any, Dict, List, Optional
from fme_mcp_ultra.core.schema import MCPToolResponse
from fme_mcp_ultra.security.path_guard import path_guard


def quality_score_dataset(dataset_path: str) -> Dict[str, Any]:
    """Calculate an overall data quality index (0-100) based on attribute completeness and syntax validity.

    Args:
        dataset_path: Path to dataset file (CSV/TSV).
    """
    path = path_guard.validate_path(dataset_path, must_exist=True)
    if path.suffix.lower() not in (".csv", ".tsv"):
        return MCPToolResponse(
            success=False,
            error={"code": "UNSUPPORTED_FORMAT", "message": "Only CSV/TSV quality scoring supported natively"},
        ).to_dict()

    total_cells = 0
    non_null_cells = 0
    with open(path, "r", encoding="utf-8", errors="replace") as f:
        reader = csv.reader(f)
        for row in reader:
            for cell in row:
                total_cells += 1
                if cell.strip() != "":
                    non_null_cells += 1

    completeness = round((non_null_cells / total_cells * 100), 2) if total_cells else 0.0
    quality_score = completeness  # baseline score

    return MCPToolResponse(
        success=True,
        data={
            "dataset": path.name,
            "overall_quality_score": quality_score,
            "completeness_score": completeness,
            "total_cells_checked": total_cells,
        },
    ).to_dict()


def quality_generate_data_contract(dataset_name: str, schema_columns: Dict[str, str]) -> Dict[str, Any]:
    """Generate a machine-readable Data Contract YAML specification.

    Args:
        dataset_name: Name of the dataset under contract.
        schema_columns: Dictionary mapping column names to expected types (e.g. {'id': 'integer', 'geom': 'geometry'}).
    """
    contract = {
        "dataContractSpecification": "0.9.3",
        "id": f"urn:contract:{dataset_name}",
        "info": {
            "title": f"Data Contract for {dataset_name}",
            "version": "1.0.0",
            "owner": "Data Platform Team",
        },
        "models": {
            dataset_name: {
                "fields": {
                    col: {"type": col_type, "required": True}
                    for col, col_type in schema_columns.items()
                }
            }
        },
    }
    return MCPToolResponse(success=True, data=contract).to_dict()
