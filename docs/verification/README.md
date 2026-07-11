# Behavioral Verification

Records the behavioral-verification pass over rick_mcp's tools + resources — epic
[#35](https://github.com/j1v37u2k3y/rick/issues/35). Unit tests prove *structure* (shape,
formats, state, errors); these reports judge *substance*: that each tool/resource is truthful,
actionable, contract-honoring, generic-safe, and — for resources — resolves correctly with zero
PII in the repo/generic path.

Each batch is one PR. Findings live here; defects too big to fix inline become `bug` issues.

## Rubric

1. **Truthful** — content is factually correct.
2. **Actionable, not filler.**
3. **Contract held** — promised fields/behaviors actually appear in output.
4. **Generic-safe** — works on the default identity (no `~/.rick_mcp/`); no PII leak.
5. **Both formats coherent** (where applicable).
6. **Chains compose** (where applicable).

Resources additionally: correct surface · `private → project → fallback` resolution ·
parameterized resolve · zero PII on the generic path.

## Batches

- [resources.md](resources.md) — `profile://` / `resume://` / `doc://` / `vault://` (#34)
- [network-live.md](network-live.md) — `rick_cve` (NVD) / `rick_recon_handle` (GitHub·CTFTime·HTB), fired against live
  APIs (#33)
- [offensive.md](offensive.md) — 11 offensive tools: recon · vuln · tool-rec · attack-chain · pivot · c2 · cloud ·
  payload · wireless · cheatsheet · threat-model (#27)
- [defensive.md](defensive.md) — 4 defensive tools: hardening · incident-response · detection-rules (Sigma/YARA) ·
  log-analysis (#28)
- [engagement.md](engagement.md) — 7 engagement tools: roe · proposal · onboarding · report-template · scoping ·
  debrief · tracker (stateful, isolated-vault verified) (#29)
