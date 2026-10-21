"""Integration tests — MCP protocol-level tool invocation."""

import json

import pytest

from rick_mcp.constants import CALLSIGN
from rick_mcp.server import mcp


def _params(**kwargs):
    """Wrap kwargs in the params structure FastMCP expects."""
    return {"params": kwargs}


def _text(result):
    """Pull first TextContent out of a fastmcp ToolResult."""
    return result.content[0].text


async def _call_tool(name, args):
    """Invoke a registered tool by name via the fastmcp local provider."""
    tool = await mcp._get_tool(name)
    return await tool.run(args)


def _tool_names():
    """Registered tool names, read sync from the local provider's component dict.

    Keys are formatted ``tool:<name>@`` by fastmcp 4.x's identity scheme.
    """
    return [k[len("tool:") : -1] for k in mcp._local_provider._components if k.startswith("tool:")]


class TestMCPProtocol:
    """Test tools through the MCP server's call_tool interface."""

    @pytest.mark.asyncio
    async def test_call_rick_recon(self):
        result = await _call_tool("rick_recon", _params(target_type="web_app"))
        assert CALLSIGN in _text(result)

    @pytest.mark.asyncio
    async def test_call_rick_status(self):
        result = await _call_tool("rick_status", {})
        assert "rick_mcp" in _text(result)

    @pytest.mark.asyncio
    async def test_call_rick_hardening(self):
        result = await _call_tool("rick_hardening", _params(technology="linux_server"))
        text = _text(result)
        assert "SSH" in text or "ssh" in text

    @pytest.mark.asyncio
    async def test_call_rick_c2_compare(self):
        result = await _call_tool("rick_c2_compare", _params(scenario="budget"))
        assert "Sliver" in _text(result)

    @pytest.mark.asyncio
    async def test_call_rick_incident_response(self):
        result = await _call_tool("rick_incident_response", _params(incident_type="ransomware"))
        text = _text(result)
        assert "containment" in text.lower() or "Containment" in text

    @pytest.mark.asyncio
    async def test_call_rick_scoping(self):
        result = await _call_tool("rick_scoping", _params(engagement_type="web_app_pentest"))
        text = _text(result)
        assert "hours" in text.lower() or "Hours" in text

    @pytest.mark.asyncio
    async def test_call_rick_detection_rules(self):
        result = await _call_tool("rick_detection_rules", _params(attack_pattern="credential_dumping"))
        text = _text(result)
        assert "sigma" in text.lower() or "Sigma" in text

    @pytest.mark.asyncio
    async def test_call_with_json_format(self):
        result = await _call_tool("rick_recon", _params(target_type="network", response_format="json"))
        parsed = json.loads(_text(result))
        assert "phase" in parsed

    @pytest.mark.asyncio
    async def test_call_invalid_input_returns_error(self):
        result = await _call_tool("rick_recon", _params(target_type="nonexistent_target"))
        assert "Error" in _text(result)


class TestMCPRegistration:
    """Verify all tools and resources are properly registered."""

    def test_tool_count(self):
        from rick_mcp.server import tool_count

        assert len(_tool_names()) == tool_count()

    def test_new_tools_registered(self):
        tool_names = _tool_names()
        new_tools = [
            "rick_c2_compare",
            "rick_payload_guide",
            "rick_cloud_attack_path",
            "rick_wireless",
            "rick_incident_response",
            "rick_detection_rules",
            "rick_log_analysis",
            "rick_scoping",
        ]
        for tool in new_tools:
            assert tool in tool_names, f"{tool} not registered"
