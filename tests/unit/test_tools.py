"""Unit tests for spatial, dataset, and utility tools."""

from pathlib import Path

from fme_mcp_ultra.tools.catalog.catalog_tools import catalog_register_asset, catalog_search_assets
from fme_mcp_ultra.tools.datasets.dataset_tools import data_profile, data_read_metadata
from fme_mcp_ultra.tools.quality.quality_tools import quality_score_dataset
from fme_mcp_ultra.tools.spatial.spatial_tools import (
    gis_buffer,
    gis_reproject,
    gis_validate_geometry,
)
from fme_mcp_ultra.tools.utilities.util_tools import (
    util_ping,
    util_validate_coordinates,
    util_version,
)


def test_gis_reproject_wgs84_to_web_mercator():
    res = gis_reproject(x=2.3522, y=48.8566, source_epsg=4326, target_epsg=3857)
    assert res["success"] is True
    assert "x" in res["data"]
    assert "y" in res["data"]
    assert res["data"]["x"] > 260000.0


def test_gis_reproject_wgs84_to_lambert93():
    res = gis_reproject(x=2.3522, y=48.8566, source_epsg=4326, target_epsg=2154)
    assert res["success"] is True
    assert 600000.0 < res["data"]["x"] < 700000.0
    assert 6800000.0 < res["data"]["y"] < 6900000.0


def test_gis_buffer_creates_valid_geojson_polygon():
    res = gis_buffer(center_lon=2.35, center_lat=48.85, radius_metres=500.0, num_points=16)
    assert res["success"] is True
    geom = res["data"]["geometry"]
    assert geom["type"] == "Polygon"
    assert len(geom["coordinates"][0]) == 17  # 16 + 1 to close ring


def test_gis_validate_geometry_detects_unclosed_polygon():
    invalid_polygon = {
        "type": "Polygon",
        "coordinates": [[[0, 0], [1, 0], [1, 1], [0, 1]]],  # Missing closing [0, 0]
    }
    res = gis_validate_geometry(invalid_polygon)
    assert res["success"] is True
    assert res["data"]["valid"] is False
    assert len(res["data"]["issues"]) > 0


def test_data_read_metadata_csv(tmp_path: Path):
    csv_file = tmp_path / "test.csv"
    csv_file.write_text("id,name,value\n1,Alpha,100\n2,Beta,200\n", encoding="utf-8")

    res = data_read_metadata(str(csv_file))
    assert res["success"] is True
    assert res["data"]["columns"] == ["id", "name", "value"]
    assert res["data"]["estimated_records"] == 2


def test_data_profile_computes_nulls(tmp_path: Path):
    csv_file = tmp_path / "test.csv"
    csv_file.write_text("id,score\n1,10\n2,\n3,30\n", encoding="utf-8")

    res = data_profile(str(csv_file))
    assert res["success"] is True
    cols = res["data"]["columns"]
    assert cols["score"]["null_count"] == 1
    assert cols["score"]["completeness_pct"] == 66.67


def test_quality_score_dataset(tmp_path: Path):
    csv_file = tmp_path / "quality.csv"
    csv_file.write_text("colA,colB\n1,X\n2,Y\n", encoding="utf-8")

    res = quality_score_dataset(str(csv_file))
    assert res["success"] is True
    assert res["data"]["overall_quality_score"] == 100.0


def test_catalog_register_and_search():
    reg = catalog_register_asset(
        "urn:layer:roads", "National Roads", "vector_layer", "Major road network"
    )
    assert reg["success"] is True

    search = catalog_search_assets("Roads")
    assert search["success"] is True
    assert search["data"]["count"] >= 1


def test_util_tools():
    assert util_ping()["data"]["status"] == "pong"
    assert "1.1.0" in util_version()["data"]["version"]
    assert util_validate_coordinates(48.85, 2.35)["data"]["valid_latitude"] is True
    assert util_validate_coordinates(120.0, 2.35)["data"]["valid_latitude"] is False
