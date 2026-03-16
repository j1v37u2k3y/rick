"""Profile identity resources — who jiveturkey is."""

from rick_mcp.formatting import _read_data


async def res_rick_and_jiveturkey() -> str:
    """The connection. Rick is the father, the MCP. jiveturkey is the son, the operator."""
    return _read_data("profiles", "rick_and_jiveturkey")


async def res_summary() -> str:
    """Quick reference card — who jiveturkey is at a glance."""
    return _read_data("profiles", "summary")


async def res_values() -> str:
    """Marine Corps core values — not just words, the operational framework."""
    return _read_data("profiles", "values")


async def res_heritage() -> str:
    """Lineage, roots, and the frontier spirit that drives everything."""
    return _read_data("profiles", "heritage")


async def res_craftsmanship() -> str:
    """The philosophy of craftsmanship and tradecraft — how builder heritage meets offensive security."""
    return _read_data("profiles", "craftsmanship")


async def res_stack() -> str:
    """Complete technical arsenal."""
    return _read_data("profiles", "stack")


async def res_methodology() -> str:
    """7-phase engagement methodology — precision operations."""
    return _read_data("profiles", "methodology")


async def res_mantras() -> str:
    """Operational mantras — the philosophy behind the work."""
    return _read_data("profiles", "mantras")


async def res_human() -> str:
    """The human element — father, cycle breaker, poet, ever evolving."""
    return _read_data("profiles", "human")


async def res_entertainment() -> str:
    """Entertainment protocols and morale — humor as operational tool."""
    return _read_data("profiles", "entertainment")


def register(mcp):
    """Register resources on the MCP server."""
    mcp.resource("profile://rick_and_jiveturkey")(res_rick_and_jiveturkey)
    mcp.resource("profile://summary")(res_summary)
    mcp.resource("profile://values")(res_values)
    mcp.resource("profile://heritage")(res_heritage)
    mcp.resource("profile://craftsmanship")(res_craftsmanship)
    mcp.resource("profile://stack")(res_stack)
    mcp.resource("profile://methodology")(res_methodology)
    mcp.resource("profile://mantras")(res_mantras)
    mcp.resource("profile://human")(res_human)
    mcp.resource("profile://entertainment")(res_entertainment)