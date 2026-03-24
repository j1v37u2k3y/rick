"""Tests for JARVIS tools — full_auto, kill_chain, next_move, sitrep."""

from unittest.mock import patch

import pytest
from pydantic import ValidationError


class TestRickFullAuto:
    @pytest.mark.asyncio
    async def test_full_auto_web_app(self):
        from rick_mcp.tools.jarvis import FullAutoInput, rick_full_auto

        result = await rick_full_auto(FullAutoInput(target="test.example.com", target_type="web_app"))
        assert "test.example.com" in result
        assert "RECONNAISSANCE" in result
        assert "VULNERABILITY" in result
        assert "ATTACK CHAIN" in result
        assert "ARSENAL" in result
        assert "POST-COMPROMISE" in result

    @pytest.mark.asyncio
    async def test_full_auto_with_engagement_id(self, tmp_path):
        from rick_mcp.tools.jarvis import FullAutoInput, rick_full_auto

        with patch("rick_mcp.tools.jarvis._STATE_DIR", tmp_path):
            result = await rick_full_auto(
                FullAutoInput(target="10.10.10.1", target_type="network", engagement_id="test-eng-1")
            )
        assert "test-eng-1" in result
        assert (tmp_path / "test-eng-1.json").exists()

    @pytest.mark.asyncio
    async def test_full_auto_ad(self):
        from rick_mcp.tools.jarvis import FullAutoInput, rick_full_auto

        result = await rick_full_auto(FullAutoInput(target="corp.local", target_type="active_directory"))
        assert "corp.local" in result

    @pytest.mark.asyncio
    async def test_full_auto_cloud(self):
        from rick_mcp.tools.jarvis import FullAutoInput, rick_full_auto

        result = await rick_full_auto(FullAutoInput(target="aws-prod", target_type="cloud_aws"))
        assert "aws-prod" in result

    def test_full_auto_input_validation(self):
        from rick_mcp.tools.jarvis import FullAutoInput

        with pytest.raises(ValidationError):
            FullAutoInput(target="", target_type="web_app")


