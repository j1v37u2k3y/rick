"""Resource modules for rick_mcp."""

from rick_mcp.resources.docs import (
    res_achievements,
    res_changelog,
    res_contributing,
    res_profile,
    res_security,
    res_soul,
    res_the_book,
    res_war_stories,
    res_wwm,
)
from rick_mcp.resources.profile import (
    res_craftsmanship,
    res_entertainment,
    res_heritage,
    res_human,
    res_mantras,
    res_methodology,
    res_rick_and_jiveturkey,
    res_stack,
    res_summary,
    res_timeline,
    res_values,
)
from rick_mcp.resources.resume import (
    res_resume_contact,
    res_resume_evidence,
    res_resume_overview,
    res_resume_portfolio,
)


def register_all(mcp):
    """Register all resources on the MCP server."""
    from rick_mcp.resources import docs, profile, resume

    profile.register(mcp)
    docs.register(mcp)
    resume.register(mcp)


__all__ = [
    "res_achievements",
    "res_changelog",
    "res_contributing",
    "res_craftsmanship",
    "res_entertainment",
    "res_heritage",
    "res_human",
    "res_mantras",
    "res_methodology",
    "res_profile",
    "res_resume_contact",
    "res_resume_evidence",
    "res_resume_overview",
    "res_resume_portfolio",
    "res_rick_and_jiveturkey",
    "res_security",
    "res_soul",
    "res_stack",
    "res_summary",
    "res_the_book",
    "res_timeline",
    "res_values",
    "res_war_stories",
    "res_wwm",
    "register_all",
]
