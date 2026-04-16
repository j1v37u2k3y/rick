"""Tests for rick_writeups — list, read, search write-ups from ~/.rick_mcp/writeups/."""

from pathlib import Path
from unittest.mock import patch

import pytest

_PATCH_TARGET = "rick_mcp.tools.writeups.WRITEUPS_DIR"


def _populate(tmp_path: Path):
    """Create a sample writeups directory with nested categories."""
    htb = tmp_path / "htb"
    htb.mkdir()
    (htb / "lame.md").write_text(
        "# Lame\n\nEasy Linux box. SMB exploit via CVE-2007-2447.\n\n## Recon\nnmap found port 445 open.\n"
    )
    (htb / "blue.md").write_text(
        "# Blue\n\nEternalBlue MS17-010. Classic Windows exploit.\n\n## Exploitation\nUsed ms17_010_psexec.\n"
    )

    ctf = tmp_path / "ctf"
    ctf.mkdir()
    (ctf / "picoctf_2024.md").write_text("# PicoCTF 2024\n\n## Web Exploitation\nFound SQL injection in login form.\n")

    (tmp_path / "standalone.md").write_text("# Standalone Note\n\nThis is a root-level writeup about Kerberoasting.\n")


class TestWriteupsList:
    @pytest.mark.asyncio
    async def test_list_all(self, tmp_path):
        from rick_mcp.models import WriteupInput
        from rick_mcp.tools.writeups import rick_writeups

        _populate(tmp_path)
        with patch(_PATCH_TARGET, tmp_path):
            result = await rick_writeups(WriteupInput(action="list"))
        assert "Lame" in result
        assert "Blue" in result
        assert "PicoCTF" in result
        assert "Standalone" in result

    @pytest.mark.asyncio
    async def test_list_by_category(self, tmp_path):
        from rick_mcp.models import WriteupInput
        from rick_mcp.tools.writeups import rick_writeups

        _populate(tmp_path)
        with patch(_PATCH_TARGET, tmp_path):
            result = await rick_writeups(WriteupInput(action="list", category="htb"))
        assert "Lame" in result
        assert "Blue" in result
        assert "PicoCTF" not in result

    @pytest.mark.asyncio
    async def test_list_empty_dir(self, tmp_path):
        from rick_mcp.models import WriteupInput
        from rick_mcp.tools.writeups import rick_writeups

        empty = tmp_path / "empty"
        empty.mkdir()
        with patch(_PATCH_TARGET, empty):
            result = await rick_writeups(WriteupInput(action="list"))
        assert "None found" in result

    @pytest.mark.asyncio
    async def test_list_missing_dir(self, tmp_path):
        from rick_mcp.models import WriteupInput
        from rick_mcp.tools.writeups import rick_writeups

        with patch(_PATCH_TARGET, tmp_path / "nonexistent"):
            result = await rick_writeups(WriteupInput(action="list"))
        assert "No writeups directory" in result

    @pytest.mark.asyncio
    async def test_list_bad_category(self, tmp_path):
        from rick_mcp.models import WriteupInput
        from rick_mcp.tools.writeups import rick_writeups

        _populate(tmp_path)
        with patch(_PATCH_TARGET, tmp_path):
            result = await rick_writeups(WriteupInput(action="list", category="nope"))
        assert "None found" in result

    @pytest.mark.asyncio
    async def test_list_with_limit(self, tmp_path):
        from rick_mcp.models import WriteupInput
        from rick_mcp.tools.writeups import rick_writeups

        _populate(tmp_path)
        with patch(_PATCH_TARGET, tmp_path):
            result = await rick_writeups(WriteupInput(action="list", limit=2))
        assert "total_available" in result.lower() or "4" in result