class TestRickKillChain:
    @pytest.mark.asyncio
    async def test_status_creates_new(self, tmp_path):
        from rick_mcp.tools.jarvis import KillChainInput, rick_kill_chain

        with patch("rick_mcp.tools.jarvis._STATE_DIR", tmp_path):
            result = await rick_kill_chain(KillChainInput(action="status", engagement_id="new-eng"))
        assert "NEW" in result or "initialized" in result.lower()
        assert (tmp_path / "new-eng.json").exists()

    @pytest.mark.asyncio
    async def test_advance_phase(self, tmp_path):
        from rick_mcp.tools.jarvis import KillChainInput, rick_kill_chain

        with patch("rick_mcp.tools.jarvis._STATE_DIR", tmp_path):
            await rick_kill_chain(KillChainInput(action="status", engagement_id="adv-eng"))
            result = await rick_kill_chain(KillChainInput(action="advance", engagement_id="adv-eng", phase=1))
        assert "Phase 1" in result or "ACTIVATED" in result

    @pytest.mark.asyncio
    async def test_add_finding(self, tmp_path):
        from rick_mcp.tools.jarvis import KillChainInput, rick_kill_chain

        with patch("rick_mcp.tools.jarvis._STATE_DIR", tmp_path):
            await rick_kill_chain(KillChainInput(action="status", engagement_id="find-eng"))
            await rick_kill_chain(KillChainInput(action="advance", engagement_id="find-eng", phase=1))
            result = await rick_kill_chain(
                KillChainInput(action="add_finding", engagement_id="find-eng", finding="Open port 443")
            )
        assert "FINDING" in result
        assert "Open port 443" in result

    @pytest.mark.asyncio
    async def test_add_finding_no_active_phase(self, tmp_path):
        from rick_mcp.tools.jarvis import KillChainInput, rick_kill_chain

        with patch("rick_mcp.tools.jarvis._STATE_DIR", tmp_path):
            await rick_kill_chain(KillChainInput(action="status", engagement_id="nophase"))
            result = await rick_kill_chain(
                KillChainInput(action="add_finding", engagement_id="nophase", finding="test")
            )
        assert "Error" in result

    @pytest.mark.asyncio
    async def test_add_finding_missing_text(self, tmp_path):
        from rick_mcp.tools.jarvis import KillChainInput, rick_kill_chain

        with patch("rick_mcp.tools.jarvis._STATE_DIR", tmp_path):
            await rick_kill_chain(KillChainInput(action="status", engagement_id="nofind"))
            result = await rick_kill_chain(KillChainInput(action="add_finding", engagement_id="nofind", phase=1))
        assert "Error" in result

    @pytest.mark.asyncio
    async def test_reset(self, tmp_path):
        from rick_mcp.tools.jarvis import KillChainInput, rick_kill_chain

        with patch("rick_mcp.tools.jarvis._STATE_DIR", tmp_path):
            await rick_kill_chain(KillChainInput(action="status", engagement_id="reset-eng"))
            result = await rick_kill_chain(KillChainInput(action="reset", engagement_id="reset-eng"))
        assert "RESET" in result

    @pytest.mark.asyncio
    async def test_reset_nonexistent(self, tmp_path):
        from rick_mcp.tools.jarvis import KillChainInput, rick_kill_chain

        with patch("rick_mcp.tools.jarvis._STATE_DIR", tmp_path):
            result = await rick_kill_chain(KillChainInput(action="reset", engagement_id="ghost"))
        assert "No engagement" in result

    @pytest.mark.asyncio
    async def test_list_empty(self, tmp_path):
        from rick_mcp.tools.jarvis import KillChainInput, rick_kill_chain

        with patch("rick_mcp.tools.jarvis._STATE_DIR", tmp_path):
            result = await rick_kill_chain(KillChainInput(action="list", engagement_id="ignored"))
        assert "No active" in result

    @pytest.mark.asyncio
    async def test_list_with_engagements(self, tmp_path):
        from rick_mcp.tools.jarvis import KillChainInput, rick_kill_chain

        with patch("rick_mcp.tools.jarvis._STATE_DIR", tmp_path):
            await rick_kill_chain(KillChainInput(action="status", engagement_id="eng-a"))
            await rick_kill_chain(KillChainInput(action="status", engagement_id="eng-b"))
            result = await rick_kill_chain(KillChainInput(action="list", engagement_id="ignored"))
        assert "eng-a" in result
        assert "eng-b" in result

    @pytest.mark.asyncio
    async def test_invalid_action(self, tmp_path):
        from rick_mcp.tools.jarvis import KillChainInput, rick_kill_chain

        with patch("rick_mcp.tools.jarvis._STATE_DIR", tmp_path):
            result = await rick_kill_chain(KillChainInput(action="explode", engagement_id="test"))
        assert "Error" in result

    @pytest.mark.asyncio
    async def test_advance_no_engagement(self, tmp_path):
        from rick_mcp.tools.jarvis import KillChainInput, rick_kill_chain

        with patch("rick_mcp.tools.jarvis._STATE_DIR", tmp_path):
            result = await rick_kill_chain(KillChainInput(action="advance", engagement_id="ghost"))
        assert "Error" in result

    @pytest.mark.asyncio
    async def test_auto_advance(self, tmp_path):
        from rick_mcp.tools.jarvis import KillChainInput, rick_kill_chain

        with patch("rick_mcp.tools.jarvis._STATE_DIR", tmp_path):
            await rick_kill_chain(KillChainInput(action="status", engagement_id="auto-adv"))
            await rick_kill_chain(KillChainInput(action="advance", engagement_id="auto-adv", phase=1))
            result = await rick_kill_chain(KillChainInput(action="advance", engagement_id="auto-adv"))
        assert "ADVANCED" in result or "Phase 2" in result

    @pytest.mark.asyncio
    async def test_advance_no_active_phase(self, tmp_path):
        from rick_mcp.tools.jarvis import KillChainInput, rick_kill_chain

        with patch("rick_mcp.tools.jarvis._STATE_DIR", tmp_path):
            await rick_kill_chain(KillChainInput(action="status", engagement_id="no-active"))
            result = await rick_kill_chain(KillChainInput(action="advance", engagement_id="no-active"))
        assert "No active" in result

    @pytest.mark.asyncio
    async def test_status_completed_engagement(self, tmp_path):
        from rick_mcp.tools.jarvis import KillChainInput, rick_kill_chain

        with patch("rick_mcp.tools.jarvis._STATE_DIR", tmp_path):
            await rick_kill_chain(KillChainInput(action="status", engagement_id="done-eng"))
            for phase in range(1, 8):
                await rick_kill_chain(KillChainInput(action="advance", engagement_id="done-eng", phase=phase))
                await rick_kill_chain(KillChainInput(action="advance", engagement_id="done-eng"))
            result = await rick_kill_chain(KillChainInput(action="status", engagement_id="done-eng"))
        assert "7/7" in result or "COMPLETE" in result


