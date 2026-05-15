"""Structural tests for `.claude/skills/`.

These tests catch drift between the skill files, the catalog, and the MCP tool
registry. They do NOT validate Claude Code's natural-language matching, runtime
behavior, or LLM output — those are non-deterministic and out of scope.

What this suite covers:

- Every skill dir has a `SKILL.md`.
- Skill dir names are kebab-case.
- Frontmatter parses and has `name` + `description`; `name` matches the dir.
- Description contains the `/<skill-name>` trigger phrase.
- Required body sections are present (Prerequisites / Workflow / Acceptance).
- MCP tools referenced via `mcp__rick_mcp__<name>` map to real registered tools.
- Sibling skills referenced as `/<skill-name>` exist on disk.
- The `SKILLS.md` catalog lists every skill, and every catalog entry resolves.
- `SKILL_TEMPLATE.md` is at the skills root, not inside a subdirectory (which
  would make it a phantom skill).
"""

import re
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
SKILLS_DIR = ROOT / ".claude" / "skills"
SKILLS_CATALOG = SKILLS_DIR / "SKILLS.md"
SKILL_TEMPLATE = SKILLS_DIR / "SKILL_TEMPLATE.md"
TOOLS_DIR = ROOT / "rick_mcp" / "tools"

REQUIRED_SECTION_PREFIXES = [
    "## Prerequisites",
    "## Workflow",
    "## Acceptance criteria",
]


def _skill_dirs() -> list[Path]:
    """All subdirectories under .claude/skills/ — one per skill."""
    return sorted(p for p in SKILLS_DIR.iterdir() if p.is_dir())


def _parse_frontmatter(text: str) -> dict[str, str] | None:
    """Extract YAML frontmatter between leading `---` markers.

    Handles simple `key: value` lines and `key: >`-folded multi-line scalars.
    Returns None if no frontmatter block is found.
    """
    m = re.match(r"^---\s*\n(.*?)\n---\s*\n", text, re.DOTALL)
    if not m:
        return None
    body = m.group(1)
    result: dict[str, str] = {}
    current_key: str | None = None
    for line in body.splitlines():
        if not line.strip():
            continue
        kv = re.match(r"^([a-zA-Z_-]+):\s*(.*)$", line)
        if kv and not line.startswith((" ", "\t")):
            key, value = kv.group(1), kv.group(2)
            if value in (">", "|"):
                current_key = key
                result[key] = ""
            else:
                result[key] = value.strip()
                current_key = None
        elif current_key is not None:
            chunk = line.strip()
            result[current_key] = f"{result[current_key]} {chunk}".strip() if result[current_key] else chunk
    return result


def _registered_tool_names() -> set[str]:
    """Tool names registered via `mcp.tool(name="rick_X", ...)` across tools/*.py."""
    pattern = re.compile(r'mcp\.tool\(\s*name="([^"]+)"')
    names: set[str] = set()
    for py in TOOLS_DIR.glob("*.py"):
        if py.name == "__init__.py":
            continue
        names.update(pattern.findall(py.read_text(encoding="utf-8")))
    return names


def _referenced_mcp_tools(skill_text: str) -> set[str]:
    """Tool names referenced as `mcp__rick_mcp__<name>` in a SKILL.md body."""
    return set(re.findall(r"mcp__rick_mcp__([a-z_]+)", skill_text))


def _referenced_skills(skill_text: str) -> set[str]:
    """Sibling skill refs in the form `/<kebab-name>`.

    Excludes underscore-form names (server-side persona prompts like `/be_rick`).
    """
    refs: set[str] = set()
    for m in re.finditer(r"`/([a-z][a-z0-9-]*)`", skill_text):
        name = m.group(1)
        if "_" in name:
            continue
        refs.add(name)
    return refs


# ---------- Tests ----------


def test_skills_dir_exists():
    assert SKILLS_DIR.is_dir(), f"{SKILLS_DIR} not found"


def test_skill_template_at_root_not_inside_subdir():
    """SKILL_TEMPLATE.md lives at the catalog root; placing it inside a subdir
    would register it as a phantom skill on Claude Code load."""
    assert SKILL_TEMPLATE.exists(), "SKILL_TEMPLATE.md missing from .claude/skills/"
    skill_names = {d.name for d in _skill_dirs()}
    assert "SKILL_TEMPLATE" not in skill_names
    assert "skill-template" not in skill_names


