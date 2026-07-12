"""Tests for meta tools — focused on rick_capabilities (the canonical capability map).

rick_capabilities (meta.py) was previously uncovered. These tests pin the map to the live
registry (tool/resource counts) and assert every capability category is present, so the
"what Rick does" surface can't silently drift from what's actually registered. Markdown is
the only format this tool emits, so assertions target verbatim description text (stable
across _fmt formatting) rather than title-cased keys.
"""

from rick_mcp import rick_capabilities
from rick_mcp.server import resource_count, tool_count

# Verbatim category description fragments (one per top-level category in the caps map).
_CATEGORY_MARKERS = [
    "Know your target before you touch it",  # offensive_recon_and_assessment
    "Exploitation, escalation, lateral movement",  # offensive_attack_methodology
    "build it right after breaking it",  # defensive_and_detection
    "honest builder's-eye verdict",  # code_review
    "Defense-first cognitive-appraisal scaffold",  # cognitive_appraisal
    "from scoping to debrief",  # engagement_lifecycle
    "Growing the craft",  # career_and_mentorship
    "Live intelligence from external sources",  # research
    "the intelligence layer",  # jarvis_tools
    "browse, read, and search",  # writeups
    "Rick talking about Rick",  # meta
    "identity resources",  # resources
    "Obsidian Second Brain bridge",  # vault_integration
]


class TestRickCapabilities:
    async def test_returns_content(self):
        out = await rick_capabilities()
        assert isinstance(out, str)
        assert len(out) > 50
        assert "encountered an issue:" not in out  # no swallowed _safe_tool error

    async def test_reflects_live_counts(self):
        # who_is_rick cites the live tool/resource counts — proves the map can't desync
        # from the registry without this failing.
        out = await rick_capabilities()
        assert str(tool_count()) in out
        assert str(resource_count()) in out

    async def test_lists_every_category(self):
        out = await rick_capabilities()
        missing = [m for m in _CATEGORY_MARKERS if m not in out]
        assert not missing, f"capability map missing categories: {missing}"

    def test_resource_count_includes_templates(self):
        # Regression: resource_count() must count parameterized resource templates
        # (e.g. vault://engagements/{codename}), not just static resources — otherwise
        # rick_status/rick_capabilities under-report and drift from README/refresh_counts.
        from rick_mcp.server import mcp

        rm = mcp._resource_manager
        assert resource_count() == len(rm.list_resources()) + len(rm.list_templates())
        assert resource_count() > len(rm.list_resources())  # at least one template is counted

    async def test_closing_note_present(self):
        out = await rick_capabilities()
        assert "Don't just read the menu" in out
