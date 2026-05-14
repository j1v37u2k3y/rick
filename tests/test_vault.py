"""Tests for rick_mcp.vault — the vault integration foundation.

Mirrors test_extended.py's pattern of monkey-patching Path.home() to a tmp_path so
~/.rick_mcp/vault/ resolves to a temp directory.
"""

from unittest.mock import patch

import pytest

from rick_mcp import vault

# ── Fixtures ─────────────────────────────────────────────────────────────────────────────────


@pytest.fixture
def fake_home(tmp_path):
    """Patch Path.home() to return tmp_path. Yields tmp_path."""
    with patch("pathlib.Path.home", return_value=tmp_path):
        yield tmp_path


@pytest.fixture
def configured_vault(fake_home):
    """Bootstrap a minimal vault inside fake_home. Yields the vault path."""
    vault_dir = fake_home / ".rick_mcp" / "vault"
    vault_dir.mkdir(parents=True)
    (vault_dir / "_CLAUDE.md").write_text("# Stub _CLAUDE.md for tests\n", encoding="utf-8")
    (vault_dir / "log.md").write_text(
        "# Vault Activity Log\n\n## [2026-05-09] init | bootstrap\n\n---\n",
        encoding="utf-8",
    )
    (vault_dir / "Engagements").mkdir()
    (vault_dir / "Templates").mkdir()
    (vault_dir / "Identity").mkdir()
    yield vault_dir


# ── is_configured / _is_configured ──────────────────────────────────────────────────────────


class TestIsConfigured:
    def test_returns_false_when_vault_missing(self, fake_home):
        assert vault._is_configured() is False

    def test_returns_false_when_claude_md_missing(self, fake_home):
        (fake_home / ".rick_mcp" / "vault").mkdir(parents=True)
        assert vault._is_configured() is False

    def test_returns_true_when_bootstrapped(self, configured_vault):
        assert vault._is_configured() is True


# ── slugify / codename helpers ──────────────────────────────────────────────────────────────


class TestSlugify:
    def test_lowercases_and_hyphenates(self):
        assert vault.slugify("Hello World") == "hello-world"

    def test_strips_non_alphanumeric(self):
        # "Foo!@#Bar" → lowercase "foo!@#bar" → @ becomes "at" → "foo!at#bar" → non-alnum runs to "-" → "foo-at-bar"
        assert vault.slugify("Foo!@#Bar") == "foo-at-bar"

    def test_collapses_runs(self):
        assert vault.slugify("a   b  c") == "a-b-c"

    def test_returns_untitled_when_empty(self):
        assert vault.slugify("!!!") == "untitled"

    def test_preserves_at_replacement(self):
        # "user@host" → replace @ with "at" → "userathost" → no non-alnum → "userathost"
        assert vault.slugify("user@host") == "userathost"


class TestCodenameFor:
    def test_default_format(self):
        result = vault.codename_for("Acme Corp", "web_app_pentest", date="2026-05-09")
        assert result == "Acme Corp - Web App Pentest (2026-05-09)"

    def test_uses_today_when_no_date(self):
        result = vault.codename_for("Acme", "red_team")
        # Just verify shape, not exact date
        assert result.startswith("Acme - Red Team (")
        assert result.endswith(")")

    def test_handles_empty_client(self):
        result = vault.codename_for("", "network_pentest", date="2026-05-09")
        assert result == "Client - Network Pentest (2026-05-09)"

    def test_strips_filesystem_unsafe_chars(self):
        result = vault.codename_for("Acme/Corp", "ad_review", date="2026-05-09")
        assert "/" not in result


class TestCodenameToFilename:
    def test_strips_slashes(self):
        assert vault.codename_to_filename("a/b\\c") == "a-b-c"

    def test_returns_default_when_empty(self):
        assert vault.codename_to_filename("   ") == "Untitled Engagement"


# ── frontmatter / preamble builders ─────────────────────────────────────────────────────────


