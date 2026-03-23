# War Stories

Anonymized engagement narratives. Names changed. Lessons kept.

---

## The Forgotten Admin Panel

**Type**: Web Application Pentest
**Scenario**: Mid-size SaaS company, annual security assessment.
**Finding**: Directory brute-forcing revealed `/admin-legacy/` — an old admin panel with no authentication. Direct
database access, user management, API key generation.
**Impact**: Critical. Full application takeover. 50,000+ user records accessible.
**Kill Chain**: Recon (ffuf) → Discovery → Direct Access → Data Exposure
**Lesson**: Decommission everything. You can't protect what you don't know exists. Asset inventory isn't glamorous but
it prevents exactly this.

---

## The ADCS Shortcut

**Type**: Active Directory Assessment
**Scenario**: Healthcare org, 15,000 endpoints, "mature" security program.
**Finding**: ADCS ESC1 misconfiguration — any authenticated user could request a certificate as any other user,
including Domain Admin.
**Impact**: Critical. Domain compromise from any user account in under 5 minutes.
**Kill Chain**: BloodHound enum → ADCS discovery (Certify) → ESC1 abuse → DA certificate → DCSync
**Lesson**: ADCS is the most overlooked attack surface in Active Directory. Most orgs have never audited their
certificate templates. Run Certify on every AD engagement.

---

## The Cloud Metadata Pivot

**Type**: Cloud Security Assessment (AWS)
**Scenario**: Fintech startup, microservices on EKS.
**Finding**: SSRF in image processing service → IMDSv1 accessible → IAM role had S3:* permissions → Production database
backups in S3 bucket.
**Impact**: Critical. Full production database access via chained low-to-medium findings.
**Kill Chain**: SSRF → IMDS → IAM creds → S3 enum → Database backups
**Lesson**: IMDSv2 should be enforced everywhere. SSRF + IMDS + overly permissive IAM = game over. Each finding alone
was a medium. Together they were catastrophic.
