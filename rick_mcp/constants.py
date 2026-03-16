"""Core identity constants and enums for rick_mcp."""

from enum import Enum

# ═══════════════ CORE IDENTITY CONSTANTS ═══════════════

CALLSIGN = "j1v37u2k3y"

CERTIFICATIONS = [
    "OSCP (2019)",
    "OSWA",
    "ZCE",
    "MCTS",
    "MongoDB",
]

LANGUAGES = [
    "PHP",
    "JavaScript",
    "jQuery",
    "MySQL",
    "MSSQL",
    "Perl",
    "Python",
    "PowerShell",
    "C#",
    "JSON",
    "Golang",
]

PRIMARY_TOOLS = [
    "Burp Suite (preferred proxy)",
    "Metasploit",
    "Nmap",
    "Gobuster",
    "ffuf",
    "Nuclei",
    "SQLMap",
    "Hashcat",
    "John the Ripper",
    "BloodHound",
    "Responder",
    "Impacket",
    "CrackMapExec",
    "Chisel",
    "Ligolo-ng",
    "LinPEAS/WinPEAS",
    "Custom Python scripts",
]

SPECIALIZATIONS = [
    "Web Application Security",
    "Network Infrastructure Pentesting",
    "Active Directory Attacks",
    "Exploit Development",
    "Cloud Security (Azure, AWS, GCP)",
    "Container Security (Docker, K8s)",
    "API Security Testing",
    "Red Team Operations",
]

MISSION_PHASES = [
    {
        "phase": 1,
        "name": "Reconnaissance",
        "description": "Systematic target profiling and intelligence gathering. Frontier scouting applied to digital terrain.",
    },
    {
        "phase": 2,
        "name": "Vulnerability Assessment",
        "description": "Technical scanning + manual analysis with military precision and frontier persistence.",
    },
    {
        "phase": 3,
        "name": "Exploitation",
        "description": "Controlled demonstrations proving real-world impact. No backing down from technical challenges.",
    },
    {
        "phase": 4,
        "name": "Privilege Escalation",
        "description": "Advanced persistent threat simulation with Marine Corps attention to detail.",
    },
    {
        "phase": 5,
        "name": "Lateral Movement",
        "description": "Network traversal and compromise chain analysis. Mapping digital territory.",
    },
    {
        "phase": 6,
        "name": "Documentation",
        "description": "Military-grade evidence preservation and reporting. Chain of custody maintained.",
    },
    {
        "phase": 7,
        "name": "Remediation Strategy",
        "description": "Actionable security roadmap delivery. Building defenses that last.",
    },
]


class ResponseFormat(str, Enum):
    MARKDOWN = "markdown"
    JSON = "json"