class TestRickNextMove:
    @pytest.mark.asyncio
    async def test_next_move_no_engagement(self, tmp_path):
        from rick_mcp.tools.jarvis import NextMoveInput, rick_next_move

        with patch("rick_mcp.tools.jarvis._STATE_DIR", tmp_path):
            result = await rick_next_move(NextMoveInput(engagement_id="ghost"))
        assert "No engagement" in result or "error" in result.lower()

    @pytest.mark.asyncio
    async def test_next_move_new_engagement(self, tmp_path):
        from rick_mcp.tools.jarvis import KillChainInput, NextMoveInput, rick_kill_chain, rick_next_move

        with patch("rick_mcp.tools.jarvis._STATE_DIR", tmp_path):
            await rick_kill_chain(KillChainInput(action="status", engagement_id="next-eng"))
            result = await rick_next_move(NextMoveInput(engagement_id="next-eng"))
        assert "rick_full_auto" in result or "recon" in result.lower()

    @pytest.mark.asyncio
    async def test_next_move_with_position(self, tmp_path):
        from rick_mcp.tools.jarvis import KillChainInput, NextMoveInput, rick_kill_chain, rick_next_move

        with patch("rick_mcp.tools.jarvis._STATE_DIR", tmp_path):
            await rick_kill_chain(KillChainInput(action="status", engagement_id="pos-eng"))
            await rick_kill_chain(KillChainInput(action="advance", engagement_id="pos-eng", phase=4))
            result = await rick_next_move(NextMoveInput(engagement_id="pos-eng", current_position="linux_webserver"))
        assert "linux_webserver" in result or "pivot" in result.lower()

    @pytest.mark.asyncio
    async def test_next_move_recon_phase_few_findings(self, tmp_path):
        from rick_mcp.tools.jarvis import KillChainInput, NextMoveInput, rick_kill_chain, rick_next_move

        with patch("rick_mcp.tools.jarvis._STATE_DIR", tmp_path):
            await rick_kill_chain(KillChainInput(action="status", engagement_id="recon-eng"))
            await rick_kill_chain(KillChainInput(action="advance", engagement_id="recon-eng", phase=1))
            result = await rick_next_move(NextMoveInput(engagement_id="recon-eng"))
        assert "recon" in result.lower() or "rick_recon" in result

    @pytest.mark.asyncio
    async def test_next_move_recon_phase_enough_findings(self, tmp_path):
        from rick_mcp.tools.jarvis import KillChainInput, NextMoveInput, rick_kill_chain, rick_next_move

        with patch("rick_mcp.tools.jarvis._STATE_DIR", tmp_path):
            await rick_kill_chain(KillChainInput(action="status", engagement_id="recon-full"))
            await rick_kill_chain(KillChainInput(action="advance", engagement_id="recon-full", phase=1))
            for f in ["Port 80 open", "Port 443 open", "Apache 2.4.49"]:
                await rick_kill_chain(KillChainInput(action="add_finding", engagement_id="recon-full", finding=f))
            result = await rick_next_move(NextMoveInput(engagement_id="recon-full"))
        assert "3 findings" in result or "advance" in result.lower()

    @pytest.mark.asyncio
    async def test_next_move_completed(self, tmp_path):
        from rick_mcp.tools.jarvis import KillChainInput, NextMoveInput, rick_kill_chain, rick_next_move

        with patch("rick_mcp.tools.jarvis._STATE_DIR", tmp_path):
            await rick_kill_chain(KillChainInput(action="status", engagement_id="done-eng"))
            for phase in range(1, 8):
                await rick_kill_chain(KillChainInput(action="advance", engagement_id="done-eng", phase=phase))
                await rick_kill_chain(KillChainInput(action="advance", engagement_id="done-eng"))
            result = await rick_next_move(NextMoveInput(engagement_id="done-eng"))
        assert "report" in result.lower()

    @pytest.mark.asyncio
    async def test_next_move_with_extra_findings(self, tmp_path):
        from rick_mcp.tools.jarvis import KillChainInput, NextMoveInput, rick_kill_chain, rick_next_move

        with patch("rick_mcp.tools.jarvis._STATE_DIR", tmp_path):
            await rick_kill_chain(KillChainInput(action="status", engagement_id="extra-eng"))
            await rick_kill_chain(KillChainInput(action="advance", engagement_id="extra-eng", phase=1))
            result = await rick_next_move(
                NextMoveInput(engagement_id="extra-eng", findings_so_far="SQLi in login, SSRF in avatar upload")
            )
        assert "SQLi" in result or "additional" in result.lower()

    @pytest.mark.asyncio
    async def test_next_move_each_phase(self, tmp_path):
        """Test that next_move gives recommendations for phases 2-7."""
        from rick_mcp.tools.jarvis import KillChainInput, NextMoveInput, rick_kill_chain, rick_next_move

        for phase in range(2, 8):
            with patch("rick_mcp.tools.jarvis._STATE_DIR", tmp_path):
                eid = f"phase-{phase}-eng"
                await rick_kill_chain(KillChainInput(action="status", engagement_id=eid))
                await rick_kill_chain(KillChainInput(action="advance", engagement_id=eid, phase=phase))
                result = await rick_next_move(NextMoveInput(engagement_id=eid))
            assert "dick_says" in result.lower() or "recommend" in result.lower() or len(result) > 100


