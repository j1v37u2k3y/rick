# Verification: JARVIS / stateful tools (#31)

Behavior + state-lifecycle + chain audit of all 12 JARVIS tools. Because these read/write
`~/.rick_mcp/dick/` — the **same store the operator's live engagement uses** — the entire audit ran in
an **isolated throwaway `HOME`** (subprocess, `HOME` redirected). The live op was verified untouched
before and after (mission-log entry count unchanged; zero test-engagement leak into the real store).
**Verdict: 10/12 pass; the lifecycle holds except rollback.** Two confirmed bugs filed:
[#60](https://github.com/j1v37u2k3y/rick/issues/60), [#61](https://github.com/j1v37u2k3y/rick/issues/61).

## Lifecycle smoke

`full_auto (create) → kill_chain add_finding ×2 → advance → tag → notes → checklist → scope_check →
sitrep → next_move → timeline → export → compare → rollback` — all cohere **except rollback** (see #60).
State persisted and read back correctly at each step (findings, phase status, tags, notes all verified
in the on-disk JSON).

## Tools

| Tool               | Verdict | Evidence                                                                                                        |
|--------------------|:-------:|-----------------------------------------------------------------------------------------------------------------|
| `rick_full_auto`   |    ✅    | Actually chains — output carries recon + vuln + attack-chain + tools + pivot; creates the engagement state.     |
| `rick_kill_chain`  |    ✅    | `add_finding`/`advance`/`status`/`list` mutate + read state correctly (findings persisted, phase 2 → `active`). |
| `rick_next_move`   |    ✅    | Returns a real recommendation reflecting position + findings.                                                   |
| `rick_sitrep`      |    ✅    | Summary reflects findings/state.                                                                                |
| `rick_notes`       |    ✅    | add/list/search round-trip (search finds the added note).                                                       |
| `rick_tag`         |    ✅    | Severity + category + MITRE ID attach to the finding in state.                                                  |
| `rick_timeline`    |    ✅    | Unified chronological events render.                                                                            |
| `rick_compare`     |    ✅    | Diffs two engagements (both IDs + deltas present).                                                              |
| `rick_checklist`   |    ✅    | generate/check/status cohere.                                                                                   |
| `rick_export`      |    ✅    | markdown / json / csv all export complete state.                                                                |
| `rick_scope_check` |    ❌    | **No CIDR matching** → #61. In-scope host in a `/24` flagged OUT OF SCOPE.                                      |
| `rick_rollback`    |    ❌    | **Non-functional** → #60. No tool ever creates a snapshot, so it always reports "no snapshots."                 |

## Confirmed bugs (filed)

- 🔴 **[#60](https://github.com/j1v37u2k3y/rick/issues/60) — `rick_rollback` never works.** `snapshot=True`
  appears exactly once in the codebase, inside the error *suggestion string* — not a real call site. No
  mutating tool passes `snapshot=True` to `_save_state`, so no snapshot is ever created; the restore
  path is unreachable. Verified: a 10-mutation lifecycle produced a state JSON with no `snapshots` key.
- 🔴 **[#61](https://github.com/j1v37u2k3y/rick/issues/61) — `rick_scope_check` has no CIDR matching.**
  Matching is substring/wildcard only (jarvis_extended.py:345). A host inside an authorized
  `10.10.10.0/24` is flagged OUT OF SCOPE. Fails *safe* (won't wrongly authorize), but unusable for
  IP-range scopes — the standard format. Exact-hostname + wildcard matching work.

Both need careful, tested fixes (snapshot granularity; IP/CIDR/hostname edge cases) rather than rushed
inline patches — especially the safety rail — so they're tracked as issues, not fixed in this report PR.

## Isolation

Live op `ENG-20260711-144701` (the operator's active Connected engagement): **7 mission-log entries
before and after**, zero `VERIFY-JARVIS*` artifacts in the real `~/.rick_mcp/dick/`. The entire
lifecycle ran in a throwaway `HOME` and never touched real state.
