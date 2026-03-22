"""Offensive tools v2 — C2 comparison, payload methodology, cloud attack paths, wireless."""

from rick_mcp.constants import CALLSIGN
from rick_mcp.formatting import _fmt, _safe_tool
from rick_mcp.models.inputs import C2CompareInput, CloudAttackInput, PayloadGuideInput, WirelessInput


async def rick_c2_compare(params: C2CompareInput) -> str:
    """C2 framework comparison. Cobalt Strike vs Sliver vs Mythic vs Havoc — scenario-based."""
    frameworks = {
        "cobalt_strike": {
            "name": "Cobalt Strike",
            "type": "Commercial",
            "cost": "$3,500+/year per operator",
            "pros": [
                "Industry standard — massive community and documentation",
                "Malleable C2 profiles for traffic blending",
                "Beacon is extremely flexible and battle-tested",
                "BOF (Beacon Object Files) for in-memory execution",
                "Excellent team server for multi-operator engagements",
            ],
            "cons": [
                "Expensive licensing",
                "Heavily signatured by EDR/AV — requires customization",
                "Cracked versions in the wild hurt OPSEC",
                "Java-based team server can be resource-heavy",
            ],
            "detection_difficulty": "Medium — heavily signatured but malleable profiles help",
            "best_for": "Professional red team engagements, long-term operations",
        },
        "sliver": {
            "name": "Sliver",
            "type": "Open Source (BishopFox)",
            "cost": "Free",
            "pros": [
                "Free and actively maintained by BishopFox",
                "Written in Go — cross-platform implants",
                "Built-in support for mTLS, WireGuard, HTTP(S), DNS",
                "Multiplayer mode for team operations",
                "Armory for extensions and BOFs",
                "Less signatured than Cobalt Strike out of the box",
            ],
            "cons": [
                "Smaller community than Cobalt Strike",
                "Less mature malleable profile equivalent",
                "Some EDRs catching up on Sliver signatures",
                "Documentation gaps in advanced features",
            ],
            "detection_difficulty": "Medium-Low — growing detection but still less targeted",
            "best_for": "Budget-conscious teams, open-source preference, quick deployments",
        },
        "mythic": {
            "name": "Mythic",
            "type": "Open Source",
            "cost": "Free",
            "pros": [
                "Modular agent architecture — multiple agent types",
                "Web-based UI for collaborative operations",
                "Excellent logging and operation tracking",
                "Supports custom agents in multiple languages",
                "Great for training and lab environments",
                "Docker-based deployment",
            ],
            "cons": [
                "Steeper learning curve for custom agent development",
                "Resource-heavy (Docker containers)",
                "Agent maturity varies by implementation",
                "Less battle-tested than Cobalt Strike in enterprise engagements",
            ],
            "detection_difficulty": "Varies by agent — custom agents can be very evasive",
            "best_for": "Custom operations, training environments, versatile tooling",
        },
        "havoc": {
            "name": "Havoc",
            "type": "Open Source",
            "cost": "Free",
            "pros": [
                "Modern C2 with sleek UI",
                "Demon agent with advanced evasion capabilities",
                "Sleep obfuscation and indirect syscalls",
                "Active development community",
                "Lightweight and fast deployment",
            ],
            "cons": [
                "Younger project — less mature than alternatives",
                "Smaller plugin ecosystem",
                "Documentation still growing",
                "Fewer transport options than Sliver",
                "Breaking changes between versions",
            ],
            "detection_difficulty": "Low — newer framework, less EDR coverage",
            "best_for": "Evasion-focused engagements, modern red team ops, rapid deployment",
        },
    }
    scenarios = {
        "stealth": {
            "scenario": "Maximum Stealth / Evasion",
            "recommendation": "Havoc or custom Mythic agent",
            "reasoning": "Havoc's Demon agent has built-in sleep obfuscation and indirect syscalls. Less signatured than CS. For maximum evasion, a custom Mythic agent gives full control over the implant behavior.",
            "runner_up": "Sliver with custom implant modifications",
        },
        "team_ops": {
            "scenario": "Multi-Operator Team Engagement",
            "recommendation": "Cobalt Strike",
            "reasoning": "Team server is purpose-built for multi-operator coordination. Mature workflows, shared sessions, and operator-specific logging make it the gold standard for team red team ops.",
            "runner_up": "Sliver multiplayer mode or Mythic web UI",
        },
        "budget": {
            "scenario": "Budget-Conscious / Open Source Only",
            "recommendation": "Sliver",
            "reasoning": "Best balance of features, stability, and community support in the free tier. BishopFox backing means active development. Cross-platform Go implants work everywhere.",
            "runner_up": "Mythic for more customization, Havoc for more evasion",
        },
        "evasion": {
            "scenario": "EDR Evasion Focus",
            "recommendation": "Havoc",
            "reasoning": "Demon agent's sleep obfuscation, indirect syscalls, and relative obscurity make it hardest for EDRs to catch out of the box. Combine with custom loaders for best results.",
            "runner_up": "Cobalt Strike with heavy malleable profile customization",
        },
        "versatility": {
            "scenario": "Maximum Versatility / Multi-Platform",
            "recommendation": "Mythic",
            "reasoning": "Modular agent architecture means you pick the right agent for each target. Python, C, Go, .NET agents available. Web UI makes operation tracking clean across diverse environments.",
            "runner_up": "Sliver for cross-platform Go implants",
        },
        "quick_deploy": {
            "scenario": "Rapid Deployment / Time-Constrained",
            "recommendation": "Sliver",
            "reasoning": "Single binary, minimal setup, generate implants in seconds. No licensing delays, no Docker overhead. From zero to C2 in under 5 minutes.",
            "runner_up": "Havoc for similarly quick setup with more evasion",
        },
    }

    s = params.scenario.lower().strip()
    scenario = scenarios.get(s)
    if not scenario:
        return f"Error: Unknown scenario '{s}'. Available: {', '.join(scenarios.keys())}"

    result = {
        **scenario,
        "frameworks": frameworks,
        "rick_note": "The best C2 is the one you understand inside and out. Learn the internals, not just the UI. And remember — the framework is just the delivery truck. Your tradecraft is the payload.",
        "authorization": "AUTHORIZED ENGAGEMENTS ONLY",
    }
    return _fmt(result, params.response_format, title=f"{CALLSIGN} C2 Framework Comparison")


