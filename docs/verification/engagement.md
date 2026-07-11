# Verification: Engagement tools (#29)

Content audit of all 7 engagement tools. The 6 document generators were judged on substance; the
stateful `rick_tracker` (create/update/read + vault projection) was verified in an **isolated
throwaway vault** (subprocess with `HOME` redirected) so nothing touched the operator's real
`~/.rick_mcp/` — which matters here because these tools have real vault side-effects (see note) and the
operator had a live engagement in progress. **Verdict: all 7 pass.** No defects; one arithmetic nit and
one operational note.

## Tools

| Tool                       | Fired                                             | Verdict | Evidence                                                                                                                                                                            |
|----------------------------|---------------------------------------------------|:-------:|-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| `rick_roe`                 | `red_team`                                        |    ✅    | Legally/operationally sound: written-auth requirement, scope confinement, no-DoS/no-SE rules, 1hr escalation, data-exposure handling. Standards PTES / OWASP / **NIST SP 800-115**. |
| `rick_engagement_proposal` | `web_app_pentest`                                 |    ✅    | Complete SOW: scope (Gray Box), PTES+OWASP+ATT&CK methodology, timeline, deliverables, terms.                                                                                       |
| `rick_client_onboarding`   | `pentest`                                         |    ✅    | Real, complete checklists: authorization, technical, contacts, scheduling + comms/ground-rules/FAQ.                                                                                 |
| `rick_report_template`     | `finding` (High)                                  |    ✅    | Correct finding scaffold (CVSS/CWE/asset/impact/PoC/remediation/refs), PlexTrac-compatible, color-coded severity.                                                                   |
| `rick_scoping`             | `web_app_pentest`, 5 targets                      |    ✅    | Internally consistent: phase allocations sum to **200h**, days = hours/8 = 25, total = days × $2,400 = $60k.                                                                        |
| `rick_debrief`             | `pentest`                                         |    ✅    | Useful structure: exec summary, attack narrative, lessons learned, tiered remediation (0-7/7-30/30-90/90+d), retest + next-engagement.                                              |
| `rick_tracker`             | create · add_finding · status · export (isolated) |    ✅    | State round-trips (finding persists to JSON); vault projection accurate + **PII-safe**.                                                                                             |

## rick_tracker — isolated stateful verification

Ran `create → add_finding → status → export_markdown → proposal → roe` against a throwaway vault
(`HOME` redirected, generic `Operator` identity):

- **State round-trip ✅** — `create` wrote engagement JSON (client/target/type), `add_finding`
  persisted the finding, `status` read it back with the count, `export_markdown` included the title.
- **Vault projection accurate ✅** — the tracker note mirrors the canonical JSON (`~/.rick_mcp/
  engagements/*.json`), with a frontmatter + findings table regenerated on each write.
- **Zero PII ✅** — the projection references `[[Identity/Operator]]` generically; grep of the
  throwaway vault for operator PII (location/military/etc.) returned **0**. No operator identity is
  hardcoded into engagement notes.
- **Isolation held ✅** — the operator's real vault gained zero test artifacts.

## Findings (notes — none filed as bugs)

- 🟡 `rick_engagement_proposal` timeline sub-phases sum to **11d** (Recon 2 + Testing 5 + Exploitation
  2 + Reporting 2) but the stated **Total is 10d** — minor arithmetic inconsistency in the timeline
  breakdown.
- 🟢 **Operational note (not a defect):** `rick_engagement_proposal`, `rick_roe`, and `rick_scoping`
  have **real vault side-effects** when a vault is configured — proposal *creates* an engagement note,
  roe *appends* to a best-effort client+type match, scoping *logs* to `log.md`. This is the intended
  vault-projection feature, but it means these tools are not pure/read-only. Verifiers (and skills)
  should treat them as writes. (This audit surfaced it the hard way; artifacts were cleaned up and the
  remaining checks moved to an isolated vault.)

All content truthful, actionable, contract-honoring, generic-safe (generic `Operator` identity; no
PII). Both formats coherent where spot-checked. No `bug` issues filed.
