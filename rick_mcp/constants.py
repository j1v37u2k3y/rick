"""Constants and enums for rick_mcp. Identity loaded from ~/.rick_mcp/identity.yaml."""

from enum import Enum

from rick_mcp.identity import (
    CALLSIGN,
    CERTIFICATIONS,
    LANGUAGES,
    PRIMARY_TOOLS,
    SPECIALIZATIONS,
)

# Re-export identity fields so the rest of the codebase can import from here
__all__ = [
    "CALLSIGN",
    "CERTIFICATIONS",
    "LANGUAGES",
    "PRIMARY_TOOLS",
    "SPECIALIZATIONS",
    "MISSION_PHASES",
    "ResponseFormat",
]

MISSION_PHASES = [
    {
        "phase": 1,
        "name": "Reconnaissance",
        "description": "Systematic target profiling and intelligence gathering.",
    },
    {
        "phase": 2,
        "name": "Vulnerability Assessment",
        "description": "Technical scanning + manual analysis with precision and persistence.",
    },
    {
        "phase": 3,
        "name": "Exploitation",
        "description": "Controlled demonstrations proving real-world impact.",
    },
    {
        "phase": 4,
        "name": "Privilege Escalation",
        "description": "Advanced persistent threat simulation with attention to detail.",
    },
    {
        "phase": 5,
        "name": "Lateral Movement",
        "description": "Network traversal and compromise chain analysis.",
    },
    {
        "phase": 6,
        "name": "Documentation",
        "description": "Evidence preservation and reporting. Chain of custody maintained.",
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
