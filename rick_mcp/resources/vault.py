"""Vault MCP resources — vault:// URIs that expose the operator's Obsidian Second Brain.

Exposes identity stubs, engagement notes, the operating manual (_CLAUDE.md), the index,
and the activity log via MCP resource URIs. Resources degrade gracefully when the vault
is not configured (returns a stub message). All resources are async and read-only.

URIs:
- vault://manual               → vault/_CLAUDE.md
- vault://index                → vault/index.md
- vault://log                  → vault/log.md
- vault://identity/hub         → vault/Identity/<NAME>.md (operator identity hub; falls back to Identity/Operator.md)
- vault://identity/methodology → vault/Identity/Methodology.md
- vault://identity/values      → vault/Identity/Values.md
- vault://identity/soul        → vault/Identity/Soul.md
- vault://identity/rick        → vault/Identity/Rick.md
- vault://engagements          → list of all engagement notes (codename + path)
- vault://engagements/{codename} → vault/Engagements/<codename>.md (single engagement, filesystem-resolved)
- vault://templates/engagement → vault/Templates/Engagement.md
- vault://status               → vault status (JSON-formatted)
"""

import json
from urllib.parse import unquote

from rick_mcp import vault


def _read_or_stub(relative_path: str, label: str) -> str:
    """Read a vault file by relative path, or return a stub message if vault unconfigured / missing."""
    if not vault._is_configured():
        return (
            f"[{label}] not available — the operator's vault at `~/.rick_mcp/vault/` is not configured. "
            f"Bootstrap it via the obsidian-second-brain skill: "
            f"`python ~/.claude/skills/obsidian-second-brain/scripts/bootstrap_vault.py "
            f"--path ~/.rick_mcp/vault --name '<your name>'`"
        )
    target = vault._vault_path() / relative_path
    if not target.exists():
        return f"[{label}] not found at `{relative_path}` in the vault."
    return target.read_text(encoding="utf-8")


async def res_vault_manual() -> str:
    """The vault's _CLAUDE.md operating manual — folder map, AI-first rules, frontmatter schemas."""
    return _read_or_stub("_CLAUDE.md", "vault://manual")


async def res_vault_index() -> str:
    """The vault's index.md — full catalog of all notes by folder."""
    return _read_or_stub("index.md", "vault://index")


async def res_vault_log() -> str:
    """The vault's log.md — chronological activity log of structural changes, ingests, saves."""
    return _read_or_stub("log.md", "vault://log")


async def res_vault_identity_hub() -> str:
    """Operator identity hub — aggregates soul, profiles, certs, tools, specializations, values.

    Resolves the filename dynamically from the operator's display name in `identity.yaml`
    (e.g. NAME="Alex Chen" → `Identity/Alex Chen.md`). Falls back to the generic `Identity/Operator.md`
    that ships in `soul-example/vault/` so forkers get a resolvable resource out of the box
    before they personalize their hub.
    """
    from rick_mcp.identity import NAME

    if not vault._is_configured():
        return (
            "[vault://identity/hub] not available — the operator's vault at `~/.rick_mcp/vault/` "
            "is not configured. Bootstrap it via the obsidian-second-brain skill: "
            "`python ~/.claude/skills/obsidian-second-brain/scripts/bootstrap_vault.py "
            "--path ~/.rick_mcp/vault --name '<your name>'`"
        )
    vault_root = vault._vault_path()
    primary = vault_root / f"Identity/{NAME}.md"
    if primary.exists():
        return primary.read_text(encoding="utf-8")
    fallback = vault_root / "Identity/Operator.md"
    if fallback.exists():
        return fallback.read_text(encoding="utf-8")
    return (
        f"[vault://identity/hub] not found at `Identity/{NAME}.md` or `Identity/Operator.md`. "
        "Create the identity hub at one of those paths."
    )


async def res_vault_identity_methodology() -> str:
    """Bridge stub for Rick's 7-phase methodology — points to ~/.rick_mcp/profiles/methodology.md."""
    return _read_or_stub("Identity/Methodology.md", "vault://identity/methodology")


async def res_vault_identity_values() -> str:
    """Bridge stub for the four core values (Honor, Courage, Commitment, Honesty)."""
    return _read_or_stub("Identity/Values.md", "vault://identity/values")


