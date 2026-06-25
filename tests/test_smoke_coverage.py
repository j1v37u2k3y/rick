"""Regression guard: every registered tool must be wired into smoke_test.py.

`smoke_test.py` is the `make setup` auto-verify step (the "verified rick loads" check).
A tool that is registered but never fired — and not an explicit network skip — would
silently erode that claim as the surface grows. This test reads `smoke_test.py` as source
text (importing it would trigger its HOME redirect) and asserts every registered tool name
appears in it, either fired or listed in the documented `SKIPPED` dict.
"""

import re
from pathlib import Path

from rick_mcp.server import mcp

_SMOKE = Path(__file__).resolve().parent.parent / "smoke_test.py"


def test_every_registered_tool_is_wired_into_smoke():
    src = _SMOKE.read_text(encoding="utf-8")
    registered = sorted(t.name for t in mcp._tool_manager.list_tools())
    missing = [name for name in registered if not re.search(rf"\b{re.escape(name)}\b", src)]
    assert not missing, (
        f"{len(missing)} registered tool(s) absent from smoke_test.py — fire them in the "
        f"tools list or add them to the SKIPPED dict: {missing}"
    )
