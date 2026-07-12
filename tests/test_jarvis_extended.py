"""Tests for JARVIS extended tools — notes, timeline, compare, scope_check, export, checklist, tag, rollback."""

import json
from unittest.mock import patch

import pytest

_PATCH_TARGET = "rick_mcp.tools.jarvis_state._STATE_DIR"


def _create_engagement(tmp_path, eng_id="test-eng", target="test.com", target_type="web_app", phase=None):
    """Helper to create an engagement with optional active phase."""
    from rick_mcp.tools.jarvis_state import KILL_CHAIN_PHASES, _save_state

    kc = [dict(p) for p in KILL_CHAIN_PHASES]
    if phase:
        kc[phase - 1]["status"] = "active"
    state = {
        "id": eng_id,
        "target": target,
        "target_type": target_type,
        "created": "2026-03-26T12:00:00+00:00",
        "kill_chain": kc,
        "mission_log": [],
        "tool_history": [],
        "notes": [],
    }
    with patch(_PATCH_TARGET, tmp_path):
        _save_state(eng_id, state)
    return state


# ═══════════════════════════════════════════════════════════════
# rick_notes
# ═══════════════════════════════════════════════════════════════


class TestRickNotes:
    @pytest.mark.asyncio
    async def test_add_note(self, tmp_path):
        from rick_mcp.models import NotesInput
        from rick_mcp.tools.jarvis_extended import rick_notes

        _create_engagement(tmp_path)
        with patch(_PATCH_TARGET, tmp_path):
            result = await rick_notes(NotesInput(engagement_id="test-eng", action="add", content="Found default creds"))
        assert "NOTE ADDED" in result
        assert "Found default creds" in result

    @pytest.mark.asyncio
    async def test_add_note_with_image(self, tmp_path):
        from rick_mcp.models import NotesInput
        from rick_mcp.tools.jarvis_extended import rick_notes

        _create_engagement(tmp_path)
        img = tmp_path / "screenshot.png"
        img.write_bytes(b"fake png")
        with patch(_PATCH_TARGET, tmp_path):
            result = await rick_notes(
                NotesInput(engagement_id="test-eng", action="add", content="Evidence", image_path=str(img))
            )
        assert "NOTE ADDED" in result

    @pytest.mark.asyncio
    async def test_add_note_bad_image(self, tmp_path):
        from rick_mcp.models import NotesInput
        from rick_mcp.tools.jarvis_extended import rick_notes

        _create_engagement(tmp_path)
        with patch(_PATCH_TARGET, tmp_path):
            result = await rick_notes(
                NotesInput(engagement_id="test-eng", action="add", content="test", image_path="/bad/path.png")
            )
        assert "Error" in result

    @pytest.mark.asyncio
    async def test_add_note_missing_content(self, tmp_path):
        from rick_mcp.models import NotesInput
        from rick_mcp.tools.jarvis_extended import rick_notes

        _create_engagement(tmp_path)
        with patch(_PATCH_TARGET, tmp_path):
            result = await rick_notes(NotesInput(engagement_id="test-eng", action="add"))
        assert "Error" in result

    @pytest.mark.asyncio
    async def test_list_notes(self, tmp_path):
        from rick_mcp.models import NotesInput
        from rick_mcp.tools.jarvis_extended import rick_notes

        _create_engagement(tmp_path)
        with patch(_PATCH_TARGET, tmp_path):
            await rick_notes(NotesInput(engagement_id="test-eng", action="add", content="Note 1"))
            await rick_notes(NotesInput(engagement_id="test-eng", action="add", content="Note 2"))
            result = await rick_notes(NotesInput(engagement_id="test-eng", action="list"))
        assert "Note 1" in result
        assert "Note 2" in result
        assert "2" in result

    @pytest.mark.asyncio
    async def test_list_empty(self, tmp_path):
        from rick_mcp.models import NotesInput
        from rick_mcp.tools.jarvis_extended import rick_notes

        _create_engagement(tmp_path)
        with patch(_PATCH_TARGET, tmp_path):
            result = await rick_notes(NotesInput(engagement_id="test-eng", action="list"))
        assert "No notes" in result

    @pytest.mark.asyncio
    async def test_search_notes(self, tmp_path):
        from rick_mcp.models import NotesInput
        from rick_mcp.tools.jarvis_extended import rick_notes

        _create_engagement(tmp_path)
        with patch(_PATCH_TARGET, tmp_path):
            await rick_notes(NotesInput(engagement_id="test-eng", action="add", content="CrowdStrike detected"))
            await rick_notes(NotesInput(engagement_id="test-eng", action="add", content="Port 443 open"))
            result = await rick_notes(NotesInput(engagement_id="test-eng", action="search", search_term="crowd"))
        assert "CrowdStrike" in result
        assert "1" in result  # 1 match

    @pytest.mark.asyncio
    async def test_search_no_term(self, tmp_path):
        from rick_mcp.models import NotesInput
        from rick_mcp.tools.jarvis_extended import rick_notes

        _create_engagement(tmp_path)
        with patch(_PATCH_TARGET, tmp_path):
            result = await rick_notes(NotesInput(engagement_id="test-eng", action="search"))
        assert "Error" in result

    @pytest.mark.asyncio
    async def test_delete_note(self, tmp_path):
        from rick_mcp.models import NotesInput
        from rick_mcp.tools.jarvis_extended import rick_notes

        _create_engagement(tmp_path)
        with patch(_PATCH_TARGET, tmp_path):
            await rick_notes(NotesInput(engagement_id="test-eng", action="add", content="To delete"))
            result = await rick_notes(NotesInput(engagement_id="test-eng", action="delete", note_index=0))
        assert "DELETED" in result

    @pytest.mark.asyncio
    async def test_delete_out_of_range(self, tmp_path):
        from rick_mcp.models import NotesInput
        from rick_mcp.tools.jarvis_extended import rick_notes

        _create_engagement(tmp_path)
        with patch(_PATCH_TARGET, tmp_path):
            result = await rick_notes(NotesInput(engagement_id="test-eng", action="delete", note_index=99))
        assert "Error" in result

    @pytest.mark.asyncio
    async def test_no_engagement(self, tmp_path):
        from rick_mcp.models import NotesInput
        from rick_mcp.tools.jarvis_extended import rick_notes

        with patch(_PATCH_TARGET, tmp_path):
            result = await rick_notes(NotesInput(engagement_id="ghost", action="list"))
        assert "No engagement" in result

    @pytest.mark.asyncio
    async def test_invalid_action(self, tmp_path):
        from rick_mcp.models import NotesInput
        from rick_mcp.tools.jarvis_extended import rick_notes

        _create_engagement(tmp_path)
        with patch(_PATCH_TARGET, tmp_path):
            result = await rick_notes(NotesInput(engagement_id="test-eng", action="explode"))
        assert "Error" in result

    @pytest.mark.asyncio
    async def test_backward_compat_string_notes(self, tmp_path):
        """Legacy string notes should display correctly."""
        from rick_mcp.models import NotesInput
        from rick_mcp.tools.jarvis_extended import rick_notes
        from rick_mcp.tools.jarvis_state import _load_state, _save_state

        _create_engagement(tmp_path)
        with patch(_PATCH_TARGET, tmp_path):
            state = _load_state("test-eng")
            state["notes"] = ["old string note"]
            _save_state("test-eng", state)
            result = await rick_notes(NotesInput(engagement_id="test-eng", action="list"))
        assert "old string note" in result