class TestFrontmatter:
    def test_basic_scalars(self):
        result = vault.frontmatter({"date": "2026-05-09", "type": "engagement"})
        assert result.startswith("---\n")
        assert result.endswith("\n---")
        assert "date: 2026-05-09" in result
        assert "type: engagement" in result

    def test_inline_array_space_padded(self):
        result = vault.frontmatter({"tags": ["a", "b", "c"]})
        assert "tags: [ a, b, c ]" in result

    def test_empty_list_renders_inline(self):
        result = vault.frontmatter({"tags": []})
        assert "tags: []" in result

    def test_bool_lowercase(self):
        result = vault.frontmatter({"ai-first": True, "draft": False})
        assert "ai-first: true" in result
        assert "draft: false" in result

    def test_quotes_special_chars(self):
        result = vault.frontmatter({"client": "Acme: Inc"})
        assert 'client: "Acme: Inc"' in result

    def test_quotes_yaml_keywords(self):
        result = vault.frontmatter({"value": "yes"})
        assert 'value: "yes"' in result

    def test_none_renders_empty(self):
        result = vault.frontmatter({"updated": None})
        assert "updated:" in result
        # Empty value, not "None"
        assert "updated: None" not in result


class TestPreamble:
    def test_wraps_with_header(self):
        result = vault.preamble("This is a note.")
        assert result.startswith("## For future Claude\n\n")
        assert "This is a note." in result

    def test_strips_whitespace(self):
        result = vault.preamble("   text   ")
        assert "text" in result
        assert "   text" not in result


# ── wikilink mappings ───────────────────────────────────────────────────────────────────────


class TestWikilinkMappings:
    def test_specialization_for_known_type(self):
        assert (
            vault.specialization_wikilink("web_app_pentest") == "[[Identity/Specializations/Web Application Security]]"
        )

    def test_specialization_empty_for_unmapped(self):
        assert vault.specialization_wikilink("unknown_type") == ""

    def test_specialization_empty_for_full_scope(self):
        # full_scope is multi-spec by design — returns ''
        assert vault.specialization_wikilink("full_scope") == ""

    def test_tools_for_web_app_includes_burp(self):
        tools = vault.tools_wikilinks("web_app_pentest")
        assert "[[Identity/Tools/Burp Suite]]" in tools
        assert "[[Identity/Tools/SQLMap]]" in tools

    def test_tools_for_ad_review_includes_bloodhound(self):
        tools = vault.tools_wikilinks("ad_review")
        assert "[[Identity/Tools/BloodHound]]" in tools
        assert "[[Identity/Tools/Impacket]]" in tools

    def test_tools_empty_for_unmapped(self):
        assert vault.tools_wikilinks("unknown_type") == []


# ── write_engagement ────────────────────────────────────────────────────────────────────────


class TestWriteEngagement:
    def test_returns_none_when_vault_unconfigured(self, fake_home):
        result = vault.write_engagement(
            "Acme - Web App Pentest (2026-05-09)",
            client="Acme",
            engagement_type="web_app_pentest",
            body="# Body",
        )
        assert result is None

    def test_creates_new_file(self, configured_vault):
        result = vault.write_engagement(
            "Acme - Web App Pentest (2026-05-09)",
            client="Acme",
            engagement_type="web_app_pentest",
            body="# Body content",
        )
        assert result is not None
        path, created = result
        assert created is True
        assert path.exists()
        assert path.parent.name == "Engagements"

    def test_writes_ai_first_frontmatter(self, configured_vault):
        result = vault.write_engagement(
            "Acme - Web App Pentest (2026-05-09)",
            client="Acme",
            engagement_type="web_app_pentest",
            body="body",
        )
        assert result is not None
        path, _ = result
        content = path.read_text(encoding="utf-8")
        assert content.startswith("---\n")
        assert "type: engagement" in content
        assert "ai-first: true" in content
        assert "client: Acme" in content
        assert "## For future Claude" in content

    def test_writes_space_padded_tags(self, configured_vault):
        result = vault.write_engagement(
            "Acme - Network Pentest (2026-05-09)",
            client="Acme",
            engagement_type="network_pentest",
            body="body",
        )
        assert result is not None
        path, _ = result
        content = path.read_text(encoding="utf-8")
        # tags: [ engagement, network-pentest ]
        assert "tags: [ engagement, network-pentest ]" in content

    def test_does_not_overwrite_by_default(self, configured_vault):
        # First write
        r1 = vault.write_engagement(
            "Acme - Web App Pentest (2026-05-09)",
            client="Acme",
            engagement_type="web_app_pentest",
            body="ORIGINAL",
        )
        assert r1 is not None
        path1, created1 = r1
        assert created1 is True
        original = path1.read_text(encoding="utf-8")
        # Second write — should preserve
        r2 = vault.write_engagement(
            "Acme - Web App Pentest (2026-05-09)",
            client="Acme",
            engagement_type="web_app_pentest",
            body="REPLACEMENT",
        )
        assert r2 is not None
        path2, created2 = r2
        assert created2 is False
        assert path2 == path1
        assert path1.read_text(encoding="utf-8") == original
        assert "ORIGINAL" in original
        assert "REPLACEMENT" not in original

    def test_overwrites_when_flagged(self, configured_vault):
        vault.write_engagement(
            "Acme - Web App Pentest (2026-05-09)",
            client="Acme",
            engagement_type="web_app_pentest",
            body="ORIGINAL",
        )
        result = vault.write_engagement(
            "Acme - Web App Pentest (2026-05-09)",
            client="Acme",
            engagement_type="web_app_pentest",
            body="REPLACEMENT",
            overwrite=True,
        )
        assert result is not None
        path, created = result
        assert created is True
        assert "REPLACEMENT" in path.read_text(encoding="utf-8")
        assert "ORIGINAL" not in path.read_text(encoding="utf-8")

    def test_filename_strips_slashes(self, configured_vault):
        result = vault.write_engagement(
            "Acme/Corp - Web App Pentest (2026-05-09)",
            client="Acme/Corp",
            engagement_type="web_app_pentest",
            body="body",
        )
        assert result is not None
        path, _ = result
        # Slashes replaced with hyphens
        assert "/" not in path.name
        assert path.name.endswith(".md")


