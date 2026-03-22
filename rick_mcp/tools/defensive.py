"""Defensive security tools — hardening blueprints, incident response, detection rules, log analysis."""

from rick_mcp.constants import CALLSIGN
from rick_mcp.formatting import _fmt, _safe_tool
from rick_mcp.models import DetectionRulesInput, HardenInput, IncidentResponseInput, LogAnalysisInput


async def rick_hardening(params: HardenInput) -> str:
    """Defensive hardening checklists by technology. The builder side — break it, then hand them the blueprint to build it right."""
    blueprints = {
        "windows_server": {
            "technology": "Windows Server Hardening",
            "critical": [
                "Disable LLMNR and NBT-NS (Responder attacks) — GPO: Computer Config > Admin Templates > Network > DNS Client > Turn Off Multicast Name Resolution",
                "Enforce SMB signing — prevents relay attacks: Set 'Microsoft network server: Digitally sign communications (always)' = Enabled",
                "Disable NTLMv1 entirely — GPO: LAN Manager authentication level = Send NTLMv2 response only, refuse LM & NTLM",
                "Enable LAPS for local admin passwords — unique per machine, rotated automatically",
                "Patch management — WSUS/SCCM/Intune, max 30-day patch cycle for critical",
                "Disable Print Spooler on servers that don't print — PrintNightmare is forever",
                "Configure Windows Firewall — default deny inbound, allow only required services",
                "Enable Credential Guard on supported systems — protects LSASS from memory dumps",
            ],
            "quick_wins": [
                "Remove local admin rights from standard users",
                "Disable PowerShell v2 (downgrade attacks)",
                "Enable PowerShell ScriptBlock and Module logging",
                "Set account lockout policy (5 attempts, 30 min lockout)",
                "Disable WDigest authentication (plaintext cred caching)",
                "Remove unnecessary features/roles",
                "Enable audit logging (logon events, privilege use, object access)",
            ],
            "advanced": [
                "Implement tiered admin model (Tier 0/1/2)",
                "Deploy AppLocker/WDAC for application whitelisting",
                "Enable Attack Surface Reduction (ASR) rules",
                "Configure JEA (Just Enough Administration) for remote management",
                "Implement PAW (Privileged Access Workstations)",
                "Deploy Microsoft ATA/Defender for Identity",
            ],
            "rick_note": "LLMNR + SMB signing + LAPS = the holy trinity of quick wins. Do these three things and you've killed 60% of the common AD attack paths. The builder doesn't just find the crack — he shows you the mortar.",
        },
        "linux_server": {
            "technology": "Linux Server Hardening",
            "critical": [
                "SSH hardening: disable root login, key-only auth, change default port, AllowUsers directive",
                "Firewall: iptables/nftables/ufw — default deny, allow only required ports",
                "Automatic security updates: unattended-upgrades (Debian) / dnf-automatic (RHEL)",
                "Remove unnecessary SUID/SGID binaries: find / -perm /4000 -o -perm /2000",
                "Disable unused services: systemctl disable/mask",
                "File permissions: restrict /etc/shadow, /etc/sudoers, config files",
                "Kernel hardening: sysctl net.ipv4.conf.all.rp_filter=1, kernel.randomize_va_space=2",
            ],
            "quick_wins": [
                "Install and configure fail2ban for SSH brute force protection",
                "Set password complexity with PAM (pam_pwquality)",
                "Configure sudo with NOPASSWD sparingly — audit all sudoers entries",
                "Set umask 027 or 077 for new file defaults",
                "Disable core dumps: * hard core 0 in limits.conf",
                "Remove/restrict compiler tools on production servers",
                "Enable audit logging: auditd with key rules for sensitive files",
            ],
            "advanced": [
                "SELinux/AppArmor enforcement mode — not permissive, not disabled",
                "Implement filesystem integrity monitoring (AIDE, OSSEC)",
                "Container runtime security: rootless Docker, user namespaces",
                "Network segmentation with firewall zones",
                "Implement centralized logging (rsyslog to SIEM)",
                "CIS benchmark automation with OpenSCAP",
            ],
            "rick_note": "SSH key-only auth + fail2ban + remove SUID binaries = immediate threat reduction. Most Linux privesc comes from SUID, sudo misconfig, or cron jobs. Fix those three and you've done 80% of the work.",
        },
        "active_directory": {
            "technology": "Active Directory Hardening",
            "critical": [
                "ADCS: Audit all certificate templates — disable ESC1-ESC8 vulnerable templates. If Manager Approval isn't needed, remove enrollment rights from Domain Users",
                "Kerberos: Set AES-only encryption, disable RC4 (DES already disabled right?). Find and rotate Kerberoastable accounts with weak SPNs",
                "LAPS: Deploy everywhere. No shared local admin passwords. Period.",
                "Tiered admin model: Tier 0 (DC/ADCS), Tier 1 (servers), Tier 2 (workstations). Admins never cross tiers.",
                "Protected Users group: Add all admin accounts. Prevents NTLM, delegation, caching.",
                "GPP: Remove any lingering Group Policy Preference passwords (cpassword)",
                "AdminSDHolder: Monitor for modifications — attackers use this for persistence",
                "Disable LLMNR/NBT-NS/WPAD via GPO across entire domain",
            ],
            "quick_wins": [
                "Run BloodHound against your own domain — see what attackers see",
                "Find and disable accounts with 'Password Never Expires'",
                "Find and fix users with 'Do not require Kerberos preauthentication' (AS-REP Roastable)",
                "Audit Domain Admins group — minimize membership aggressively",
                "Enable AD audit logging (4768, 4769, 4776, 4624, 4625)",
                "Disable anonymous LDAP binding",
                "Set ms-DS-MachineAccountQuota to 0 (prevent users from joining rogue machines)",
            ],
            "advanced": [
                "Implement Red Forest (ESAE) or modern PAM architecture",
                "Deploy Microsoft Defender for Identity / ATA for anomaly detection",
                "Implement Authentication Policies and Silos",
                "Configure Fine-Grained Password Policies for admin accounts",
                "Monitor DCShadow, DCSync, and Golden Ticket indicators",
                "Regular Purple Team exercises against AD attack paths",
            ],
            "rick_note": "Run BloodHound on yourself before someone else does. ADCS templates are the #1 thing I find in AD engagements — most orgs have ESC1 vulnerable templates and don't even know it. Fix Kerberoasting by using gMSA accounts for services.",
        },
        "web_application": {
            "technology": "Web Application Hardening",
            "critical": [
                "Input validation: Server-side validation on ALL inputs. Never trust client-side. Parameterized queries for ALL database calls — no string concatenation, ever.",
                "Authentication: MFA everywhere. Bcrypt/Argon2 for password hashing (not MD5/SHA1). Account lockout with progressive delays.",
                "Session management: Secure, HttpOnly, SameSite=Strict cookies. Regenerate session ID on auth. Absolute + idle timeouts.",
                "HTTPS: TLS 1.2+ only. HSTS with preload. No mixed content.",
                "Security headers: CSP, X-Frame-Options, X-Content-Type-Options, Referrer-Policy, Permissions-Policy",
                "Access control: Server-side authorization on every request. IDOR checks on every resource access. Deny by default.",
                "File upload: Whitelist extensions, validate content type, store outside webroot, rename files, scan for malware",
            ],
            "quick_wins": [
                "Deploy security headers (one nginx/Apache config change)",
                "Enable CSRF tokens on all state-changing operations",
                "Remove verbose error messages and stack traces in production",
                "Disable directory listing",
                "Remove default/unused endpoints and admin panels",
                "Set appropriate CORS policy (not Access-Control-Allow-Origin: *)",
                "Implement rate limiting on auth endpoints",
            ],
            "advanced": [
                "Implement WAF (ModSecurity, AWS WAF, Cloudflare) as defense-in-depth",
                "Deploy RASP (Runtime Application Self-Protection)",
                "Implement Content Security Policy with nonce-based script loading",
                "Subresource Integrity (SRI) for all third-party scripts",
                "Implement request signing for APIs",
                "Security regression testing in CI/CD pipeline",
                "Regular DAST + manual pentest cycle",
            ],
            "rick_note": "Parameterized queries. Security headers. Server-side validation. These three things prevent 70% of web vulns. The rest is access control — check authorization on every request, not just the UI. Build it right from the foundation.",
        },
        "cloud_aws": {
            "technology": "AWS Cloud Hardening",
            "critical": [
                "IAM: Enforce MFA on all accounts, especially root. Use IAM roles, not access keys. Implement least privilege — use IAM Access Analyzer.",
                "S3: Block public access at account level. Enable default encryption. Enable access logging. Review bucket policies.",
                "CloudTrail: Enable in all regions. Enable log file validation. Send to S3 with lifecycle policy. Enable CloudWatch alerts.",
                "GuardDuty: Enable in all regions. Configure SNS notifications for findings.",
                "Networking: Use VPC flow logs. Security groups = deny all inbound by default. No 0.0.0.0/0 on SSH/RDP.",
                "IMDSv2: Require IMDSv2 on all EC2 instances (prevents SSRF metadata theft)",
                "KMS: Use customer-managed keys for sensitive data. Enable key rotation.",
            ],
            "quick_wins": [
                "Enable AWS Config for configuration compliance",
                "Run Prowler/ScoutSuite against your account",
                "Delete unused access keys and IAM users",
                "Enable S3 versioning on critical buckets",
                "Tag all resources for accountability",
                "Set up billing alerts (crypto mining detection)",
                "Enable EBS default encryption",
            ],
            "advanced": [
                "Implement AWS Organizations with SCPs",
                "Deploy AWS Control Tower for multi-account governance",
                "Implement PrivateLink for service-to-service communication",
                "Use AWS Secrets Manager with automatic rotation",
                "Implement AWS Config rules for continuous compliance",
                "Set up cross-account logging to security account",
            ],
            "rick_note": "IMDSv2 is the single most impactful quick win in AWS. It kills the SSRF-to-metadata attack chain. After that, IAM Access Analyzer to find overpermissioned roles. Most AWS compromises start with excessive IAM permissions.",
        },
        "cloud_azure": {
            "technology": "Azure Cloud Hardening",
            "critical": [
                "Entra ID (AAD): Enforce MFA for all users. Configure Conditional Access policies. Disable legacy authentication protocols.",
                "Azure AD Connect: If hybrid, secure the sync account. Monitor AADC server like a DC — it has DCSync rights.",
                "Storage: Disable public blob access. Enable defender for storage. Use private endpoints. Enable soft delete.",
                "NSG: Default deny inbound. No RDP/SSH from 0.0.0.0/0. Use Azure Bastion instead.",
                "Key Vault: Use managed identities instead of secrets where possible. Enable soft delete and purge protection.",
                "Defender for Cloud: Enable on all subscriptions. Set to Enhanced tier for workloads.",
                "Activity Log: Send to Log Analytics workspace. Set up alerts for admin actions.",
            ],
            "quick_wins": [
                "Run ScoutSuite/Prowler against your tenant",
                "Enable Security Defaults if no Conditional Access",
                "Review and remove stale guest accounts",
                "Audit app registrations and service principal permissions",
                "Enable diagnostic logging on all resources",
                "Review RBAC assignments — remove Owner at subscription level",
                "Disable SSPR for admin accounts (or add extra verification)",
            ],
            "advanced": [
                "Implement PIM (Privileged Identity Management) for JIT admin access",
                "Deploy Azure Policy for compliance guardrails",
                "Configure Managed Identity wherever possible (eliminate secrets)",
                "Implement Landing Zones with management group hierarchy",
                "Set up Microsoft Sentinel for SIEM/SOAR",
                "Configure ADCS (if on-prem) with hardened templates before AAD integration",
            ],
            "rick_note": "Azure AD Connect sync server is Tier 0 — protect it like a domain controller because it essentially IS one. Conditional Access + PIM + managed identities = the Azure hardening trifecta. Most Azure compromises I see start with overpermissioned service principals.",
        },
        "kubernetes": {
            "technology": "Kubernetes Hardening",
            "critical": [
                "RBAC: Least privilege. No cluster-admin for service accounts. Audit all ClusterRoleBindings.",
                "Pod Security: Enforce pod security standards (restricted). No privileged containers. No root containers.",
                "Network Policies: Default deny all ingress/egress. Whitelist only required communication.",
                "Secrets: Use external secrets manager (Vault, AWS SM, Azure KV). Don't store secrets in etcd unencrypted.",
                "API Server: Enable audit logging. Restrict anonymous access. Use OIDC for user auth.",
                "Node Security: Keep kubelet read-only port disabled. Restrict node access. Patch nodes regularly.",
                "Image Security: Use private registries. Scan images with trivy/grype. Enforce signed images.",
            ],
            "quick_wins": [
                "Run kube-bench against CIS Kubernetes Benchmark",
                "Remove default service account token automounting (automountServiceAccountToken: false)",
                "Set resource limits on all pods (prevent resource abuse)",
                "Disable hostNetwork, hostPID, hostIPC in pod specs",
                "Don't mount Docker socket into containers",
                "Review all namespaces for overpermissioned service accounts",
                "Enable OPA/Kyverno for policy enforcement",
            ],
            "advanced": [
                "Implement service mesh (Istio/Linkerd) for mTLS between services",
                "Deploy Falco for runtime threat detection",
                "Implement GitOps with sealed secrets",
                "Configure pod-to-pod encryption",
                "Implement multi-tenancy with namespace isolation",
                "Regular penetration testing of cluster (kube-hunter, peirates)",
            ],
            "rick_note": "Docker socket mount = game over. Service account token automounting = free lateral movement. Fix these two things first. Then network policies — default deny is the only sane default. Container security is construction inspection — check the structural integrity of every pod.",
        },
        "network": {
            "technology": "Network Infrastructure Hardening",
            "critical": [
                "Segmentation: Implement proper VLANs and firewall zones. DMZ for public-facing. Management VLAN isolated.",
                "Authentication: TACACS+/RADIUS for all device auth. No local-only accounts on network devices.",
                "Encryption: SSH only (no telnet). SNMPv3 (no v1/v2c with community strings). Encrypted management.",
                "Access Control: ACLs on all inter-VLAN routing. Management access from jump box only.",
                "Port Security: 802.1X for network access control. Disable unused ports. No trunk ports to user VLANs.",
                "Firmware: Keep network device firmware current. Subscribe to vendor security advisories.",
            ],
            "quick_wins": [
                "Change all default credentials (yes, people still forget this)",
                "Disable Telnet and HTTP management — SSH and HTTPS only",
                "Replace SNMPv1/v2c with SNMPv3 (or disable SNMP entirely)",
                "Disable CDP/LLDP on user-facing ports",
                "Enable logging to centralized syslog",
                "Disable unused services (finger, small-servers, etc.)",
                "Set login banner with legal warning",
            ],
            "advanced": [
                "Implement NAC (Network Access Control) with posture checking",
                "Deploy network IDS/IPS at segment boundaries",
                "Implement DNS sinkholing for malware domains",
                "Configure DNSSEC",
                "Implement BGP security (RPKI, route filtering)",
                "Regular network architecture review and threat modeling",
            ],
            "rick_note": "SNMP community strings and default creds — I find these on almost every internal pentest. It takes 5 minutes to check and 5 minutes to fix. Segmentation is the big one — flat networks are a pentester's playground.",
        },
        "database": {
            "technology": "Database Hardening",
            "critical": [
                "Authentication: No default credentials. Strong passwords. Integrated auth (Windows/Kerberos) where possible.",
                "Authorization: Principle of least privilege. No app accounts with SA/DBA rights. Separate read/write roles.",
                "Network: Database not directly internet-accessible. Firewall to application tier only. Encrypted connections (TLS).",
                "MSSQL: Disable xp_cmdshell. Remove unnecessary linked servers. Disable sa account or set very strong password.",
                "MySQL: Remove anonymous users and test databases. Set bind-address to specific IP. Disable local_infile.",
                "PostgreSQL: Configure pg_hba.conf restrictively. Disable trust authentication. Set password_encryption = scram-sha-256.",
                "Encryption: Enable TDE for data at rest. TLS for data in transit. Encrypt backups.",
            ],
            "quick_wins": [
                "Run vendor security assessment tool (DBSAT for Oracle, etc.)",
                "Remove default/sample databases",
                "Audit all database users and their privileges",
                "Enable audit logging for DDL, DML on sensitive tables, and logon/logoff",
                "Disable unnecessary features and stored procedures",
                "Set up automated backup with encryption and testing",
                "Review and restrict linked server configurations (MSSQL)",
            ],
            "advanced": [
                "Implement database activity monitoring (DAM)",
                "Deploy dynamic data masking for non-production environments",
                "Implement row-level security for multi-tenant apps",
                "Set up database firewall/proxy (ProxySQL, pgbouncer with auth)",
                "Regular vulnerability scanning of database instances",
                "Implement secrets rotation for application database credentials",
            ],
            "rick_note": "xp_cmdshell on MSSQL and COPY TO PROGRAM on PostgreSQL — these are the RCE shortcuts. Disable them. Linked servers in MSSQL are lateral movement highways — audit every single one. The database is the crown jewels — harden it like the vault it is.",
        },
    }
    t = params.technology.lower().strip()
    bp = blueprints.get(t)
    if not bp:
        return f"Error: Unknown technology '{t}'. Available: {', '.join(blueprints.keys())}"

    # Filter by priority if requested
    priority = (params.priority or "all").lower()
    if priority == "critical":
        bp = {k: v for k, v in bp.items() if k in ("technology", "critical", "rick_note")}
    elif priority == "quick_wins":
        bp = {k: v for k, v in bp.items() if k in ("technology", "quick_wins", "rick_note")}

    return _fmt(bp, params.response_format, title=f"{CALLSIGN} Hardening Blueprint")


