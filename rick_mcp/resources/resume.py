"""Resume resources — the MCP as living resume."""

from rick_mcp.formatting import _read_data


async def res_resume_overview() -> str:
    """This MCP server is a living resume. This resource explains how."""
    return _read_data("resume", "overview")


async def res_resume_evidence() -> str:
    """Maps each tool to the skills it proves. The exhibit list."""
    return _read_data("resume", "evidence")


async def res_resume_portfolio() -> str:
    """External portfolio — public work and gated contact."""
    return _read_data("resume", "portfolio")


async def res_resume_contact() -> str:
    """How to engage. Next steps."""
    return _read_data("resume", "contact")


def register(mcp):
    """Register resources on the MCP server."""
    mcp.resource("resume://overview")(res_resume_overview)
    mcp.resource("resume://evidence")(res_resume_evidence)
    mcp.resource("resume://portfolio")(res_resume_portfolio)
    mcp.resource("resume://contact")(res_resume_contact)