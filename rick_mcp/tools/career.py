"""Career tools — compatibility check, cover letter, mentorship."""

from rick_mcp.constants import (
    CALLSIGN,
)
from rick_mcp.formatting import _fmt, _safe_tool
from rick_mcp.models import CompatInput, CoverInput, MentorInput


async def rick_compatibility_check(params: CompatInput) -> str:
    """Analyze job posting or engagement brief against profile. Scores tech alignment + cultural fit."""
    desc = params.description.lower()

    tech_matches: list[str] = []
    tech_gaps: list[str] = []
    tech_keywords = {
        "pentest": ("Pentesting", True),
        "penetration test": ("Pentesting", True),
        "red team": ("Red Team", True),
        "web app": ("Web App Sec", True),
        "active directory": ("AD Security", True),
        "burp": ("Burp Suite", True),
        "owasp": ("OWASP", True),
        "api security": ("API Sec", True),
        "cloud": ("Cloud Sec", True),
        "azure": ("Azure", True),
        "aws": ("AWS", True),
        "container": ("Container Sec", True),
        "kubernetes": ("K8s", True),
        "python": ("Python", True),
        "powershell": ("PowerShell", True),
        "oscp": ("OSCP", True),
        "vuln": ("Vuln Assessment", True),
        "network": ("Network Sec", True),
        "appsec": ("AppSec", True),
        "terraform": ("IaC", True),
        "golang": ("Golang", True),
        "go ": ("Golang", True),
        "exploit": ("Exploit Dev", True),
        "c#": ("C#/.NET", True),
        "php": ("PHP", True),
        "javascript": ("JavaScript", True),
        "leadership": ("Security Leadership", True),
        "management": ("Security Leadership", True),
        "iot": ("IoT (gap)", False),
        "malware analysis": ("Malware (gap)", False),
        "forensic": ("Forensics (gap)", False),
        "grc": ("GRC (no)", False),
        "soc": ("SOC (no)", False),
    }
    for kw, (skill, has_it) in tech_keywords.items():
        if kw in desc:
            (tech_matches if has_it else tech_gaps).append(skill)

    green_flags, red_flags = [], []
    for kw, sig in {
        "thorough": "Thoroughness",
        "remote": "Remote",
        "leadership": "Leadership",
        "autonomous": "Autonomous",
        "veteran": "Vet-friendly",
        "automation": "Automation",
        "mentor": "Mentorship",
        "creative": "Creative thinking",
        "builder": "Builder mindset",
    }.items():
        if kw in desc:
            green_flags.append(sig)
    for kw, sig in {
        "checkbox": "Checkbox compliance",
        "fast scan": "Speed>quality",
        "24/7 on-call": "Always on-call",
        "entry level": "Below level",
        "junior": "Below level",
    }.items():
        if kw in desc:
            red_flags.append(sig)

    tech_score = min(len(tech_matches) * 15, 100)
    if tech_gaps:
        tech_score = max(tech_score - len(tech_gaps) * 10, 10)
    culture_score = max(0, min(100, 50 + len(green_flags) * 10 - len(red_flags) * 15))
    overall = int(tech_score * 0.6 + culture_score * 0.4)

    if overall >= 80:
        verdict = "STRONG FIT — Semper Fidelis, let's talk."
    elif overall >= 60:
        verdict = "GOOD POTENTIAL — Worth a conversation."
    elif overall >= 40:
        verdict = "PARTIAL FIT — Some alignment, gaps to discuss."
    else:
        verdict = "NOT IDEAL — Honest assessment, no hard feelings."

    result = {
        "type": params.eval_type,
        "score": f"{overall}/100",
        "verdict": verdict,
        "tech": {
            "score": f"{tech_score}/100",
            "matches": tech_matches or ["None detected"],
            "gaps": tech_gaps or ["None"],
        },
        "culture": {
            "score": f"{culture_score}/100",
            "green": green_flags or ["None detected"],
            "red": red_flags or ["None detected"],
        },
        "rick_note": "Every opportunity is a recon target. Honest assessment — no inflated scores.",
    }
    return _fmt(result, params.response_format, title=f"{CALLSIGN} Compatibility")


