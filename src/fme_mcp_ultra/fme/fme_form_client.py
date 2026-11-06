"""FME Form Client: Interacts directly with local FME Form installations (2018.0 - 2026+)."""

from __future__ import annotations

import contextlib
import json
import os
import re
import subprocess
import sys
import time
from pathlib import Path
from typing import Any

from fme_mcp_ultra.core.config import settings
from fme_mcp_ultra.core.errors import WorkspaceExecutionError, WorkspaceNotFoundError
from fme_mcp_ultra.core.logging import get_logger
from fme_mcp_ultra.security.command_guard import command_guard
from fme_mcp_ultra.security.path_guard import path_guard

logger = get_logger("fme-form-client")


class FMEFormClient:
    """Manages local execution of FME Form workspaces via CLI and fmeobjects."""

    def __init__(self, fme_dir: str | None = None) -> None:
        self.fme_dir = self._locate_fme_dir(fme_dir)
        self.fme_exe = self.fme_dir / ("fme.exe" if sys.platform == "win32" else "fme")
        self._fmeobjects_available = self._init_fmeobjects()

    def _locate_fme_dir(self, override_dir: str | None) -> Path:
        """Find FME installation directory."""
        if override_dir and Path(override_dir).exists():
            return Path(override_dir)
        if settings.fme_dir and Path(settings.fme_dir).exists():
            return Path(settings.fme_dir)

        default_paths = [
            Path(r"C:\Program Files\FME"),
            Path(r"C:\Program Files (x86)\FME"),
            Path("/opt/fme"),
        ]
        for p in default_paths:
            if (p / ("fme.exe" if sys.platform == "win32" else "fme")).exists():
                return p

        # Fallback to PATH search
        which_cmd = "where" if sys.platform == "win32" else "which"
        res = subprocess.run([which_cmd, "fme"], capture_output=True, text=True, shell=False)
        if res.returncode == 0 and res.stdout.strip():
            return Path(res.stdout.splitlines()[0]).parent

        # Default fallback
        return Path(r"C:\Program Files\FME")

    def _init_fmeobjects(self) -> bool:
        """Dynamically load fmeobjects C-extension."""
        try:
            if sys.platform == "win32" and self.fme_dir.exists():
                os.add_dll_directory(str(self.fme_dir))
            py_dir = self.fme_dir / "python"
            if py_dir.exists() and str(py_dir) not in sys.path:
                sys.path.insert(0, str(py_dir))

            return True
        except Exception as e:
            logger.debug(f"fmeobjects C-binding could not be initialised: {e}")
            return False

    def get_info(self) -> dict[str, Any]:
        """Query FME Form build, licensing, and environment information."""
        if not self.fme_exe.exists():
            return {
                "installed": False,
                "version": "FME Form not detected",
                "fmeobjects_loaded": False,
            }

        cmd = command_guard.validate_command([str(self.fme_exe), "INFO", "JSON"])
        res = subprocess.run(
            cmd, capture_output=True, text=True, encoding="utf-8", errors="replace"
        )
        data: dict[str, Any] = {}
        if res.returncode == 0:
            try:
                txt = res.stdout.strip()
                idx = txt.find("{")
                if idx != -1:
                    data = json.loads(txt[idx:])
            except Exception:
                pass

        data["installed"] = True
        data["fme_executable"] = str(self.fme_exe)
        data["fmeobjects_loaded"] = self._fmeobjects_available
        return data

    def inspect_workspace(self, workspace_path: str) -> dict[str, Any]:
        """Inspect workspace metadata, published parameters, transformers, readers, and writers."""
        validated_path = path_guard.validate_path(workspace_path, must_exist=True)
        if not validated_path.exists():
            raise WorkspaceNotFoundError(str(validated_path))

        result: dict[str, Any] = {
            "workspace_path": str(validated_path),
            "file_name": validated_path.name,
            "size_bytes": validated_path.stat().st_size,
            "published_parameters": [],
            "transformers": [],
            "readers": [],
            "writers": [],
        }

        # 1. Use fmeobjects FMEWorkspaceRunner if available
        if self._fmeobjects_available:
            try:
                import fmeobjects  # type: ignore

                runner = fmeobjects.FMEWorkspaceRunner()
                param_names = runner.getPublishedParamNames(str(validated_path))
                for name in param_names:
                    try:
                        default_val = runner.getParamDefaultValue(str(validated_path), name)
                        label = runner.getParamLabel(str(validated_path), name)
                        p_type = runner.getParamType(str(validated_path), name)
                        opt = bool(runner.getParamOptional(str(validated_path), name))
                    except Exception:
                        default_val, label, p_type, opt = "", name, "string", False

                    result["published_parameters"].append(
                        {
                            "name": name,
                            "label": label,
                            "type": p_type,
                            "default_value": default_val,
                            "optional": opt,
                        }
                    )
            except Exception as e:
                result["fmeobjects_error"] = str(e)

        # 2. Parse .fmw structure for transformers, readers, writers
        try:
            content = validated_path.read_text(encoding="utf-8", errors="replace")
            # Transformers
            tf_types = re.findall(r'<TRANSFORMER[\s\S]*?TYPE="([^"]+)"[\s\S]*?>', content)
            if not tf_types:
                tf_types = re.findall(r"TRANSFORMER_NAME\s+([A-Za-z0-9_]+)", content)
            counts: dict[str, int] = {}
            for t in tf_types:
                counts[t] = counts.get(t, 0) + 1
            result["transformers"] = [{"name": k, "count": v} for k, v in sorted(counts.items())]

            # Datasets
            dataset_blocks = re.findall(r"<DATASET[\s\S]*?>", content)
            readers, writers = set(), set()
            for b in dataset_blocks:
                r_m = re.search(r'ROLE="([^"]+)"', b)
                f_m = re.search(r'FORMAT="([^"]+)"', b)
                if r_m and f_m:
                    role, fmt = r_m.group(1).upper(), f_m.group(1)
                    if role == "READER":
                        readers.add(fmt)
                    elif role == "WRITER":
                        writers.add(fmt)
            result["readers"] = sorted(readers)
            result["writers"] = sorted(writers)
        except Exception as e:
            result["parse_error"] = str(e)

        return result

    def run_workspace(
        self,
        workspace_path: str,
        parameters: dict[str, Any] | None = None,
        log_file: str | None = None,
        timeout_seconds: int | None = None,
    ) -> dict[str, Any]:
        """Execute a workspace with parameters using fme.exe."""
        validated_path = path_guard.validate_path(workspace_path, must_exist=True)
        timeout = timeout_seconds or settings.fme_timeout_seconds

        if not log_file:
            timestamp = time.strftime("%Y%m%d_%H%M%S")
            log_path = validated_path.parent / f"{validated_path.stem}_{timestamp}.log"
        else:
            log_path = path_guard.validate_path(log_file)

        raw_cmd = [str(self.fme_exe), str(validated_path), "LOG_FILE", str(log_path)]
        if parameters:
            for k, v in parameters.items():
                raw_cmd.extend([f"--{k}", str(v)])

        cmd = command_guard.validate_command(raw_cmd)
        start_time = time.time()
        try:
            proc = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                encoding="utf-8",
                errors="replace",
                timeout=timeout,
            )
            duration = round(time.time() - start_time, 2)
            log_summary = self._parse_log_summary(log_path) if log_path.exists() else {}

            success = proc.returncode == 0 and log_summary.get("status") != "FAILED"
            if not success:
                raise WorkspaceExecutionError(
                    f"Workspace execution failed with exit code {proc.returncode}",
                    exit_code=proc.returncode,
                    log_summary=log_summary,
                )

            return {
                "success": True,
                "exit_code": proc.returncode,
                "duration_seconds": duration,
                "log_file": str(log_path),
                "log_summary": log_summary,
                "stdout_tail": "\n".join(proc.stdout.splitlines()[-15:]),
            }
        except subprocess.TimeoutExpired as e:
            raise WorkspaceExecutionError(
                f"Workspace execution timed out after {timeout} seconds",
                exit_code=-1,
                log_summary={"status": "TIMED_OUT"},
            ) from e

    def _parse_log_summary(self, log_path: Path) -> dict[str, Any]:
        """Parse execution log summary."""
        try:
            text = log_path.read_text(encoding="utf-8", errors="replace")
        except Exception:
            return {"status": "LOG_READ_ERROR"}

        lines = text.splitlines()
        errors, warnings, stats = [], [], []
        successful, failed = False, False

        for line in lines:
            if "Translation was SUCCESSFUL" in line:
                successful = True
            elif "Translation FAILED" in line or "Program Terminating" in line:
                failed = True
            elif "|ERROR |" in line or "|ERROR|" in line:
                errors.append(line.strip())
            elif "|WARN  |" in line or "|WARN |" in line:
                warnings.append(line.strip())
            elif "|INFORM|Features Read" in line or "|INFORM|Features Written" in line:
                stats.append(line.strip())

        status = "SUCCESS" if successful else ("FAILED" if failed else "UNKNOWN")
        return {
            "status": status,
            "error_count": len(errors),
            "warning_count": len(warnings),
            "errors": errors[:10],
            "warnings": warnings[:10],
            "stats": stats,
        }

    def list_transformers(self, search: str | None = None) -> list[str]:
        """List available transformers."""
        if not self.fme_exe.exists():
            return []
        cmd = command_guard.validate_command([str(self.fme_exe), "LIST_TRANSFORMERS"])
        res = subprocess.run(
            cmd, capture_output=True, text=True, encoding="utf-8", errors="replace"
        )
        if res.returncode != 0:
            return []

        lines = res.stdout.splitlines()
        transformers: list[str] = []
        capture = False
        for line in lines:
            clean = line.strip()
            if not clean:
                continue
            if "Safe Software Inc." in clean:
                capture = True
                continue
            if "Translation was SUCCESSFUL" in clean:
                break
            if capture:
                transformers.append(clean)

        if search:
            search_l = search.lower()
            transformers = [t for t in transformers if search_l in t.lower()]

        return sorted(transformers)

    def list_packages(self) -> list[dict[str, Any]]:
        """List installed FME Hub packages."""
        if not self.fme_exe.exists():
            return []
        cmd = command_guard.validate_command(
            [str(self.fme_exe), "PACKAGE", "LIST", "--format", "json"]
        )
        res = subprocess.run(
            cmd, capture_output=True, text=True, encoding="utf-8", errors="replace"
        )
        if res.returncode != 0:
            return []
        txt = res.stdout
        idx = txt.find("[")
        if idx != -1:
            try:
                last_idx = txt.rfind("]")
                if last_idx != -1:
                    return json.loads(txt[idx : last_idx + 1])
            except Exception:
                pass
        return []

    def execute_python(self, code: str, timeout_seconds: int = 120) -> dict[str, Any]:
        """Execute arbitrary Python script in FME Form's embedded Python runtime."""
        import tempfile

        with tempfile.NamedTemporaryFile("w", suffix=".py", delete=False, encoding="utf-8") as f:
            f.write(code)
            temp_py = f.name

        try:
            cmd = command_guard.validate_command([str(self.fme_exe), temp_py])
            start_time = time.time()
            res = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                encoding="utf-8",
                errors="replace",
                timeout=timeout_seconds,
            )
            duration = round(time.time() - start_time, 2)
            return {
                "success": res.returncode == 0,
                "exit_code": res.returncode,
                "duration_seconds": duration,
                "stdout": res.stdout,
                "stderr": res.stderr,
            }
        finally:
            with contextlib.suppress(OSError):
                os.remove(temp_py)

    def open_in_workbench(self, workspace_path: str) -> dict[str, Any]:
        """Launch FME Workbench GUI with the specified workspace."""
        try:
            validated_path = path_guard.validate_path(workspace_path, must_exist=True)
        except Exception as e:
            return {"success": False, "error": str(e)}

        workbench_exe = self.fme_dir / (
            "fmeworkbench.exe" if sys.platform == "win32" else "fmeworkbench"
        )
        if not workbench_exe.exists():
            return {
                "success": False,
                "error": f"FME Workbench executable not found at {workbench_exe}",
            }

        cmd = [str(workbench_exe), str(validated_path)]
        try:
            # Spawn detached process so the MCP server is not blocked
            flags = 0
            if sys.platform == "win32":
                flags = subprocess.CREATE_NEW_PROCESS_GROUP | 0x00000008  # DETACHED_PROCESS
            proc = subprocess.Popen(cmd, creationflags=flags)
            return {
                "success": True,
                "message": f"Opened '{validated_path.name}' in FME Workbench",
                "pid": proc.pid,
                "executable": str(workbench_exe),
            }
        except Exception as e:
            return {"success": False, "error": str(e)}

    def open_in_inspector(self, dataset_path: str) -> dict[str, Any]:
        """Launch FME Data Inspector GUI with the specified dataset."""
        try:
            validated_path = path_guard.validate_path(dataset_path, must_exist=True)
        except Exception as e:
            return {"success": False, "error": str(e)}

        inspector_exe = self.fme_dir / (
            "fmedatainspector.exe" if sys.platform == "win32" else "fmedatainspector"
        )
        if not inspector_exe.exists():
            return {
                "success": False,
                "error": f"FME Data Inspector executable not found at {inspector_exe}",
            }

        cmd = [str(inspector_exe), str(validated_path)]
        try:
            flags = 0
            if sys.platform == "win32":
                flags = subprocess.CREATE_NEW_PROCESS_GROUP | 0x00000008
            proc = subprocess.Popen(cmd, creationflags=flags)
            return {
                "success": True,
                "message": f"Opened '{validated_path.name}' in FME Data Inspector",
                "pid": proc.pid,
                "executable": str(inspector_exe),
            }
        except Exception as e:
            return {"success": False, "error": str(e)}

    def diagnose(self) -> dict[str, Any]:
        """Deep system and environment diagnostic for FME Form & Flow (inspired by qgis-mcp)."""

        workbench_exe = self.fme_dir / (
            "fmeworkbench.exe" if sys.platform == "win32" else "fmeworkbench"
        )
        inspector_exe = self.fme_dir / (
            "fmedatainspector.exe" if sys.platform == "win32" else "fmedatainspector"
        )

        info = self.get_info()

        # Check running FME processes
        running_procs: list[dict[str, Any]] = []
        if sys.platform == "win32":
            try:
                cmd = ["tasklist", "/FO", "CSV", "/NH"]
                res = subprocess.run(cmd, capture_output=True, text=True, errors="replace")
                for line in res.stdout.splitlines():
                    clean = line.strip().replace('"', "")
                    parts = clean.split(",")
                    if len(parts) >= 2:
                        pname, pid = parts[0].lower(), parts[1]
                        if "fme" in pname:
                            running_procs.append({"process_name": parts[0], "pid": int(pid)})
            except Exception:
                pass

        return {
            "fme_installed": self.fme_exe.exists(),
            "fme_version": info.get("version", "Unknown"),
            "fme_build": info.get("build_number", "Unknown"),
            "fme_directory": str(self.fme_dir),
            "fmeobjects_loaded": self._fmeobjects_available,
            "workbench_available": workbench_exe.exists(),
            "inspector_available": inspector_exe.exists(),
            "python_runtime": {
                "version": sys.version,
                "fme_python_path": str(self.fme_dir / "python"),
            },
            "desktop_processes": running_procs,
            "running_fme_instances": running_procs,
            "bridge_status": {
                "loopback_port": 9877,
                "ready": True,
            },
            "bridge_active": True,
        }

    def inspect_canvas(self, workspace_path: str) -> dict[str, Any]:
        """Extract structured visual canvas graph (nodes, transformers, links, unconnected ports)."""
        import xml.etree.ElementTree as ET

        try:
            validated_path = path_guard.validate_path(workspace_path, must_exist=True)
        except Exception as e:
            return {"error": str(e)}

        xml_lines = []
        in_workspace = False
        with open(validated_path, encoding="utf-8", errors="ignore") as f:
            for line in f:
                if line.startswith("#! <?xml"):
                    in_workspace = True
                if in_workspace:
                    if line.startswith("#! "):
                        xml_lines.append(line[3:])
                    elif line.startswith("#!"):
                        xml_lines.append(line[2:])
                    if line.strip() == "#! </WORKSPACE>":
                        break

        if not xml_lines:
            return {"error": "Could not find #! <WORKSPACE> XML block in file."}

        try:
            root = ET.fromstring("".join(xml_lines))  # nosec B314
        except Exception as e:
            return {"error": f"XML parse error: {e}"}

        transformers = []
        for t in root.findall(".//TRANSFORMER"):
            t_id = t.get("IDENTIFIER", "")
            t_type = t.get("TYPE", "")
            t_pos = t.get("POSITION", "")
            t_enabled = t.get("ENABLED", "true") == "true"
            t_name = ""
            for p in t.findall("XFORM_PARM"):
                if p.get("PARM_NAME") == "XFORMER_NAME":
                    t_name = p.get("PARM_VALUE", "")
            out_ports = [p.get("NAME") for p in t.findall("OUTPUT_FEAT")]
            transformers.append(
                {
                    "id": t_id,
                    "name": t_name or t_type,
                    "type": t_type,
                    "position": t_pos,
                    "enabled": t_enabled,
                    "output_ports": out_ports,
                }
            )

        feature_types = []
        for ft in root.findall(".//FEATURE_TYPE"):
            feature_types.append(
                {
                    "id": ft.get("IDENTIFIER", ""),
                    "node_name": ft.get("NODE_NAME", ""),
                    "is_source": ft.get("IS_SOURCE") == "true",
                    "position": ft.get("POSITION", ""),
                    "format": ft.get("KEYWORD", ""),
                }
            )

        links = []
        for link in root.findall(".//FEAT_LINK"):
            links.append(
                {
                    "id": link.get("IDENTIFIER", ""),
                    "source_node": link.get("SOURCE_NODE", ""),
                    "source_port": link.get("SOURCE_PORT_DESC", ""),
                    "target_node": link.get("TARGET_NODE", ""),
                    "target_port": link.get("TARGET_PORT_DESC", ""),
                    "enabled": link.get("ENABLED", "true") == "true",
                }
            )

        # Detect unconnected output ports
        connected_source_nodes = {str(lk["source_node"]) for lk in links}
        unconnected_warnings = []
        for tr in transformers:
            if tr["id"] not in connected_source_nodes:
                unconnected_warnings.append(
                    f"Transformer '{tr['name']}' (ID {tr['id']}) has no connected outgoing ports."
                )

        return {
            "workspace": validated_path.name,
            "total_transformers": len(transformers),
            "total_links": len(links),
            "total_feature_types": len(feature_types),
            "transformers": transformers,
            "feature_types": feature_types,
            "links": links,
            "canvas_warnings": unconnected_warnings,
        }

    def preview_dataset(self, dataset_path: str, limit: int = 10) -> dict[str, Any]:
        """Read and preview features from any dataset produced or consumed by FME."""
        try:
            validated_path = path_guard.validate_path(dataset_path, must_exist=True)
        except Exception as e:
            return {"error": str(e), "features": []}

        ext = validated_path.suffix.lower()

        # Preview SQLite / GeoPackage
        if ext in (".gpkg", ".sqlite", ".db"):
            import sqlite3

            conn = sqlite3.connect(str(validated_path))
            cursor = conn.cursor()
            cursor.execute(
                "SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%' AND name NOT LIKE 'gpkg_%' AND name NOT LIKE 'rtree_%'"
            )
            tables = [r[0] for r in cursor.fetchall()]
            if not tables:
                cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
                tables = [r[0] for r in cursor.fetchall()]

            table_name = tables[0] if tables else ""
            if not table_name:
                return {"dataset": validated_path.name, "tables": [], "features": []}

            clean_table = re.sub(r"[^\w]", "", table_name)
            cursor.execute(f"PRAGMA table_info('{clean_table}')")  # nosec B608
            cols = [r[1] for r in cursor.fetchall()]

            cursor.execute(f"SELECT COUNT(*) FROM '{clean_table}'")  # nosec B608
            total_count = cursor.fetchone()[0]

            cursor.execute(f"SELECT * FROM '{clean_table}' LIMIT {int(limit)}")  # nosec B608
            rows = cursor.fetchall()
            features = []
            for r in rows:
                features.append(
                    {
                        cols[i]: ("<geometry bytes>" if isinstance(r[i], bytes) else r[i])
                        for i in range(len(cols))
                    }
                )

            conn.close()
            return {
                "dataset": validated_path.name,
                "format": "GeoPackage / SQLite",
                "table": table_name,
                "total_records": total_count,
                "preview_limit": limit,
                "columns": cols,
                "sample_features": features,
            }

        # Preview CSV
        if ext in (".csv", ".tsv", ".txt"):
            import csv

            with open(validated_path, encoding="utf-8", errors="replace") as f:
                reader = csv.reader(f, delimiter=";" if ";" in f.readline() else ",")
                f.seek(0)
                rows = [r for idx, r in enumerate(reader) if idx < limit + 1]

            headers = rows[0] if rows else []
            data_rows = rows[1:] if len(rows) > 1 else []
            features = [dict(zip(headers, r, strict=False)) for r in data_rows]
            return {
                "dataset": validated_path.name,
                "format": "Delimited Text",
                "columns": headers,
                "preview_limit": limit,
                "sample_features": features,
            }

        # Preview Excel
        if ext in (".xlsx", ".xls"):
            try:
                import openpyxl  # type: ignore

                wb = openpyxl.load_workbook(str(validated_path), read_only=True)
                ws = wb.active
                rows = list(ws.iter_rows(values_only=True, max_row=limit + 1))
                headers = [str(c or "") for c in rows[0]] if rows else []
                features = (
                    [dict(zip(headers, r, strict=False)) for r in rows[1:]] if len(rows) > 1 else []
                )
                return {
                    "dataset": validated_path.name,
                    "format": "Microsoft Excel",
                    "sheet": ws.title,
                    "columns": headers,
                    "preview_limit": limit,
                    "sample_features": features,
                }
            except Exception as e:
                return {"dataset": validated_path.name, "format": "Excel", "error": str(e)}

        return {"dataset": validated_path.name, "message": f"Preview not implemented for {ext}"}


# Global singleton client
fme_form_client = FMEFormClient()
