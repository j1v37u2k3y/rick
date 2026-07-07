# Verification: Resources — profile / resume / doc / vault (#34)

Audited the four resource families: read the source (resolution + PII logic), cross-checked the
served surface live (`ListMcpResources` + a `vault://status` read), and confirmed generic-safety
via the shared loaders. **Verdict: resources pass.** The only findings were two doc-accuracy
issues in how `rick_capabilities` *describes* resources — both fixed in this PR.

## Surface

35 static resources + 1 parameterized template (`vault://engagements/{codename}`) = **36
registered**, matching `resource_count()`. (The template lists under resource-templates, not the
static resource list — expected MCP behavior, not a discrepancy.)

| Family | Count | Resolution | Verdict |
|--------|------:|------------|:------:|
| `profile://` | 11 | `_read_data`: private `~/.rick_mcp/profiles/` → bundled `data/profiles/` (generic) → fallback string | ✅ |
| `resume://`  | 4  | `_read_data`: private → bundled `data/resume/` (generic) → fallback | ✅ |
| `doc://`     | 9  | per-resource private (`~/.rick_mcp/soul|docs/`) → repo root (`_read_md`) / `_read_data` → fallback | ✅ |
| `vault://`   | 12 | `_read_or_stub`: graceful stub when unconfigured; `identity/hub` resolves by `NAME` → `Operator.md` fallback | ✅ |

## Rubric judgment

- **Truthful / actionable** — content is the operator's real identity surface; live reads
  resolved and returned coherent content (`vault://status` returns valid JSON: configured,
  path, engagement count, templates, identity-layer presence).
- **Generic-safe ✅** — every `profile://` / `resume://` resource falls back to the bundled
  generic templates under `rick_mcp/data/`, and `doc://` falls back to generic repo files, so a
  fork with no `~/.rick_mcp/` still gets resolvable, non-PII content. Verified in `_read_data` /
  `_read_md`.
- **Zero PII in the repo path ✅** — resources serve the operator's *private* `~/.rick_mcp/`
  content to the operator's *own* AI (by design, not a leak); the repo-shipped fallbacks are
  generic (enforced separately by the no-PII-in-repo rule + `soul-example/`).
- **Resolution order ✅** — `private → project/bundled → fallback`, confirmed per family.
- **Parameterized resolve ✅** — `vault://engagements/{codename}` decodes the URI param and
  enforces a containment check (`resolved.relative_to(engagements_dir)`) before any read, so it
  is path-traversal-safe (defense-in-depth; also covered by `tests/test_vault.py`).
- **Graceful degradation ✅** — every `vault://` resource returns a clear bootstrap stub when
  the vault is unconfigured.

## Findings (fixed in this PR)

- 🟡 `rick_capabilities` listed `profile://` as **10 resources** and omitted `craftsmanship`
  (11 exist). → corrected to 11 and added `craftsmanship`.
- 🟡 `rick_capabilities` `resources.categories` omitted the `vault://` family (12 resources)
  entirely. → added a `vault://` entry. The dynamic total (`resource_count()` → 36) was already
  correct.

No defects in the resources themselves; no `bug` issues filed.
