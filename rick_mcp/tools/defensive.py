"""Defensive security tools — hardening blueprints."""

from rick_mcp.constants import CALLSIGN
from rick_mcp.formatting import _fmt, _safe_tool
from rick_mcp.models import HardenInput


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