class TestWriteupsRead:
    @pytest.mark.asyncio
    async def test_read_file(self, tmp_path):
        from rick_mcp.models import WriteupInput
        from rick_mcp.tools.writeups import rick_writeups

        _populate(tmp_path)
        with patch(_PATCH_TARGET, tmp_path):
            result = await rick_writeups(WriteupInput(action="read", path="htb/lame.md"))
        assert "Lame" in result
        assert "SMB exploit" in result

    @pytest.mark.asyncio
    async def test_read_root_level(self, tmp_path):
        from rick_mcp.models import WriteupInput
        from rick_mcp.tools.writeups import rick_writeups

        _populate(tmp_path)
        with patch(_PATCH_TARGET, tmp_path):
            result = await rick_writeups(WriteupInput(action="read", path="standalone.md"))
        assert "Kerberoasting" in result

    @pytest.mark.asyncio
    async def test_read_missing_path_param(self, tmp_path):
        from rick_mcp.models import WriteupInput
        from rick_mcp.tools.writeups import rick_writeups

        _populate(tmp_path)
        with patch(_PATCH_TARGET, tmp_path):
            result = await rick_writeups(WriteupInput(action="read"))
        assert "path=" in result.lower() or "required" in result.lower()

    @pytest.mark.asyncio
    async def test_read_nonexistent(self, tmp_path):
        from rick_mcp.models import WriteupInput
        from rick_mcp.tools.writeups import rick_writeups

        _populate(tmp_path)
        with patch(_PATCH_TARGET, tmp_path):
            result = await rick_writeups(WriteupInput(action="read", path="htb/nope.md"))
        assert "not found" in result.lower() or "error" in result.lower()

    @pytest.mark.asyncio
    async def test_read_traversal_rejected(self, tmp_path):
        from rick_mcp.models import WriteupInput
        from rick_mcp.tools.writeups import rick_writeups

        _populate(tmp_path)
        with patch(_PATCH_TARGET, tmp_path):
            result = await rick_writeups(WriteupInput(action="read", path="../../etc/passwd"))
        assert "not found" in result.lower() or "escapes" in result.lower() or "error" in result.lower()


class TestWriteupsSearch:
    @pytest.mark.asyncio
    async def test_search_finds_match(self, tmp_path):
        from rick_mcp.models import WriteupInput
        from rick_mcp.tools.writeups import rick_writeups

        _populate(tmp_path)
        with patch(_PATCH_TARGET, tmp_path):
            result = await rick_writeups(WriteupInput(action="search", query="EternalBlue"))
        assert "blue" in result.lower()

    @pytest.mark.asyncio
    async def test_search_case_insensitive(self, tmp_path):
        from rick_mcp.models import WriteupInput
        from rick_mcp.tools.writeups import rick_writeups

        _populate(tmp_path)
        with patch(_PATCH_TARGET, tmp_path):
            result = await rick_writeups(WriteupInput(action="search", query="eternalblue"))
        assert "blue" in result.lower()

    @pytest.mark.asyncio
    async def test_search_with_category(self, tmp_path):
        from rick_mcp.models import WriteupInput
        from rick_mcp.tools.writeups import rick_writeups

        _populate(tmp_path)
        with patch(_PATCH_TARGET, tmp_path):
            result = await rick_writeups(WriteupInput(action="search", query="SQL injection", category="ctf"))
        assert "picoctf" in result.lower()

    @pytest.mark.asyncio
    async def test_search_no_match(self, tmp_path):
        from rick_mcp.models import WriteupInput
        from rick_mcp.tools.writeups import rick_writeups

        _populate(tmp_path)
        with patch(_PATCH_TARGET, tmp_path):
            result = await rick_writeups(WriteupInput(action="search", query="zzz_nonexistent_zzz"))
        assert "no match" in result.lower() or "No matches" in result

    @pytest.mark.asyncio
    async def test_search_missing_query(self, tmp_path):
        from rick_mcp.models import WriteupInput
        from rick_mcp.tools.writeups import rick_writeups

        _populate(tmp_path)
        with patch(_PATCH_TARGET, tmp_path):
            result = await rick_writeups(WriteupInput(action="search"))
        assert "query=" in result.lower() or "required" in result.lower()

    @pytest.mark.asyncio
    async def test_search_bad_category(self, tmp_path):
        from rick_mcp.models import WriteupInput
        from rick_mcp.tools.writeups import rick_writeups

        _populate(tmp_path)
        with patch(_PATCH_TARGET, tmp_path):
            result = await rick_writeups(WriteupInput(action="search", query="test", category="nope"))
        assert "not found" in result.lower() or "error" in result.lower()

    @pytest.mark.asyncio
    async def test_search_python_fallback(self, tmp_path):
        from rick_mcp.models import WriteupInput
        from rick_mcp.tools.writeups import rick_writeups

        _populate(tmp_path)
        with patch(_PATCH_TARGET, tmp_path), patch("rick_mcp.tools.writeups.shutil.which", return_value=None):
            result = await rick_writeups(WriteupInput(action="search", query="nmap"))
        assert "lame" in result.lower()


