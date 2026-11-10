"""Unit tests for FME Custom Transformer Bridge."""

from __future__ import annotations

from unittest.mock import MagicMock

from fme_mcp_ultra.fme.transformer_bridge import (
    MCPAgentBridgeTransformer,
    is_bridge_running,
)


class MockFeature:
    """Mock FME Feature class mimicking fmeobjects.FMEFeature."""

    def __init__(self, feature_type: str = "TestFeature", attrs: dict | None = None) -> None:
        self.feature_type = feature_type
        self.attributes = attrs or {"id": 101, "address": "10 Rue de la Paix, 75002 Paris"}

    def getFeatureType(self) -> str:
        return self.feature_type

    def getAttribute(self, name: str) -> object:
        return self.attributes.get(name)

    def setAttribute(self, name: str, value: object) -> None:
        self.attributes[name] = value

    def getAllAttributeNames(self) -> list[str]:
        return list(self.attributes.keys())


def test_is_bridge_running_offline():
    assert not is_bridge_running(port=59999)


def test_transformer_bridge_offline_graceful():
    transformer = MCPAgentBridgeTransformer()
    # Force offline
    transformer.connected = False
    transformer.sock = None
    transformer.pyoutput = MagicMock()

    feat = MockFeature()
    transformer.input(feat)

    assert feat.getAttribute("_mcp_status") == "BRIDGE_STANDALONE"
    assert feat.getAttribute("_mcp_bridge_port") == 9877
    transformer.pyoutput.assert_called_once_with(feat)


def test_transformer_bridge_connected_send():
    transformer = MCPAgentBridgeTransformer()
    transformer.connected = True
    transformer.sock = MagicMock()
    transformer.pyoutput = MagicMock()

    feat = MockFeature()
    feat.setAttribute("_ai_action", "GEOCODE_AI")
    transformer.input(feat)

    assert feat.getAttribute("_mcp_status") == "CONNECTED"
    assert "streamed to AI Agent" in feat.getAttribute("_ai_response")
    transformer.sock.sendall.assert_called_once()
    transformer.pyoutput.assert_called_once_with(feat)
    transformer.close()
