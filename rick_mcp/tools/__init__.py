"""Tool modules for rick_mcp."""

from rick_mcp.tools.appraisal import rick_cognitive_appraisal
from rick_mcp.tools.career import rick_compatibility_check, rick_cover_letter, rick_mentorship
from rick_mcp.tools.code_review import rick_code_review
from rick_mcp.tools.cve import rick_cve
from rick_mcp.tools.defensive import rick_detection_rules, rick_hardening, rick_incident_response, rick_log_analysis
from rick_mcp.tools.engagement import (
    rick_client_onboarding,
    rick_debrief,
    rick_engagement_proposal,
    rick_report_template,
    rick_roe,
    rick_scoping,
    rick_tracker,
)
from rick_mcp.tools.jarvis import rick_full_auto, rick_kill_chain, rick_next_move, rick_sitrep
from rick_mcp.tools.jarvis_extended import (
    rick_checklist,
    rick_compare,
    rick_export,
    rick_notes,
    rick_rollback,
    rick_scope_check,
    rick_tag,
    rick_timeline,
)
from rick_mcp.tools.meta import rick_capabilities, rick_demo, rick_health, rick_mantra, rick_mode, rick_status
from rick_mcp.tools.offensive import rick_recon, rick_tool_recommend, rick_vuln_assess
from rick_mcp.tools.offensive_chains import rick_attack_chain, rick_pivot_plan
from rick_mcp.tools.offensive_extended import rick_c2_compare, rick_cloud_attack_path, rick_payload_guide, rick_wireless
from rick_mcp.tools.offensive_tradecraft import rick_cheatsheet, rick_threat_model
from rick_mcp.tools.recon_handle import rick_recon_handle
from rick_mcp.tools.writeups import rick_writeups


def register_all(mcp):
    """Register all tools on the MCP server."""
    from rick_mcp.tools import (
        appraisal,
        career,
        code_review,
        cve,
        defensive,
        engagement,
        jarvis,
        jarvis_extended,
        meta,
        offensive,
        recon_handle,
        writeups,
    )

    offensive.register(mcp)
    defensive.register(mcp)
    engagement.register(mcp)
    career.register(mcp)
    code_review.register(mcp)
    appraisal.register(mcp)
    meta.register(mcp)
    cve.register(mcp)
    jarvis.register(mcp)
    jarvis_extended.register(mcp)
    recon_handle.register(mcp)
    writeups.register(mcp)


__all__ = [
    "rick_attack_chain",
    "rick_checklist",
    "rick_compare",
    "rick_export",
    "rick_full_auto",
    "rick_kill_chain",
    "rick_next_move",
    "rick_notes",
    "rick_rollback",
    "rick_scope_check",
    "rick_sitrep",
    "rick_tag",
    "rick_timeline",
    "rick_c2_compare",
    "rick_cheatsheet",
    "rick_client_onboarding",
    "rick_cloud_attack_path",
    "rick_code_review",
    "rick_cognitive_appraisal",
    "rick_compatibility_check",
    "rick_detection_rules",
    "rick_cover_letter",
    "rick_cve",
    "rick_capabilities",
    "rick_debrief",
    "rick_demo",
    "rick_engagement_proposal",
    "rick_hardening",
    "rick_health",
    "rick_incident_response",
    "rick_log_analysis",
    "rick_mantra",
    "rick_mentorship",
    "rick_mode",
    "rick_payload_guide",
    "rick_pivot_plan",
    "rick_recon",
    "rick_recon_handle",
    "rick_report_template",
    "rick_roe",
    "rick_scoping",
    "rick_status",
    "rick_threat_model",
    "rick_tool_recommend",
    "rick_tracker",
    "rick_vuln_assess",
    "rick_wireless",
    "rick_writeups",
    "register_all",
]