async def rick_incident_response(params: IncidentResponseInput) -> str:
    """IR playbook by incident type. Containment, eradication, recovery — the full cycle."""
    playbooks = {
        "ransomware": {
            "incident_type": "Ransomware",
            "containment": [
                "IMMEDIATE: Isolate affected systems from network (disconnect, don't power off)",
                "Identify patient zero and initial infection vector",
                "Block C2 domains/IPs at firewall and DNS",
                "Disable compromised accounts",
                "Preserve evidence — snapshot affected systems before remediation",
                "Activate incident response team and establish war room",
                "Notify legal and executive leadership",
                "DO NOT pay ransom without exhausting all recovery options",
            ],
            "eradication": [
                "Identify ransomware variant (ID Ransomware, ransom note analysis)",
                "Check for available decryptors (nomoreransom.org)",
                "Scan all systems for ransomware IOCs and persistence mechanisms",
                "Remove all malware artifacts, backdoors, and persistence",
                "Reset all credentials — assume full domain compromise",
                "Patch the vulnerability used for initial access",
                "Rebuild compromised systems from known-good images",
            ],
            "recovery": [
                "Restore from verified clean backups (test backup integrity first)",
                "Rebuild domain controllers if AD was compromised",
                "Restore systems in priority order (critical business functions first)",
                "Monitor restored systems closely for re-infection indicators",
                "Validate data integrity post-restore",
                "Implement enhanced monitoring on all restored systems",
                "Gradual network reconnection with validation at each step",
            ],
            "lessons_learned": [
                "How did initial access occur? Fix the root cause.",
                "Were backups adequate and tested? Implement 3-2-1 backup strategy.",
                "Was detection timely? Improve monitoring and alerting.",
                "Was the IR plan adequate? Update based on findings.",
                "Document full timeline for legal/insurance purposes.",
            ],
            "tools": ["Velociraptor", "KAPE", "FTK Imager", "Volatility", "YARA", "CrowdStrike Falcon"],
            "rick_note": "Don't turn off machines — you'll lose volatile memory evidence. Isolate, image, investigate. And NEVER pay without exhausting every option. The attackers' decryptor fails 30% of the time anyway.",
        },
        "data_breach": {
            "incident_type": "Data Breach",
            "containment": [
                "Identify scope — what data was accessed/exfiltrated",
                "Preserve all logs (web, application, database, network)",
                "Block the exfiltration channel (IP, domain, protocol)",
                "Revoke compromised API keys, tokens, and credentials",
                "Isolate affected databases and applications",
                "Engage legal counsel — breach notification requirements vary by jurisdiction",
                "Document everything from minute one",
            ],
            "eradication": [
                "Identify and patch the vulnerability exploited",
                "Remove attacker access (backdoors, web shells, rogue accounts)",
                "Audit all access controls on affected data stores",
                "Review and restrict database permissions",
                "Implement additional monitoring on compromised systems",
                "Rotate all secrets and credentials related to affected systems",
            ],
            "recovery": [
                "Verify data integrity in affected databases",
                "Restore any modified data from clean backups",
                "Implement enhanced access controls and monitoring",
                "Deploy DLP solutions to prevent future exfiltration",
                "Prepare breach notification per legal requirements (GDPR: 72 hours)",
                "Engage PR/communications for stakeholder notification",
                "Offer credit monitoring if PII was compromised",
            ],
            "lessons_learned": [
                "Was data classification in place? Classify and label sensitive data.",
                "Were access controls appropriate? Implement least privilege.",
                "Was exfiltration detected in real-time? Improve DLP and monitoring.",
                "Were notification requirements met? Review compliance obligations.",
                "Was encryption at rest in place? Encrypt all sensitive data stores.",
            ],
            "tools": ["Splunk", "ELK Stack", "Velociraptor", "KAPE", "NetworkMiner", "Wireshark"],
            "rick_note": "The clock starts ticking the moment you confirm the breach. GDPR gives you 72 hours for notification. Document everything — timestamps, actions taken, decisions made. Legal will need every detail.",
        },
        "insider_threat": {
            "incident_type": "Insider Threat",
            "containment": [
                "DO NOT alert the insider — coordinate with HR and legal first",
                "Increase monitoring on suspect's accounts and systems",
                "Preserve all email, file access, and network logs",
                "Audit recent data access and file transfers",
                "Restrict access to sensitive systems without tipping off",
                "Coordinate with legal on employee privacy requirements",
                "Document chain of custody for all evidence",
            ],
            "eradication": [
                "Work with HR on formal investigation and disciplinary process",
                "Revoke all access upon HR/legal approval",
                "Audit all systems the insider had access to",
                "Check for data exfiltration (USB, cloud storage, email forwards)",
                "Review for planted backdoors or persistence mechanisms",
                "Identify any accomplices or compromised colleagues",
            ],
            "recovery": [
                "Rotate all credentials the insider had access to",
                "Review and revoke any delegated permissions",
                "Audit shared accounts and service accounts",
                "Implement enhanced access monitoring",
                "Review and update access control policies",
                "Conduct damage assessment on exposed data/systems",
            ],
            "lessons_learned": [
                "Were behavioral indicators missed? Implement UEBA.",
                "Was least privilege enforced? Review access control model.",
                "Was data loss prevention in place? Implement DLP.",
                "Were audit logs sufficient? Enhance logging and monitoring.",
                "Was there an insider threat program? Establish or improve one.",
            ],
            "tools": [
                "Splunk UBA",
                "Microsoft Sentinel",
                "DLP solutions",
                "UEBA platforms",
                "Digital forensics toolkit",
            ],
            "rick_note": "Insider threats are the hardest to detect and the most damaging. The key is behavioral baselines — you can't spot anomalies without knowing what normal looks like. And always coordinate with HR and legal before taking action.",
        },
        "bec": {
            "incident_type": "Business Email Compromise",
            "containment": [
                "Identify all compromised email accounts",
                "Force password reset and revoke all active sessions",
                "Enable MFA immediately on compromised accounts",
                "Review and remove malicious inbox rules (forwarding, delegation)",
                "Check for OAuth app consents granted by compromised account",
                "Block malicious IPs/domains at email gateway",
                "Alert financial team if wire transfer fraud is suspected",
                "Contact bank immediately if funds were transferred (within 24-48 hours for recall)",
            ],
            "eradication": [
                "Audit all email rules across the organization",
                "Review OAuth/app permissions for all accounts",
                "Check for lateral phishing sent from compromised account",
                "Remove any persistent access (legacy auth, app passwords)",
                "Scan for credential harvesting infrastructure",
                "Review conditional access policies for gaps",
            ],
            "recovery": [
                "Implement conditional access policies blocking legacy auth",
                "Deploy email authentication (SPF, DKIM, DMARC = reject)",
                "Enable MFA for all accounts (if not already)",
                "Implement anti-phishing policies in email gateway",
                "Train employees on BEC indicators and reporting",
                "Establish out-of-band verification for financial requests",
                "Review and update email security policies",
            ],
            "lessons_learned": [
                "Was MFA enforced? It should be mandatory, not optional.",
                "Were email authentication records (SPF/DKIM/DMARC) properly configured?",
                "Was there a financial verification procedure for wire transfers?",
                "Were users trained to recognize BEC attempts?",
                "Was legacy authentication still enabled?",
            ],
            "tools": ["Microsoft 365 Security Center", "Email header analyzers", "Hawk (M365 IR)", "AADInternals"],
            "rick_note": "BEC is the #1 financial loss vector in cybercrime. The attacker doesn't need malware — they just need one compromised email and a convincing invoice. Out-of-band verification for all financial requests. Period.",
        },
        "supply_chain": {
            "incident_type": "Supply Chain Compromise",
            "containment": [
                "Identify affected software/components and their deployment scope",
                "Isolate systems running compromised software versions",
                "Block update servers/domains for compromised vendor",
                "Freeze all deployments and CI/CD pipelines pending review",
                "Inventory all systems and environments with affected components",
                "Contact vendor for IOCs and remediation guidance",
                "Activate third-party breach clause in vendor contracts",
            ],
            "eradication": [
                "Remove or rollback compromised software to known-good version",
                "Scan all systems for IOCs provided by vendor/community",
                "Audit CI/CD pipelines for tampered build artifacts",
                "Verify integrity of all software dependencies (checksums, signatures)",
                "Remove any backdoors or persistence planted via compromised software",
                "Review and rotate secrets accessible to compromised components",
            ],
            "recovery": [
                "Rebuild affected systems from verified clean images",
                "Re-deploy applications with verified clean dependencies",
                "Implement software composition analysis (SCA) in CI/CD",
                "Set up dependency monitoring (Dependabot, Snyk, etc.)",
                "Review and strengthen vendor security requirements",
                "Implement binary authorization for container deployments",
            ],
            "lessons_learned": [
                "Was SBOM (Software Bill of Materials) maintained?",
                "Were dependencies pinned to specific verified versions?",
                "Was there a process for vendor security assessment?",
                "Were build artifacts signed and verified?",
                "Was there visibility into third-party code changes?",
            ],
            "tools": ["Snyk", "Dependabot", "OWASP Dependency-Check", "Sigstore/cosign", "Syft (SBOM)", "Grype"],
            "rick_note": "SolarWinds changed everything. You can't trust your supply chain blindly. SBOM, dependency pinning, build verification — these aren't optional anymore. If you can't verify it, you can't trust it.",
        },
    }

    it = params.incident_type.lower().strip()
    playbook = playbooks.get(it)
    if not playbook:
        return f"Error: Unknown incident type '{it}'. Available: {', '.join(playbooks.keys())}"

    return _fmt(playbook, params.response_format, title=f"{CALLSIGN} Incident Response Playbook")