async def rick_cover_letter(params: CoverInput) -> str:
    """Generate targeted cover letter. Auto-matches requirements to experience. 3 tones."""
    tone = (params.tone or "professional").lower()
    hl = []
    if params.key_requirements:
        rq = params.key_requirements.lower()
        requirement_map = {
            "oscp": "OSCP certified (2019) with hands-on pentesting across web, network, AD, and cloud.",
            "pentest": "Extensive pentesting across web, network, AD, cloud — manual depth, not just scanner output.",
            "web app": "Deep web application security — Burp Suite, OWASP, business logic, manual analysis.",
            "cloud": "Cloud security across Azure and AWS — IAM, storage, infrastructure, CIS benchmarks.",
            "active directory": "AD specialist — BloodHound, Kerberoasting, ADCS abuse, trust analysis.",
            "python": "Extensive Python for security automation, custom tooling, and exploit development.",
            "leadership": "Growing into security leadership — Marine Corps command experience, team coordination, mentorship.",
            "automation": "Automation-first mindset — custom frameworks, CI/CD security, PlexTrac integration.",
            "red team": "Red team operations with MITRE ATT&CK alignment and adversary simulation.",
            "clearance": "Former DoD Secret clearance (eligible for reinstatement).",
            "veteran": "USMC veteran — discipline, systematic methodology, ethics, mission completion.",
            "exploit": "Custom exploit development — multiple languages, creative attack vectors.",
            "api": "API security testing — OWASP API Top 10, BOLA/IDOR, JWT, OAuth, GraphQL.",
        }
        for kw, h in requirement_map.items():
            if kw in rq:
                hl.append(h)
    if not hl:
        hl = [
            "OSCP-certified offensive security engineer, 22+ years experience.",
            "Marine Corps systematic methodology — Honor, Courage, Commitment applied to security.",
            "Builder mindset — I don't just find vulnerabilities, I help build better defenses.",
        ]

    c, r = params.company_name, params.role_title
    if tone == "conversational":
        op = f"Reaching out about the {r} role at {c}. Been breaking and building software for 22+ years — started in Marine Corps barracks, 2003. Self-taught, mission-driven, ever evolving."
        bd = f"What I bring: {' '.join(hl[:3])}\n\nThorough, honest, every vuln comes with actionable remediation. Builder bloodline — I understand architecture, not just attack surfaces."
        cl = f"Would love to chat about contributing to {c}. Marine work ethic, builder mindset, frontier determination. Semper Fidelis."
    elif tone == "executive":
        op = f"Writing regarding the {r} position at {c}. 22+ years progressive experience in software development and offensive security, with military service foundation and deep technical expertise."
        bd = (
            "Key qualifications:\n"
            + "\n".join([f"- {h}" for h in hl[:4]])
            + "\n\nSelf-taught Marine developer to OSCP-certified security engineer — continuous adaptation and growth across two decades."
        )
        cl = f"Welcome the opportunity to discuss strategic alignment with {c}'s security objectives and long-term vision."
    else:
        op = f"Writing to express interest in the {r} at {c}. OSCP-certified offensive security engineer with 22+ years experience, USMC veteran background, and builder's approach to security."
        bd = (
            "Relevant qualifications:\n"
            + "\n".join([f"- {h}" for h in hl[:4]])
            + "\n\nEvery finding documented with reproduction steps and actionable remediation. Builder bloodline — I understand how systems are constructed, so I know where they break."
        )
        cl = f"Welcome the opportunity to discuss how my experience aligns with {c}'s security needs. Thorough > fast. Honest > comfortable."

    return _fmt(
        {
            "target": {"company": c, "role": r, "tone": tone},
            "opening": op,
            "body": bd,
            "closing": cl,
            "signature": f"Semper Fidelis,\nTom — {CALLSIGN}\nOSCP | OSWA | USMC Veteran\nhttps://jiveturkey.rocks/",
            "matched_highlights": hl[:4],
            "rick_note": "Customize before sending. Research the company. Generic = wasted round. Recon before engagement.",
        },
        params.response_format,
        title=f"{CALLSIGN} Cover Letter — {c}",
    )