async def res_vault_identity_soul() -> str:
    """Bridge stub for the soul — points to ~/.rick_mcp/soul/SOUL.md."""
    return _read_or_stub("Identity/Soul.md", "vault://identity/soul")


async def res_vault_identity_rick() -> str:
    """Bridge stub for the Rick / j1v37u2k3y father-son frame."""
    return _read_or_stub("Identity/Rick.md", "vault://identity/rick")


async def res_vault_engagements() -> str:
    """List of all engagement notes in vault/Engagements/ — codename + relative path + size."""
    if not vault._is_configured():
        return "[vault://engagements] not available — vault not configured. Bootstrap via obsidian-second-brain skill."
    items = []
    for path in vault.list_engagements():
        items.append(
            {
                "codename": path.stem,
                "path": vault.relative_path(path),
                "size_bytes": path.stat().st_size,
            }
        )
    if not items:
        return (
            "No engagement notes yet. Use `rick_engagement_proposal` or `rick_tracker(action='create')` to create one."
        )
    return json.dumps({"engagements": items, "total": len(items)}, indent=2)


async def res_vault_engagement_detail(codename: str) -> str:
    """Read a single engagement note by codename (filesystem-resolved).

    Codename is the file stem in vault/Engagements/ — e.g.
    "HTB - MonitorsFour (2026-05-09)" → vault/Engagements/HTB - MonitorsFour (2026-05-09).md.
    FastMCP passes URI path params percent-encoded; the handler decodes before resolving.

    Mirrors the list resource (`vault://engagements`): filesystem is canonical for the vault
    projection layer. Works for both proposal-shape notes (created by `rick_engagement_proposal`)
    and tracker-shape notes (created by `rick_tracker create`, named by ENG-ID).

    Defense-in-depth: the resolved target must remain inside `vault/Engagements/`. Slashes are
    stripped by `codename_to_filename`, but the resolved path is verified to be inside the
    engagements dir before any filesystem read — guards against future filter changes and
    against symlinks inside the dir pointing outside the vault.
    """
    if not vault._is_configured():
        return (
            f"[vault://engagements/{codename}] not available — the operator's vault at "
            "`~/.rick_mcp/vault/` is not configured. Bootstrap it via the obsidian-second-brain skill."
        )
    decoded = unquote(codename)
    safe = vault.codename_to_filename(decoded)
    eng_dir = vault._engagements_dir()
    target = eng_dir / f"{safe}.md"
    try:
        resolved = target.resolve(strict=False)
        resolved.relative_to(eng_dir.resolve(strict=False))
    except ValueError:
        return f"[vault://engagements/{codename}] invalid codename — resolves outside the engagements directory."
    if not target.exists():
        available = [p.stem for p in vault.list_engagements()]
        hint = f" Available codenames: {', '.join(available)}." if available else " No engagement notes exist yet."
        return f"[vault://engagements/{codename}] not found at `Engagements/{safe}.md`.{hint}"
    return target.read_text(encoding="utf-8")


async def res_vault_template_engagement() -> str:
    """The Engagement template (Templater-based) — wired to Rick's 7-phase methodology."""
    return _read_or_stub("Templates/Engagement.md", "vault://templates/engagement")


async def res_vault_status() -> str:
    """Vault status — configured, path, engagement count, templates present, identity layer presence."""
    return json.dumps(vault.status(), indent=2)


def register(mcp):
    """Register vault:// resources on the MCP server."""
    mcp.resource("vault://manual")(res_vault_manual)
    mcp.resource("vault://index")(res_vault_index)
    mcp.resource("vault://log")(res_vault_log)
    mcp.resource("vault://identity/hub")(res_vault_identity_hub)
    mcp.resource("vault://identity/methodology")(res_vault_identity_methodology)
    mcp.resource("vault://identity/values")(res_vault_identity_values)
    mcp.resource("vault://identity/soul")(res_vault_identity_soul)
    mcp.resource("vault://identity/rick")(res_vault_identity_rick)
    mcp.resource("vault://engagements")(res_vault_engagements)
    mcp.resource("vault://engagements/{codename}")(res_vault_engagement_detail)
    mcp.resource("vault://templates/engagement")(res_vault_template_engagement)
    mcp.resource("vault://status")(res_vault_status)