async def rick_payload_guide(params: PayloadGuideInput) -> str:
    """Payload generation methodology. Evasion, encoding, delivery vectors mapped to MITRE ATT&CK."""
    guides = {
        "initial_access": {
            "category": "Initial Access Payload Methodology",
            "methodology": [
                "1. Identify target environment (OS, AV/EDR, email gateway)",
                "2. Select delivery vector (phishing, drive-by, supply chain)",
                "3. Choose payload format based on target defenses",
                "4. Apply encoding/obfuscation layers",
                "5. Test against target's security stack in lab",
                "6. Establish C2 callback channel",
            ],
            "evasion_techniques": [
                "Signed binary proxy execution (LOLBAS)",
                "DLL side-loading with legitimate applications",
                "Template injection in Office documents",
                "ISO/IMG/VHD containers to bypass MOTW",
                "HTML smuggling for payload delivery",
                "Polyglot files (valid in multiple formats)",
            ],
            "encoding_strategies": [
                "XOR with rotating keys",
                "AES-256 encrypted shellcode with runtime decryption",
                "Base64 + custom alphabet encoding",
                "String stacking to avoid static signatures",
                "Environmental keying (decrypt only on target)",
            ],
            "delivery_vectors": [
                "Spearphishing attachment (T1566.001)",
                "Spearphishing link (T1566.002)",
                "Drive-by compromise (T1189)",
                "Supply chain compromise (T1195)",
                "Trusted relationship abuse (T1199)",
            ],
            "mitre_mapping": ["T1566", "T1189", "T1195", "T1199", "T1059", "T1204"],
            "detection_considerations": [
                "Email gateway scanning — test with target's vendor",
                "AMSI bypass needed for PowerShell/VBA payloads",
                "ETW patching for .NET payloads",
                "Mark-of-the-Web bypass for downloaded files",
            ],
            "rick_note": "The best initial access payload is the one that looks like normal business. Blend in, don't stand out. If the SOC can tell it's a payload from the delivery alone, you've already lost.",
        },
        "persistence": {
            "category": "Persistence Payload Methodology",
            "methodology": [
                "1. Enumerate existing persistence mechanisms on target",
                "2. Identify writable locations with auto-execution",
                "3. Choose persistence method matching target's security posture",
                "4. Deploy with minimal footprint — one mechanism, tested",
                "5. Verify persistence survives reboot/logout",
                "6. Document for cleanup during engagement close",
            ],
            "evasion_techniques": [
                "Registry run key with obfuscated command",
                "Scheduled tasks with SYSTEM context",
                "WMI event subscriptions (fileless)",
                "DLL search order hijacking",
                "COM object hijacking",
                "Service creation with legitimate-looking names",
            ],
            "encoding_strategies": [
                "Encrypted payload stored in registry values",
                "Shellcode in ADS (Alternate Data Streams)",
                "Steganography in image files for payload storage",
                "Environment variable shellcode assembly",
            ],
            "delivery_vectors": [
                "Boot or logon autostart execution (T1547)",
                "Scheduled task/job (T1053)",
                "Event triggered execution (T1546)",
                "Create or modify system process (T1543)",
                "Hijack execution flow (T1574)",
            ],
            "mitre_mapping": ["T1547", "T1053", "T1546", "T1543", "T1574", "T1546.003"],
            "detection_considerations": [
                "Autoruns will catch most common persistence",
                "Sysmon Event IDs 12/13 for registry modifications",
                "Scheduled task creation logged in Security Event 4698",
                "WMI persistence detectable via WMI activity logging",
            ],
            "rick_note": "One solid persistence mechanism is better than five noisy ones. And ALWAYS document what you planted — cleanup is part of the job. Three boys are watching.",
        },
        "lateral_movement": {
            "category": "Lateral Movement Payload Methodology",
            "methodology": [
                "1. Enumerate accessible hosts and credentials",
                "2. Identify lateral movement protocols available (SMB, WinRM, RDP, SSH)",
                "3. Choose technique based on target defenses and available creds",
                "4. Stage payload on target or use fileless technique",
                "5. Execute with appropriate privilege level",
                "6. Verify new session and update engagement tracker",
            ],
            "evasion_techniques": [
                "Pass-the-Hash with SMB (avoids plaintext creds)",
                "Overpass-the-Hash for Kerberos ticket generation",
                "DCOM execution for non-standard lateral movement",
                "WinRM with certificate-based auth",
                "SSH key-based movement (Linux environments)",
                "RDP with NLA and stolen credentials",
            ],
            "encoding_strategies": [
                "In-memory payload execution via WMI",
                "PowerShell remoting with AMSI bypass",
                "Service binary replacement with encrypted stager",
                "Named pipe communication for peer-to-peer C2",
            ],
            "delivery_vectors": [
                "Remote services (T1021)",
                "Lateral tool transfer (T1570)",
                "Use alternate authentication material (T1550)",
                "Exploitation of remote services (T1210)",
                "Internal spearphishing (T1534)",
            ],
            "mitre_mapping": ["T1021", "T1570", "T1550", "T1210", "T1534", "T1047"],
            "detection_considerations": [
                "Type 3 logon events (4624) for network authentication",
                "Service installation events (7045) for PSExec-style movement",
                "WinRM connections logged in Microsoft-Windows-WinRM/Operational",
                "Named pipe creation visible to Sysmon Event ID 17/18",
            ],
            "rick_note": "Lateral movement is where engagements get noisy. Every hop is a detection opportunity. Know your blue team's blind spots and move through them. Slow is smooth, smooth is fast.",
        },
        "exfil": {
            "category": "Exfiltration Payload Methodology",
            "methodology": [
                "1. Identify target data and its location",
                "2. Stage data in temporary location with compression/encryption",
                "3. Select exfil channel based on network controls",
                "4. Chunk data to avoid size-based detection",
                "5. Exfiltrate during business hours to blend with normal traffic",
                "6. Verify data integrity post-transfer",
            ],
            "evasion_techniques": [
                "DNS tunneling for slow, stealthy exfil",
                "HTTPS to legitimate cloud services (OneDrive, S3, GDrive)",
                "Steganography in images uploaded to social media",
                "Encrypted channels over allowed protocols",
                "Scheduled transfers during peak traffic hours",
                "Data chunking below DLP threshold sizes",
            ],
            "encoding_strategies": [
                "AES-256 encryption before transfer",
                "ZIP with password protection",
                "Base64 encoding over DNS TXT records",
                "Custom encoding to avoid DLP pattern matching",
                "Compression to reduce transfer volume",
            ],
            "delivery_vectors": [
                "Exfiltration over C2 channel (T1041)",
                "Exfiltration over alternative protocol (T1048)",
                "Exfiltration over web service (T1567)",
                "Automated exfiltration (T1020)",
                "Transfer data to cloud account (T1537)",
            ],
            "mitre_mapping": ["T1041", "T1048", "T1567", "T1020", "T1537", "T1030"],
            "detection_considerations": [
                "DLP solutions monitor for PII/sensitive data patterns",
                "DNS query volume anomalies for DNS tunneling",
                "Large outbound transfers to cloud storage",
                "Unusual protocols on standard ports",
                "After-hours data transfers to external destinations",
            ],
            "rick_note": "In a real engagement, you prove the exfil path — you don't actually take the data. Stage fake data, demonstrate the channel works, document it, move on. The finding is the vulnerability, not the data.",
        },
    }

    pt = params.payload_type.lower().strip()
    guide = guides.get(pt)
    if not guide:
        return f"Error: Unknown payload type '{pt}'. Available: {', '.join(guides.keys())}"

    guide["authorization"] = "AUTHORIZED ENGAGEMENTS ONLY"
    return _fmt(guide, params.response_format, title=f"{CALLSIGN} Payload Methodology Guide")