# ═══════════════════════════════════════════════════════════════
# rick_timeline
# ═══════════════════════════════════════════════════════════════


class TestRickTimeline:
    @pytest.mark.asyncio
    async def test_timeline_basic(self, tmp_path):
        from rick_mcp.models import TimelineInput
        from rick_mcp.tools.jarvis_extended import rick_timeline
        from rick_mcp.tools.jarvis_state import _load_state, _save_state

        _create_engagement(tmp_path, phase=1)
        with patch(_PATCH_TARGET, tmp_path):
            state = _load_state("test-eng")
            state["kill_chain"][0]["findings"] = [{"description": "Port 80", "timestamp": "2026-03-26T13:00:00Z"}]
            state["mission_log"] = [{"timestamp": "2026-03-26T12:00:00Z", "entry": "Started"}]
            state["tool_history"] = [{"tool": "rick_recon", "timestamp": "2026-03-26T12:30:00Z", "summary": "Recon"}]
            _save_state("test-eng", state)
            result = await rick_timeline(TimelineInput(engagement_id="test-eng"))
        assert "FINDING" in result
        assert "LOG" in result
        assert "TOOL" in result

    @pytest.mark.asyncio
    async def test_timeline_filter_type(self, tmp_path):
        from rick_mcp.models import TimelineInput
        from rick_mcp.tools.jarvis_extended import rick_timeline
        from rick_mcp.tools.jarvis_state import _load_state, _save_state

        _create_engagement(tmp_path, phase=1)
        with patch(_PATCH_TARGET, tmp_path):
            state = _load_state("test-eng")
            state["kill_chain"][0]["findings"] = [{"description": "Port 80", "timestamp": "2026-03-26T13:00:00Z"}]
            state["mission_log"] = [{"timestamp": "2026-03-26T12:00:00Z", "entry": "Started"}]
            _save_state("test-eng", state)
            result = await rick_timeline(TimelineInput(engagement_id="test-eng", filter_type="finding"))
        assert "FINDING" in result
        assert "LOG" not in result

    @pytest.mark.asyncio
    async def test_timeline_filter_phase(self, tmp_path):
        from rick_mcp.models import TimelineInput
        from rick_mcp.tools.jarvis_extended import rick_timeline
        from rick_mcp.tools.jarvis_state import _load_state, _save_state

        _create_engagement(tmp_path, phase=1)
        with patch(_PATCH_TARGET, tmp_path):
            state = _load_state("test-eng")
            state["kill_chain"][0]["findings"] = [{"description": "P1 finding", "timestamp": "2026-03-26T13:00:00Z"}]
            state["kill_chain"][1]["findings"] = [{"description": "P2 finding", "timestamp": "2026-03-26T14:00:00Z"}]
            _save_state("test-eng", state)
            result = await rick_timeline(TimelineInput(engagement_id="test-eng", filter_phase=1))
        assert "P1 finding" in result
        assert "P2 finding" not in result

    @pytest.mark.asyncio
    async def test_timeline_no_engagement(self, tmp_path):
        from rick_mcp.models import TimelineInput
        from rick_mcp.tools.jarvis_extended import rick_timeline

        with patch(_PATCH_TARGET, tmp_path):
            result = await rick_timeline(TimelineInput(engagement_id="ghost"))
        assert "No engagement" in result

    @pytest.mark.asyncio
    async def test_timeline_empty(self, tmp_path):
        from rick_mcp.models import TimelineInput
        from rick_mcp.tools.jarvis_extended import rick_timeline

        _create_engagement(tmp_path)
        with patch(_PATCH_TARGET, tmp_path):
            result = await rick_timeline(TimelineInput(engagement_id="test-eng"))
        assert "No events" in result


