"""Tool modules for rick_mcp."""

from rick_mcp.tools.career import rick_compatibility_check, rick_cover_letter, rick_mentorship
from rick_mcp.tools.cve import rick_cve
from rick_mcp.tools.defensive import rick_hardening
from rick_mcp.tools.engagement import (
    rick_client_onboarding,
    rick_debrief,
    rick_engagement_proposal,
    rick_report_template,
    rick_roe,
    rick_tracker,
)
from rick_mcp.tools.meta import rick_demo, rick_health, rick_mode, rick_status
from rick_mcp.tools.offensive import (
    rick_attack_chain,
    rick_cheatsheet,
    rick_pivot_plan,
    rick_recon,
    rick_threat_model,
    rick_tool_recommend,
    rick_vuln_assess,
)


def register_all(mcp):
    """Register all tools on the MCP server."""
    from rick_mcp.tools import career, cve, defensive, engagement, meta, offensive

    offensive.register(mcp)
    defensive.register(mcp)
    engagement.register(mcp)
    career.register(mcp)
    meta.register(mcp)
    cve.register(mcp)


__all__ = [
    "rick_attack_chain",
    "rick_cheatsheet",
    "rick_client_onboarding",
    "rick_compatibility_check",
    "rick_cover_letter",
    "rick_cve",
    "rick_debrief",
    "rick_demo",
    "rick_engagement_proposal",
    "rick_hardening",
    "rick_health",
    "rick_mentorship",
    "rick_mode",
    "rick_pivot_plan",
    "rick_recon",
    "rick_report_template",
    "rick_roe",
    "rick_status",
    "rick_threat_model",
    "rick_tool_recommend",
    "rick_tracker",
    "rick_vuln_assess",
    "register_all",
]