async def rick_cloud_attack_path(params: CloudAttackInput) -> str:
    """Cloud-specific attack paths. IAM misconfigs, metadata abuse, privilege escalation by provider."""
    paths = {
        "azure": {
            "provider": "Microsoft Azure",
            "attack_paths": [
                {
                    "name": "App Service to Managed Identity Abuse",
                    "steps": [
                        "1. Compromise web app via vuln (SQLi, RCE, SSRF)",
                        "2. Access IMDS at 169.254.169.254 for managed identity token",
                        "3. Enumerate permissions with stolen token (az CLI)",
                        "4. Pivot to Key Vault, Storage, or other Azure resources",
                        "5. Escalate via role assignments if User Access Administrator",
                    ],
                    "mitre_technique": "T1552.005 — Cloud Instance Metadata API",
                },
                {
                    "name": "Azure AD to Global Admin",
                    "steps": [
                        "1. Password spray against Azure AD (o365spray, MSOLSpray)",
                        "2. Enumerate users/groups with compromised account",
                        "3. Check for Privileged Role Administrator assignments",
                        "4. Abuse PIM (Privileged Identity Management) if misconfigured",
                        "5. Elevate to Global Administrator",
                    ],
                    "mitre_technique": "T1078.004 — Cloud Accounts",
                },
                {
                    "name": "Storage Account Key to Data Exfil",
                    "steps": [
                        "1. Find storage account keys in code repos or Key Vault",
                        "2. Enumerate blob containers and file shares",
                        "3. Access sensitive data (backups, configs, PII)",
                        "4. Check for shared access signatures (SAS) tokens in URLs",
                    ],
                    "mitre_technique": "T1530 — Data from Cloud Storage",
                },
            ],
            "iam_misconfigs": [
                "Overly permissive role assignments (Contributor at subscription level)",
                "Service principals with owner permissions",
                "Guest users with elevated privileges",
                "Missing conditional access policies",
                "PIM not enforced for privileged roles",
            ],
            "metadata_abuse": [
                "IMDS v1 accessible without special headers (use IMDSv2 equivalent)",
                "Managed identity tokens retrievable from IMDS",
                "Token audience can be changed to access different resources",
                "Environment variables leak credentials in App Services",
            ],
            "privilege_escalation": [
                "User Access Administrator → assign yourself Global Admin",
                "Automation Account RunAs → subscription-level access",
                "Logic App managed identity → cross-resource pivot",
                "Function App with Key Vault access → secret extraction",
            ],
            "tools": ["ROADtools", "AzureHound", "MicroBurst", "o365spray", "TokenTacticsV2", "az CLI"],
            "rick_note": "Azure AD is the crown jewel. Own the identity plane, own the kingdom. Start with password spray, escalate through IAM misconfigs. Check every managed identity — they're often overpermissioned.",
        },
        "aws": {
            "provider": "Amazon Web Services",
            "attack_paths": [
                {
                    "name": "EC2 Instance to IAM Role Abuse",
                    "steps": [
                        "1. Compromise EC2 via exposed service or SSRF",
                        "2. Query IMDS v1 at 169.254.169.254/latest/meta-data/iam/",
                        "3. Retrieve temporary credentials from instance role",
                        "4. Enumerate permissions with stolen credentials (enumerate-iam)",
                        "5. Pivot to S3, Lambda, or other AWS services",
                    ],
                    "mitre_technique": "T1552.005 — Cloud Instance Metadata API",
                },
                {
                    "name": "Lambda to Cross-Account Pivot",
                    "steps": [
                        "1. Identify Lambda functions with overpermissioned execution roles",
                        "2. Modify Lambda code or environment variables",
                        "3. Use Lambda role to assume cross-account roles",
                        "4. Access target account resources",
                    ],
                    "mitre_technique": "T1078.004 — Cloud Accounts",
                },
                {
                    "name": "S3 Bucket Misconfiguration Chain",
                    "steps": [
                        "1. Discover public or misconfigured S3 buckets",
                        "2. Extract sensitive data (backups, logs, configs)",
                        "3. Find embedded credentials in config files",
                        "4. Use discovered creds to escalate access",
                    ],
                    "mitre_technique": "T1530 — Data from Cloud Storage",
                },
            ],
            "iam_misconfigs": [
                "IAM users with inline policies granting admin access",
                "Wildcard (*) resource permissions on sensitive actions",
                "Missing MFA enforcement on console access",
                "Access keys that haven't been rotated in 90+ days",
                "Cross-account role trust policies too broad",
                "IMDSv1 still enabled on EC2 instances",
            ],
            "metadata_abuse": [
                "IMDSv1 token retrieval without TTL header (SSRF goldmine)",
                "IMDSv2 requires PUT with hop limit — blocks most SSRF",
                "User data scripts may contain plaintext credentials",
                "Instance profile credentials rotated every ~6 hours",
            ],
            "privilege_escalation": [
                "iam:PassRole + lambda:CreateFunction → admin via Lambda execution role",
                "iam:CreatePolicyVersion → write new admin policy",
                "iam:AttachUserPolicy → attach AdministratorAccess to self",
                "sts:AssumeRole → pivot through overly trusting roles",
                "ec2:RunInstances + iam:PassRole → launch instance with admin role",
            ],
            "tools": ["Pacu", "enumerate-iam", "ScoutSuite", "Prowler", "CloudMapper", "aws CLI"],
            "rick_note": "AWS privesc is a game of IAM policy analysis. Learn to read JSON policies like blueprints. The iam:PassRole + create combo is the skeleton key — look for it in every engagement.",
        },
        "gcp": {
            "provider": "Google Cloud Platform",
            "attack_paths": [
                {
                    "name": "Compute Instance to Service Account Abuse",
                    "steps": [
                        "1. Compromise GCE instance via exposed service",
                        "2. Query metadata server at metadata.google.internal",
                        "3. Retrieve service account token from metadata",
                        "4. Enumerate permissions with stolen token",
                        "5. Pivot to Cloud Storage, BigQuery, or other services",
                    ],
                    "mitre_technique": "T1552.005 — Cloud Instance Metadata API",
                },
                {
                    "name": "Cloud Function to Project Takeover",
                    "steps": [
                        "1. Identify Cloud Functions with overpermissioned service accounts",
                        "2. Deploy malicious function or modify existing",
                        "3. Use service account to modify IAM policies",
                        "4. Grant yourself Owner role on the project",
                    ],
                    "mitre_technique": "T1078.004 — Cloud Accounts",
                },
                {
                    "name": "GCS Bucket to Credential Harvest",
                    "steps": [
                        "1. Enumerate accessible Cloud Storage buckets",
                        "2. Check for allUsers/allAuthenticatedUsers permissions",
                        "3. Extract service account keys from backups/configs",
                        "4. Activate keys for persistent access",
                    ],
                    "mitre_technique": "T1530 — Data from Cloud Storage",
                },
            ],
            "iam_misconfigs": [
                "Primitive roles (Owner/Editor) assigned broadly",
                "Service account keys not rotated",
                "allUsers or allAuthenticatedUsers on GCS buckets",
                "Default service accounts with Editor role",
                "Missing organization policy constraints",
            ],
            "metadata_abuse": [
                "Metadata server accessible at metadata.google.internal",
                "Service account tokens available via metadata API",
                "Project-level metadata may contain startup scripts with secrets",
                "Custom metadata attributes can store sensitive config",
            ],
            "privilege_escalation": [
                "iam.serviceAccounts.getAccessToken → impersonate any SA",
                "iam.serviceAccountKeys.create → generate persistent key",
                "resourcemanager.projects.setIamPolicy → grant Owner to self",
                "deploymentmanager.deployments.create → deploy as project editor",
                "cloudfunctions.functions.create + iam.serviceAccounts.actAs → function as SA",
            ],
            "tools": ["ScoutSuite", "GCPBucketBrute", "gcloud CLI", "Cartography", "gcphound"],
            "rick_note": "GCP's IAM is different from AWS/Azure — it's resource-based, not identity-based. Understand the hierarchy: org → folder → project → resource. Inheritance flows down, so check every level.",
        },
    }

    provider = params.cloud_provider.lower().strip()
    path = paths.get(provider)
    if not path:
        return f"Error: Unknown provider '{provider}'. Available: {', '.join(paths.keys())}"

    path["authorization"] = "AUTHORIZED ENGAGEMENTS ONLY"
    return _fmt(path, params.response_format, title=f"{CALLSIGN} Cloud Attack Paths")


