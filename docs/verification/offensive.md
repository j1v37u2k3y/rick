# Verification: Offensive tools (#27)

Content audit of all 11 offensive tools — judged **substance, not shape**: are the commands valid, the
facts correct, the chains sound? Fired each with a representative input (both formats spot-checked) and
graded against the rubric, with emphasis on the cheatsheet commands actually being runnable.
**Verdict: all 11 pass.** No behavioral defects; five minor taxonomy/dedup notes, none filed as bugs.

## Tools

| Tool                     | Fired                            | Verdict | Evidence                                                                                                                                                                               |
|--------------------------|----------------------------------|:-------:|----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| `rick_recon`             | `active_directory`               |    ✅    | Phase-appropriate: BloodHound-first, Kerberoast/AS-REP, ADCS ESC1-8, LAPS, trust mapping. Right tools (Rubeus/Certify/PowerView).                                                      |
| `rick_vuln_assess`       | `injection`                      |    ✅    | Correct OWASP **A03:2021**; error/UNION/blind/second-order/NoSQL/LDAP — real depth, not a scanner echo.                                                                                |
| `rick_tool_recommend`    | kerberoast-after-foothold        |    ✅    | AD-correct picks; methodology gate + validation checklist + `chain_to` all fire.                                                                                                       |
| `rick_attack_chain`      | `external_to_da`                 |    ✅    | **Sound** path, correct MITRE IDs (T1190, T1566.001, T1003.006 DCSync, T1550.002 PtH, T1558.001 Golden), right order, ADCS as the shortcut.                                            |
| `rick_pivot_plan`        | `linux_webserver`                |    ✅    | Valid commands: chisel `--reverse`/`R:socks`, ligolo `:11601`, ssh `-D`/`-L`/`-R`, IMDS curl.                                                                                          |
| `rick_c2_compare`        | `stealth`                        |    ✅    | Facts correct: Havoc Demon (sleep obf + indirect syscalls), CS ~$3,500/yr + malleable/BOF, Sliver=BishopFox/Go/mTLS.                                                                   |
| `rick_cloud_attack_path` | `aws`                            |    ✅    | Textbook IAM privesc (`iam:PassRole`+`lambda:CreateFunction`, `iam:CreatePolicyVersion`, `iam:AttachUserPolicy`); IMDSv2 PUT+hop-limit blocks SSRF; T1552.005/T1078.004/T1530 correct. |
| `rick_payload_guide`     | `initial_access`                 |    ✅    | Accurate + **safe-by-default** — methodology & MITRE mapping (T1566.001/.002, T1189/95/99), no weaponized payloads. MOTW-bypass via ISO/HTML-smuggling correct.                        |
| `rick_wireless`          | `wifi`                           |    ✅    | Facts correct: PMKID (no client), WPS/Reaver, handshake→hashcat, hcxdumptool/hcxtools.                                                                                                 |
| `rick_cheatsheet`        | nmap · impacket · hashcat · ffuf |    ✅    | **Commands/flags valid** — see below.                                                                                                                                                  |
| `rick_threat_model`      | `active_directory`               |    ✅    | STRIDE + principle anchors + chain-validation all coherent; event IDs 1102/4768/4769/4776, GPP cpassword, ESC1-8 correct.                                                              |

## Cheatsheet command validation (the load-bearing check)

- **hashcat** — every mode number correct: NTLM `1000`, NTLMv2 `5600`, Kerberoast (TGS-REP) `13100`,
  AS-REP `18200`, SHA512-unix `1800`, bcrypt `3200`, MSSQL2012+ `1731`, WPA `22000`. Attack modes
  `-a 1/3/6` + mask charsets (`?l?u?d?s?a`) valid.
- **impacket** — `GetUserSPNs -request` (Kerberoast), `GetNPUsers -no-pass` (AS-REP), `getST
  -impersonate` (S4U2Self/Proxy), `secretsdump -just-dc-ntlm`, `ntlmrelayx -t … -smb2support -socks`
  — all valid.
- **ffuf** — `-mc/-fc`, `-fs/-ms`, `-fw/-mw`, `-fl`, `-fr`, `-recursion-depth`, multi-wordlist
  `-w wl:FUZZ1` — valid.
- **nmap** — all 11 invocations valid (`-sS -sV -sC -p- -oA`, NSE `--script vuln`, `ssl-enum-ciphers`,
  `dns-zone-transfer` with `--script-args`).

## Findings (notes — none filed as bugs)

- 🟡 `rick_attack_chain` lists Kerberoasting / AS-REP Roasting under **Privilege Escalation**; MITRE
  classes T1558.003/.004 as **Credential Access** (they also correctly appear under Credential Access
  later). Operationally defensible, taxonomically loose.
- 🟡 `rick_wireless` MITRE mapping is loose for WiFi — `T1557.002` is LLMNR/NBT-NS-specific and `T1563`
  is remote-session-hijack; `T1040`/`T1498` fit well.
- 🟡 `rick_tool_recommend` lists **Hashcat in both Primary and Secondary** — redundant (harmless if the
  cross-phase listing is intentional).
- 🟡 `rick_tool_recommend` methodology gate returns `Reconnaissance` regardless of an "after foothold"
  scenario — gate doesn't reflect stated phase context.
- 🟢 `rick_recon` files "User enum via RPC/LDAP" under **Passive** — unauthenticated LDAP/RPC enum is
  arguably active (touches the DC).

All content is truthful, actionable, contract-honoring, and generic-safe (titles use the public
callsign; no PII). Both output formats coherent where spot-checked. No `bug` issues filed.