async def rick_detection_rules(params: DetectionRulesInput) -> str:
    """Generate Sigma/YARA rule templates for common attack patterns. Purple team tradecraft."""
    rules = {
        "credential_dumping": {
            "pattern": "Credential Dumping Detection",
            "sigma_template": """title: LSASS Memory Access Detection
id: rick-sigma-cred-001
status: experimental
description: Detects potential LSASS memory access for credential dumping
logsource:
    category: process_access
    product: windows
detection:
    selection:
        TargetImage|endswith: '\\\\lsass.exe'
        GrantedAccess|contains:
            - '0x1010'
            - '0x1038'
            - '0x1F0FFF'
            - '0x1F1FFF'
    filter:
        SourceImage|endswith:
            - '\\\\wmiprvse.exe'
            - '\\\\svchost.exe'
    condition: selection and not filter
level: critical
tags:
    - attack.credential_access
    - attack.t1003.001""",
            "yara_template": """rule credential_dump_strings {
    meta:
        description = "Detects credential dumping tool artifacts"
        author = "j1v37u2k3y"
        mitre = "T1003"
    strings:
        $s1 = "sekurlsa::logonpasswords" ascii wide nocase
        $s2 = "lsadump::dcsync" ascii wide nocase
        $s3 = "token::elevate" ascii wide nocase
        $s4 = "privilege::debug" ascii wide nocase
        $s5 = "MiniDumpWriteDump" ascii wide
    condition:
        2 of them
}""",
            "log_sources": ["Sysmon Event ID 10 (ProcessAccess)", "Windows Security 4656/4663", "EDR telemetry"],
            "mitre_mapping": ["T1003.001 — LSASS Memory", "T1003.002 — SAM", "T1003.003 — NTDS", "T1003.006 — DCSync"],
            "rick_note": "LSASS access is the canary in the coal mine. If you see process access to lsass.exe with suspicious granted access masks, investigate immediately. Credential Guard prevents most of this — deploy it.",
        },
        "lateral_movement": {
            "pattern": "Lateral Movement Detection",
            "sigma_template": """title: Suspicious Remote Service Creation
id: rick-sigma-lateral-001
status: experimental
description: Detects remote service creation indicative of PSExec or similar tools
logsource:
    product: windows
    service: system
detection:
    selection:
        EventID: 7045
        ServiceFileName|contains:
            - 'ADMIN$'
            - '\\\\\\\\127.0.0.1'
            - 'cmd.exe /c'
            - 'powershell'
    condition: selection
level: high
tags:
    - attack.lateral_movement
    - attack.t1021.002""",
            "yara_template": """rule lateral_movement_tool {
    meta:
        description = "Detects common lateral movement tool artifacts"
        author = "j1v37u2k3y"
        mitre = "T1021"
    strings:
        $psexec = "psexec" ascii wide nocase
        $wmiexec = "wmiexec" ascii wide nocase
        $smbexec = "smbexec" ascii wide nocase
        $atexec = "atexec" ascii wide nocase
        $dcomexec = "dcomexec" ascii wide nocase
    condition:
        any of them
}""",
            "log_sources": [
                "Windows System Event 7045",
                "Windows Security 4624 Type 3",
                "Sysmon Event ID 1/3",
                "Windows Security 4648",
            ],
            "mitre_mapping": [
                "T1021.002 — SMB/Admin Shares",
                "T1021.006 — Windows Remote Management",
                "T1047 — WMI",
                "T1021.001 — RDP",
            ],
            "rick_note": "Type 3 logon events from unexpected sources are your best lateral movement indicator. Combine with service creation events (7045) and you'll catch PSExec-style movement. Also watch for named pipe creation — Sysmon 17/18.",
        },
        "c2_beaconing": {
            "pattern": "C2 Beaconing Detection",
            "sigma_template": """title: Periodic DNS/HTTP Beaconing Pattern
id: rick-sigma-c2-001
status: experimental
description: Detects periodic network connections indicative of C2 beaconing
logsource:
    category: proxy
detection:
    selection:
        cs-method: 'GET'
    filter_legitimate:
        cs-host|endswith:
            - '.microsoft.com'
            - '.windows.com'
            - '.google.com'
    timeframe: 1h
    condition: selection and not filter_legitimate | count(cs-uri-stem) by cs-host > 60
level: medium
tags:
    - attack.command_and_control
    - attack.t1071.001""",
            "yara_template": """rule c2_beacon_config {
    meta:
        description = "Detects C2 beacon configuration artifacts"
        author = "j1v37u2k3y"
        mitre = "T1071"
    strings:
        $cfg1 = "sleeptime" ascii wide nocase
        $cfg2 = "jitter" ascii wide nocase
        $cfg3 = "publickey" ascii wide
        $cfg4 = "C2Server" ascii wide
        $ua = "Mozilla/5.0" ascii wide
    condition:
        3 of ($cfg*) or ($cfg4 and $ua)
}""",
            "log_sources": ["DNS query logs", "Proxy/Web gateway logs", "Netflow data", "Zeek/Bro connection logs"],
            "mitre_mapping": [
                "T1071.001 — Web Protocols",
                "T1071.004 — DNS",
                "T1573 — Encrypted Channel",
                "T1572 — Protocol Tunneling",
            ],
            "rick_note": "Beaconing is all about patterns. Look for consistent intervals (even with jitter), fixed packet sizes, and connections to recently registered domains. Statistical analysis beats signature matching for C2 detection.",
        },
        "data_exfil": {
            "pattern": "Data Exfiltration Detection",
            "sigma_template": """title: Large Outbound Data Transfer
id: rick-sigma-exfil-001
status: experimental
description: Detects unusually large outbound data transfers
logsource:
    category: firewall
detection:
    selection:
        action: 'allow'
        direction: 'outbound'
    filter_internal:
        dst_ip|startswith:
            - '10.'
            - '172.16.'
            - '192.168.'
    condition: selection and not filter_internal | sum(bytes_out) by src_ip > 104857600
    timeframe: 1h
level: high
tags:
    - attack.exfiltration
    - attack.t1048""",
            "yara_template": """rule staging_compression {
    meta:
        description = "Detects data staging with compression for exfiltration"
        author = "j1v37u2k3y"
        mitre = "T1560"
    strings:
        $rar = "Rar!" ascii
        $7z = { 37 7A BC AF 27 1C }
        $zip_password = "zip -P" ascii nocase
        $tar_gz = "tar czf" ascii
        $makecab = "makecab" ascii nocase
    condition:
        any of them
}""",
            "log_sources": [
                "Firewall logs (outbound bytes)",
                "DLP alerts",
                "Cloud storage audit logs",
                "DNS query volume anomalies",
            ],
            "mitre_mapping": [
                "T1048 — Exfiltration Over Alternative Protocol",
                "T1041 — Exfiltration Over C2",
                "T1567 — Exfiltration Over Web Service",
                "T1560 — Archive Collected Data",
            ],
            "rick_note": "Baseline your normal outbound traffic first. Without a baseline, every large transfer looks suspicious and you'll drown in false positives. Watch for data staging behavior — compression, encryption, and chunking before transfer.",
        },
        "persistence": {
            "pattern": "Persistence Mechanism Detection",
            "sigma_template": """title: Suspicious Registry Run Key Modification
id: rick-sigma-persist-001
status: experimental
description: Detects modifications to registry run keys for persistence
logsource:
    product: windows
    category: registry_set
detection:
    selection:
        TargetObject|contains:
            - '\\\\CurrentVersion\\\\Run'
            - '\\\\CurrentVersion\\\\RunOnce'
        Details|contains:
            - 'powershell'
            - 'cmd.exe'
            - 'mshta'
            - 'wscript'
            - 'cscript'
            - 'AppData'
            - 'Temp'
    condition: selection
level: high
tags:
    - attack.persistence
    - attack.t1547.001""",
            "yara_template": """rule persistence_mechanism {
    meta:
        description = "Detects persistence mechanism setup artifacts"
        author = "j1v37u2k3y"
        mitre = "T1547"
    strings:
        $reg1 = "reg add" ascii wide nocase
        $reg2 = "CurrentVersion\\\\Run" ascii wide
        $schtask = "schtasks /create" ascii wide nocase
        $wmi_persist = "__EventFilter" ascii wide
        $startup = "\\\\Start Menu\\\\Programs\\\\Startup" ascii wide
    condition:
        2 of them
}""",
            "log_sources": [
                "Sysmon Event ID 12/13/14 (Registry)",
                "Sysmon Event ID 11 (FileCreate in startup)",
                "Windows Security 4698 (Scheduled Task)",
                "WMI Activity logs",
            ],
            "mitre_mapping": [
                "T1547.001 — Registry Run Keys",
                "T1053.005 — Scheduled Task",
                "T1546.003 — WMI Event Subscription",
                "T1547.009 — Shortcut Modification",
            ],
            "rick_note": "Autoruns is your best friend for persistence hunting. Monitor the registry run keys, scheduled tasks, and WMI subscriptions. If you're not watching Sysmon events 12/13, you're blind to half the persistence techniques out there.",
        },
        "privilege_escalation": {
            "pattern": "Privilege Escalation Detection",
            "sigma_template": """title: Suspicious Token Manipulation
id: rick-sigma-privesc-001
status: experimental
description: Detects potential token impersonation and privilege escalation
logsource:
    product: windows
    service: security
detection:
    selection_token:
        EventID: 4672
    selection_user:
        SubjectUserName|endswith: '$'
    filter_system:
        SubjectUserName:
            - 'SYSTEM'
            - 'LOCAL SERVICE'
            - 'NETWORK SERVICE'
    condition: selection_token and not selection_user and not filter_system
level: high
tags:
    - attack.privilege_escalation
    - attack.t1134""",
            "yara_template": """rule privesc_tool {
    meta:
        description = "Detects privilege escalation tool artifacts"
        author = "j1v37u2k3y"
        mitre = "T1134"
    strings:
        $potato1 = "JuicyPotato" ascii wide nocase
        $potato2 = "PrintSpoofer" ascii wide nocase
        $potato3 = "GodPotato" ascii wide nocase
        $potato4 = "SweetPotato" ascii wide nocase
        $uac = "UACBypass" ascii wide nocase
        $impersonate = "ImpersonateNamedPipeClient" ascii wide
    condition:
        any of them
}""",
            "log_sources": [
                "Windows Security 4672 (Special Privileges)",
                "Windows Security 4673 (Privileged Service)",
                "Sysmon Event ID 1 (Process Create)",
                "ETW Microsoft-Windows-Kernel-Process",
            ],
            "mitre_mapping": [
                "T1134 — Access Token Manipulation",
                "T1068 — Exploitation for Privilege Escalation",
                "T1548.002 — UAC Bypass",
                "T1543.003 — Windows Service",
            ],
            "rick_note": "The Potato family keeps growing — JuicyPotato, PrintSpoofer, GodPotato, SweetPotato. Monitor for SeImpersonatePrivilege abuse. If a service account has this privilege and it's compromised, it's game over for local privesc.",
        },
    }

    ap = params.attack_pattern.lower().strip()
    rule = rules.get(ap)
    if not rule:
        return f"Error: Unknown attack pattern '{ap}'. Available: {', '.join(rules.keys())}"

    rule["authorization"] = "AUTHORIZED DETECTION ENGINEERING ONLY"
    return _fmt(rule, params.response_format, title=f"{CALLSIGN} Detection Rules")


