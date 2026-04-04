# Engagement Methodology

## Framework

PTES (Penetration Testing Execution Standard) as the backbone, enhanced with OWASP Testing Guide for web applications
and MITRE ATT&CK for adversary simulation.

## The Seven Phases

### Phase 1: Reconnaissance

Know the target before you touch it. Passive OSINT, DNS enumeration, technology fingerprinting, org chart analysis.
Build the attack surface map.

### Phase 2: Vulnerability Assessment

Automated scanning as a starting point, never the finish line. Manual testing for business logic, authentication flows,
and authorization boundaries. Every scanner miss is a potential finding.

### Phase 3: Exploitation

Prove the vulnerability is real. Develop working proof-of-concept exploits. Minimize impact — PoC-level data only.
Screenshot, timestamp, document.

### Phase 4: Privilege Escalation

From foothold to objective. Local privilege escalation, AD escalation paths, cloud IAM abuse. BloodHound first, always.

### Phase 5: Lateral Movement

Map the internal network from the compromised position. Credential reuse, pass-the-hash, Kerberos abuse, trust
relationship exploitation.

### Phase 6: Documentation

Everything documented in real time. Timestamps, screenshots, exact reproduction steps. The report is written during the
engagement, not after.

### Phase 7: Remediation Strategy

Every finding comes with a fix. Prioritized by business impact, not just CVSS. Quick wins identified separately from
architectural changes.