# ═══════════════════════════════════════════════════════════════
# rick_compare
# ═══════════════════════════════════════════════════════════════


class TestRickCompare:
    @pytest.mark.asyncio
    async def test_compare_basic(self, tmp_path):
        from rick_mcp.models import CompareInput
        from rick_mcp.tools.jarvis_extended import rick_compare

        _create_engagement(tmp_path, eng_id="eng-a", target="v1.example.com")
        _create_engagement(tmp_path, eng_id="eng-b", target="v2.example.com")
        with patch(_PATCH_TARGET, tmp_path):
            result = await rick_compare(CompareInput(engagement_id_a="eng-a", engagement_id_b="eng-b"))
        assert "eng-a" in result
        assert "eng-b" in result
        assert "v1.example.com" in result
        assert "v2.example.com" in result

    @pytest.mark.asyncio
    async def test_compare_missing(self, tmp_path):
        from rick_mcp.models import CompareInput
        from rick_mcp.tools.jarvis_extended import rick_compare

        with patch(_PATCH_TARGET, tmp_path):
            result = await rick_compare(CompareInput(engagement_id_a="ghost-a", engagement_id_b="ghost-b"))
        assert "not found" in result.lower()

    @pytest.mark.asyncio
    async def test_compare_identical(self, tmp_path):
        from rick_mcp.models import CompareInput
        from rick_mcp.tools.jarvis_extended import rick_compare

        _create_engagement(tmp_path, eng_id="same-a")
        _create_engagement(tmp_path, eng_id="same-b")
        with patch(_PATCH_TARGET, tmp_path):
            result = await rick_compare(CompareInput(engagement_id_a="same-a", engagement_id_b="same-b"))
        assert "No differences" in result or "differences" in result.lower()


# ═══════════════════════════════════════════════════════════════
# rick_scope_check
# ═══════════════════════════════════════════════════════════════