async def rick_log_analysis(params: LogAnalysisInput) -> str:
    """Log review methodology by source. What to look for, IOCs, and tools."""
    guides = {
        "windows_event": {
            "source": "Windows Event Logs",
            "what_to_look_for": [
                "4624/4625 — Successful/Failed logons (watch Type 3=network, Type 10=RDP)",
                "4648 — Explicit credential logon (RunAs, mapped drives with different creds)",
                "4672 — Special privileges assigned (admin logon)",
                "4688 — Process creation (enable command line logging!)",
                "4697/7045 — Service installation (PSExec, persistence)",
                "4698/4702 — Scheduled task created/modified",
                "4720/4726 — User account created/deleted",
                "4732/4733 — Member added/removed from security group",
                "4768/4769 — Kerberos TGT/TGS requests (Kerberoasting)",
                "4776 — NTLM authentication (credential validation)",
                "1102 — Audit log cleared (anti-forensics!)",
            ],
            "key_iocs": [
                "Multiple 4625 events from single source (brute force)",
                "4624 Type 3 from unusual workstations to servers",
                "4672 on non-admin accounts (privilege escalation)",
                "Service installations with suspicious paths or names",
                "Event log clearing (1102) — massive red flag",
                "TGS requests for service accounts (Kerberoasting indicator)",
                "Process creation with encoded PowerShell (-enc, -encodedcommand)",
            ],
            "tools": [
                "Event Viewer",
                "Get-WinEvent (PowerShell)",
                "EvtxECmd (Eric Zimmerman)",
                "Chainsaw",
                "Hayabusa",
                "Sigma + sigmac",
            ],
            "rick_note": "Enable command line logging in 4688 events — without it, you see process creation but not WHAT was executed. That's like seeing someone entered a room but not what they did inside. Also enable PowerShell ScriptBlock logging — 4104 is gold.",
        },
        "syslog": {
            "source": "Linux Syslog",
            "what_to_look_for": [
                "auth.log / secure — SSH logins, sudo usage, PAM events",
                "Failed SSH attempts — possible brute force",
                "Successful SSH from unexpected IPs or at unusual times",
                "sudo commands — especially unusual commands from unexpected users",
                "Cron job modifications — persistence mechanism",
                "User/group creation or modification",
                "Package installation (apt, yum) — unauthorized software",
                "Kernel messages — module loading, capability changes",
                "systemd — service start/stop/enable patterns",
            ],
            "key_iocs": [
                "Rapid failed SSH attempts from single IP (brute force)",
                "SSH login from foreign IP followed by privilege escalation",
                "New cron jobs in /etc/crontab or user crontabs",
                "sudo to root from unexpected user accounts",
                "Kernel module loading (insmod/modprobe) — rootkit indicator",
                "Unexpected service creation or modification",
                "Binary execution from /tmp, /dev/shm, or /var/tmp",
            ],
            "tools": ["journalctl", "grep/awk/sed", "Lnav (log navigator)", "GoAccess", "OSSEC", "Wazuh"],
            "rick_note": "auth.log is your lifeline on Linux. If it's been tampered with or cleared, that tells you something too. Configure remote syslog to a hardened log server — attackers can't delete what they can't reach.",
        },
        "cloud_trail": {
            "source": "Cloud Audit Trails (AWS CloudTrail / Azure Activity Log / GCP Audit Log)",
            "what_to_look_for": [
                "ConsoleLogin events — especially from unusual locations or without MFA",
                "IAM policy changes — CreatePolicy, AttachUserPolicy, PutRolePolicy",
                "Security group modifications — AuthorizeSecurityGroupIngress",
                "S3/Storage bucket policy changes — public access granted",
                "EC2/VM instance creation in unusual regions",
                "Lambda/Function creation or modification",
                "Key/secret creation and access patterns",
                "CloudTrail/logging disabled or modified (anti-forensics)",
                "AssumeRole calls — cross-account access patterns",
            ],
            "key_iocs": [
                "Console login from new geographic location without MFA",
                "Rapid IAM policy modifications (privilege escalation)",
                "S3 bucket made public after years of being private",
                "EC2 instances launched in regions you don't use (crypto mining)",
                "CloudTrail stopped or trail deleted (immediate investigation)",
                "Unusual API calls from service accounts",
                "Access key usage from IP addresses outside your ranges",
            ],
            "tools": [
                "AWS CloudTrail + Athena",
                "Azure Monitor + Log Analytics",
                "GCP Cloud Audit Logs",
                "ScoutSuite",
                "Prowler",
                "CloudQuery",
            ],
            "rick_note": "If CloudTrail gets turned off, that's your five-alarm fire. It means someone with admin access is covering their tracks. Enable CloudTrail in ALL regions with log file validation — attackers love spinning up resources in regions you're not watching.",
        },
        "web_server": {
            "source": "Web Server Logs (Apache, Nginx, IIS)",
            "what_to_look_for": [
                "4xx/5xx error spikes — scanning/fuzzing activity",
                "Directory traversal attempts (../, %2e%2e%2f)",
                "SQL injection patterns (UNION SELECT, ' OR 1=1, SLEEP())",
                "XSS attempts in parameters (<script>, javascript:, onerror)",
                "Unusual user agents (sqlmap, nikto, gobuster, nuclei)",
                "POST requests to unexpected endpoints",
                "Large response sizes from endpoints that should return small data",
                "Authentication endpoint abuse (credential stuffing)",
                "Path traversal to sensitive files (/etc/passwd, web.config)",
            ],
            "key_iocs": [
                "Massive 404 spike from single IP (directory brute-force)",
                "SQL error messages in response (misconfigured error handling)",
                "Sequential parameter fuzzing patterns",
                "Web shell access patterns (POST to unusual file, cmd/exec parameters)",
                "Successful access to admin panels from external IPs",
                "File upload followed by direct access to uploaded file",
                "Request patterns matching known exploit paths",
            ],
            "tools": ["GoAccess", "AWStats", "ELK Stack", "Splunk", "OWASP ModSecurity", "fail2ban"],
            "rick_note": "Most web attacks leave clear signatures in access logs — but only if you're looking. The trick is filtering signal from noise. Start with unusual response codes, then unusual user agents, then unusual parameter patterns. Layer your analysis.",
        },
        "firewall": {
            "source": "Firewall Logs",
            "what_to_look_for": [
                "Denied outbound connections — C2 attempts blocked",
                "Port scanning patterns — sequential ports from single source",
                "Connections to known malicious IPs/domains (threat intel feeds)",
                "Unusual protocol usage on standard ports (DNS tunneling on 53)",
                "Large outbound data transfers (data exfiltration)",
                "Internal-to-internal denied traffic (lateral movement attempts)",
                "Connections to TOR exit nodes or anonymization services",
                "New outbound connections to unusual countries",
            ],
            "key_iocs": [
                "Denied connection attempts to known C2 infrastructure",
                "Internal host scanning multiple internal IPs on same port",
                "High-volume DNS queries to single domain (DNS tunneling)",
                "Outbound connections on unusual ports (4444, 5555, 8888)",
                "Beaconing patterns — regular interval connections to same destination",
                "Sudden spike in outbound traffic volume from single host",
                "Internal host connecting to DMZ systems it normally doesn't",
            ],
            "tools": [
                "pfSense/OPNsense dashboards",
                "FortiAnalyzer",
                "Palo Alto Panorama",
                "Splunk",
                "Graylog",
                "Zeek/Bro",
            ],
            "rick_note": "Denied outbound connections are gold — they tell you something TRIED to talk to the outside and was blocked. Aggregate and analyze denied connections before allowed ones. Also, baseline your DNS traffic — DNS tunneling hides in plain sight.",
        },
        "dns": {
            "source": "DNS Logs",
            "what_to_look_for": [
                "Queries to newly registered domains (< 30 days old)",
                "High-entropy domain names (DGA — Domain Generation Algorithm)",
                "Unusually long subdomain labels (DNS tunneling)",
                "High query volume to single domain (C2 beaconing or tunneling)",
                "TXT record queries (often used for C2 data transfer)",
                "Queries for domains on threat intelligence blocklists",
                "NXDOMAIN response spikes (DGA domains or fast-flux)",
                "PTR lookups for internal IP ranges (network recon)",
            ],
            "key_iocs": [
                "Subdomains > 50 characters (DNS tunneling indicator)",
                "Query frequency > 1 per second to same domain (aggressive tunneling)",
                "TXT record queries to unusual domains (data exfil channel)",
                "Multiple NXDOMAIN responses for similar domain patterns (DGA)",
                "Queries for known C2/malware domains",
                "DNS queries to non-standard resolvers (8.8.8.8 from internal net)",
                "ANY/AXFR queries from non-DNS servers (zone transfer attempts)",
            ],
            "tools": [
                "Zeek/Bro DNS logs",
                "PassiveDNS",
                "dnstwist",
                "Splunk DNS Analytics",
                "Infoblox",
                "BIND query logging",
            ],
            "rick_note": "DNS is the protocol everyone forgets to monitor. It's allowed through almost every firewall, it's rarely inspected, and attackers know it. If you only add one new data source to your SIEM, make it DNS query logs.",
        },
    }

    ls = params.log_source.lower().strip()
    guide = guides.get(ls)
    if not guide:
        return f"Error: Unknown log source '{ls}'. Available: {', '.join(guides.keys())}"

    return _fmt(guide, params.response_format, title=f"{CALLSIGN} Log Analysis Guide")


def register(mcp):
    """Register tools on the MCP server."""
    mcp.tool(
        name="rick_hardening",
        annotations={
            "title": "Hardening Blueprints",
            "readOnlyHint": True,
            "destructiveHint": False,
            "idempotentHint": True,
            "openWorldHint": False,
        },
    )(_safe_tool(rick_hardening))
    mcp.tool(
        name="rick_incident_response",
        annotations={
            "title": "Incident Response Playbooks",
            "readOnlyHint": True,
            "destructiveHint": False,
            "idempotentHint": True,
            "openWorldHint": False,
        },
    )(_safe_tool(rick_incident_response))
    mcp.tool(
        name="rick_detection_rules",
        annotations={
            "title": "Detection Rule Templates",
            "readOnlyHint": True,
            "destructiveHint": False,
            "idempotentHint": True,
            "openWorldHint": False,
        },
    )(_safe_tool(rick_detection_rules))
    mcp.tool(
        name="rick_log_analysis",
        annotations={
            "title": "Log Analysis Guide",
            "readOnlyHint": True,
            "destructiveHint": False,
            "idempotentHint": True,
            "openWorldHint": False,
        },
    )(_safe_tool(rick_log_analysis))
