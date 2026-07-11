# Verification: Defensive tools (#28)

Content audit of the 4 defensive tools — judged **substance, not shape**, with the load-bearing check
being that `rick_detection_rules` emits **valid** Sigma/YARA that maps to the attack pattern. Fired each
with representative inputs (both formats spot-checked). **Verdict: all 4 pass.** No defects; three
minor currency/precision notes, none filed as bugs.

## Tools

| Tool                     | Fired                                                | Verdict | Evidence                                                                                                                                                                            |
|--------------------------|------------------------------------------------------|:-------:|-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| `rick_hardening`         | `active_directory`                                   |    ✅    | Real best practice: ESC1-8 template audit, LAPS, Tier 0/1/2, Protected Users, `ms-DS-MachineAccountQuota=0`, GPP cpassword removal, gMSA for Kerberoast.                            |
| `rick_incident_response` | `ransomware`                                         |    ✅    | Sound containment→eradication→recovery→lessons: isolate (not power-off), nomoreransom.org, assume domain compromise, 3-2-1 backups. Real DFIR tools (Velociraptor/KAPE/Volatility). |
| `rick_detection_rules`   | credential_dumping · lateral_movement · c2_beaconing |    ✅    | **Valid Sigma + YARA** — see below.                                                                                                                                                 |
| `rick_log_analysis`      | `windows_event`                                      |    ✅    | Every event ID correct (4624 Type 3/10, 4648, 4672, 4688, 7045, 4768/4769, 4776, 1102); IOCs sound; 4104 ScriptBlock + 4688 cmdline callouts right.                                 |

## Detection-rule validation (the load-bearing check)

Three attack patterns, each producing a well-formed rule that maps to the correct technique:

- **credential_dumping** — Sigma `logsource: category: process_access` (correct for Sysmon EID 10),
  real LSASS `GrantedAccess` masks (`0x1010`/`0x1F0FFF`/`0x1F1FFF`), `selection and not filter`,
  `attack.t1003.001`. YARA matches real Mimikatz strings (`sekurlsa::logonpasswords`,
  `lsadump::dcsync`, `MiniDumpWriteDump`), `2 of them`.
- **lateral_movement** — Sigma EID `7045` with the correct `ServiceFileName` field + `ADMIN$` /
  `cmd.exe /c` indicators, `attack.t1021.002`. YARA on Impacket exec-module names, `any of them`.
- **c2_beaconing** — Sigma proxy aggregation `count(cs-uri-stem) by cs-host > 60` over `timeframe: 1h`,
  `attack.t1071.001`. YARA on beacon-config artifacts (`sleeptime`/`jitter`/UA), `3 of ($cfg*)`.

MITRE mappings correct throughout (T1003.001/.002/.003/.006, T1021.002/.006, T1071.001/.004, T1573/T1572).

## Findings (notes — none filed as bugs)

- 🟢 `credential_dumping` Sigma uses `GrantedAccess|contains` — a substring match can theoretically
  over-match (`0x1010` ⊂ `0x11010`); an exact-value list is marginally more precise. Common real-world
  tradeoff, not wrong.
- 🟢 `rick_log_analysis` lists `sigmac` as a tool — that's the deprecated Sigma converter (now
  pySigma / the `sigma` CLI). Currency nit.
- 🟢 `rick_hardening` has a casual aside ("DES already disabled right?") inside the Critical
  checklist — a touch informal for a blueprint (the Rick voice), not a content error.

All content truthful, actionable, contract-honoring, generic-safe (titles use the public callsign; no
PII). Both markdown and json formats coherent (Sigma/YARA survive json as clean string fields). No
`bug` issues filed.