class TestRickScopeCheck:
    @pytest.mark.asyncio
    async def test_add_scope(self, tmp_path):
        from rick_mcp.models import ScopeCheckInput
        from rick_mcp.tools.jarvis_extended import rick_scope_check

        _create_engagement(tmp_path)
        with patch(_PATCH_TARGET, tmp_path):
            result = await rick_scope_check(
                ScopeCheckInput(engagement_id="test-eng", add_scope="10.0.0.0/24, *.example.com")
            )
        assert "test-eng" in result

    @pytest.mark.asyncio
    async def test_check_in_scope(self, tmp_path):
        from rick_mcp.models import ScopeCheckInput
        from rick_mcp.tools.jarvis_extended import rick_scope_check
        from rick_mcp.tools.jarvis_state import _load_state, _save_state

        _create_engagement(tmp_path)
        with patch(_PATCH_TARGET, tmp_path):
            state = _load_state("test-eng")
            state["scope"] = ["10.0.0.0/24", "*.example.com"]
            _save_state("test-eng", state)
            result = await rick_scope_check(ScopeCheckInput(engagement_id="test-eng", target="app.example.com"))
        assert "IN SCOPE" in result

    @pytest.mark.asyncio
    async def test_check_out_of_scope(self, tmp_path):
        from rick_mcp.models import ScopeCheckInput
        from rick_mcp.tools.jarvis_extended import rick_scope_check
        from rick_mcp.tools.jarvis_state import _load_state, _save_state

        _create_engagement(tmp_path)
        with patch(_PATCH_TARGET, tmp_path):
            state = _load_state("test-eng")
            state["scope"] = ["10.0.0.0/24"]
            _save_state("test-eng", state)
            result = await rick_scope_check(ScopeCheckInput(engagement_id="test-eng", target="evil.attacker.com"))
        assert "OUT OF SCOPE" in result

    @pytest.mark.asyncio
    async def test_check_ip_in_cidr(self, tmp_path):
        # Regression (#61): an IP inside an authorized CIDR must be IN SCOPE.
        from rick_mcp.models import ScopeCheckInput
        from rick_mcp.tools.jarvis_extended import rick_scope_check
        from rick_mcp.tools.jarvis_state import _load_state, _save_state

        _create_engagement(tmp_path)
        with patch(_PATCH_TARGET, tmp_path):
            state = _load_state("test-eng")
            state["scope"] = ["10.10.10.0/24"]
            _save_state("test-eng", state)
            result = await rick_scope_check(ScopeCheckInput(engagement_id="test-eng", target="10.10.10.99"))
        assert "IN SCOPE" in result

    @pytest.mark.asyncio
    async def test_check_ip_outside_cidr(self, tmp_path):
        from rick_mcp.models import ScopeCheckInput
        from rick_mcp.tools.jarvis_extended import rick_scope_check
        from rick_mcp.tools.jarvis_state import _load_state, _save_state

        _create_engagement(tmp_path)
        with patch(_PATCH_TARGET, tmp_path):
            state = _load_state("test-eng")
            state["scope"] = ["10.10.10.0/24"]
            _save_state("test-eng", state)
            result = await rick_scope_check(ScopeCheckInput(engagement_id="test-eng", target="8.8.8.8"))
        assert "OUT OF SCOPE" in result

    @pytest.mark.asyncio
    async def test_check_single_ip_scope(self, tmp_path):
        # A bare IP scope item is treated as a /32 — exact host match, no substring bleed.
        from rick_mcp.models import ScopeCheckInput
        from rick_mcp.tools.jarvis_extended import rick_scope_check
        from rick_mcp.tools.jarvis_state import _load_state, _save_state

        _create_engagement(tmp_path)
        with patch(_PATCH_TARGET, tmp_path):
            state = _load_state("test-eng")
            state["scope"] = ["10.10.10.99"]
            _save_state("test-eng", state)
            hit = await rick_scope_check(ScopeCheckInput(engagement_id="test-eng", target="10.10.10.99"))
            miss = await rick_scope_check(ScopeCheckInput(engagement_id="test-eng", target="10.10.10.9"))
        assert "IN SCOPE" in hit
        assert "OUT OF SCOPE" in miss

    @pytest.mark.asyncio
    async def test_check_no_scope(self, tmp_path):
        from rick_mcp.models import ScopeCheckInput
        from rick_mcp.tools.jarvis_extended import rick_scope_check

        _create_engagement(tmp_path)
        with patch(_PATCH_TARGET, tmp_path):
            result = await rick_scope_check(ScopeCheckInput(engagement_id="test-eng", target="anything"))
        assert "UNKNOWN" in result

    @pytest.mark.asyncio
    async def test_set_roe(self, tmp_path):
        from rick_mcp.models import ScopeCheckInput
        from rick_mcp.tools.jarvis_extended import rick_scope_check

        _create_engagement(tmp_path)
        with patch(_PATCH_TARGET, tmp_path):
            await rick_scope_check(ScopeCheckInput(engagement_id="test-eng", set_roe="No social engineering"))
            result = await rick_scope_check(ScopeCheckInput(engagement_id="test-eng", action="phishing"))
        assert "REVIEW ROE" in result
        assert "No social engineering" in result

    @pytest.mark.asyncio
    async def test_view_scope(self, tmp_path):
        from rick_mcp.models import ScopeCheckInput
        from rick_mcp.tools.jarvis_extended import rick_scope_check

        _create_engagement(tmp_path)
        with patch(_PATCH_TARGET, tmp_path):
            result = await rick_scope_check(ScopeCheckInput(engagement_id="test-eng"))
        assert "No scope defined" in result or "scope" in result.lower()

    @pytest.mark.asyncio
    async def test_no_engagement(self, tmp_path):
        from rick_mcp.models import ScopeCheckInput
        from rick_mcp.tools.jarvis_extended import rick_scope_check

        with patch(_PATCH_TARGET, tmp_path):
            result = await rick_scope_check(ScopeCheckInput(engagement_id="ghost"))
        assert "No engagement" in result


