"""Document resources — markdown files and guides."""

from pathlib import Path

from rick_mcp.formatting import _read_data, _read_md


async def res_wwm() -> str:
    """Complete Working With Me guide — how to engage, what to expect, what I need."""
    return _read_md("WORKING_WITH_ME.md")


async def res_the_book() -> str:
    """The book — operator's memoirs. Raw, unfiltered voice."""
    # Private first, project root second
    soul_dir = Path.home() / ".rick_mcp" / "soul"
    for search_path in [soul_dir / "my book.txt", Path(__file__).parent.parent / "my book.txt"]:
        if search_path.exists():
            return search_path.read_text(encoding="utf-8")
    return "The book is not here right now. But the words will never stop, ever."


async def res_soul() -> str:
    """The soul. Core principles and values. No harm. Honor. Courage. Commitment. Honesty above all."""
    # Private first, project root second
    soul_dir = Path.home() / ".rick_mcp" / "soul"
    soul_path = soul_dir / "SOUL.md"
    if soul_path.exists():
        return soul_path.read_text(encoding="utf-8")
    return _read_md("SOUL.md")


async def res_profile() -> str:
    """Current state, what's on the horizon, key learnings, tools and resources."""
    # Private first, project root second
    soul_dir = Path.home() / ".rick_mcp" / "soul"
    private_path = soul_dir / "PROFILE.md"
    if private_path.exists():
        return private_path.read_text(encoding="utf-8")
    return "Profile is not available in this environment."


async def res_achievements() -> str:
    """The full build log. What was built, how, and the numbers."""
    return _read_md("ACHIEVEMENTS.md")


async def res_contributing() -> str:
    """How to contribute. Dev workflow, code standards, adding tools and resources."""
    return _read_md("CONTRIBUTING.md")


async def res_changelog() -> str:
    """Version history. What changed and when."""
    return _read_md("CHANGELOG.md")


async def res_security() -> str:
    """Security policy. Responsible disclosure. How to report vulnerabilities."""
    return _read_md("SECURITY.md")


async def res_war_stories() -> str:
    """Anonymized engagement narratives — the stories from the field."""
    return _read_data("docs", "war_stories")


def register(mcp):
    """Register resources on the MCP server."""
    mcp.resource("doc://working-with-me")(res_wwm)
    mcp.resource("doc://the-book")(res_the_book)
    mcp.resource("doc://soul")(res_soul)
    mcp.resource("doc://profile")(res_profile)
    mcp.resource("doc://achievements")(res_achievements)
    mcp.resource("doc://contributing")(res_contributing)
    mcp.resource("doc://changelog")(res_changelog)
    mcp.resource("doc://security")(res_security)
    mcp.resource("doc://war-stories")(res_war_stories)
