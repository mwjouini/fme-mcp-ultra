# Tools Reference Catalogue

A complete index of tools exposed by `fme-mcp-ultra`, organized by domain.

---

## 📁 Workspaces & Jobs

### `fme_discover_workspaces`
Crawls an authorised directory to discover `.fmw` workspace files.
- **Arguments**:
  - `directory` (*string, optional*): Base path to scan (defaults to current working directory).
  - `recursive` (*boolean, optional*): Recursively scan subdirectories (default `true`).

### `fme_get_workspace`
Inspects an FME workspace without execution.
- **Arguments**:
  - `workspace_path` (*string, required*): Path to the `.fmw` file.
- **Returns**: Published parameters, transformers count, readers, writers, file size.

### `fme_run_workspace`
Executes an FME workspace synchronously.
- **Arguments**:
  - `workspace_path` (*string, required*): Path to the `.fmw` file.
  - `parameters` (*object, optional*): Published parameters key-value mapping.
  - `log_file` (*string, optional*): Target path for execution log.
  - `timeout_seconds` (*integer, optional*): Execution timeout (default 600).

---

## 🌍 Spatial Intelligence

### `gis_reproject`
Transforms 2D coordinates between common CRS.
- **Arguments**:
  - `x` (*number, required*): Longitude / Easting.
  - `y` (*number, required*): Latitude / Northing.
  - `source_epsg` (*integer, default 4326*): Source EPSG code.
  - `target_epsg` (*integer, default 2154*): Target EPSG code (e.g. Lambert-93 or 3857 Web Mercator).

### `gis_buffer`
Generates a circular buffer polygon around a center coordinate.
- **Arguments**:
  - `center_lon` (*number, required*): Longitude in degrees.
  - `center_lat` (*number, required*): Latitude in degrees.
  - `radius_metres` (*number, required*): Radius in metres.
  - `num_points` (*integer, default 32*): Number of perimeter vertices.

### `gis_validate_geometry`
Validates structural integrity and closed polygon rings.
- **Arguments**:
  - `geojson_geometry` (*object, required*): GeoJSON geometry object.

---

## 📊 Data Engineering & Quality

### `data_read_metadata`
Inspects tabular or spatial file metadata.
- **Arguments**:
  - `dataset_path` (*string, required*): Path to dataset file (CSV, GeoJSON, etc.).

### `data_profile`
Computes column statistics, null counts, and completeness percentages.
- **Arguments**:
  - `dataset_path` (*string, required*): Path to tabular dataset.
  - `max_rows` (*integer, default 1000*): Sample size ceiling.

### `quality_score_dataset`
Computes overall quality score index (0–100) based on completeness.
- **Arguments**:
  - `dataset_path` (*string, required*): Path to CSV dataset.