# ═══════════════════════════════════════════════════════════════
# rick_export
# ═══════════════════════════════════════════════════════════════


class TestRickExport:
    @pytest.mark.asyncio
    async def test_export_markdown(self, tmp_path):
        from rick_mcp.models import ExportInput
        from rick_mcp.tools.jarvis_extended import rick_export

        _create_engagement(tmp_path, phase=1)
        with patch(_PATCH_TARGET, tmp_path):
            result = await rick_export(ExportInput(engagement_id="test-eng", export_format="markdown"))
        assert "# Engagement Report" in result
        assert "test.com" in result

    @pytest.mark.asyncio
    async def test_export_json(self, tmp_path):
        from rick_mcp.models import ExportInput
        from rick_mcp.tools.jarvis_extended import rick_export

        _create_engagement(tmp_path)
        with patch(_PATCH_TARGET, tmp_path):
            result = await rick_export(ExportInput(engagement_id="test-eng", export_format="json"))
        data = json.loads(result)
        assert data["id"] == "test-eng"

    @pytest.mark.asyncio
    async def test_export_csv(self, tmp_path):
        from rick_mcp.models import ExportInput
        from rick_mcp.tools.jarvis_extended import rick_export
        from rick_mcp.tools.jarvis_state import _load_state, _save_state

        _create_engagement(tmp_path, phase=1)
        with patch(_PATCH_TARGET, tmp_path):
            state = _load_state("test-eng")
            state["kill_chain"][0]["findings"] = [{"description": "Port 80", "timestamp": "2026-03-26T13:00:00Z"}]
            _save_state("test-eng", state)
            result = await rick_export(ExportInput(engagement_id="test-eng", export_format="csv"))
        assert "phase" in result
        assert "Port 80" in result

    @pytest.mark.asyncio
    async def test_export_no_engagement(self, tmp_path):
        from rick_mcp.models import ExportInput
        from rick_mcp.tools.jarvis_extended import rick_export

        with patch(_PATCH_TARGET, tmp_path):
            result = await rick_export(ExportInput(engagement_id="ghost"))
        assert "No engagement" in result


# ═══════════════════════════════════════════════════════════════
# rick_checklist
# ═══════════════════════════════════════════════════════════════


