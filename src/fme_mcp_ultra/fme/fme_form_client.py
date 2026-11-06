"""FME Form Client: Interacts directly with local FME Form 2025.2+ installations."""

from __future__ import annotations

import json
import os
import re
import subprocess
import sys
import time
from pathlib import Path
from typing import Any, Dict, List, Optional

from fme_mcp_ultra.core.config import settings
from fme_mcp_ultra.core.errors import FMEMCPError, WorkspaceExecutionError, WorkspaceNotFoundError
from fme_mcp_ultra.core.logging import get_logger
from fme_mcp_ultra.security.command_guard import command_guard
from fme_mcp_ultra.security.path_guard import path_guard

logger = get_logger("fme-form-client")


class FMEFormClient:
    """Manages local execution of FME Form workspaces via CLI and fmeobjects."""

    def __init__(self, fme_dir: Optional[str] = None) -> None:
        self.fme_dir = self._locate_fme_dir(fme_dir)
        self.fme_exe = self.fme_dir / ("fme.exe" if sys.platform == "win32" else "fme")
        self._fmeobjects_available = self._init_fmeobjects()

    def _locate_fme_dir(self, override_dir: Optional[str]) -> Path:
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
            import fmeobjects  # type: ignore

            return True
        except Exception as e:
            logger.debug(f"fmeobjects C-binding could not be initialised: {e}")
            return False

    def get_info(self) -> Dict[str, Any]:
        """Query FME Form build, licensing, and environment information."""
        if not self.fme_exe.exists():
            return {
                "installed": False,
                "version": "FME Form not detected",
                "fmeobjects_loaded": False,
            }

        cmd = command_guard.validate_command([str(self.fme_exe), "INFO", "JSON"])
        res = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8", errors="replace")
        data: Dict[str, Any] = {}
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

    def inspect_workspace(self, workspace_path: str) -> Dict[str, Any]:
        """Inspect workspace metadata, published parameters, transformers, readers, and writers."""
        validated_path = path_guard.validate_path(workspace_path, must_exist=True)
        if not validated_path.exists():
            raise WorkspaceNotFoundError(str(validated_path))

        result: Dict[str, Any] = {
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
            counts: Dict[str, int] = {}
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
            result["readers"] = sorted(list(readers))
            result["writers"] = sorted(list(writers))
        except Exception as e:
            result["parse_error"] = str(e)

        return result

    def run_workspace(
        self,
        workspace_path: str,
        parameters: Optional[Dict[str, Any]] = None,
        log_file: Optional[str] = None,
        timeout_seconds: Optional[int] = None,
    ) -> Dict[str, Any]:
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
        except subprocess.TimeoutExpired:
            raise WorkspaceExecutionError(
                f"Workspace execution timed out after {timeout} seconds",
                exit_code=-1,
                log_summary={"status": "TIMED_OUT"},
            )

    def _parse_log_summary(self, log_path: Path) -> Dict[str, Any]:
        """Parse execution log summary."""
        try:
            text = log_path.read_text(encoding="utf-8", errors="replace")
        except Exception:
            return {"status": "LOG_READ_ERROR"}

        lines = text.splitlines()
        errors, warnings, stats = [], [], []
        successful, failed = False, False

        for l in lines:
            if "Translation was SUCCESSFUL" in l:
                successful = True
            elif "Translation FAILED" in l or "Program Terminating" in l:
                failed = True
            elif "|ERROR |" in l or "|ERROR|" in l:
                errors.append(l.strip())
            elif "|WARN  |" in l or "|WARN |" in l:
                warnings.append(l.strip())
            elif "|INFORM|Features Read" in l or "|INFORM|Features Written" in l:
                stats.append(l.strip())

        status = "SUCCESS" if successful else ("FAILED" if failed else "UNKNOWN")
        return {
            "status": status,
            "error_count": len(errors),
            "warning_count": len(warnings),
            "errors": errors[:10],
            "warnings": warnings[:10],
            "stats": stats,
        }

    def list_transformers(self, search: Optional[str] = None) -> List[str]:
        """List available transformers."""
        if not self.fme_exe.exists():
            return []
        cmd = command_guard.validate_command([str(self.fme_exe), "LIST_TRANSFORMERS"])
        res = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8", errors="replace")
        if res.returncode != 0:
            return []

        lines = res.stdout.splitlines()
        transformers: List[str] = []
        capture = False
        for l in lines:
            clean = l.strip()
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

    def list_packages(self) -> List[Dict[str, Any]]:
        """List installed FME Hub packages."""
        if not self.fme_exe.exists():
            return []
        cmd = command_guard.validate_command([str(self.fme_exe), "PACKAGE", "LIST", "--format", "json"])
        res = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8", errors="replace")
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

    def execute_python(self, code: str, timeout_seconds: int = 120) -> Dict[str, Any]:
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
            try:
                os.remove(temp_py)
            except OSError:
                pass


# Global singleton client
fme_form_client = FMEFormClient()