@pytest.mark.parametrize("skill_dir", _skill_dirs(), ids=lambda p: p.name)
def test_skill_has_skill_md(skill_dir: Path):
    assert (skill_dir / "SKILL.md").exists(), f"{skill_dir.name} missing SKILL.md"


@pytest.mark.parametrize("skill_dir", _skill_dirs(), ids=lambda p: p.name)
def test_skill_dir_is_kebab_case(skill_dir: Path):
    assert "_" not in skill_dir.name, f"{skill_dir.name} uses snake_case; project convention is kebab-case"


@pytest.mark.parametrize("skill_dir", _skill_dirs(), ids=lambda p: p.name)
def test_frontmatter_required_fields(skill_dir: Path):
    text = (skill_dir / "SKILL.md").read_text(encoding="utf-8")
    fm = _parse_frontmatter(text)
    assert fm is not None, f"{skill_dir.name}: no YAML frontmatter block found"
    assert "name" in fm, f"{skill_dir.name}: frontmatter missing `name`"
    assert "description" in fm, f"{skill_dir.name}: frontmatter missing `description`"
    assert fm["description"], f"{skill_dir.name}: `description` is empty"


@pytest.mark.parametrize("skill_dir", _skill_dirs(), ids=lambda p: p.name)
def test_frontmatter_name_matches_dir(skill_dir: Path):
    text = (skill_dir / "SKILL.md").read_text(encoding="utf-8")
    fm = _parse_frontmatter(text)
    assert fm is not None
    assert fm["name"] == skill_dir.name, f"{skill_dir.name}: frontmatter name `{fm['name']}` does not match dir"


@pytest.mark.parametrize("skill_dir", _skill_dirs(), ids=lambda p: p.name)
def test_description_includes_slash_trigger(skill_dir: Path):
    """The description powers natural-language matching; the canonical
    `/<skill-name>` form must be present so explicit invocation works."""
    text = (skill_dir / "SKILL.md").read_text(encoding="utf-8")
    fm = _parse_frontmatter(text)
    assert fm is not None
    expected = f"/{skill_dir.name}"
    assert expected in fm["description"], f"{skill_dir.name}: description missing trigger phrase `{expected}`"


@pytest.mark.parametrize("skill_dir", _skill_dirs(), ids=lambda p: p.name)
def test_required_body_sections_present(skill_dir: Path):
    text = (skill_dir / "SKILL.md").read_text(encoding="utf-8")
    missing = [s for s in REQUIRED_SECTION_PREFIXES if s not in text]
    assert not missing, f"{skill_dir.name}: missing required sections {missing}"


@pytest.mark.parametrize("skill_dir", _skill_dirs(), ids=lambda p: p.name)
def test_referenced_mcp_tools_exist(skill_dir: Path):
    text = (skill_dir / "SKILL.md").read_text(encoding="utf-8")
    referenced = _referenced_mcp_tools(text)
    registered = _registered_tool_names()
    missing = referenced - registered
    assert not missing, f"{skill_dir.name}: references nonexistent MCP tools: {sorted(missing)}"


def test_referenced_sibling_skills_exist():
    """Every `/<skill-name>` reference inside a SKILL.md must resolve to a real
    skill dir (self-references allowed)."""
    skill_names = {d.name for d in _skill_dirs()}
    failures: list[str] = []
    for d in _skill_dirs():
        text = (d / "SKILL.md").read_text(encoding="utf-8")
        refs = _referenced_skills(text)
        missing = refs - skill_names
        missing.discard(d.name)
        if missing:
            failures.append(f"{d.name}: {sorted(missing)}")
    assert not failures, "Skills reference nonexistent siblings: " + "; ".join(failures)


def test_catalog_lists_every_skill():
    catalog = SKILLS_CATALOG.read_text(encoding="utf-8")
    missing = [d.name for d in _skill_dirs() if f"/{d.name}" not in catalog]
    assert not missing, f"SKILLS.md catalog does not list: {missing}"


def test_every_catalog_entry_is_a_real_skill():
    """Every `/<skill-name>` slash reference in the catalog must resolve to a
    real skill dir — catches ghosts left behind by deletions."""
    catalog = SKILLS_CATALOG.read_text(encoding="utf-8")
    refs = {m for m in re.findall(r"`/([a-z][a-z0-9-]+)`", catalog) if "_" not in m}
    skill_names = {d.name for d in _skill_dirs()}
    ghosts = refs - skill_names
    assert not ghosts, f"SKILLS.md references nonexistent skills: {sorted(ghosts)}"
