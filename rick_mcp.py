"""
RICK MCP SERVER — SEMPER FIDELIS

Thin wrapper. The real code lives in the rick_mcp/ package.
This file exists so `python rick_mcp.py` still works.

Check the clock. What makes it tick. Re-read that.
"""

from rick_mcp.server import _build_banner, mcp  # noqa: F401

if __name__ == "__main__":
    print(_build_banner())
    mcp.run()