class TestRickChecklist:
    @pytest.mark.asyncio
    async def test_generate_checklist(self, tmp_path):
        from rick_mcp.models import ChecklistInput
        from rick_mcp.tools.jarvis_extended import rick_checklist

        _create_engagement(tmp_path, phase=1)
        with patch(_PATCH_TARGET, tmp_path):
            result = await rick_checklist(ChecklistInput(engagement_id="test-eng", action="generate"))
        assert "GENERATED" in result

    @pytest.mark.asyncio
    async def test_generate_specific_phase(self, tmp_path):
        from rick_mcp.models import ChecklistInput
        from rick_mcp.tools.jarvis_extended import rick_checklist

        _create_engagement(tmp_path)
        with patch(_PATCH_TARGET, tmp_path):
            result = await rick_checklist(ChecklistInput(engagement_id="test-eng", action="generate", phase=4))
        assert "GENERATED" in result

    @pytest.mark.asyncio
    async def test_generate_no_phase(self, tmp_path):
        from rick_mcp.models import ChecklistInput
        from rick_mcp.tools.jarvis_extended import rick_checklist

        _create_engagement(tmp_path)  # No active phase
        with patch(_PATCH_TARGET, tmp_path):
            result = await rick_checklist(ChecklistInput(engagement_id="test-eng", action="generate"))
        assert "Error" in result

    @pytest.mark.asyncio
    async def test_check_item(self, tmp_path):
        from rick_mcp.models import ChecklistInput
        from rick_mcp.tools.jarvis_extended import rick_checklist

        _create_engagement(tmp_path, phase=1)
        with patch(_PATCH_TARGET, tmp_path):
            await rick_checklist(ChecklistInput(engagement_id="test-eng", action="generate"))
            result = await rick_checklist(ChecklistInput(engagement_id="test-eng", action="check", item_index=0))
        assert "CHECK" in result

    @pytest.mark.asyncio
    async def test_uncheck_item(self, tmp_path):
        from rick_mcp.models import ChecklistInput
        from rick_mcp.tools.jarvis_extended import rick_checklist

        _create_engagement(tmp_path, phase=1)
        with patch(_PATCH_TARGET, tmp_path):
            await rick_checklist(ChecklistInput(engagement_id="test-eng", action="generate"))
            await rick_checklist(ChecklistInput(engagement_id="test-eng", action="check", item_index=0))
            result = await rick_checklist(ChecklistInput(engagement_id="test-eng", action="uncheck", item_index=0))
        assert "UNCHECK" in result

    @pytest.mark.asyncio
    async def test_check_out_of_range(self, tmp_path):
        from rick_mcp.models import ChecklistInput
        from rick_mcp.tools.jarvis_extended import rick_checklist

        _create_engagement(tmp_path)
        with patch(_PATCH_TARGET, tmp_path):
            result = await rick_checklist(ChecklistInput(engagement_id="test-eng", action="check", item_index=99))
        assert "Error" in result

    @pytest.mark.asyncio
    async def test_status(self, tmp_path):
        from rick_mcp.models import ChecklistInput
        from rick_mcp.tools.jarvis_extended import rick_checklist

        _create_engagement(tmp_path, phase=1)
        with patch(_PATCH_TARGET, tmp_path):
            await rick_checklist(ChecklistInput(engagement_id="test-eng", action="generate"))
            result = await rick_checklist(ChecklistInput(engagement_id="test-eng", action="status"))
        assert "0/" in result  # 0 checked out of N

    @pytest.mark.asyncio
    async def test_status_empty(self, tmp_path):
        from rick_mcp.models import ChecklistInput
        from rick_mcp.tools.jarvis_extended import rick_checklist

        _create_engagement(tmp_path)
        with patch(_PATCH_TARGET, tmp_path):
            result = await rick_checklist(ChecklistInput(engagement_id="test-eng", action="status"))
        assert "No checklist" in result

    @pytest.mark.asyncio
    async def test_invalid_action(self, tmp_path):
        from rick_mcp.models import ChecklistInput
        from rick_mcp.tools.jarvis_extended import rick_checklist

        _create_engagement(tmp_path)
        with patch(_PATCH_TARGET, tmp_path):
            result = await rick_checklist(ChecklistInput(engagement_id="test-eng", action="explode"))
        assert "Error" in result


# ═══════════════════════════════════════════════════════════════
# rick_tag
# ═══════════════════════════════════════════════════════════════