class TestDickHelpers:
    def test_phase_advice_all_phases(self):
        from rick_mcp.tools.jarvis import _phase_advice

        for phase in range(1, 8):
            advice = _phase_advice(phase)
            assert len(advice) > 20

    def test_phase_advice_unknown(self):
        from rick_mcp.tools.jarvis import _phase_advice

        assert _phase_advice(99) == "Execute with precision."

    def test_state_file_sanitizes(self):
        from rick_mcp.tools.jarvis import _state_file

        path = _state_file("test/../../../etc/passwd")
        # Path traversal chars (/, .) are stripped — no directory escape
        assert "/" not in path.name
        assert ".." not in path.name

    def test_load_state_missing(self, tmp_path):
        from rick_mcp.tools.jarvis import _load_state

        with patch("rick_mcp.tools.jarvis._STATE_DIR", tmp_path):
            state = _load_state("nonexistent")
        assert state == {}

    def test_save_and_load_state(self, tmp_path):
        from rick_mcp.tools.jarvis import _load_state, _save_state

        with patch("rick_mcp.tools.jarvis._STATE_DIR", tmp_path):
            _save_state("test-id", {"id": "test-id", "target": "example.com"})
            state = _load_state("test-id")
        assert state["id"] == "test-id"
        assert state["target"] == "example.com"

    def test_input_validation_kill_chain(self):
        from rick_mcp.tools.jarvis import KillChainInput

        with pytest.raises(ValidationError):
            KillChainInput(action="status", engagement_id="x", phase=0)
        with pytest.raises(ValidationError):
            KillChainInput(action="status", engagement_id="x", phase=8)