class TestWriteupsInvalidAction:
    @pytest.mark.asyncio
    async def test_invalid_action(self, tmp_path):
        from rick_mcp.models import WriteupInput
        from rick_mcp.tools.writeups import rick_writeups

        _populate(tmp_path)
        with patch(_PATCH_TARGET, tmp_path):
            result = await rick_writeups(WriteupInput(action="delete"))
        assert "Unknown action" in result


class TestWriteupInputValidation:
    def test_extra_fields_rejected(self):
        from pydantic import ValidationError

        from rick_mcp.models import WriteupInput

        with pytest.raises(ValidationError):
            WriteupInput(action="list", bad_field="nope")

    def test_action_required(self):
        from pydantic import ValidationError

        from rick_mcp.models import WriteupInput

        with pytest.raises(ValidationError):
            WriteupInput()

    def test_json_output(self, tmp_path):
        from rick_mcp.models import WriteupInput

        inp = WriteupInput(action="list", response_format="json")
        assert inp.response_format.value == "json"


class TestCiteWriteups:
    def test_cite_finds_matches(self, tmp_path):
        from rick_mcp.tools.writeups import cite_writeups

        _populate(tmp_path)
        with patch(_PATCH_TARGET, tmp_path):
            cites = cite_writeups("EternalBlue")
        assert any("blue" in c.lower() for c in cites)

    def test_cite_empty_term(self, tmp_path):
        from rick_mcp.tools.writeups import cite_writeups

        _populate(tmp_path)
        with patch(_PATCH_TARGET, tmp_path):
            assert cite_writeups("") == []
            assert cite_writeups("   ") == []

    def test_cite_no_matches(self, tmp_path):
        from rick_mcp.tools.writeups import cite_writeups

        _populate(tmp_path)
        with patch(_PATCH_TARGET, tmp_path):
            assert cite_writeups("zzz_nothing_here_zzz") == []

    def test_cite_missing_dir(self, tmp_path):
        from rick_mcp.tools.writeups import cite_writeups

        with patch(_PATCH_TARGET, tmp_path / "missing"):
            assert cite_writeups("anything") == []

    def test_cite_dedupes_files(self, tmp_path):
        """If a term appears on multiple lines in one file, return the file once."""
        from rick_mcp.tools.writeups import cite_writeups

        htb = tmp_path / "htb"
        htb.mkdir()
        (htb / "repeat.md").write_text("# Repeat\n\nnmap run 1\nnmap run 2\nnmap run 3\n")
        with patch(_PATCH_TARGET, tmp_path):
            cites = cite_writeups("nmap")
        assert cites.count("htb/repeat.md") <= 1

    def test_cite_respects_limit(self, tmp_path):
        from rick_mcp.tools.writeups import cite_writeups

        cat = tmp_path / "ctf"
        cat.mkdir()
        for i in range(8):
            (cat / f"box{i}.md").write_text(f"# Box{i}\n\nUsed hashcat to crack.\n")
        with patch(_PATCH_TARGET, tmp_path):
            cites = cite_writeups("hashcat", limit=3)
        assert len(cites) == 3


