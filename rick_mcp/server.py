"""
RICK MCP SERVER

A forkable Model Context Protocol server for security professionals.
Load your identity from ~/.rick_mcp/identity.yaml.
The tools are the craft. The identity is yours.
"""

from mcp.server.fastmcp import FastMCP

from __version__ import __version__

# Initialize logging before anything else
from rick_mcp.logging_config import logger  # noqa: F401

# Create the MCP server instance
mcp = FastMCP("rick_mcp")

# Register all resources and tools (must be after mcp creation)
from rick_mcp.prompts import register as register_prompts  # noqa: E402
from rick_mcp.resources import register_all as register_resources  # noqa: E402
from rick_mcp.tools import register_all as register_tools  # noqa: E402

register_resources(mcp)
register_tools(mcp)
register_prompts(mcp)


def tool_count() -> int:
    """Dynamic tool count from the MCP registry."""
    return len(mcp._tool_manager.list_tools())


def resource_count() -> int:
    """Dynamic resource count from the MCP registry."""
    return len(mcp._resource_manager.list_resources())


def _build_banner() -> str:
    """Build startup banner dynamically from identity config."""
    from rick_mcp.identity import CALLSIGN, MOTTO, TAGLINE, is_configured

    tc = tool_count()
    rc = resource_count()

    if is_configured():
        motto_line = f"\n     {MOTTO}\n" if MOTTO else ""
        return f"""
    ═══════════════════════════════════════════════════
     RICK MCP v{__version__} — {CALLSIGN}
    ═══════════════════════════════════════════════════
{motto_line}
     {TAGLINE}

     {tc} Tools | {rc} Resources
     The tools are the craft. The identity is yours.

    ═══════════════════════════════════════════════════
"""
    else:
        return f"""
    ═══════════════════════════════════════════════════
     RICK MCP v{__version__}
    ═══════════════════════════════════════════════════

     A forkable MCP server for security professionals.
     Configure your identity: ~/.rick_mcp/identity.yaml

     {tc} Tools | {rc} Resources

    ═══════════════════════════════════════════════════
"""


if __name__ == "__main__":
    print(_build_banner())
    mcp.run()