async def rick_wireless(params: WirelessInput) -> str:
    """Wireless recon and attack methodology. WiFi, Bluetooth, RFID — physical layer tradecraft."""
    playbooks = {
        "wifi": {
            "type": "WiFi (802.11)",
            "recon_methodology": [
                "1. Passive scan — identify SSIDs, BSSIDs, channels, encryption types",
                "2. Client probing — capture probe requests to identify client devices",
                "3. Hidden SSID discovery via deauth + reassociation capture",
                "4. Signal strength mapping for physical AP location",
                "5. Identify enterprise vs personal (WPA2-Enterprise = RADIUS)",
                "6. Check for WPS enabled (easy win if present)",
                "7. Identify captive portal implementations",
            ],
            "attack_vectors": [
                "WPA2-PSK handshake capture + offline cracking (hashcat)",
                "Evil Twin AP — impersonate legitimate AP with stronger signal",
                "KARMA attack — respond to all client probe requests",
                "WPS PIN brute force (Reaver/Bully)",
                "PMKID capture — no client needed, grab from AP directly",
                "EAP downgrade — force clients to use weaker auth",
                "Captive portal bypass / credential harvesting",
                "Deauth flood for denial of service (demonstration only)",
            ],
            "tools": [
                "Aircrack-ng suite (airmon-ng, airodump-ng, aireplay-ng)",
                "Hashcat (WPA2 cracking with GPU acceleration)",
                "Wireshark (packet analysis)",
                "Bettercap (MitM and evil twin)",
                "Fluxion (automated evil twin + captive portal)",
                "Reaver/Bully (WPS attacks)",
                "hcxdumptool/hcxtools (PMKID capture)",
                "WiFi Pineapple (hardware platform)",
            ],
            "mitre_mapping": ["T1557.002", "T1040", "T1498", "T1563"],
            "rick_note": "WiFi is the front door nobody locks properly. PMKID capture changed the game — you don't even need a client connected. Always check for WPS first, it's the low-hanging fruit that's still everywhere.",
        },
        "bluetooth": {
            "type": "Bluetooth (Classic + BLE)",
            "recon_methodology": [
                "1. Scan for discoverable devices (hcitool scan / bluetoothctl)",
                "2. Enumerate services on discovered devices (SDP)",
                "3. BLE advertising packet capture for IoT devices",
                "4. Identify device types, firmware versions, manufacturers",
                "5. Check for default PINs (0000, 1234)",
                "6. Map BLE GATT services and characteristics",
            ],
            "attack_vectors": [
                "Bluejacking — send unsolicited messages to discoverable devices",
                "Bluesnarfing — unauthorized access to device data (phonebook, calendar)",
                "KNOB attack — key negotiation downgrade to 1-byte entropy",
                "BLE GATT manipulation — read/write characteristics without auth",
                "Bluetooth impersonation (BIAS) attack",
                "BLE relay attack — forward BLE signals over distance",
                "Firmware extraction via BLE debug interfaces",
            ],
            "tools": [
                "hcitool / bluetoothctl (built-in Linux BT tools)",
                "Bettercap (BLE enumeration and MitM)",
                "GATTacker (BLE MitM proxy)",
                "Ubertooth One (hardware — raw BT packet capture)",
                "nRF Connect (BLE service browser)",
                "Wireshark with BT/BLE dissectors",
                "CrackLE (BLE link layer encryption cracking)",
            ],
            "mitre_mapping": ["T1011.001", "T1040", "T1557"],
            "rick_note": "Bluetooth gets overlooked in most pentests because people forget it's there. BLE is in everything now — badges, locks, medical devices, cars. The GATT services are usually wide open. Check them.",
        },
        "rfid": {
            "type": "RFID / NFC (125kHz / 13.56MHz)",
            "recon_methodology": [
                "1. Identify card technology in use (125kHz vs 13.56MHz)",
                "2. Determine card type (HID Prox, iCLASS, MIFARE, DESFire)",
                "3. Read card data from willing participant (or demonstration card)",
                "4. Analyze access control system make/model",
                "5. Map card reader locations and access zones",
                "6. Identify multi-factor requirements (card + PIN, card + biometric)",
            ],
            "attack_vectors": [
                "125kHz clone — copy HID Prox card with Proxmark3 (trivial)",
                "MIFARE Classic key recovery (nested/darkside/hardnested attacks)",
                "MIFARE sector dump and clone to magic card",
                "Long-range skimming with amplified antenna",
                "Replay attacks against weak implementations",
                "iCLASS legacy key extraction (known master key)",
                "NFC relay attack — extend card range via phone relay",
                "Brute force facility codes on known formats",
            ],
            "tools": [
                "Proxmark3 (gold standard for RFID/NFC research)",
                "Flipper Zero (portable multi-tool — 125kHz and NFC)",
                "ACR122U (USB NFC reader/writer)",
                "libnfc (NFC library for custom tools)",
                "MFOC/MFCUK (MIFARE Classic attack tools)",
                "iCopy-XS (standalone card cloner)",
                "RFIDler (open-source RFID tool)",
            ],
            "mitre_mapping": ["T1200", "T1556", "T1078"],
            "rick_note": "If the building uses 125kHz HID Prox cards, game over — those clone in 3 seconds with a Proxmark3. Most physical access control is security theater. Always recommend upgrading to DESFire EV2+ with diversified keys.",
        },
    }

    wt = params.wireless_type.lower().strip()
    playbook = playbooks.get(wt)
    if not playbook:
        return f"Error: Unknown wireless type '{wt}'. Available: {', '.join(playbooks.keys())}"

    playbook["authorization"] = "AUTHORIZED ENGAGEMENTS ONLY"
    return _fmt(playbook, params.response_format, title=f"{CALLSIGN} Wireless Attack Playbook")


def register(mcp):
    """Register tools on the MCP server."""
    mcp.tool(
        name="rick_c2_compare",
        annotations={
            "title": "C2 Framework Comparison",
            "readOnlyHint": True,
            "destructiveHint": False,
            "idempotentHint": True,
            "openWorldHint": False,
        },
    )(_safe_tool(rick_c2_compare))
    mcp.tool(
        name="rick_payload_guide",
        annotations={
            "title": "Payload Methodology Guide",
            "readOnlyHint": True,
            "destructiveHint": False,
            "idempotentHint": True,
            "openWorldHint": False,
        },
    )(_safe_tool(rick_payload_guide))
    mcp.tool(
        name="rick_cloud_attack_path",
        annotations={
            "title": "Cloud Attack Paths",
            "readOnlyHint": True,
            "destructiveHint": False,
            "idempotentHint": True,
            "openWorldHint": False,
        },
    )(_safe_tool(rick_cloud_attack_path))
    mcp.tool(
        name="rick_wireless",
        annotations={
            "title": "Wireless Attack Playbooks",
            "readOnlyHint": True,
            "destructiveHint": False,
            "idempotentHint": True,
            "openWorldHint": False,
        },
    )(_safe_tool(rick_wireless))
