"""Offensive security tools — recon, vuln assessment, tool recommendation."""

from rick_mcp.constants import CALLSIGN
from rick_mcp.formatting import _fmt, _safe_tool, _sanitize
from rick_mcp.models import (
    ReconInput,
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
    from rick_mcp.tools import offensive_chains, offensive_extended

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

    # Delegate to split modules
    offensive_chains.register(mcp)
    offensive_extended.register(mcp)
