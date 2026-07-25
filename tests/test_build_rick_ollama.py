"""Tests for scripts/build_rick_ollama.py + rick_mcp.prompts.build_ollama_system().

The persona builder is single-source (soul + identity → one lean local-model system prompt);
the script renders it and pushes to an Ollama host via /api/create. Network is never touched:
post_create's urlopen is mocked, and main()'s push path patches post_create itself.
"""

import importlib.util
import json
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from rick_mcp import prompts

# scripts/ isn't an importable package — load the module by path (it's side-effect-free on
# import; main() is guarded by __name__ == "__main__").
_PATH = Path(__file__).resolve().parent.parent / "scripts" / "build_rick_ollama.py"
_spec = importlib.util.spec_from_file_location("build_rick_ollama", _PATH)
bro = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(bro)


class TestBuildOllamaSystem:
    def test_configured_persona_structure(self, monkeypatch):
        monkeypatch.setattr(prompts, "_read_soul", lambda: "# The Soul\nDo no harm.\n\n## Vault projections\n- [[x]]")
        out = prompts.build_ollama_system()
        for header in ("## Who", "## The Soul", "## How you work", "## Tool use", "## Voice"):
            assert header in out
        assert "Do no harm." in out
        # the vault-projections tail (wikilinks) must be trimmed out
        assert "## Vault projections" not in out
        assert "[[x]]" not in out

    def test_generic_persona_has_no_configured_identity(self, monkeypatch):
        monkeypatch.setattr(prompts, "is_configured", lambda: False)
        monkeypatch.setattr(prompts, "_read_soul", lambda: "Honor. Courage. Commitment.")
        out = prompts.build_ollama_system()
        assert "the operator" in out
        assert "Honor. Courage. Commitment." in out
        assert "A security professional" in out  # generic bio, not a real name

    def test_trim_soul_without_marker_is_identity(self):
        assert prompts._trim_soul("soul body, no projections") == "soul body, no projections"

    def test_bio_generic_branch(self, monkeypatch):
        monkeypatch.setattr(prompts, "is_configured", lambda: False)
        assert prompts._ollama_bio().startswith("A security professional")


class TestCreateRequest:
    def test_default_body_shape(self):
        body = bro.create_request("SYS", "rick", "rick")
        assert body["model"] == "rick"
        assert body["from"] == "rick"
        assert body["system"] == "SYS"
        assert body["parameters"]["num_ctx"] == 16384
        assert body["stream"] is False

    def test_custom_params_override(self):
        body = bro.create_request("S", "base", "m", params={"temperature": 0.1})
        assert body["parameters"] == {"temperature": 0.1}


class TestPostCreate:
    @staticmethod
    def _fake_urlopen(lines):
        resp = MagicMock()
        resp.read.return_value = "\n".join(lines).encode()
        cm = MagicMock()
        cm.__enter__.return_value = resp
        cm.__exit__.return_value = False
        return cm

    def test_success_returns_status_messages(self):
        cm = self._fake_urlopen(['{"status":"reading"}', '{"status":"success"}'])
        with patch.object(bro.urllib.request, "urlopen", return_value=cm):
            msgs = bro.post_create("http://box:11434", {"model": "rick"})
        assert msgs[-1]["status"] == "success"

    def test_error_line_raises(self):
        cm = self._fake_urlopen(['{"error":"no such model: bogus"}'])
        with patch.object(bro.urllib.request, "urlopen", return_value=cm):
            with pytest.raises(RuntimeError, match="no such model"):
                bro.post_create("http://box", {})

    def test_blank_and_nonjson_lines_are_skipped(self):
        cm = self._fake_urlopen(["", "  ", "not json", '{"status":"ok"}'])
        with patch.object(bro.urllib.request, "urlopen", return_value=cm):
            msgs = bro.post_create("http://box", {})
        assert len(msgs) == 1 and msgs[0]["status"] == "ok"


class TestMain:
    def test_print_emits_persona(self, capsys, monkeypatch):
        monkeypatch.setattr(prompts, "_read_soul", lambda: "SOUL STUB")
        rc = bro.main(["--print"])
        out = capsys.readouterr().out
        assert rc == 0
        assert "## Voice" in out
        assert "SOUL STUB" in out

    def test_dry_run_elides_system(self, capsys):
        rc = bro.main(["--dry-run"])
        data = json.loads(capsys.readouterr().out)
        assert rc == 0
        assert data["model"] == "rick"
        assert data["system"].endswith("chars>")  # persona elided, not leaked

    def test_push_success_returns_zero(self, monkeypatch):
        monkeypatch.setattr(bro, "post_create", lambda host, body: [])
        assert bro.main(["--host", "http://h:11434", "--model-name", "rick"]) == 0

    def test_push_failure_returns_one(self, monkeypatch):
        def boom(host, body):
            raise bro.urllib.error.URLError("connection refused")

        monkeypatch.setattr(bro, "post_create", boom)
        assert bro.main([]) == 1
