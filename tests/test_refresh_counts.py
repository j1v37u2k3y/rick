"""Tests for scripts/refresh_counts.py — the count-sync tooling.

This script is the single source of truth that keeps tool/resource/skill/test counts (and the
test + coverage-floor badges) synced across README, SKILLS.md, and the soul-example resume
files — and CI's `refresh_counts.py --check` gate enforces it. `count_tests()` and `main()` are
exercised via mocks (subprocess + patched TARGETS/ROOT), so the suite never shells out to a
nested pytest or rewrites the real files.
"""

import importlib.util
import sys
from pathlib import Path
from unittest.mock import patch

import pytest

from __version__ import __version__

# Load scripts/refresh_counts.py by path — `scripts/` isn't an importable package, and the
# module is side-effect-free on import (main() is guarded by __name__ == "__main__").
_RC_PATH = Path(__file__).resolve().parent.parent / "scripts" / "refresh_counts.py"
_spec = importlib.util.spec_from_file_location("refresh_counts", _RC_PATH)
rc = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(rc)


class TestVersionHelpers:
    def test_read_version_matches_source(self):
        assert rc.read_version() == __version__

    def test_short_version_drops_patch(self):
        assert rc.short_version("3.14.1") == "v3.14"
        assert rc.short_version("1.0.0") == "v1.0"
        assert rc.short_version("10.20.30") == "v10.20"


class TestReplaceTags:
    def test_rewrites_tagged_region(self):
        text = "lead <!-- counts:tools -->0<!-- /counts:tools --> trail"
        out = rc.replace_tags(text, {"tools": "48"})
        assert "<!-- counts:tools -->48<!-- /counts:tools -->" in out
        assert "lead" in out and "trail" in out

    def test_leaves_untagged_text_untouched(self):
        assert rc.replace_tags("no tags here", {"tools": "48"}) == "no tags here"

    def test_rewrites_multiple_keys_independently(self):
        text = "<!-- counts:tools -->0<!-- /counts:tools --> / <!-- counts:tests -->0<!-- /counts:tests -->"
        out = rc.replace_tags(text, {"tools": "48", "tests": "873"})
        assert "counts:tools -->48<" in out
        assert "counts:tests -->873<" in out

    def test_unknown_key_is_noop(self):
        text = "<!-- counts:tools -->5<!-- /counts:tools -->"
        # A key with no matching tag in the text leaves it unchanged.
        assert rc.replace_tags(text, {"resources": "36"}) == text


class TestReplaceBadges:
    def test_rewrites_test_badge_number(self):
        out = rc.replace_badges("badge tests-1%20passed end", {"tests": "873"})
        assert "tests-873%20passed" in out

    def test_noop_when_key_absent(self):
        text = "tests-1%20passed"
        assert rc.replace_badges(text, {}) == text

    def test_noop_when_no_badge_present(self):
        assert rc.replace_badges("no badge here", {"tests": "873"}) == "no badge here"


class TestCounters:
    def test_count_registered_counts_and_skips_init(self, tmp_path):
        (tmp_path / "a.py").write_text("mcp.tool(\nmcp.tool(\n", encoding="utf-8")
        (tmp_path / "b.py").write_text("mcp.tool(\n", encoding="utf-8")
        (tmp_path / "__init__.py").write_text("mcp.tool(\n", encoding="utf-8")  # must be skipped
        assert rc.count_registered(tmp_path, "tool") == 3

    def test_count_registered_kind_specific(self, tmp_path):
        (tmp_path / "r.py").write_text("mcp.resource(\nmcp.tool(\n", encoding="utf-8")
        assert rc.count_registered(tmp_path, "resource") == 1
        assert rc.count_registered(tmp_path, "tool") == 1

    def test_count_skills_is_positive_int(self):
        n = rc.count_skills()
        assert isinstance(n, int) and n > 0


class TestComputeCounts:
    def test_skip_tests_omits_tests_key(self):
        counts = rc.compute_counts(skip_tests=True)
        assert {"version", "version-full", "tools", "resources", "skills"} <= set(counts)
        assert "tests" not in counts  # skipped → not computed

    def test_values_are_well_formed(self):
        counts = rc.compute_counts(skip_tests=True, skip_coverage=True)
        assert counts["version"].startswith("v")
        assert counts["version-full"] == __version__
        assert counts["tools"].isdigit() and int(counts["tools"]) > 0
        assert counts["resources"].isdigit() and int(counts["resources"]) > 0


