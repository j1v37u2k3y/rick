# Verification: Network/live — rick_cve + rick_recon_handle (#33)

Fired both tools against the **real** APIs (NVD, GitHub, CTFTime, HTB) — the unit tests mock these, so
this batch judges live accuracy, cache behavior, and per-source graceful degradation. **Verdict: both
pass.** One cosmetic output bug fixed inline (CWE de-duplication); two enhancement notes, no defects
filed.

## rick_cve — live NVD ✅

| Check                    | Input                  |                                                  Result                                                   |
|--------------------------|------------------------|:---------------------------------------------------------------------------------------------------------:|
| Accurate ID lookup       | `CVE-2021-44228`       |        ✅ CVSS **10.0 CRITICAL**, CWE-20/400/502/917, correct Log4Shell JNDI description, real refs        |
| Keyword search           | `apache log4j` (max 3) | ✅ 23 total, `max_results` honored, all real (CVE-2017-5645 deserialization RCE 9.8, CVE-2020-9488 LOW, …) |
| Not-found (valid format) | `CVE-2099-99999`       |                              ✅ clean `No CVEs found for query: …` — no crash                              |
| Zero-result keyword      | `qzx…zzz`              |                                          ✅ same graceful message                                          |
| Both formats             | markdown + json        |                                              ✅ both coherent                                              |
| 24h file cache           | shared cache layer     |                     ✅ (mechanism proven live via `rick_recon_handle`'s `cached` flag)                     |

**Rubric:** truthful ✅ · actionable (CVSS/severity/CWEs/refs — real triage data) ✅ · contract held
(`response_format`, `max_results`) ✅ · generic-safe (title uses the public callsign; no PII) ✅ · both
formats ✅ · graceful on not-found + (unit-tested) network error ✅.

## rick_recon_handle — live GitHub / CTFTime / HTB ✅

| Check                  | Input           |                                                                 Result                                                                  |
|------------------------|-----------------|:---------------------------------------------------------------------------------------------------------------------------------------:|
| Accurate live GitHub   | `j1v37u2k3y`    |           ✅ 22 repos, real repo list (`rick`, `jarvis`, `NeoSetup`…), `created_at` 2020-12-04, top languages, activity count            |
| Cache hit/miss         | same handle ×2  |                                              ✅ `cached: false` → `true`, identical payload                                              |
| Per-source degradation | any handle      |     ✅ CTFTime/HTB return search/profile URLs + a note (need numeric ID / API token); optional `ctftime_id` / `github_token` enrich      |
| Not-found              | bogus handle    | ✅ `github.found: false`, `GitHub HTTP 404 — not found`; pivots + other sources still resolve (one source failing doesn't kill the rest) |
| Both formats           | json + markdown |                                                             ✅ both coherent                                                             |

**Rubric:** truthful ✅ · actionable (profile + repos + languages + pivot URLs — a real OSINT start
point) ✅ · contract held (per-source structure, `cached` flag accurate) ✅ · generic-safe (only
already-public GitHub data; `bio/location/company` were null anyway) ✅ · both formats ✅ · graceful
per-source ✅.

## Findings

- 🟢 **Fixed in this PR** — `rick_cve` emitted duplicate CWEs (live: `CVE-2020-9488` → `["CWE-295",
  "CWE-295"]`) because NVD lists a CWE per weakness node and the extractor appended without dedup.
  Now order-preserving-deduped (`cve.py`), with a regression test mirroring the real duplicate.
- 🟡 **Enhancement (not filed)** — `rick_cve` keyword results follow NVD's default ordering, not
  severity/recency. Searching `apache log4j` with a small `max_results` buries the headline vuln
  (Log4Shell wasn't in the top 3). Faithful passthrough, but sorting by CVSS or recency would surface
  the important ones first.
- 🟡 **Enhancement (not filed)** — `rick_cve` output carries no `cached` indicator, while
  `rick_recon_handle` does. Minor observability inconsistency between the two network tools.

No `bug` issues filed — no behavioral defects in either tool against live data.
