"""Spatial Tools: High-value geospatial intelligence and geometric algorithms."""

from __future__ import annotations

import math
from typing import Any, Dict, List, Optional
from fme_mcp_ultra.core.schema import MCPToolResponse
from fme_mcp_ultra.security.audit_log import audit_logger


def gis_reproject(
    x: float,
    y: float,
    source_epsg: int = 4326,
    target_epsg: int = 2154,
) -> Dict[str, Any]:
    """Reproject 2D coordinates between common coordinate reference systems.

    Supports EPSG:4326 (WGS84) to EPSG:2154 (Lambert-93 / RGF93 France) and standard Web Mercator EPSG:3857.

    Args:
        x: X coordinate (Longitude in WGS84).
        y: Y coordinate (Latitude in WGS84).
        source_epsg: Source EPSG code (default 4326).
        target_epsg: Target EPSG code (default 2154).
    """
    if source_epsg == target_epsg:
        return MCPToolResponse(success=True, data={"x": x, "y": y, "epsg": target_epsg}).to_dict()

    # Accurate closed-form projection for EPSG:4326 -> EPSG:3857 (Spherical Mercator)
    if source_epsg == 4326 and target_epsg == 3857:
        r_major = 6378137.0
        out_x = r_major * math.radians(x)
        scale = x / 180.0
        lat_rad = math.radians(max(min(y, 89.5), -89.5))
        out_y = 3189068.5 * math.log((1.0 + math.sin(lat_rad)) / (1.0 - math.sin(lat_rad)))
        return MCPToolResponse(
            success=True,
            data={"source_epsg": source_epsg, "target_epsg": target_epsg, "x": round(out_x, 3), "y": round(out_y, 3)},
        ).to_dict()

    # Closed-form projection for EPSG:4326 -> EPSG:2154 (Lambert-93 approximation)
    if source_epsg == 4326 and target_epsg == 2154:
        # Standard French Lambert-93 projection algorithm
        deg_to_rad = math.pi / 180.0
        lon_rad = x * deg_to_rad
        lat_rad = y * deg_to_rad
        # Parameters of GRS80 / Lambert 93
        a = 6378137.0
        e = 0.08181919106
        lc = 3.0 * deg_to_rad
        phi0 = 46.5 * deg_to_rad
        phi1 = 44.0 * deg_to_rad
        phi2 = 49.0 * deg_to_rad
        x0 = 700000.0
        y0 = 6600000.0

        m1 = math.cos(phi1) / math.sqrt(1.0 - e * e * math.sin(phi1) ** 2)
        m2 = math.cos(phi2) / math.sqrt(1.0 - e * e * math.sin(phi2) ** 2)
        t1 = math.tan(math.pi / 4.0 - phi1 / 2.0) / (
            ((1.0 - e * math.sin(phi1)) / (1.0 + e * math.sin(phi1))) ** (e / 2.0)
        )
        t2 = math.tan(math.pi / 4.0 - phi2 / 2.0) / (
            ((1.0 - e * math.sin(phi2)) / (1.0 + e * math.sin(phi2))) ** (e / 2.0)
        )
        t0 = math.tan(math.pi / 4.0 - phi0 / 2.0) / (
            ((1.0 - e * math.sin(phi0)) / (1.0 + e * math.sin(phi0))) ** (e / 2.0)
        )
        t = math.tan(math.pi / 4.0 - lat_rad / 2.0) / (
            ((1.0 - e * math.sin(lat_rad)) / (1.0 + e * math.sin(lat_rad))) ** (e / 2.0)
        )

        n = math.log(m1 / m2) / math.log(t1 / t2)
        f = m1 / (n * (t1 ** n))
        rho0 = a * f * (t0 ** n)
        rho = a * f * (t ** n)
        gamma = n * (lon_rad - lc)

        l93_x = x0 + rho * math.sin(gamma)
        l93_y = y0 + rho0 - rho * math.cos(gamma)

        return MCPToolResponse(
            success=True,
            data={"source_epsg": source_epsg, "target_epsg": target_epsg, "x": round(l93_x, 2), "y": round(l93_y, 2)},
        ).to_dict()

    return MCPToolResponse(
        success=False,
        error={"code": "UNSUPPORTED_CRS", "message": f"Transformation EPSG:{source_epsg} -> EPSG:{target_epsg} requires PROJ or FME Form."},
    ).to_dict()


def gis_buffer(
    center_lon: float,
    center_lat: float,
    radius_metres: float,
    num_points: int = 32,
) -> Dict[str, Any]:
    """Generate a geographic circular buffer polygon as a standard GeoJSON geometry.

    Args:
        center_lon: Longitude of circle center.
        center_lat: Latitude of circle center.
        radius_metres: Buffer radius in metres.
        num_points: Number of vertices approximating the circle perimeter (default 32).
    """
    coordinates = []
    earth_radius = 6378137.0
    lat_rad = math.radians(center_lat)
    lon_rad = math.radians(center_lon)

    for i in range(num_points + 1):
        angle = (2 * math.pi * i) / num_points
        dx = radius_metres * math.cos(angle)
        dy = radius_metres * math.sin(angle)

        d_lat = dy / earth_radius
        d_lon = dx / (earth_radius * math.cos(lat_rad))

        pt_lat = math.degrees(lat_rad + d_lat)
        pt_lon = math.degrees(lon_rad + d_lon)
        coordinates.append([round(pt_lon, 6), round(pt_lat, 6)])

    geojson_polygon = {
        "type": "Polygon",
        "coordinates": [coordinates],
    }

    return MCPToolResponse(
        success=True,
        data={
            "center": [center_lon, center_lat],
            "radius_metres": radius_metres,
            "geometry": geojson_polygon,
        },
    ).to_dict()


def gis_validate_geometry(geojson_geometry: Dict[str, Any]) -> Dict[str, Any]:
    """Validate a GeoJSON geometry for structural completeness and closed rings.

    Args:
        geojson_geometry: GeoJSON geometry dictionary (Point, LineString, Polygon).
    """
    g_type = geojson_geometry.get("type")
    coords = geojson_geometry.get("coordinates")

    if not g_type or coords is None:
        return MCPToolResponse(success=False, error={"code": "INVALID_GEOJSON", "message": "Missing type or coordinates"}).to_dict()

    issues = []
    if g_type == "Polygon":
        if not isinstance(coords, list) or len(coords) == 0:
            issues.append("Polygon must contain at least one outer ring")
        else:
            outer_ring = coords[0]
            if len(outer_ring) < 4:
                issues.append("Polygon outer ring must contain at least 4 coordinate positions")
            if outer_ring and outer_ring[0] != outer_ring[-1]:
                issues.append("Polygon ring is not closed (first vertex does not match last vertex)")

    is_valid = len(issues) == 0
    return MCPToolResponse(
        success=True,
        data={"type": g_type, "valid": is_valid, "issues": issues},
    ).to_dict()