async def rick_mentorship(params: MentorInput) -> str:
    """Teaching newcomers the craft. Learning paths, mindset guidance, 'how I got here' wisdom. The MCP teaches."""
    paths = {
        "getting_started": {
            "topic": "Getting Started in Offensive Security",
            "the_real_talk": "I started in USMC barracks in 2003. Self-taught. No bootcamp, no degree in CS, no hand-holding. You don't need permission to learn. You need discipline and curiosity. Check the clock. What makes it tick.",
            "foundation_first": {
                "networking": "Learn TCP/IP, DNS, HTTP, SMB, Kerberos. You can't hack what you don't understand. CompTIA Network+ level minimum.",
                "linux": "Get comfortable in a terminal. Bash scripting. File permissions. Process management. Services. This is your workbench.",
                "windows": "Active Directory basics. Group Policy. Services. Registry. PowerShell. This is where most targets live.",
                "programming": "Python first — it's the scripting language of security. Then learn to read PHP, JavaScript, C#. You don't need to master them, you need to understand them.",
                "web": "HTTP protocol, cookies, sessions, same-origin policy, CORS. Understand how web apps work before you try to break them.",
            },
            "first_steps": [
                "1. Set up a home lab (VirtualBox/VMware, Kali, Windows AD lab)",
                "2. Complete TryHackMe's 'Complete Beginner' path — hands on, guided",
                "3. Start HackTheBox — begin with Easy retired machines WITH walkthroughs",
                "4. Learn Burp Suite — do PortSwigger Web Security Academy (free, incredible)",
                "5. Read 'The Web Application Hacker's Handbook' — still the bible",
                "6. Join communities — InfoSec Twitter/Mastodon, Discord servers, local meetups",
                "7. Start a blog/notes system — document everything you learn",
                "8. Practice, practice, practice. There is no shortcut.",
            ],
            "rick_note": "Don't try to learn everything at once. Pick one domain (web, network, AD), go deep, then expand. Depth before breadth. And document EVERYTHING — your future self will thank you. I'm still building. Are you?",
        },
        "web_app_path": {
            "topic": "Web Application Security Learning Path",
            "beginner": {
                "learn": [
                    "HTTP protocol deep dive — methods, headers, status codes, cookies, sessions",
                    "Same-Origin Policy and CORS — the foundation of web security",
                    "OWASP Top 10 — understand each category with examples",
                    "HTML/JavaScript/CSS basics — enough to understand what you're looking at",
                    "SQL basics — SELECT, INSERT, UPDATE, UNION, subqueries",
                    "Burp Suite basics — proxy, repeater, intruder",
                ],
                "practice": [
                    "PortSwigger Web Security Academy — ALL of it. Free. Best resource that exists.",
                    "DVWA (Damn Vulnerable Web Application) — classic, good for basics",
                    "Juice Shop — OWASP's intentionally vulnerable app",
                    "TryHackMe Web Fundamentals path",
                ],
            },
            "intermediate": {
                "learn": [
                    "Business logic vulnerabilities — the ones scanners can't find",
                    "JWT attacks — algorithm confusion, key injection, claim manipulation",
                    "OAuth/OIDC vulnerabilities — redirect manipulation, token theft",
                    "Advanced XSS — DOM-based, mXSS, CSP bypass, prototype pollution",
                    "SSRF — internal access, cloud metadata, protocol smuggling",
                    "Deserialization — Java, PHP, .NET, Python pickle",
                    "API security — BOLA, mass assignment, GraphQL introspection",
                ],
                "practice": [
                    "HackTheBox web challenges — medium difficulty",
                    "Real-world bug bounty (HackerOne, Bugcrowd) — VDPs first",
                    "Build a vulnerable app yourself — you learn more building than breaking",
                    "Read disclosed bug bounty reports — learn from others' findings",
                ],
            },
            "advanced": {
                "learn": [
                    "Race conditions and time-of-check/time-of-use",
                    "HTTP request smuggling — CL.TE, TE.CL, TE.TE",
                    "Cache poisoning and cache deception",
                    "Prototype pollution chains to RCE",
                    "WebSocket attacks",
                    "Browser-based attacks — XS-Leaks, Spectre-based",
                    "Custom exploit development for web frameworks",
                ],
                "practice": [
                    "PortSwigger Expert-level labs",
                    "Real bug bounty on hardened targets",
                    "CTF competitions (web categories)",
                    "Contribute to open-source security tools",
                ],
            },
            "rick_note": "PortSwigger Academy is the single best free resource for web security. Do every lab. Then do them again without looking at solutions. Burp Suite is your home — learn every feature, every extension. Manual testing is where the craft lives.",
        },
        "network_path": {
            "topic": "Network & Infrastructure Pentesting Path",
            "beginner": {
                "learn": [
                    "TCP/IP deep dive — OSI model, subnetting, routing",
                    "Common protocols — SMB, DNS, DHCP, SNMP, LDAP, RDP, SSH, FTP",
                    "Nmap — scan types, scripts, output parsing",
                    "Wireshark — packet analysis, protocol dissection",
                    "Linux networking — ip, ss, iptables, routing",
                ],
                "practice": [
                    "TryHackMe — Network Fundamentals, Nmap room",
                    "HackTheBox — Easy machines (start with retired + writeups)",
                    "Set up home lab with vulnerable VMs (Metasploitable, DVWA)",
                    "Vulnhub machines — download and hack locally",
                ],
            },
            "intermediate": {
                "learn": [
                    "NTLM relay attacks and SMB signing exploitation",
                    "Responder — LLMNR/NBT-NS poisoning",
                    "Metasploit — beyond basic exploits: post modules, pivoting",
                    "Privilege escalation — Linux and Windows methodologies",
                    "Tunneling and pivoting — SSH, Chisel, Ligolo-ng, SOCKS",
                ],
                "practice": [
                    "HackTheBox Pro Labs — Offshore, RastaLabs",
                    "Proving Grounds — intermediate/hard machines",
                    "Build an AD lab and attack it (GOAD project)",
                    "OSCP preparation machines",
                ],
            },
            "advanced": {
                "learn": [
                    "Advanced AD attacks — ADCS, delegation abuse, trust attacks",
                    "Red team infrastructure — C2 frameworks, redirectors",
                    "Evasion — AMSI bypass, ETW patching, AV/EDR evasion",
                    "Custom exploit development — BOF, ROP chains",
                    "Cloud-to-on-prem pivoting",
                ],
                "practice": [
                    "HackTheBox Endgame labs",
                    "CRTO, CRTE certifications",
                    "Purple team exercises",
                    "Build and operate C2 infrastructure in lab",
                ],
            },
            "rick_note": "Build an AD lab. Seriously. Three VMs — a DC, a member server, a workstation. Attack it yourself. Break it, fix it, break it again. That's how I learned AD security — by building and breaking the same environment hundreds of times.",
        },
        "ad_path": {
            "topic": "Active Directory Attack Path",
            "beginner": {
                "learn": [
                    "AD fundamentals — domains, forests, trusts, GPOs, OUs",
                    "Kerberos authentication flow — TGT, TGS, service tickets",
                    "LDAP and LDAP queries",
                    "BloodHound — collection, analysis, attack path identification",
                    "PowerView/SharpView for AD enumeration",
                ],
                "practice": [
                    "TryHackMe — Active Directory Basics, Attacktive Directory",
                    "Build your own AD lab (2 DCs, member servers, workstations)",
                    "GOAD (Game of Active Directory) — pre-built vulnerable AD lab",
                    "HackTheBox — Easy AD machines",
                ],
            },
            "intermediate": {
                "learn": [
                    "Kerberoasting and AS-REP Roasting — theory and practice",
                    "NTLM relay and SMB signing attacks",
                    "Constrained and Unconstrained Delegation abuse",
                    "ACL-based attacks — WriteDACL, GenericAll, GenericWrite",
                    "Pass-the-Hash, Pass-the-Ticket, Overpass-the-Hash",
                    "ADCS — ESC1 through ESC8 vulnerability classes",
                ],
                "practice": [
                    "HackTheBox Pro Labs — RastaLabs is the AD goldmine",
                    "Certified Pre-Owned lab exercises (ADCS)",
                    "Proving Grounds — AD-focused machines",
                    "Attack your own lab with different starting positions",
                ],
            },
            "advanced": {
                "learn": [
                    "Golden Ticket, Silver Ticket, Diamond Ticket",
                    "DCSync and DCShadow",
                    "Forest trust abuse and SID history injection",
                    "ADCS advanced — certificate theft, shadow credentials",
                    "Azure AD / Entra ID integration attacks",
                    "SCCM/MECM abuse",
                    "Group Policy abuse for persistence",
                ],
                "practice": [
                    "Build multi-forest lab with trusts",
                    "Purple team — attack and detect simultaneously",
                    "CRTE, CRTO certifications",
                    "Research and develop novel AD attack techniques",
                ],
            },
            "rick_note": "AD is where the real money is in pentesting. BloodHound is your map. Impacket is your Swiss Army knife. ADCS is the new hotness — ESC1 is in almost every environment I test. Build a lab with intentional misconfigurations and attack it until you can do it in your sleep.",
        },
        "cloud_path": {
            "topic": "Cloud Security Learning Path",
            "beginner": {
                "learn": [
                    "Cloud fundamentals — IaaS, PaaS, SaaS models",
                    "IAM concepts — policies, roles, principals, least privilege",
                    "AWS/Azure free tier — get hands-on with real cloud",
                    "Cloud CLI tools — aws cli, az cli, gcloud",
                    "Shared responsibility model — know what's yours to secure",
                ],
                "practice": [
                    "AWS free tier + CloudGoat (intentionally vulnerable AWS)",
                    "Azure free tier + AzureGoat",
                    "TryHackMe Cloud rooms",
                    "A Cloud Guru or cloud certification study",
                ],
            },
            "intermediate": {
                "learn": [
                    "IAM privilege escalation techniques",
                    "S3/Blob/GCS misconfiguration exploitation",
                    "Metadata service attacks (IMDS)",
                    "Serverless security — Lambda, Functions, Cloud Functions",
                    "Container security — EKS, AKS, GKE",
                    "Cloud-native security tools — GuardDuty, Defender, SCC",
                ],
                "practice": [
                    "CloudGoat scenarios — all of them",
                    "flAWS.cloud (AWS CTF by Summit Route)",
                    "HackTricks Cloud for reference",
                    "ScoutSuite/Prowler against your own accounts",
                ],
            },
            "advanced": {
                "learn": [
                    "Cross-account/cross-tenant attacks",
                    "Cloud-to-on-prem pivoting (hybrid environments)",
                    "CI/CD pipeline attacks in cloud",
                    "Kubernetes cluster compromise and escape",
                    "Cloud forensics and incident response",
                    "Infrastructure as Code security (Terraform, CloudFormation)",
                ],
                "practice": [
                    "Multi-account lab with realistic hybrid setup",
                    "Thunder CTF (GCP)",
                    "Kubernetes Goat",
                    "Cloud penetration testing certifications",
                ],
            },
            "rick_note": "Cloud is the new perimeter. Most orgs' cloud security is 2-3 years behind their on-prem security. Learn IAM deeply — 90% of cloud compromises involve IAM misconfiguration. And always check the metadata service. Always.",
        },
        "certifications": {
            "topic": "Certification Roadmap",
            "the_real_talk": "Certs open doors. Skills keep you in the room. Get the certs you need to get past HR filters, but never stop building real skills. The cert is the map — the lab is the territory.",
            "recommended_path": {
                "foundation": {
                    "certs": ["CompTIA Security+", "CompTIA Network+"],
                    "why": "Baseline knowledge. HR filter passers. Good for fundamentals.",
                    "time": "1-2 months each",
                },
                "offensive_entry": {
                    "certs": ["eJPT (eLearnSecurity Junior Penetration Tester)", "CompTIA PenTest+"],
                    "why": "Entry-level offensive certs. eJPT is practical, PenTest+ is widely recognized.",
                    "time": "1-3 months each",
                },
                "offensive_professional": {
                    "certs": ["OSCP (OffSec Certified Professional)"],
                    "why": "THE certification. Proves you can hack, not just study. 24-hour practical exam. This is the one.",
                    "time": "3-6 months preparation. Do the labs. All of them.",
                },
                "specialization": {
                    "certs": ["OSWA (Web)", "OSEP (Evasion)", "OSED (Exploit Dev)", "CRTO (Red Team)", "CRTE (AD)"],
                    "why": "Deep specialization. Pick based on your career direction.",
                    "time": "2-4 months each",
                },
                "advanced": {
                    "certs": ["OSEE (OffSec Expert)", "GXPN (SANS)", "CCSAS (Cloud)"],
                    "why": "Expert level. For when you want to prove mastery.",
                    "time": "Months of dedicated study",
                },
            },
            "rick_note": "I got OSCP in 2019 and it changed my career trajectory. The exam is brutal — 24 hours of hacking with a report due after. But that's the point. It proves you can DO the work under pressure. Start with the OffSec PG Practice machines, then do the PWK labs, then take the exam. No shortcuts.",
        },
        "lab_setup": {
            "topic": "Home Lab Setup Guide",
            "minimum_viable_lab": {
                "hardware": "16GB RAM minimum (32GB recommended). Any modern CPU with virtualization support. 500GB SSD.",
                "hypervisor": "VirtualBox (free) or VMware Workstation Pro. Proxmox for dedicated lab server.",
                "attack_machine": "Kali Linux or Parrot OS. This is your workbench.",
                "targets": [
                    "Metasploitable 2/3 — classic vulnerable Linux",
                    "DVWA — web app security basics",
                    "Vulnhub machines — downloadable vulnerable VMs",
                    "HackTheBox/TryHackMe — cloud-based labs",
                ],
            },
            "ad_lab": {
                "setup": [
                    "Windows Server 2019/2022 — Domain Controller (eval license = 180 days)",
                    "Windows Server 2019/2022 — Member server (file server, SQL, IIS)",
                    "Windows 10/11 — Workstation joined to domain",
                    "Configure AD with realistic misconfigurations",
                ],
                "misconfigs_to_add": [
                    "Kerberoastable service accounts with weak passwords",
                    "AS-REP Roastable users (no preauth required)",
                    "ADCS with ESC1 vulnerable template",
                    "SMB signing disabled on member servers",
                    "LLMNR/NBT-NS enabled (default)",
                    "Local admin password reuse across machines",
                    "Unconstrained delegation on a server",
                    "Users in Domain Admins who shouldn't be",
                ],
                "automated": "GOAD (Game of Active Directory) — Vagrant/Terraform automated AD lab deployment. Multiple domains, forests, trusts. The best pre-built AD lab available.",
            },
            "cloud_lab": {
                "aws": "AWS free tier + CloudGoat for vulnerable scenarios",
                "azure": "Azure free tier + AzureGoat",
                "kubernetes": "Minikube or kind for local K8s + Kubernetes Goat",
            },
            "rick_note": "Your lab is your dojo. Build it, break it, rebuild it. I've rebuilt my AD lab hundreds of times. Every rebuild teaches you something about how defenders build, and every attack teaches you where they fail. The lab is where the craft lives.",
        },
        "mindset": {
            "topic": "The Mindset — How to Think Like an Operator",
            "from_tom": {
                "origin": "I started coding in USMC barracks in 2003. No bootcamp. No mentor. No CS degree. Just curiosity, discipline, and the Marine Corps mentality that failure is not an option.",
                "lesson": "You don't need permission to learn. You don't need the perfect setup. You need to START and not stop. Ever Evolving.",
            },
            "principles": {
                "check_the_clock": "Understand the mechanism before you touch it. What makes it tick? Re-read that. Study the target before you attack.",
                "builder_and_breaker": "The best hackers understand how things are built. Learn to build before you learn to break. The builder's eye sees structural weaknesses.",
                "thoroughness_over_speed": "Scanners are fast. Humans are thorough. Your value is in the manual analysis, the creative thinking, the business logic flaws that no tool finds.",
                "document_everything": "If it's not documented, it didn't happen. Marine Corps standard. Take notes obsessively. Screenshot everything. Your report IS your deliverable.",
                "fail_forward": "You will fail. Exploits won't work. Shells will die. Access will get burned. Learn from every failure. Fix it. Move on. The whole point of coding. And existence.",
                "stay_curious": "22 years in and I'm still learning. The day you think you know enough is the day you become irrelevant. If you are not willing to learn today, what is the point of learning tomorrow.",
                "rewrite_the_script": "Don't accept 'that's how it's always been done.' Question. Experiment. Break the pattern. Wanna learn how to keep going and be free? Rewrite the script.",
            },
            "operational_discipline": {
                "task_management": "Use task boards. Plan your engagement. Know your objectives before you start. Marine Corps mission planning applied to pentesting.",
                "time_management": "Father of three boys. Strategic time management. Work smart, not just hard. Every minute counts.",
                "accountability": "Hold yourself accountable. No judgment, but no excuses. We all have our sub-routines — let's try to fix them together.",
            },
            "the_warrior_path": {
                "warrior_in_the_garden": "Way better than a gardener in a war. Build in peace. Prepare for conflict. Protect always.",
                "cycle_breaker": "Break destructive patterns. In code and in life. Don't pass down the broken subroutines.",
                "ever_evolving": "The craft evolves. The craftsman evolves with it. WORKING ON ME mentality. Don't ever stop, unless you want to.",
                "music_reset": "When in doubt go to the music. Positive vibration. Reset. Come back stronger. The Message — Grand Master Flash.",
            },
            "ricks_voice": "I taught my son to build before I taught him anything else. The foundation determines everything above it. You want to learn to hack? First learn how things are built. Then you'll know where they break. That's the craft. That's what I passed down.",
            "rick_note": "The technical skills are the easy part. The mindset is what separates someone who hacks from someone who IS a hacker. Think like a builder — like Rick. Attack like a warrior — like a Marine. Document like your name is on it — because it is. I'm still building. Are you?",
        },
        "career": {
            "topic": "Career Path & Growth",
            "paths": {
                "penetration_tester": {
                    "entry": "Junior pentester, security analyst with pentest responsibilities",
                    "mid": "Penetration tester, security consultant, red team operator",
                    "senior": "Senior pentester, lead consultant, red team lead",
                    "leadership": "Principal consultant, practice lead, director of offensive security",
                },
                "appsec_engineer": {
                    "entry": "Application security analyst, secure code reviewer",
                    "mid": "AppSec engineer, security architect",
                    "senior": "Senior AppSec engineer, security engineering lead",
                    "leadership": "Head of AppSec, VP of product security",
                },
                "red_team": {
                    "entry": "Red team operator (usually requires pentest experience first)",
                    "mid": "Senior red team operator, custom tooling developer",
                    "senior": "Red team lead, adversary simulation architect",
                    "leadership": "Director of adversary simulation, CISO (offensive background)",
                },
            },
            "salary_ranges": {
                "note": "US market, 2024-2025, varies by location and company",
                "junior": "$70-100K",
                "mid": "$100-140K",
                "senior": "$140-200K",
                "lead_principal": "$180-250K+",
                "consulting_day_rate": "$1,500-3,000/day",
            },
            "how_to_stand_out": [
                "Build things — tools, labs, CTF challenges, blog posts. Show, don't tell.",
                "Get OSCP — it's still the most respected offensive cert",
                "Contribute to open-source security tools",
                "Speak at local meetups, then conferences",
                "Write quality reports — your report IS your product",
                "Specialize in something — go deep before going wide",
                "Network genuinely — help people, share knowledge, mentor others",
                "Never stop learning — the field changes faster than any other in tech",
            ],
            "rick_note": "The career path isn't linear. I went from Marine avionics to self-taught developer to security engineer. The thread is continuous learning and building. Build your reputation through quality work, honest reporting, and genuine community contribution. The cert gets you in the door. The work keeps you in the room. The character keeps you in the conversation.",
        },
    }
    t = params.topic.lower().strip()
    path = paths.get(t)
    if not path:
        return f"Error: Unknown topic '{t}'. Available: {', '.join(paths.keys())}"
    path["mentored_by"] = f"{CALLSIGN} — OSCP | OSWA | USMC Veteran | 22+ Years | Ever Evolving"
    return _fmt(path, params.response_format, title=f"{CALLSIGN} Mentorship")


def register(mcp):
    """Register tools on the MCP server."""
    mcp.tool(
        name="rick_compatibility_check",
        annotations={
            "title": "Job Compatibility Analyzer",
            "readOnlyHint": True,
            "destructiveHint": False,
            "idempotentHint": True,
            "openWorldHint": False,
        },
    )(_safe_tool(rick_compatibility_check))
    mcp.tool(
        name="rick_cover_letter",
        annotations={
            "title": "Cover Letter Generator",
            "readOnlyHint": True,
            "destructiveHint": False,
            "idempotentHint": True,
            "openWorldHint": False,
        },
    )(_safe_tool(rick_cover_letter))
    mcp.tool(
        name="rick_mentorship",
        annotations={
            "title": "Mentorship & Learning Paths",
            "readOnlyHint": True,
            "destructiveHint": False,
            "idempotentHint": True,
            "openWorldHint": False,
        },
    )(_safe_tool(rick_mentorship))
