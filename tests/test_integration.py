"""Integration tests — MCP protocol-level tool invocation."""

import json

import pytest

from rick_mcp.server import mcp


def _params(**kwargs):
    """Wrap kwargs in the params structure FastMCP expects."""
    return {"params": kwargs}


class TestMCPProtocol:
    """Test tools through the MCP server's call_tool interface."""

    @pytest.mark.asyncio
    async def test_call_rick_recon(self):
        result = await mcp.call_tool("rick_recon", _params(target_type="web_app"))
        content = result[0] if not isinstance(result, tuple) else result[0]
        text = (
            content[0].text
            if isinstance(content, list)
            else (content.text if hasattr(content, "text") else str(content))
        )
        assert "operator" in text

    @pytest.mark.asyncio
    async def test_call_rick_status(self):
        result = await mcp.call_tool("rick_status", {})
        content = result[0] if not isinstance(result, tuple) else result[0]
        text = (
            content[0].text
            if isinstance(content, list)
            else (content.text if hasattr(content, "text") else str(content))
        )
        assert "rick_mcp" in text

    @pytest.mark.asyncio
    async def test_call_rick_hardening(self):
        result = await mcp.call_tool("rick_hardening", _params(technology="linux_server"))
        content = result[0] if not isinstance(result, tuple) else result[0]
        text = (
            content[0].text
            if isinstance(content, list)
            else (content.text if hasattr(content, "text") else str(content))
        )
        assert "SSH" in text or "ssh" in text

    @pytest.mark.asyncio
    async def test_call_rick_c2_compare(self):
        result = await mcp.call_tool("rick_c2_compare", _params(scenario="budget"))
        content = result[0] if not isinstance(result, tuple) else result[0]
        text = (
            content[0].text
            if isinstance(content, list)
            else (content.text if hasattr(content, "text") else str(content))
        )
        assert "Sliver" in text

    @pytest.mark.asyncio
    async def test_call_rick_incident_response(self):
        result = await mcp.call_tool("rick_incident_response", _params(incident_type="ransomware"))
        content = result[0] if not isinstance(result, tuple) else result[0]
        text = (
            content[0].text
            if isinstance(content, list)
            else (content.text if hasattr(content, "text") else str(content))
        )
        assert "containment" in text.lower() or "Containment" in text

    @pytest.mark.asyncio
    async def test_call_rick_scoping(self):
        result = await mcp.call_tool("rick_scoping", _params(engagement_type="web_app_pentest"))
        content = result[0] if not isinstance(result, tuple) else result[0]
        text = (
            content[0].text
            if isinstance(content, list)
            else (content.text if hasattr(content, "text") else str(content))
        )
        assert "hours" in text.lower() or "Hours" in text

    @pytest.mark.asyncio
    async def test_call_rick_detection_rules(self):
        result = await mcp.call_tool("rick_detection_rules", _params(attack_pattern="credential_dumping"))
        content = result[0] if not isinstance(result, tuple) else result[0]
        text = (
            content[0].text
            if isinstance(content, list)
            else (content.text if hasattr(content, "text") else str(content))
        )
        assert "sigma" in text.lower() or "Sigma" in text

    @pytest.mark.asyncio
    async def test_call_with_json_format(self):
        result = await mcp.call_tool("rick_recon", _params(target_type="network", response_format="json"))
        content = result[0] if not isinstance(result, tuple) else result[0]
        text = (
            content[0].text
            if isinstance(content, list)
            else (content.text if hasattr(content, "text") else str(content))
        )
        parsed = json.loads(text)
        assert "phase" in parsed

    @pytest.mark.asyncio
    async def test_call_invalid_input_returns_error(self):
        result = await mcp.call_tool("rick_recon", _params(target_type="nonexistent_target"))
        content = result[0] if not isinstance(result, tuple) else result[0]
        text = (
            content[0].text
            if isinstance(content, list)
            else (content.text if hasattr(content, "text") else str(content))
        )
        assert "Error" in text


class TestMCPRegistration:
    """Verify all tools and resources are properly registered."""

    def test_tool_count(self):
        from rick_mcp.server import tool_count

        tool_names = [t.name for t in mcp._tool_manager.list_tools()]
        assert len(tool_names) == tool_count()

    def test_new_tools_registered(self):
        tool_names = [t.name for t in mcp._tool_manager.list_tools()]
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
