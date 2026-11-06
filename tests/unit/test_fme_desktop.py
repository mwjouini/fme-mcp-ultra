"""Unit tests for FME Desktop integration, diagnosis, canvas inspection, and loopback bridge."""

from pathlib import Path

from fme_mcp_ultra.fme.fme_bridge import FMEBridgeClient, FMEBridgeServer
from fme_mcp_ultra.fme.fme_form_client import fme_form_client
from fme_mcp_ultra.tools.workspaces.workspace_tools import (
    fme_diagnose,
    fme_inspect_canvas,
    fme_open_in_inspector,
    fme_open_in_workbench,
    fme_preview_dataset,
)


def test_fme_diagnose():
    """Verify diagnose reports FME installation status and processes."""
    diag = fme_form_client.diagnose()
    assert isinstance(diag, dict)
    assert "fme_installed" in diag
    assert "fme_version" in diag
    assert "desktop_processes" in diag
    assert "bridge_status" in diag

    tool_res = fme_diagnose()
    assert tool_res["success"] is True
    assert "fme_installed" in tool_res["data"]
    assert "bridge_status" in tool_res["data"]


def test_fme_inspect_canvas(tmp_path: Path):
    """Verify inspect_canvas parses workspace XML nodes, links, and parameters."""
    dummy_fmw = tmp_path / "test_workspace.fmw"
    dummy_fmw.write_text(
        """#! <?xml version="1.0" encoding="utf-8" ?>
#! <WORKSPACE
#!   TITLE="Sample Canvas"
#!   MAX_LOOP_ITERATIONS=""
#!   EXPLICIT_BOOKMARK_ORDER="false"
#! >
#! <DATASETS>
#! </DATASETS>
#! <DATA_TYPES>
#! </DATA_TYPES>
#! <GEOM_TYPES>
#! </GEOM_TYPES>
#! <FEATURE_TYPES>
#!   <FEATURE_TYPE IS_SOURCE="true" NODE_NAME="InputData" POSITION="100 -200">
#!   </FEATURE_TYPE>
#! </FEATURE_TYPES>
#! <FMESERVER>
#! </FMESERVER>
#! <GLOBAL_PARAMETERS>
#! </GLOBAL_PARAMETERS>
#! <COMMENTS>
#! </COMMENTS>
#! <CONSTANTS>
#! </CONSTANTS>
#! <TRANSFORMERS>
#!   <TRANSFORMER IDENTIFIER="1" TYPE="Tester" POSITION="500 -200">
#!     <XFORM_PARM PARM_NAME="XFORMER_NAME" PARM_VALUE="Tester_1"/>
#!     <OUTPUT_FEAT NAME="PASSED"/>
#!   </TRANSFORMER>
#! </TRANSFORMERS>
#! <FEAT_LINKS>
#!   <FEAT_LINK IDENTIFIER="1" SOURCE_NODE="InputData" TARGET_NODE="Tester" SOURCE_PORT_DESC="OUTPUT" TARGET_PORT_DESC="TEST"/>
#! </FEAT_LINKS>
#! </WORKSPACE>
""",
        encoding="utf-8",
    )

    client_res = fme_form_client.inspect_canvas(str(dummy_fmw))
    assert client_res["workspace"] == "test_workspace.fmw"
    assert client_res["total_transformers"] == 1
    assert client_res["transformers"][0]["type"] == "Tester"
    assert client_res["total_links"] == 1

    tool_res = fme_inspect_canvas(str(dummy_fmw))
    assert tool_res["success"] is True
    assert tool_res["data"]["total_transformers"] == 1


def test_fme_preview_dataset_csv(tmp_path: Path):
    """Verify preview_dataset returns headers and sample records for CSV."""
    csv_file = tmp_path / "sample.csv"
    csv_file.write_text(
        "ID,NAME,SCORE\n101,Site Alpha,95.5\n102,Site Beta,88.0\n", encoding="utf-8"
    )

    client_res = fme_form_client.preview_dataset(str(csv_file), limit=5)
    assert client_res["format"] == "Delimited Text"
    assert client_res["columns"] == ["ID", "NAME", "SCORE"]
    assert len(client_res["sample_features"]) == 2
    assert client_res["sample_features"][0]["NAME"] == "Site Alpha"

    tool_res = fme_preview_dataset(str(csv_file), limit=5)
    assert tool_res["success"] is True
    assert len(tool_res["data"]["sample_features"]) == 2


def test_fme_open_in_workbench_missing():
    """Verify error handling when workspace file does not exist."""
    res = fme_open_in_workbench("C:/non_existent/workspace.fmw")
    assert res["success"] is False
    assert "not exist" in str(res["data"])


def test_fme_open_in_inspector_missing():
    """Verify error handling when dataset file does not exist."""
    res = fme_open_in_inspector("C:/non_existent/dataset.gpkg")
    assert res["success"] is False
    assert "not exist" in str(res["data"])


def test_fme_bridge_loopback_socket():
    """Verify FMEBridgeServer and FMEBridgeClient roundtrip communication."""
    port = 9889  # Distinct port for test
    server = FMEBridgeServer(host="127.0.0.1", port=port)
    client = FMEBridgeClient(host="127.0.0.1", port=port)

    assert client.is_bridge_active(timeout=0.2) is False

    server.start()
    try:
        assert client.is_bridge_active(timeout=1.0) is True

        # Send ping
        ping_resp = client.send_command("ping")
        assert ping_resp["status"] == "SUCCESS"
        assert ping_resp["result"]["pong"] is True

        # Send diagnose
        diag_resp = client.send_command("diagnose")
        assert diag_resp["status"] == "SUCCESS"
        assert "fme_installed" in diag_resp["result"]

        # Send invalid command
        bad_resp = client.send_command("non_existent_command")
        assert bad_resp["status"] == "ERROR"
    finally:
        server.stop()
