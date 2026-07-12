# Verification: Career + Meta + code_review tools (#30)

Content audit of all 10 tools. Identity-dependent tools were checked **both** configured (live, via the
operator's real identity) and generic (isolated subprocess with no `identity.yaml`) to prove
generic-safety. **Verdict: all 10 pass.** One count bug fixed inline; one vault-side-effect defect filed
as [#58](https://github.com/j1v37u2k3y/rick/issues/58).

## Tools

| Tool                       | Verdict | Evidence                                                                                                                                                                                   |
|----------------------------|:-------:|--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| `rick_compatibility_check` |    ✅    | Honest scoring — role posting → 78/100 (tech 100, culture 45), flagged a real gap, **no inflation**. Generic-safe (no PII).                                                                |
| `rick_cover_letter`        |    ✅    | Coherent output; **generic-safe** — zero PII with no `identity.yaml`.                                                                                                                      |
| `rick_mentorship`          |    ✅    | Sound learning path (networking→linux→windows→prog→web; THM → HTB → PortSwigger → WAHH — real, ordered resources).                                                                         |
| `rick_status`              |    ✅    | Accurate after fix: version 3.14.1, 48 tools, **36** resources (was 35 — see fix).                                                                                                         |
| `rick_health`              |    ✅    | Reports state (ALL PASS). Note: probes a subset (21 tools / 22 resources), not the full fleet.                                                                                             |
| `rick_demo`                |    ✅    | Represents the fleet correctly (one tool per category, accurate samples). **But has a vault side-effect** → #58.                                                                           |
| `rick_mode`                |    ✅    | All **7 personas** build + voice — configured (`be_rick` loads soul/book/identity) **and** generic (all 7 build with zero PII).                                                            |
| `rick_mantra`              |    ✅    | Pulls from the operator's stored mantras (configured); generic-safe with no identity.                                                                                                      |
| `rick_capabilities`        |    ✅    | Categories complete and accurate; count fixed (headline now matches the 36-sum category breakdown).                                                                                        |
| `rick_code_review`         |    ✅    | Rubric correct (craftsmanship/security/architecture, severity + verdict scales, scoring, inspection method). Bundled default **and** `~/.rick_mcp/code_review.yaml` override both resolve. |

## Fixed inline — resource count under-reported (35 → 36)

`server.py:resource_count()` returned `len(list_resources())` = **35**, omitting the parameterized
resource template `vault://engagements/{codename}` (templates live in `list_templates()`, not
`list_resources()`). So `rick_status` / `rick_capabilities` / `rick_demo` / the banner all reported 35,
disagreeing with the README + `refresh_counts` (36) — and with `rick_capabilities`' own category
breakdown, which sums to 36. Fixed to count statics **+** templates; added a regression test
(`test_resource_count_includes_templates`). Tests reference `resource_count()` dynamically, so nothing
else broke.

## Generic-safety (isolated, no identity.yaml)

Fired in a subprocess with `HOME` redirected (generic `Operator` identity):

- **All 7 `rick_mode` personas** (`be_rick`, `dick_mode`, `jarvis`, `pentest_mode`, `mentor_mode`,
  `evaluate_fit`, `engagement_ops`) build and voice with **zero PII**.
- `rick_cover_letter`, `rick_compatibility_check`, `rick_mantra` — all generic-safe, zero PII.
- `rick_code_review` — bundled rubric loads generically; a planted `~/.rick_mcp/code_review.yaml`
  override was picked up (marker appeared in output), confirming the override → bundled → minimal
  resolution.

## Findings

- 🟢 **Fixed in this PR** — resource count 35 → 36 (see above).
- 🔴 **Filed [#58](https://github.com/j1v37u2k3y/rick/issues/58)** — `rick_demo` mutates the vault: it
  fires `rick_scoping`, which logs to `vault/log.md` on every run (a tour tool shouldn't write). Needs
  a design fix (dry-run mode / static samples).
- 🟡 `rick_health` probes a subset (21 tools / 22 resources) rather than the full 48/36 — coverage is
  partial (it passes what it checks, but doesn't exercise every tool/resource).
- 🟡 Engagement-count mismatch: `rick_health` reports "2 engagements" while `rick_capabilities` reports
  3 — different stores (`~/.rick_mcp/engagements/` tracker vs `vault/Engagements/`).

All content truthful, actionable, contract-honoring, generic-safe. No PII on the generic path. Both
formats coherent where spot-checked.