class TestRickTag:
    @pytest.mark.asyncio
    async def test_tag_severity(self, tmp_path):
        from rick_mcp.models import TagInput
        from rick_mcp.tools.jarvis_extended import rick_tag
        from rick_mcp.tools.jarvis_state import _load_state, _save_state

        _create_engagement(tmp_path, phase=1)
        with patch(_PATCH_TARGET, tmp_path):
            state = _load_state("test-eng")
            state["kill_chain"][0]["findings"] = [{"description": "SQLi", "timestamp": "2026-03-26T13:00:00Z"}]
            _save_state("test-eng", state)
            result = await rick_tag(TagInput(engagement_id="test-eng", phase=1, finding_index=0, severity="critical"))
        assert "TAGGED" in result
        assert "critical" in result

    @pytest.mark.asyncio
    async def test_tag_mitre(self, tmp_path):
        from rick_mcp.models import TagInput
        from rick_mcp.tools.jarvis_extended import rick_tag
        from rick_mcp.tools.jarvis_state import _load_state, _save_state

        _create_engagement(tmp_path, phase=1)
        with patch(_PATCH_TARGET, tmp_path):
            state = _load_state("test-eng")
            state["kill_chain"][0]["findings"] = [{"description": "SQLi", "timestamp": "2026-03-26T13:00:00Z"}]
            _save_state("test-eng", state)
            result = await rick_tag(TagInput(engagement_id="test-eng", phase=1, finding_index=0, mitre_id="T1059.001"))
        assert "TAGGED" in result
        assert "T1059.001" in result

    @pytest.mark.asyncio
    async def test_tag_bad_severity(self, tmp_path):
        from rick_mcp.models import TagInput
        from rick_mcp.tools.jarvis_extended import rick_tag
        from rick_mcp.tools.jarvis_state import _load_state, _save_state

        _create_engagement(tmp_path, phase=1)
        with patch(_PATCH_TARGET, tmp_path):
            state = _load_state("test-eng")
            state["kill_chain"][0]["findings"] = [{"description": "test", "timestamp": "2026-03-26T13:00:00Z"}]
            _save_state("test-eng", state)
            result = await rick_tag(TagInput(engagement_id="test-eng", phase=1, finding_index=0, severity="banana"))
        assert "Error" in result

    @pytest.mark.asyncio
    async def test_tag_bad_mitre(self, tmp_path):
        from rick_mcp.models import TagInput
        from rick_mcp.tools.jarvis_extended import rick_tag
        from rick_mcp.tools.jarvis_state import _load_state, _save_state

        _create_engagement(tmp_path, phase=1)
        with patch(_PATCH_TARGET, tmp_path):
            state = _load_state("test-eng")
            state["kill_chain"][0]["findings"] = [{"description": "test", "timestamp": "2026-03-26T13:00:00Z"}]
            _save_state("test-eng", state)
            result = await rick_tag(TagInput(engagement_id="test-eng", phase=1, finding_index=0, mitre_id="TXYZ"))
        assert "Error" in result

    @pytest.mark.asyncio
    async def test_tag_no_tags(self, tmp_path):
        from rick_mcp.models import TagInput
        from rick_mcp.tools.jarvis_extended import rick_tag
        from rick_mcp.tools.jarvis_state import _load_state, _save_state

        _create_engagement(tmp_path, phase=1)
        with patch(_PATCH_TARGET, tmp_path):
            state = _load_state("test-eng")
            state["kill_chain"][0]["findings"] = [{"description": "test", "timestamp": "2026-03-26T13:00:00Z"}]
            _save_state("test-eng", state)
            result = await rick_tag(TagInput(engagement_id="test-eng", phase=1, finding_index=0))
        assert "Error" in result

    @pytest.mark.asyncio
    async def test_tag_out_of_range(self, tmp_path):
        from rick_mcp.models import TagInput
        from rick_mcp.tools.jarvis_extended import rick_tag

        _create_engagement(tmp_path, phase=1)
        with patch(_PATCH_TARGET, tmp_path):
            result = await rick_tag(TagInput(engagement_id="test-eng", phase=1, finding_index=99, severity="high"))
        assert "Error" in result

    @pytest.mark.asyncio
    async def test_tag_no_engagement(self, tmp_path):
        from rick_mcp.models import TagInput
        from rick_mcp.tools.jarvis_extended import rick_tag

        with patch(_PATCH_TARGET, tmp_path):
            result = await rick_tag(TagInput(engagement_id="ghost", phase=1, finding_index=0, severity="high"))
        assert "No engagement" in result

    @pytest.mark.asyncio
    async def test_tag_category(self, tmp_path):
        from rick_mcp.models import TagInput
        from rick_mcp.tools.jarvis_extended import rick_tag
        from rick_mcp.tools.jarvis_state import _load_state, _save_state

        _create_engagement(tmp_path, phase=1)
        with patch(_PATCH_TARGET, tmp_path):
            state = _load_state("test-eng")
            state["kill_chain"][0]["findings"] = [{"description": "XSS", "timestamp": "2026-03-26T13:00:00Z"}]
            _save_state("test-eng", state)
            result = await rick_tag(TagInput(engagement_id="test-eng", phase=1, finding_index=0, category="injection"))
        assert "TAGGED" in result
        assert "injection" in result