class TestRickSitrep:
    @pytest.mark.asyncio
    async def test_sitrep_no_engagement(self, tmp_path):
        from rick_mcp.tools.jarvis import SitrepInput, rick_sitrep

        with patch("rick_mcp.tools.jarvis._STATE_DIR", tmp_path):
            result = await rick_sitrep(SitrepInput(engagement_id="ghost"))
        assert "No engagement" in result or "error" in result.lower()

    @pytest.mark.asyncio
    async def test_sitrep_new_engagement(self, tmp_path):
        from rick_mcp.tools.jarvis import KillChainInput, SitrepInput, rick_kill_chain, rick_sitrep

        with patch("rick_mcp.tools.jarvis._STATE_DIR", tmp_path):
            await rick_kill_chain(KillChainInput(action="status", engagement_id="sit-eng"))
            result = await rick_sitrep(SitrepInput(engagement_id="sit-eng"))
        assert "SITREP" in result
        assert "0/7" in result or "sit-eng" in result

    @pytest.mark.asyncio
    async def test_sitrep_with_findings(self, tmp_path):
        from rick_mcp.tools.jarvis import KillChainInput, SitrepInput, rick_kill_chain, rick_sitrep

        with patch("rick_mcp.tools.jarvis._STATE_DIR", tmp_path):
            await rick_kill_chain(KillChainInput(action="status", engagement_id="sit-find"))
            await rick_kill_chain(KillChainInput(action="advance", engagement_id="sit-find", phase=1))
            await rick_kill_chain(
                KillChainInput(action="add_finding", engagement_id="sit-find", finding="Port 443 open")
            )
            result = await rick_sitrep(SitrepInput(engagement_id="sit-find"))
        assert "Port 443" in result
        assert "1" in result  # at least 1 finding

    @pytest.mark.asyncio
    async def test_sitrep_completed(self, tmp_path):
        from rick_mcp.tools.jarvis import KillChainInput, SitrepInput, rick_kill_chain, rick_sitrep

        with patch("rick_mcp.tools.jarvis._STATE_DIR", tmp_path):
            await rick_kill_chain(KillChainInput(action="status", engagement_id="sit-done"))
            for phase in range(1, 8):
                await rick_kill_chain(KillChainInput(action="advance", engagement_id="sit-done", phase=phase))
                await rick_kill_chain(KillChainInput(action="advance", engagement_id="sit-done"))
            result = await rick_sitrep(SitrepInput(engagement_id="sit-done"))
        assert "7/7" in result or "COMPLETE" in result

    @pytest.mark.asyncio
    async def test_sitrep_with_mission_log(self, tmp_path):
        from rick_mcp.tools.jarvis import SitrepInput, _save_state, rick_sitrep

        with patch("rick_mcp.tools.jarvis._STATE_DIR", tmp_path):
            _save_state(
                "log-eng",
                {
                    "id": "log-eng",
                    "target": "test.com",
                    "target_type": "web_app",
                    "kill_chain": [
                        dict(p)
                        for p in __import__("rick_mcp.tools.jarvis", fromlist=["KILL_CHAIN_PHASES"]).KILL_CHAIN_PHASES
                    ],
                    "mission_log": [{"timestamp": "2026-03-23T12:00:00Z", "entry": "Test entry"}],
                },
            )
            result = await rick_sitrep(SitrepInput(engagement_id="log-eng"))
        assert "Test entry" in result

    @pytest.mark.asyncio
    async def test_sitrep_backward_compat(self, tmp_path):
        """Old state files without mission_log/tool_history should work."""
        from rick_mcp.tools.jarvis import KILL_CHAIN_PHASES, SitrepInput, _save_state, rick_sitrep

        with patch("rick_mcp.tools.jarvis._STATE_DIR", tmp_path):
            _save_state(
                "old-eng",
                {
                    "id": "old-eng",
                    "target": "legacy.com",
                    "kill_chain": [dict(p) for p in KILL_CHAIN_PHASES],
                },
            )
            result = await rick_sitrep(SitrepInput(engagement_id="old-eng"))
        assert "legacy.com" in result


class TestStateHelpers:
    def test_add_mission_log(self, tmp_path):
        from rick_mcp.tools.jarvis import KILL_CHAIN_PHASES, _add_mission_log, _load_state, _save_state

        with patch("rick_mcp.tools.jarvis._STATE_DIR", tmp_path):
            _save_state("ml-eng", {"id": "ml-eng", "kill_chain": [dict(p) for p in KILL_CHAIN_PHASES]})
            _add_mission_log("ml-eng", "Test log entry")
            state = _load_state("ml-eng")
        assert len(state["mission_log"]) == 1
        assert state["mission_log"][0]["entry"] == "Test log entry"

    def test_add_tool_history(self, tmp_path):
        from rick_mcp.tools.jarvis import KILL_CHAIN_PHASES, _add_tool_history, _load_state, _save_state

        with patch("rick_mcp.tools.jarvis._STATE_DIR", tmp_path):
            _save_state("th-eng", {"id": "th-eng", "kill_chain": [dict(p) for p in KILL_CHAIN_PHASES]})
            _add_tool_history("th-eng", "rick_recon", "Recon for web_app")
            state = _load_state("th-eng")
        assert len(state["tool_history"]) == 1
        assert state["tool_history"][0]["tool"] == "rick_recon"

    def test_add_note(self, tmp_path):
        from rick_mcp.tools.jarvis import KILL_CHAIN_PHASES, _add_note, _load_state, _save_state

        with patch("rick_mcp.tools.jarvis._STATE_DIR", tmp_path):
            _save_state("note-eng", {"id": "note-eng", "kill_chain": [dict(p) for p in KILL_CHAIN_PHASES]})
            _add_note("note-eng", "Client uses CrowdStrike")
            state = _load_state("note-eng")
        assert "Client uses CrowdStrike" in state["notes"]

    def test_helpers_no_state(self, tmp_path):
        """Helpers should silently return when engagement doesn't exist."""
        from rick_mcp.tools.jarvis import _add_mission_log, _add_note, _add_tool_history

        with patch("rick_mcp.tools.jarvis._STATE_DIR", tmp_path):
            _add_mission_log("ghost", "entry")
            _add_tool_history("ghost", "tool")
            _add_note("ghost", "note")
        # No error raised — silent return
