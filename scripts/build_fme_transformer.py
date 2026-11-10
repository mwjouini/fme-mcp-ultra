"""Generator for MCPAgentBridge FME Custom Transformer (.fmx) and demo workspace (.fmw)."""

from __future__ import annotations

import os
from pathlib import Path

FME_PYTHON_SOURCE = """# MCPAgentBridge FME Custom Transformer Script
# Runs natively inside FME Form's embedded Python. Zero external setup.
import contextlib
import json
import socket
import sys
import time

try:
    import fmeobjects
except ImportError:
    pass

class MCPAgentBridgeTransformer:
    def __init__(self):
        self.host = "127.0.0.1"
        self.port = 9877
        self.sock = None
        self.connected = False
        self._init_connection()

    def _init_connection(self):
        try:
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.sock.settimeout(0.8)
            self.sock.connect((self.host, self.port))
            self.connected = True
        except Exception:
            self.connected = False
            self.sock = None

    def input(self, feature):
        action = feature.getAttribute("_ai_action") or "INSPECT"
        feature_type = (
            feature.getFeatureType()
            if hasattr(feature, "getFeatureType")
            else str(feature.getAttribute("fme_feature_type") or "Feature")
        )

        attrs = {}
        if hasattr(feature, "getAllAttributeNames"):
            for name in feature.getAllAttributeNames():
                if not name.startswith("fme_") and not name.startswith("_mcp_"):
                    val = feature.getAttribute(name)
                    if val is not None:
                        attrs[name] = str(val)

        payload = {
            "jsonrpc": "2.0",
            "method": "fme_feature_event",
            "params": {
                "action": action,
                "feature_type": feature_type,
                "attributes": attrs,
                "timestamp": time.time(),
            },
        }

        if self.connected and self.sock:
            try:
                msg = (json.dumps(payload) + "\\n").encode("utf-8")
                self.sock.sendall(msg)
                status = "AI_CONNECTED"
                resp = f"Sent to AI Agent on port {self.port}"
            except Exception as err:
                status = f"BRIDGE_ERROR: {err}"
                resp = "Bridge socket send error"
                self.connected = False
        else:
            status = "STANDALONE_FME"
            resp = "Processed via FME Embedded Python (MCP bridge ready on port 9877)"

        feature.setAttribute("_mcp_status", status)
        feature.setAttribute("_ai_action_used", action)
        feature.setAttribute("_ai_bridge_port", self.port)
        feature.setAttribute("_ai_response", resp)

        if hasattr(self, "pyoutput"):
            self.pyoutput(feature)

    def close(self):
        if self.sock:
            with contextlib.suppress(Exception):
                self.sock.close()
            self.sock = None
            self.connected = False
"""


def encode_fme_text(text: str) -> str:
    """Encode python code into FME mapping XML representation."""
    encoded = text.replace("&", "&amp;")
    encoded = encoded.replace("<", "&lt;").replace(">", "&gt;")
    encoded = encoded.replace("(", "&openparen;").replace(")", "&closeparen;")
    encoded = encoded.replace(" ", "&lt;space&gt;")
    encoded = encoded.replace("\\n", "&lt;lf&gt;").replace("\n", "&lt;lf&gt;")
    encoded = encoded.replace('"', "&quot;")
    return encoded