class TestCoverageBadge:
    # The coverage badge tracks the enforced floor ("coverage ≥N%"), not a point measurement —
    # a point % isn't reproducible across environments (CI Linux vs local macOS differ), so it
    # can't be CI-enforced. The floor is deterministic + repo-local, so it can.
    def test_replace_badges_syncs_coverage_floor(self):
        out = rc.replace_badges("img coverage-%E2%89%A51%25 end", {"coverage": "90"})
        assert "coverage-%E2%89%A590%25" in out

    def test_replace_badges_coverage_noop_when_key_absent(self):
        text = "coverage-%E2%89%A51%25"
        assert rc.replace_badges(text, {"tests": "5"}) == text

    def test_read_coverage_floor_matches_pyproject(self):
        import re as _re

        floor = rc.read_coverage_floor()
        assert floor is not None and floor.isdigit()
        text = (rc.ROOT / "pyproject.toml").read_text(encoding="utf-8")
        m = _re.search(r"^fail_under\s*=\s*(\d+)", text, _re.MULTILINE)
        assert m and floor == m.group(1)

    def test_read_coverage_floor_none_when_absent(self, tmp_path):
        (tmp_path / "pyproject.toml").write_text("[tool.foo]\nx = 1\n", encoding="utf-8")
        with patch.object(rc, "ROOT", tmp_path):
            assert rc.read_coverage_floor() is None

    def test_compute_counts_includes_coverage_floor(self):
        counts = rc.compute_counts(skip_tests=True)
        assert counts["coverage"] == rc.read_coverage_floor()

    def test_compute_counts_skip_coverage_omits_key(self):
        counts = rc.compute_counts(skip_tests=True, skip_coverage=True)
        assert "coverage" not in counts


class TestCountTests:
    def test_parses_collected_count(self):
        fake = type("R", (), {"returncode": 0, "stdout": "noise\n917 tests collected in 0.5s\n", "stderr": ""})()
        with patch.object(rc.subprocess, "run", return_value=fake):
            assert rc.count_tests() == 917

    def test_raises_on_nonzero_exit(self):
        fake = type("R", (), {"returncode": 1, "stdout": "", "stderr": "boom"})()
        with (
            patch.object(rc.subprocess, "run", return_value=fake),
            pytest.raises(RuntimeError, match="collection failed"),
        ):
            rc.count_tests()

    def test_raises_on_empty_output(self):
        fake = type("R", (), {"returncode": 0, "stdout": "   \n", "stderr": ""})()
        with patch.object(rc.subprocess, "run", return_value=fake), pytest.raises(RuntimeError, match="no output"):
            rc.count_tests()

    def test_raises_on_unparseable_summary(self):
        fake = type("R", (), {"returncode": 0, "stdout": "something unexpected\n", "stderr": ""})()
        with patch.object(rc.subprocess, "run", return_value=fake), pytest.raises(RuntimeError, match="unparseable"):
            rc.count_tests()


class TestMain:
    def _target(self, tmp_path, body):
        f = tmp_path / "doc.md"
        f.write_text(body, encoding="utf-8")
        return f

    def test_writes_when_drift(self, tmp_path, monkeypatch):
        target = self._target(tmp_path, "<!-- counts:tools -->0<!-- /counts:tools -->")
        monkeypatch.setattr(rc, "TARGETS", [target])
        monkeypatch.setattr(rc, "ROOT", tmp_path)
        monkeypatch.setattr(rc, "compute_counts", lambda **kw: {"tools": "48"})
        monkeypatch.setattr(sys, "argv", ["refresh_counts.py"])
        assert rc.main() == 0
        assert "48" in target.read_text(encoding="utf-8")

    def test_check_detects_drift_without_writing(self, tmp_path, monkeypatch):
        target = self._target(tmp_path, "<!-- counts:tools -->0<!-- /counts:tools -->")
        monkeypatch.setattr(rc, "TARGETS", [target])
        monkeypatch.setattr(rc, "ROOT", tmp_path)
        monkeypatch.setattr(rc, "compute_counts", lambda **kw: {"tools": "48"})
        monkeypatch.setattr(sys, "argv", ["refresh_counts.py", "--check"])
        assert rc.main() == 1  # drift → exit 1
        assert "-->0<!--" in target.read_text(encoding="utf-8")  # untouched in check mode

    def test_check_clean_when_synced(self, tmp_path, monkeypatch):
        target = self._target(tmp_path, "<!-- counts:tools -->48<!-- /counts:tools -->")
        monkeypatch.setattr(rc, "TARGETS", [target])
        monkeypatch.setattr(rc, "ROOT", tmp_path)
        monkeypatch.setattr(rc, "compute_counts", lambda **kw: {"tools": "48"})
        monkeypatch.setattr(sys, "argv", ["refresh_counts.py", "--check"])
        assert rc.main() == 0
