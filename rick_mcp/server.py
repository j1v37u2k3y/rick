"""
RICK MCP SERVER

A forkable Model Context Protocol server for security professionals.
Load your identity from ~/.rick_mcp/identity.yaml.
The tools are the craft. The identity is yours.
"""

from fastmcp import FastMCP

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


# Registered components live in a single dict on the local provider, keyed by
# "<kind>:<identity>@" — `tool:`, `resource:`, `template:`, `prompt:`.
# The public `list_*()` methods are async; the banner and `rick_status` call
# these counters synchronously, so we filter the component dict directly.
def _count_components(kind: str) -> int:
    prefix = f"{kind}:"
    return sum(1 for k in mcp._local_provider._components if k.startswith(prefix))


def tool_count() -> int:
    """Dynamic tool count from the MCP registry."""
    return _count_components("tool")


def resource_count() -> int:
    """Dynamic resource count from the MCP registry.

    Includes both static resources and parameterized resource templates
    (e.g. vault://engagements/{codename}) — counting statics alone
    under-reports by the template count and drifts from the
    README/refresh_counts total.
    """
    return _count_components("resource") + _count_components("template")


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