def build_fmx_content() -> str:
    encoded_py = encode_fme_text(FME_PYTHON_SOURCE)
    guid = "08e5e6b1-4f32-4759-86ab-590d9841f231"

    return f"""#! <?xml version="1.0" encoding="UTF-8" ?>
#! <TRANSFORMER
# TRANSFORMER_BEGIN MCPAgentBridge,1,Web,{guid},"Linked Always",Yes,NO_PARALLELISM,,No,25810,YES,No,,No,
#
# <p style=" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px;"><b>MCPAgentBridge</b> connects FME Workbench directly to AI Agents &amp; MCP Servers (Claude, Antigravity, Cursor, ChatGPT). Runs entirely within FME Form's embedded Python runtime - no external Python installation required on Windows.</p>
# TRANSFORMER_END
#!   ARCGIS_COMPATIBILITY="ARCGIS_AUTO"
#!   ATTR_TYPE_ENCODING="SDF"
#!   BLOCKED_LOOPING="Yes"
#!   CATEGORY="Web"
#!   DESCRIPTION="&#10;&lt;p&gt;Connects FME Workbench directly to AI Agents and MCP servers using FME embedded Python.&lt;/p&gt;"
#!   DOC_EXTENTS="1200 400"
#!   DOC_TOP_LEFT="0 0"
#!   EXPLICIT_BOOKMARK_ORDER="false"
#!   FME_BUILD_NUM="25810"
#!   FME_DOCUMENT_GUID="{guid}"
#!   FME_LINKED_TRANSFORMER_VERSION="1"
#!   FME_NAMES_ENCODING="UTF-8"
#!   FME_PROCESS_COUNT="NO_PARALLELISM"
#!   FME_PROCESS_GROUPS_ORDERED="No"
#!   FME_SERVER_SERVICES=""
#!   FMX_ATTRIBUTE_PROPOGATION_MODE="AUTO"
#!   FMX_INSERT_MODE="Linked Always"
#!   LAST_SAVE_BUILD="FME(R) 2025.2.0.0 (20251120 - Build 25810 - WIN64)"
#!   LAST_SAVE_DATE="2026-11-10T15:00:00"
#!   PYTHON_COMPATIBILITY="310+"
#!   TITLE="MCPAgentBridge"
#!   WORKSPACE_VERSION="1"
#!   XFORM_DEPRECATED="No"
#!   ZOOM_SCALE="100"
#! >
#! <DATASETS>
#! </DATASETS>
#! <DATA_TYPES>
#! </DATA_TYPES>
#! <GEOM_TYPES>
#! </GEOM_TYPES>
#! <FEATURE_TYPES>
#! </FEATURE_TYPES>
#! <FMESERVER>
#! </FMESERVER>
#! <GLOBAL_PARAMETERS>
#! <GLOBAL_PARAMETER
#!   GUI_LINE="GUI CHOICE_OR_ATTR AI_ACTION INSPECT%VALIDATE_GEOMETRY%ANALYZE%GEOCODE_AUDIT AI Action:"
#!   DEFAULT_VALUE="INSPECT"
#!   IS_STAND_ALONE="false"
#! />
#! <GLOBAL_PARAMETER
#!   GUI_LINE="GUI INTEGER BRIDGE_PORT Bridge Port (Default 9877):"
#!   DEFAULT_VALUE="9877"
#!   IS_STAND_ALONE="false"
#! />
#! </GLOBAL_PARAMETERS>
#! <USER_PARAMETERS>
#! </USER_PARAMETERS>
#! <COMMENTS>
#! </COMMENTS>
#! <TRANSFORMERS>
#! <TRANSFORMER
#!   IDENTIFIER="1"
#!   TYPE="PythonCaller"
#!   VERSION="4"
#!   POSITION="500 200"
#!   BOUNDING_RECT="500 200 450 65"
#!   ORDER="500000000000001"
#!   PARMS_EDITED="true"
#!   ENABLED="true"
#!   LAST_PARM_EDIT="25810"
#! >
#!     <OUTPUT_FEAT NAME="OUTPUT"/>
#!     <FEAT_COLLAPSED COLLAPSED="0"/>
#!     <XFORM_ATTR ATTR_NAME="_mcp_status" IS_USER_CREATED="false" FEAT_INDEX="0" />
#!     <XFORM_ATTR ATTR_NAME="_ai_action_used" IS_USER_CREATED="false" FEAT_INDEX="0" />
#!     <XFORM_ATTR ATTR_NAME="_ai_bridge_port" IS_USER_CREATED="false" FEAT_INDEX="0" />
#!     <XFORM_ATTR ATTR_NAME="_ai_response" IS_USER_CREATED="false" FEAT_INDEX="0" />
#!     <XFORM_PARM PARM_NAME="NEW_ATTRIBUTES" PARM_VALUE="_mcp_status _ai_action_used _ai_bridge_port _ai_response"/>
#!     <XFORM_PARM PARM_NAME="PYTHONSOURCE" PARM_VALUE="{encoded_py}"/>
#!     <XFORM_PARM PARM_NAME="PYTHONSYMBOL" PARM_VALUE="MCPAgentBridgeTransformer"/>
#!     <XFORM_PARM PARM_NAME="XFORMER_NAME" PARM_VALUE="MCPAgentBridge_Caller"/>
#! </TRANSFORMER>
#! </TRANSFORMERS>
#! <FEAT_LINKS>
#! </FEAT_LINKS>
#! </TRANSFORMER>
# ============================================================================
DEFAULT_MACRO WB_CURRENT_CONTEXT
DEFAULT_MACRO MCPAgentBridge_WORKSPACE_NAME ""
INCLUDE [puts {{MACRO WB_OLD_CONTEXT_$(MCPAgentBridge_WORKSPACE_NAME) $(WB_CURRENT_CONTEXT)}}; \\
         puts {{MACRO WB_CURRENT_CONTEXT $(MCPAgentBridge_WORKSPACE_NAME)}}]

FACTORY_DEF * TeeFactory \\
   FACTORY_NAME "$(MCPAgentBridge_WORKSPACE_NAME)_Input_Splitter" \\
   INPUT FEATURE_TYPE "$(MCPAgentBridge_WORKSPACE_NAME)_Input" \\
   OUTPUT FEATURE_TYPE "$(MCPAgentBridge_WORKSPACE_NAME)_Input"

FACTORY_DEF {{*}} PythonFactory \\
   FACTORY_NAME {{ $(MCPAgentBridge_WORKSPACE_NAME)_MCPAgentBridge_Caller }} \\
   FLUSH_WHEN_GROUPS_CHANGE No \\
   INPUT FEATURE_TYPE "$(MCPAgentBridge_WORKSPACE_NAME)_Input" \\
   SYMBOL_NAME {{ MCPAgentBridgeTransformer }} \\
   SOURCE_CODE {{ {encoded_py} }} \\
   OUTPUT {{ PYOUTPUT FEATURE_TYPE "$(MCPAgentBridge_WORKSPACE_NAME)_Output" }}

INCLUDE [puts {{MACRO WB_CURRENT_CONTEXT $(WB_OLD_CONTEXT_$(MCPAgentBridge_WORKSPACE_NAME))}}]
"""


def main() -> None:
    repo_root = Path(__file__).resolve().parent.parent
    transformers_dir = repo_root / "transformers"
    transformers_dir.mkdir(parents=True, exist_ok=True)

    fmx_file = transformers_dir / "MCPAgentBridge.fmx"
    content = build_fmx_content()
    fmx_file.write_text(content, encoding="utf-8")
    print(f"Generated: {fmx_file} ({len(content)} bytes)")

    # Also deploy directly to user's FME Transformers folder if present
    user_fme_dir = Path(os.environ.get("USERPROFILE", "")) / "Documents" / "FME" / "Transformers"
    if user_fme_dir.exists():
        target_fmx = user_fme_dir / "MCPAgentBridge.fmx"
        target_fmx.write_text(content, encoding="utf-8")
        print(f"Deployed directly to FME User Transformers: {target_fmx}")

    desktop_fmx = Path(os.environ.get("USERPROFILE", "")) / "Desktop" / "MCPAgentBridge.fmx"
    desktop_fmx.write_text(content, encoding="utf-8")
    print(f"Copied to Desktop for upload: {desktop_fmx}")


if __name__ == "__main__":
    main()
