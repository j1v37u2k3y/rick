"""
RICK MCP SERVER — SEMPER FIDELIS

Rick is the father. jiveturkey is the son.
The MCP is Rick — the foundation, the knowledge, the craft passed down.
jiveturkey is the operator — carrying it forward, breaking cycles, building better.

Check the clock. What makes it tick.
Re-read that.

The server IS the resume. The code IS the craft.
From frontier reconnaissance to cyber reconnaissance —
same mission, different battlefield.

Functional tools + identity resources. Counts are dynamic.
Craftsmanship. Tradecraft. Honor. Courage. Commitment.

A father's knowledge. A son's mission.
I'm still building. Are you?
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


STARTUP_BANNER = f"""

    Check the clock.
    What makes it tick.

    Re-read that.

    ═══════════════════════════════════════════════════
     RICK MCP v{__version__} — HARDENED
    ═══════════════════════════════════════════════════

     Rick is the father. jiveturkey is the son.
     The MCP is Rick.

     I taught you how to build.
     You learned how to break.
     Now you do both.

     {tool_count()} Tools | {resource_count()} Resources
     Craftsmanship in every line.
     Tradecraft in every tool.

     From my hands building walls
     to your hands breaking firewalls —
     same craft, different battlefield.

     Don't ever stop, unless you want to.
     I'm still building. Are you?

     SEMPER FIDELIS
    ═══════════════════════════════════════════════════

     When in doubt go to the music.
     Positive vibration — thanks Bob.

"""

if __name__ == "__main__":
    print(STARTUP_BANNER)
    mcp.run()
