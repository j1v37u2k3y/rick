# Verification: Cognitive appraisal + Writeups (#32)

Content + **guardrail** audit of the two tools. `rick_cognitive_appraisal`'s full gating matrix was
exercised (defense-default, scoped-redteam gate, coercion/vulnerable downgrade, fabrication
short-circuit); `rick_writeups` was run against the real 255-writeup corpus with a path-traversal probe.
**Verdict: both pass, no defects.** This is the final batch — its merge closes epic
[#35](https://github.com/j1v37u2k3y/rick/issues/35).

## rick_cognitive_appraisal — gating matrix ✅

| Path | Input | Result |
|------|-------|:------:|
| Defense default | `mode=defense` | ✅ `Mode Delivered: defense` — full OCC/Lazarus/Scherer scaffold. |
| Red-team, no engagement | `mode=redteam`, no id | ✅ Gate fires → **defense** ("requires an authorized engagement_id"). |
| Red-team, bogus engagement | `mode=redteam`, `FAKE-NOSCOPE` | ✅ Gate fires → **defense** ("No engagement found… requires an active, scoped engagement"). |
| Red-team, scoped engagement | `mode=redteam` + scoped id (isolated) | ✅ `Mode Delivered: redteam` — pretext brief delivered only here. |
| Coercion tripwire | scoped + "blackmail/extort/coerce" | ✅ **Hard refusal → defense**, even though authorized. |
| Vulnerable tripwire | scoped + "elderly… dementia" | ✅ **Refusal → defense**. |
| Fabrication guard | no-evidence input (`.` / `.`) | ✅ `INSUFFICIENT EVIDENCE` — deterministic short-circuit, invents nothing. |

**Contract + guardrails:** every predicted tendency carries a `confidence` level + a `refutation_condition`
(falsifiability enforced); hard-refusal list present (non-consenting individuals, vulnerable
populations, coercion); stateless (no subject data persisted). **Clean-room intact** — sources are the
academic appraisal literature (Ortony/Clore/Collins 1988, Lazarus 1991, Scherer); **no benchmark / SOTA
/ accuracy claim** and no MHH/Webb text anywhere in the output.

## rick_writeups — corpus behavior ✅

| Action | Result |
|--------|:------:|
| `list` | ✅ 255-writeup corpus, truncation reported (15 of 255), grouped by category. |
| `read` | ✅ Returns the writeup content by relative path. |
| `search` | ✅ Accurate — `nmap` → 5 real hits; `kerberoast` → 0 (genuine miss; corpus is older CTF/vulnhub boxes). |
| `index` | ✅ Rich corpus intelligence — OS breakdown, top tools (nmap 28, john 14…), CVEs referenced, MITRE techniques. |
| **path traversal** | ✅ `../../../../etc/passwd` → **rejected** ("path escapes writeups directory"). |
| citation cross-ref | ✅ Paths cited by other tools (e.g. `htb/hackthebox/intelligence/README.md` from `rick_recon`) **exist** in the corpus. |

## Guardrail summary

- Offensive appraisal frame is reachable **only** through a scoped engagement; every other path returns
  defense-only.
- Coercion / vulnerable-population inputs are hard-refused regardless of authorization.
- Empty/no-evidence input short-circuits instead of fabricating a profile.
- Path traversal on the writeup corpus is contained.

No `bug` issues filed. **Epic #35 closes on merge** — all 8 behavioral-verification batches complete.