# ── append_engagement_section ───────────────────────────────────────────────────────────────


class TestAppendEngagementSection:
    def test_returns_none_when_vault_unconfigured(self, fake_home):
        result = vault.append_engagement_section("Acme", section_heading="Debrief", section_body="content")
        assert result is None

    def test_returns_none_when_engagement_missing(self, configured_vault):
        result = vault.append_engagement_section("Nonexistent", section_heading="Debrief", section_body="content")
        assert result is None

    def test_appends_to_existing_engagement(self, configured_vault):
        # Create an engagement first
        vault.write_engagement(
            "Acme - Web App Pentest (2026-05-09)",
            client="Acme",
            engagement_type="web_app_pentest",
            body="# Initial body",
        )
        # Append a debrief section
        result = vault.append_engagement_section(
            "Acme - Web App Pentest (2026-05-09)",
            section_heading="Debrief",
            section_body="Engagement complete. Findings documented.",
        )
        assert result is not None
        content = result.read_text(encoding="utf-8")
        assert "# Initial body" in content
        assert "## Debrief" in content
        assert "Engagement complete" in content
        assert "_Updated " in content


# ── append_log_entry ────────────────────────────────────────────────────────────────────────


class TestAppendLogEntry:
    def test_returns_false_when_vault_unconfigured(self, fake_home):
        assert vault.append_log_entry("test", "desc") is False

    def test_returns_false_when_log_missing(self, fake_home):
        # Vault dir + _CLAUDE.md but no log.md
        vault_dir = fake_home / ".rick_mcp" / "vault"
        vault_dir.mkdir(parents=True)
        (vault_dir / "_CLAUDE.md").write_text("stub")
        assert vault.append_log_entry("test", "desc") is False

    def test_appends_to_existing_log(self, configured_vault):
        result = vault.append_log_entry("engagement", "Acme proposal created")
        assert result is True
        content = (configured_vault / "log.md").read_text(encoding="utf-8")
        assert "engagement | Acme proposal created" in content


# ── list_engagements / read_template / status ───────────────────────────────────────────────


class TestListEngagements:
    def test_empty_when_unconfigured(self, fake_home):
        assert vault.list_engagements() == []

    def test_empty_when_no_engagements(self, configured_vault):
        assert vault.list_engagements() == []

    def test_lists_md_files(self, configured_vault):
        (configured_vault / "Engagements" / "Eng A.md").write_text("a")
        (configured_vault / "Engagements" / "Eng B.md").write_text("b")
        # Non-md should be excluded
        (configured_vault / "Engagements" / "ignore.txt").write_text("x")
        result = vault.list_engagements()
        names = [p.name for p in result]
        assert "Eng A.md" in names
        assert "Eng B.md" in names
        assert "ignore.txt" not in names


class TestReadTemplate:
    def test_returns_none_when_unconfigured(self, fake_home):
        assert vault.read_template("Engagement") is None

    def test_returns_none_when_template_missing(self, configured_vault):
        assert vault.read_template("Nonexistent") is None

    def test_reads_template(self, configured_vault):
        (configured_vault / "Templates" / "Engagement.md").write_text("# Engagement Template", encoding="utf-8")
        result = vault.read_template("Engagement")
        assert result == "# Engagement Template"


