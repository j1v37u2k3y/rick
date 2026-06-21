# Contributing to Rick MCP

Rick is forkable by design — clone it, fill it, make it yours. If you're sending changes
back upstream, build like your name's on it, because once someone forks it, it is. The bar
is the one in [`CLAUDE.md`](CLAUDE.md): honest work, tested, no padding.

## Getting started

```bash
git clone https://github.com/j1v37u2k3y/rick.git
cd rick
make setup
```

`make setup` builds the venv, installs `requirements-dev.txt`, wires the pre-commit hooks,
and creates `~/.rick_mcp/soul/`. Every `make` target uses the venv — no manual activation.

Dev/test dependencies live in **one** place: `requirements-dev.txt` (Dependabot keeps it
current). The project isn't packaged for distribution — don't reach for `pip install -e .`,
it won't build.

## The loop

1. Branch from `main`.
2. Make the change.
3. `make check` — lint, format, type-check, file-length, tests. All green, or it doesn't ship.
4. Commit. Pre-commit runs the same gates; if a hook fixes a file mid-commit, the commit
   didn't happen — re-stage and commit fresh. Never amend over a hook.
5. Open a PR against `main`.

`make fix` auto-fixes lint + format. `make check` is the whole pipeline in one shot — run it
before you push, because CI runs the exact same gates and won't be more forgiving than you.

## The rules that bite

Enforced by pre-commit and CI. Full detail in [`CLAUDE.md`](CLAUDE.md) — this is the short list:

- **Tests for everything.** Every tool needs tests: valid inputs, error cases, both output
  formats. 80% coverage minimum, enforced.
- **1500 lines per Python file, max.** Split before you hit the cap.
- **Counts aren't hand-edited.** Tool / resource / test counts live in `rick_capabilities`
  and the README headline, auto-synced by `scripts/refresh_counts.py`. Don't hardcode them
  anywhere else — including here.
- **Fresh version bump per feature** in `__version__.py` — a new entry, not an amend to a
  shipped release.
- **No identity in source.** Personal data loads from `~/.rick_mcp/`; the Python stays generic.

## Adding a tool

The full checklist — input model → async function → `register()` with annotations → wire
into `tools/__init__.py` → tests → `rick_capabilities` → README table → `CHANGELOG.md` →
version bump — lives in [`CLAUDE.md`](CLAUDE.md) § Adding a Tool. Follow it there. One source
of truth, no drift.

Resources follow the same `register(mcp)` pattern (see `CLAUDE.md` § Architecture); skills
live at `.claude/skills/` with their own authoring rules in
[`.claude/skills/SKILLS.md`](.claude/skills/SKILLS.md).

## Commits

Conventional commits, scoped to where the change lands:

```
feat(tools): rick_new_tool — what it does
fix(recon): handle empty-response edge case
docs(readme): document the new tool
ci: add pip-audit gate
```

**No `Co-Authored-By` trailers, no "Generated with …" footers.** Commits are attributed to
you, clean. (See [`CLAUDE.md`](CLAUDE.md) § Git / Commit Conventions.)

## Pull requests

- One feature or fix per PR. Keep it focused.
- `make check` green, tests included, docs updated if behavior changed.
- In the description, say what it does and why — the honest version, not the sales pitch.

## Principles

- No harm. Ever. Point blank. Full stop.
- Facts, not opinions.
- Thorough > fast.
- Honest findings, no padded reports.
- The craft demands quality.

## Security

Found a vulnerability? See [SECURITY.md](SECURITY.md) — don't open a public issue.
