"""Create a demo FME Workspace (.fmw) showing MCPAgentBridge in action."""

from __future__ import annotations
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parent))
from build_fme_transformer import encode_fme_text, FME_PYTHON_SOURCE

def build_demo_fmw() -> str:
    encoded_py = encode_fme_text(FME_PYTHON_SOURCE)
    return f"""#! <?xml version="1.0" encoding="UTF-8" ?>
#! <WORKSPACE
#    Command line to run this workspace:
#        "C:\\Program Files\\FME\\fme.exe" MCPAgentBridge_Demo.fmw
#!   ARCGIS_COMPATIBILITY="ARCGIS_AUTO"
#!   ATTR_TYPE_ENCODING="SDF"
#!   CATEGORY=""
#!   DESCRIPTION="Demo workspace demonstrating AI Agent &amp; MCP integration with FME Form"
#!   DOC_EXTENTS="1500 500"
#!   DOC_TOP_LEFT="0 0"
#!   ENABLE_DATA_CACHING="Yes"
#!   ENABLE_FEATURE_COUNTING="Yes"
#!   FME_BUILD_NUM="25810"
#!   FME_DOCUMENT_GUID="a19451df-29bb-4c28-910f-21cb03fae881"
#!   FME_GEOMETRY_HANDLING="Enhanced"
#!   FME_NAMES_ENCODING="UTF-8"
#!   FME_REPROJECTION_ENGINE="FME"
#!   LAST_SAVE_BUILD="FME(R) 2025.2.0.0 (20251120 - Build 25810 - WIN64)"
#!   LAST_SAVE_DATE="2026-11-10T15:00:00"
#!   PYTHON_COMPATIBILITY="310+"
#!   TITLE="MCPAgentBridge Demo"
#!   WORKSPACE_VERSION="1"
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
#! </GLOBAL_PARAMETERS>
#! <COMMENTS>
#! </COMMENTS>
#! <CONSTANTS>
#! </CONSTANTS>
#! <BOOKMARKS>
#! </BOOKMARKS>
#! <TRANSFORMERS>
#! <TRANSFORMER
#!   IDENTIFIER="1"
#!   TYPE="Creator"
#!   VERSION="5"
#!   POSITION="100 200"
#!   BOUNDING_RECT="100 200 450 65"
#!   ORDER="500000000000001"
#!   PARMS_EDITED="true"
#!   ENABLED="true"
#! >
#!     <OUTPUT_FEAT NAME="CREATED"/>
#!     <FEAT_COLLAPSED COLLAPSED="0"/>
#!     <XFORM_PARM PARM_NAME="CREATOR_NAME" PARM_VALUE="Creator"/>
#!     <XFORM_PARM PARM_NAME="NUM_CLONES" PARM_VALUE="5"/>
#!     <XFORM_PARM PARM_NAME="XFORMER_NAME" PARM_VALUE="Creator"/>
#! </TRANSFORMER>
#! <TRANSFORMER
#!   IDENTIFIER="2"
#!   TYPE="AttributeCreator"
#!   VERSION="9"
#!   POSITION="500 200"
#!   BOUNDING_RECT="500 200 450 65"
#!   ORDER="500000000000002"
#!   PARMS_EDITED="true"
#!   ENABLED="true"
#! >
#!     <OUTPUT_FEAT NAME="OUTPUT"/>
#!     <FEAT_COLLAPSED COLLAPSED="0"/>
#!     <XFORM_ATTR ATTR_NAME="_ai_action" IS_USER_CREATED="false" FEAT_INDEX="0" />
#!     <XFORM_ATTR ATTR_NAME="sample_address" IS_USER_CREATED="false" FEAT_INDEX="0" />
#!     <XFORM_PARM PARM_NAME="XFORMER_NAME" PARM_VALUE="Setup_AI_Params"/>
#! </TRANSFORMER>
#! <TRANSFORMER
#!   IDENTIFIER="3"
#!   TYPE="PythonCaller"
#!   VERSION="4"
#!   POSITION="950 200"
#!   BOUNDING_RECT="950 200 450 65"
#!   ORDER="500000000000003"
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
#!     <XFORM_PARM PARM_NAME="XFORMER_NAME" PARM_VALUE="MCPAgentBridge"/>
#! </TRANSFORMER>
#! </TRANSFORMERS>
#! <FEAT_LINKS>
#! <FEAT_LINK
#!   IDENTIFIER="101"
#!   SOURCE_NODE="1"
#!   TARGET_NODE="2"
#!   SOURCE_PORT_NAME="CREATED"
#!   TARGET_PORT_NAME="Input"
#!   EXTRA_CP_POINTS=""
#! />
#! <FEAT_LINK
#!   IDENTIFIER="102"
#!   SOURCE_NODE="2"
#!   TARGET_NODE="3"
#!   SOURCE_PORT_NAME="OUTPUT"
#!   TARGET_PORT_NAME="Input"
#!   EXTRA_CP_POINTS=""
#! />
#! </FEAT_LINKS>
#! </WORKSPACE>
# ============================================================================
DEFAULT_MACRO WB_CURRENT_CONTEXT
READER_TYPE NULL
NULL_DATASET null
WRITER_TYPE NULL
NULL_DEST NULL

FACTORY_DEF * CreationFactory \\
   FACTORY_NAME Creator_Creator \\
   OUTPUT FEATURE_TYPE Creator_CREATED

FACTORY_DEF * TeeFactory \\
   FACTORY_NAME Setup_AI_Params \\
   INPUT FEATURE_TYPE Creator_CREATED \\
   OUTPUT FEATURE_TYPE Setup_AI_Params_OUTPUT \\
   _ai_action "VALIDATE_AND_ENRICH" \\
   sample_address "10 Rue de la Paix, 75002 Paris"

FACTORY_DEF {{*}} PythonFactory \\
   FACTORY_NAME MCPAgentBridge_Caller \\
   FLUSH_WHEN_GROUPS_CHANGE No \\
   INPUT FEATURE_TYPE Setup_AI_Params_OUTPUT \\
   SYMBOL_NAME {{ MCPAgentBridgeTransformer }} \\
   SOURCE_CODE {{ {encoded_py} }} \\
   OUTPUT {{ PYOUTPUT FEATURE_TYPE MCPAgentBridge_OUTPUT }}
"""

def main() -> None:
    demo_file = Path("e:/fme_mcp/fme-mcp-ultra/examples/workbench/MCPAgentBridge_Demo.fmw")
    content = build_demo_fmw()
    demo_file.write_text(content, encoding="utf-8")
    print(f"Generated demo workspace: {demo_file} ({len(content)} bytes)")

if __name__ == "__main__":
    main()