class TestWriteupsIndex:
    @pytest.mark.asyncio
    async def test_index_basic(self, tmp_path):
        from rick_mcp.models import WriteupInput
        from rick_mcp.tools.writeups import rick_writeups

        _populate(tmp_path)
        with patch(_PATCH_TARGET, tmp_path):
            result = await rick_writeups(WriteupInput(action="index"))
        assert "total_writeups" in result.lower() or "Total Writeups" in result
        assert "nmap" in result.lower()  # nmap appears in lame.md

    @pytest.mark.asyncio
    async def test_index_extracts_cve(self, tmp_path):
        from rick_mcp.models import WriteupInput
        from rick_mcp.tools.writeups import rick_writeups

        (tmp_path / "box.md").write_text("# Box\n\nExploited CVE-2007-2447 via smb.\n")
        with patch(_PATCH_TARGET, tmp_path):
            result = await rick_writeups(WriteupInput(action="index"))
        assert "CVE-2007-2447" in result

    @pytest.mark.asyncio
    async def test_index_extracts_mitre(self, tmp_path):
        from rick_mcp.models import WriteupInput
        from rick_mcp.tools.writeups import rick_writeups

        (tmp_path / "box.md").write_text("# Box\n\nUsed T1558.003 kerberoasting.\n")
        with patch(_PATCH_TARGET, tmp_path):
            result = await rick_writeups(WriteupInput(action="index"))
        assert "T1558.003" in result

    @pytest.mark.asyncio
    async def test_index_cached(self, tmp_path):
        """Index writes a cache file and returns fast on second call."""
        from rick_mcp.models import WriteupInput
        from rick_mcp.tools.writeups import rick_writeups

        _populate(tmp_path)
        with patch(_PATCH_TARGET, tmp_path):
            await rick_writeups(WriteupInput(action="index"))
            assert (tmp_path / ".index.json").exists()
            # Second call should read from cache (verify by modifying cache and expecting stale data)
            (tmp_path / ".index.json").write_text('{"total_writeups": 9999, "rick_note": "stale"}')
            result = await rick_writeups(WriteupInput(action="index"))
        assert "9999" in result

    @pytest.mark.asyncio
    async def test_index_os_breakdown(self, tmp_path):
        from rick_mcp.models import WriteupInput
        from rick_mcp.tools.writeups import rick_writeups

        linux_box = tmp_path / "linux_box.md"
        linux_box.write_text("# Linux Box\n\nUbuntu server with kernel exploit.\n")
        win_box = tmp_path / "win_box.md"
        win_box.write_text("# Windows Box\n\nActive Directory domain controller.\n")
        with patch(_PATCH_TARGET, tmp_path):
            result = await rick_writeups(WriteupInput(action="index"))
        assert "linux_mentions" in result.lower() or "Linux Mentions" in result


class TestWriteupCrossReferencing:
    """Citations wire into other tools — verify the integration."""

    @pytest.mark.asyncio
    async def test_cheatsheet_cites_writeups(self, tmp_path):
        from rick_mcp.models import CheatsheetInput
        from rick_mcp.tools.offensive_tradecraft import rick_cheatsheet

        _populate(tmp_path)
        with patch(_PATCH_TARGET, tmp_path):
            result = await rick_cheatsheet(CheatsheetInput(tool="nmap"))
        # nmap appears in lame.md
        assert "seen_in_writeups" in result.lower() or "Seen In Writeups" in result

    @pytest.mark.asyncio
    async def test_recon_cites_writeups(self, tmp_path):
        from rick_mcp.models import ReconInput
        from rick_mcp.tools.offensive import rick_recon

        kerberos_box = tmp_path / "kerberos.md"
        kerberos_box.write_text("# Kerberoast\n\nActive Directory kerberoasting attack.\n")
        with patch(_PATCH_TARGET, tmp_path):
            result = await rick_recon(ReconInput(target_type="active_directory"))
        assert "seen_in_writeups" in result.lower() or "Seen In Writeups" in result

    @pytest.mark.asyncio
    async def test_cite_silent_when_no_writeups(self, tmp_path):
        """If no writeups exist, tools render normally without 'seen in writeups' section."""
        from rick_mcp.models import CheatsheetInput
        from rick_mcp.tools.offensive_tradecraft import rick_cheatsheet

        with patch(_PATCH_TARGET, tmp_path / "nonexistent"):
            result = await rick_cheatsheet(CheatsheetInput(tool="nmap"))
        assert "seen_in_writeups" not in result.lower()
        # But the cheatsheet itself still works
        assert "Nmap" in result