# ═══════════════════════════════════════════════════════════════
# rick_rollback
# ═══════════════════════════════════════════════════════════════


class TestRickRollback:
    @pytest.mark.asyncio
    async def test_rollback_preview(self, tmp_path):
        from rick_mcp.models import RollbackInput
        from rick_mcp.tools.jarvis_extended import rick_rollback
        from rick_mcp.tools.jarvis_state import _load_state, _save_state

        _create_engagement(tmp_path)
        with patch(_PATCH_TARGET, tmp_path):
            state = _load_state("test-eng")
            _save_state(
                "test-eng", {"id": "test-eng", "target": "v2", "kill_chain": state["kill_chain"]}, snapshot=True
            )
            result = await rick_rollback(RollbackInput(engagement_id="test-eng"))
        assert "confirm" in result.lower()

    @pytest.mark.asyncio
    async def test_rollback_execute(self, tmp_path):
        from rick_mcp.models import RollbackInput
        from rick_mcp.tools.jarvis_extended import rick_rollback
        from rick_mcp.tools.jarvis_state import _load_state, _save_state

        _create_engagement(tmp_path)
        with patch(_PATCH_TARGET, tmp_path):
            state = _load_state("test-eng")
            _save_state(
                "test-eng", {"id": "test-eng", "target": "v2", "kill_chain": state["kill_chain"]}, snapshot=True
            )
            result = await rick_rollback(RollbackInput(engagement_id="test-eng", confirm=True))
            restored = _load_state("test-eng")
        assert "ROLLED BACK" in result
        assert restored["target"] == "test.com"

    @pytest.mark.asyncio
    async def test_rollback_no_snapshots(self, tmp_path):
        from rick_mcp.models import RollbackInput
        from rick_mcp.tools.jarvis_extended import rick_rollback

        _create_engagement(tmp_path)
        with patch(_PATCH_TARGET, tmp_path):
            result = await rick_rollback(RollbackInput(engagement_id="test-eng", confirm=True))
        assert "No snapshots" in result

    @pytest.mark.asyncio
    async def test_kill_chain_mutation_creates_snapshot(self, tmp_path):
        # Regression (#60): a REAL rick_kill_chain mutation must create a snapshot so rollback
        # works end-to-end — not only when a test hand-crafts one. Previously nothing ever
        # passed snapshot=True, so rollback always reported "No snapshots."
        from rick_mcp.models import KillChainInput, RollbackInput
        from rick_mcp.tools.jarvis import rick_kill_chain
        from rick_mcp.tools.jarvis_extended import rick_rollback
        from rick_mcp.tools.jarvis_state import _load_state

        def _findings(st):
            return sum(len(p.get("findings", [])) for p in st.get("kill_chain", []))

        _create_engagement(tmp_path)
        with patch(_PATCH_TARGET, tmp_path):
            await rick_kill_chain(
                KillChainInput(action="add_finding", engagement_id="test-eng", phase=1, finding="probe")
            )
            after_add = _load_state("test-eng")
            assert after_add.get("snapshots"), "add_finding must create a snapshot"
            assert _findings(after_add) == 1
            result = await rick_rollback(RollbackInput(engagement_id="test-eng", confirm=True))
            reverted = _load_state("test-eng")
        assert "ROLLED BACK" in result
        assert _findings(reverted) == 0

    @pytest.mark.asyncio
    async def test_rollback_no_engagement(self, tmp_path):
        from rick_mcp.models import RollbackInput
        from rick_mcp.tools.jarvis_extended import rick_rollback

        with patch(_PATCH_TARGET, tmp_path):
            result = await rick_rollback(RollbackInput(engagement_id="ghost"))
        assert "No engagement" in result
