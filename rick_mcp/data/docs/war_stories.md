# War Stories — From the Field

Anonymized engagement narratives. The names are changed, the lessons are real.

---

## The Forgotten Admin Panel

**Scenario**: Web application pentest for a mid-size financial services company. Production app with standard security headers, WAF in place, solid authentication.

**Approach**: Standard recon showed nothing interesting. Directory brute-forcing with a custom wordlist found `/admin-legacy/` — a forgotten admin panel from a previous version of the application, running behind the same WAF but with no authentication.

**Finding**: Unauthenticated access to legacy admin panel with full database read/write. The panel was built 5 years ago, never decommissioned, and had direct SQL query functionality.

**Impact**: Critical. Full database access including PII for 200k+ customers. Could have been exploited for data exfiltration or ransomware staging.

**Lesson**: Decommission everything. If it's not in use, it shouldn't be accessible. Asset inventory isn't optional — you can't protect what you don't know exists. The WAF doesn't help if the door behind it is wide open.

---

## The Service Account That Could

**Scenario**: Active Directory security review for a healthcare organization. 15,000 endpoints, mature security team, recent investments in EDR.

**Approach**: BloodHound analysis revealed a service account (svc_backup) with Kerberoastable SPN. Requested the TGS ticket, cracked the password offline in 4 minutes using hashcat with rockyou.txt. The password was `Backup2019!`.

**Finding**: svc_backup was a member of Domain Admins. One cracked service account password = full domain compromise.

**Impact**: Critical. Complete Active Directory takeover from a standard user account with no special access.

**Lesson**: Service accounts are the skeleton keys of AD. Use Group Managed Service Accounts (gMSA) — they rotate their own passwords automatically. Never put service accounts in Domain Admins. And if you must use a regular service account, make the password 25+ characters of random gibberish.

---

## The Cloud Misconfiguration Cascade

**Scenario**: Cloud security audit for a SaaS startup running on AWS. ~50 microservices, 3 AWS accounts, CI/CD through GitHub Actions.

**Approach**: ScoutSuite scan identified an S3 bucket with public read access. The bucket contained Terraform state files with embedded AWS access keys. The keys belonged to a role with `iam:*` permissions.

**Finding**: Public S3 bucket → Terraform state → AWS keys → IAM admin access → full account takeover. Total time from discovery to domain admin equivalent: 12 minutes.

**Impact**: Critical. Full control of all three AWS accounts, including production customer data.

**Lesson**: Never store secrets in Terraform state without encryption. Never give `iam:*` to automation roles. Never allow public S3 access at the account level — use the account-level S3 Block Public Access setting. And always, always encrypt your state files.

---

## The Printer That Owned the Network

**Scenario**: Internal network penetration test for a manufacturing company. Flat network, 500 endpoints, mix of Windows and Linux.

**Approach**: Network scan identified a multifunction printer with default credentials (admin:admin). The printer had LDAP integration configured with a service account — and the credentials were visible in the printer's web interface in plaintext.

**Finding**: Default printer credentials → LDAP service account credentials in plaintext → service account had Domain Admin rights (because "it needed to scan to email").

**Impact**: Critical. Domain compromise through a printer.

**Lesson**: Printers are computers. Treat them like it. Change default credentials, segment them on their own VLAN, and never — ever — give a printer's service account Domain Admin rights. Least privilege isn't just for people.

---

## The Intern's Forwarding Rule

**Scenario**: Business Email Compromise investigation for a law firm. CFO received a wire transfer request that looked legitimate but wasn't.

**Approach**: Forensic analysis of M365 audit logs. Found that an intern's account had been compromised via password spray (password was `Summer2025!`). The attacker created an inbox rule forwarding all emails containing "wire", "transfer", "payment", or "invoice" to an external email address. They monitored for 3 weeks before sending the fraudulent request.

**Finding**: Compromised account with malicious inbox forwarding rule → 3 weeks of email surveillance → socially engineered wire transfer request that matched the firm's actual communication patterns.

**Impact**: High. $340,000 wire transfer initiated (caught by bank before completion due to new verification procedure implemented after our security awareness training).

**Lesson**: MFA everywhere. Disable legacy authentication. Monitor inbox rule creation — it's the #1 persistence mechanism in BEC. And the verification procedure we recommended in previous training literally saved them six figures. Security awareness training works.