class TestStatus:
    def test_unconfigured(self, fake_home):
        s = vault.status()
        assert s["configured"] is False
        assert s["engagements_count"] == 0
        assert s["templates_present"] == []

    def test_configured_no_engagements(self, configured_vault):
        s = vault.status()
        assert s["configured"] is True
        assert s["engagements_count"] == 0
        assert s["identity_layer_present"] is True

    def test_configured_with_engagements_and_templates(self, configured_vault):
        (configured_vault / "Engagements" / "A.md").write_text("a")
        (configured_vault / "Engagements" / "B.md").write_text("b")
        (configured_vault / "Templates" / "Engagement.md").write_text("t")
        s = vault.status()
        assert s["engagements_count"] == 2
        assert "Engagement" in s["templates_present"]


# ── relative_path ───────────────────────────────────────────────────────────────────────────


class TestRelativePath:
    def test_returns_relative_when_inside_vault(self, configured_vault):
        p = configured_vault / "Engagements" / "test.md"
        result = vault.relative_path(p)
        assert result == "Engagements/test.md"

    def test_returns_absolute_when_outside_vault(self, configured_vault, tmp_path):
        outside = tmp_path / "elsewhere.md"
        result = vault.relative_path(outside)
        assert result == str(outside)


# ── vault:// MCP resources ──────────────────────────────────────────────────────────────────


