"""Test session configuration.

Adds an autouse fixture that isolates ~/.rick_mcp by patching pathlib.Path.home() to a
fresh tmp_path for every test. This prevents tools that write to ~/.rick_mcp/{vault,
engagements,dick} from polluting the operator's real home during tests.

Tests that explicitly patch Path.home themselves (e.g. tracker_dir fixtures) will re-patch
within their own scope, layering on top of this baseline. Tests that need access to the
operator's real home for some reason should use the `real_home` fixture (not provided here
because nothing in the suite needs it currently).
"""

from unittest.mock import patch

import pytest


@pytest.fixture(autouse=True)
def _isolate_rick_mcp_home(tmp_path, monkeypatch):
    """Auto-patch pathlib.Path.home to tmp_path for every test.

    Effect: every reference to Path.home() during a test resolves under tmp_path, so:
    - ~/.rick_mcp/vault/ is absent unless the test bootstraps it
    - ~/.rick_mcp/engagements/ is absent unless the test creates it
    - ~/.rick_mcp/dick/ (jarvis state) is absent unless the test seeds it

    Tests that need a configured vault should bootstrap it under tmp_path themselves
    (see test_vault.configured_vault fixture for the pattern).
    """
    with patch("pathlib.Path.home", return_value=tmp_path):
        yield tmp_path