class TestVaultResources:
    @pytest.mark.asyncio
    async def test_manual_returns_stub_when_unconfigured(self, fake_home):
        from rick_mcp.resources.vault import res_vault_manual

        result = await res_vault_manual()
        assert "not configured" in result.lower() or "not available" in result.lower()

    @pytest.mark.asyncio
    async def test_manual_reads_claude_md(self, configured_vault):
        from rick_mcp.resources.vault import res_vault_manual

        (configured_vault / "_CLAUDE.md").write_text("# Test Manual\n\nContent.\n", encoding="utf-8")
        result = await res_vault_manual()
        assert "Test Manual" in result

    @pytest.mark.asyncio
    async def test_index_reads_index_md(self, configured_vault):
        from rick_mcp.resources.vault import res_vault_index

        (configured_vault / "index.md").write_text("# Index\n", encoding="utf-8")
        result = await res_vault_index()
        assert "Index" in result

    @pytest.mark.asyncio
    async def test_log_reads_log_md(self, configured_vault):
        from rick_mcp.resources.vault import res_vault_log

        result = await res_vault_log()
        # configured_vault fixture seeds log.md with bootstrap entry
        assert "Activity Log" in result

    @pytest.mark.asyncio
    async def test_identity_tom_returns_stub_when_missing(self, configured_vault):
        from rick_mcp.resources.vault import res_vault_identity_tom

        result = await res_vault_identity_tom()
        assert "not found" in result.lower()

    @pytest.mark.asyncio
    async def test_identity_tom_reads_when_present(self, configured_vault):
        from rick_mcp.resources.vault import res_vault_identity_tom

        (configured_vault / "Identity" / "Tom.md").write_text("# Tom hub\n", encoding="utf-8")
        result = await res_vault_identity_tom()
        assert "Tom hub" in result

    @pytest.mark.asyncio
    async def test_engagements_lists_when_present(self, configured_vault):
        import json as _json

        from rick_mcp.resources.vault import res_vault_engagements

        (configured_vault / "Engagements" / "Eng A.md").write_text("a", encoding="utf-8")
        (configured_vault / "Engagements" / "Eng B.md").write_text("b", encoding="utf-8")
        result = await res_vault_engagements()
        parsed = _json.loads(result)
        assert parsed["total"] == 2
        codenames = [e["codename"] for e in parsed["engagements"]]
        assert "Eng A" in codenames
        assert "Eng B" in codenames

    @pytest.mark.asyncio
    async def test_engagements_empty_message_when_none(self, configured_vault):
        from rick_mcp.resources.vault import res_vault_engagements

        result = await res_vault_engagements()
        assert "No engagement notes" in result

    @pytest.mark.asyncio
    async def test_engagements_unconfigured(self, fake_home):
        from rick_mcp.resources.vault import res_vault_engagements

        result = await res_vault_engagements()
        assert "not available" in result.lower() or "not configured" in result.lower()

    @pytest.mark.asyncio
    async def test_status_returns_json(self, configured_vault):
        import json as _json

        from rick_mcp.resources.vault import res_vault_status

        result = await res_vault_status()
        parsed = _json.loads(result)
        assert parsed["configured"] is True
        assert "engagements_count" in parsed

    @pytest.mark.asyncio
    async def test_template_engagement_when_present(self, configured_vault):
        from rick_mcp.resources.vault import res_vault_template_engagement

        (configured_vault / "Templates" / "Engagement.md").write_text("# Engagement Template\n", encoding="utf-8")
        result = await res_vault_template_engagement()
        assert "Engagement Template" in result

    @pytest.mark.asyncio
    async def test_engagement_detail_returns_stub_when_unconfigured(self, fake_home):
        from rick_mcp.resources.vault import res_vault_engagement_detail

        result = await res_vault_engagement_detail("Anything")
        assert "not available" in result.lower() or "not configured" in result.lower()

    @pytest.mark.asyncio
    async def test_engagement_detail_returns_not_found_for_missing_codename(self, configured_vault):
        from rick_mcp.resources.vault import res_vault_engagement_detail

        result = await res_vault_engagement_detail("Nonexistent Engagement")
        assert "not found" in result.lower()

    @pytest.mark.asyncio
    async def test_engagement_detail_reads_proposal_shape(self, configured_vault):
        from rick_mcp.resources.vault import res_vault_engagement_detail

        codename = "HTB - MonitorsFour (2026-05-09)"
        body = "# HTB MonitorsFour\n\nProposal-shape content.\n"
        (configured_vault / "Engagements" / f"{codename}.md").write_text(body, encoding="utf-8")
        result = await res_vault_engagement_detail(codename)
        assert "Proposal-shape content." in result

    @pytest.mark.asyncio
    async def test_engagement_detail_reads_tracker_shape(self, configured_vault):
        from rick_mcp.resources.vault import res_vault_engagement_detail

        codename = "ENG-20260513-143022"
        body = "# Tracker engagement\n\nFindings table here.\n"
        (configured_vault / "Engagements" / f"{codename}.md").write_text(body, encoding="utf-8")
        result = await res_vault_engagement_detail(codename)
        assert "Findings table here." in result

    @pytest.mark.asyncio
    async def test_engagement_detail_not_found_hint_lists_available(self, configured_vault):
        from rick_mcp.resources.vault import res_vault_engagement_detail

        existing = "Test Corp - Web App Pentest (2026-05-09)"
        (configured_vault / "Engagements" / f"{existing}.md").write_text("x", encoding="utf-8")
        result = await res_vault_engagement_detail("Bogus Name")
        assert "not found" in result.lower()
        assert existing in result

    @pytest.mark.asyncio
    async def test_engagement_detail_decodes_percent_encoded_codename(self, configured_vault):
        from rick_mcp.resources.vault import res_vault_engagement_detail

        codename = "HTB - MonitorsFour (2026-05-09)"
        body = "# HTB MonitorsFour\n\nDecoded content.\n"
        (configured_vault / "Engagements" / f"{codename}.md").write_text(body, encoding="utf-8")
        # FastMCP passes the URI path param percent-encoded
        encoded = "HTB%20-%20MonitorsFour%20(2026-05-09)"
        result = await res_vault_engagement_detail(encoded)
        assert "Decoded content." in result

    @pytest.mark.asyncio
    async def test_engagement_detail_path_traversal_rejected(self, configured_vault):
        from rick_mcp.resources.vault import res_vault_engagement_detail

        # Write a secret file outside the engagements dir
        (configured_vault / "_CLAUDE.md").write_text("SECRET MANUAL CONTENT", encoding="utf-8")
        # Slashes are stripped by codename_to_filename; even if a future change allowed them,
        # the containment check guards. Attempt encoded slashes that decode to a traversal.
        result = await res_vault_engagement_detail("..%2F..%2F_CLAUDE")
        assert "SECRET MANUAL CONTENT" not in result
        # Resolves to a sanitized filename inside Engagements/, so "not found" is the expected outcome
        assert "not found" in result.lower() or "invalid codename" in result.lower()

    @pytest.mark.asyncio
    async def test_engagement_detail_symlink_escape_rejected(self, configured_vault, tmp_path):
        from rick_mcp.resources.vault import res_vault_engagement_detail

        # Create a secret file outside the engagements dir, then symlink into Engagements/
        secret = tmp_path / "outside_secret.md"
        secret.write_text("OUTSIDE SECRET", encoding="utf-8")
        link = configured_vault / "Engagements" / "escape.md"
        link.symlink_to(secret)
        result = await res_vault_engagement_detail("escape")
        assert "OUTSIDE SECRET" not in result
        assert "invalid codename" in result.lower()
