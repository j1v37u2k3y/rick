"""Pydantic input models for all rick_mcp tools."""

from pydantic import BaseModel, ConfigDict, Field

from rick_mcp.constants import ResponseFormat


class ReconInput(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True, extra="forbid")
    target_type: str = Field(
        ...,
        description="Target: 'web_app', 'network', 'cloud_azure', 'cloud_aws', 'active_directory', 'api', 'container', 'mobile'",
        min_length=1,
        max_length=50,
    )
    scope_notes: str | None = Field(default=None, max_length=500)
    response_format: ResponseFormat = Field(default=ResponseFormat.MARKDOWN)


class VulnInput(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True, extra="forbid")
    vuln_category: str = Field(
        ...,
        description="Category: 'injection', 'auth', 'xss', 'ssrf', 'idor', 'file_upload', 'deserialization', 'misconfig', 'crypto', 'privesc'",
        min_length=1,
        max_length=50,
    )
    context: str | None = Field(default=None, max_length=500)
    response_format: ResponseFormat = Field(default=ResponseFormat.MARKDOWN)


class CodeReviewInput(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True, extra="forbid")
    focus: str | None = Field(
        default="full",
        description="Lens: 'full', 'security', 'craftsmanship', 'architecture'",
        max_length=20,
    )
    language: str | None = Field(
        default=None, description="Language hint: python, javascript, typescript, go, etc.", max_length=50
    )
    response_format: ResponseFormat = Field(default=ResponseFormat.MARKDOWN)


class ROEInput(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True, extra="forbid")
    engagement_type: str = Field(
        ...,
        description="Type: 'pentest', 'red_team', 'vuln_assessment', 'phishing', 'cloud_audit', 'app_security'",
        min_length=1,
        max_length=50,
    )
    client_name: str | None = Field(default="[CLIENT]", max_length=100)
    duration_days: int | None = Field(default=10, ge=1, le=90)
    response_format: ResponseFormat = Field(default=ResponseFormat.MARKDOWN)


class ReportInput(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True, extra="forbid")
    section: str = Field(
        ..., description="Section: 'executive_summary', 'finding', 'methodology', 'scope', 'remediation', 'appendix'"
    )
    finding_title: str | None = Field(default=None, max_length=200)
    severity: str | None = Field(default=None)
    description: str | None = Field(default=None, max_length=1000)
    response_format: ResponseFormat = Field(default=ResponseFormat.MARKDOWN)


class ToolRecInput(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True, extra="forbid")
    scenario: str = Field(..., description="Describe the task/scenario", min_length=5, max_length=500)
    response_format: ResponseFormat = Field(default=ResponseFormat.MARKDOWN)


class ProposalInput(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True, extra="forbid")
    engagement_type: str = Field(
        ...,
        description="Type: 'web_app_pentest', 'network_pentest', 'ad_review', 'cloud_audit', 'red_team', 'api_security', 'full_scope'",
        min_length=1,
        max_length=50,
    )
    client_name: str | None = Field(default="[CLIENT]", max_length=100)
    estimated_days: int | None = Field(default=10, ge=1, le=90)
    special_requirements: str | None = Field(default=None, max_length=500)
    response_format: ResponseFormat = Field(default=ResponseFormat.MARKDOWN)


class OnboardInput(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True, extra="forbid")
    client_name: str | None = Field(default="[CLIENT]", max_length=100)
    engagement_type: str | None = Field(default="pentest", max_length=50)
    response_format: ResponseFormat = Field(default=ResponseFormat.MARKDOWN)


class CompatInput(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True, extra="forbid")
    description: str = Field(..., description="Job posting or engagement brief", min_length=10, max_length=3000)
    eval_type: str | None = Field(default="engagement", description="'engagement', 'role', 'contract'")
    response_format: ResponseFormat = Field(default=ResponseFormat.MARKDOWN)


class CoverInput(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True, extra="forbid")
    company_name: str = Field(..., min_length=1, max_length=100)
    role_title: str = Field(..., min_length=1, max_length=200)
    key_requirements: str | None = Field(default=None, max_length=1000)
    tone: str | None = Field(default="professional", description="'professional', 'conversational', 'executive'")
    response_format: ResponseFormat = Field(default=ResponseFormat.MARKDOWN)


class AttackChainInput(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True, extra="forbid")
    scenario: str = Field(
        ...,
        description="Starting position or target scenario: 'external_to_da', 'phishing_to_lateral', 'web_to_internal', 'cloud_to_onprem', 'insider_threat', 'supply_chain'",
        min_length=1,
        max_length=50,
    )
    target_environment: str | None = Field(
        default=None, description="Additional context about the target environment", max_length=500
    )
    response_format: ResponseFormat = Field(default=ResponseFormat.MARKDOWN)


class PivotInput(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True, extra="forbid")
    position: str = Field(
        ...,
        description="Current position: 'linux_webserver', 'windows_workstation', 'windows_server', 'container', 'cloud_instance', 'database_server', 'network_device'",
        min_length=1,
        max_length=50,
    )
    target_network: str | None = Field(default=None, description="Where you're trying to reach", max_length=500)
    response_format: ResponseFormat = Field(default=ResponseFormat.MARKDOWN)


class HardenInput(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True, extra="forbid")
    technology: str = Field(
        ...,
        description="Technology to harden: 'windows_server', 'linux_server', 'active_directory', 'web_application', 'cloud_aws', 'cloud_azure', 'kubernetes', 'network', 'database'",
        min_length=1,
        max_length=50,
    )
    priority: str | None = Field(default="all", description="'critical', 'quick_wins', 'all'")
    response_format: ResponseFormat = Field(default=ResponseFormat.MARKDOWN)


class CheatsheetInput(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True, extra="forbid")
    tool: str = Field(
        ...,
        description="Tool: 'nmap', 'burp', 'ffuf', 'hashcat', 'bloodhound', 'impacket', 'crackmapexec', 'chisel', 'sqlmap', 'kerbrute'",
        min_length=1,
        max_length=50,
    )
    response_format: ResponseFormat = Field(default=ResponseFormat.MARKDOWN)


class DebriefInput(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True, extra="forbid")
    engagement_type: str = Field(
        ...,
        description="Type: 'pentest', 'red_team', 'vuln_assessment', 'cloud_audit', 'app_security'",
        min_length=1,
        max_length=50,
    )
    client_name: str | None = Field(default="[CLIENT]", max_length=100)
    key_findings: str | None = Field(
        default=None, description="Comma-separated key findings for the debrief", max_length=1000
    )
    response_format: ResponseFormat = Field(default=ResponseFormat.MARKDOWN)


class MentorInput(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True, extra="forbid")
    topic: str = Field(
        ...,
        description="Topic: 'getting_started', 'web_app_path', 'network_path', 'ad_path', 'cloud_path', 'certifications', 'lab_setup', 'mindset', 'career'",
        min_length=1,
        max_length=50,
    )
    current_level: str | None = Field(default="beginner", description="'beginner', 'intermediate', 'advanced'")
    response_format: ResponseFormat = Field(default=ResponseFormat.MARKDOWN)


class ThreatModelInput(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True, extra="forbid")
    target: str = Field(
        ...,
        description="System to model: 'web_app', 'api', 'microservices', 'mobile_app', 'cloud_infra', 'ci_cd_pipeline', 'iot', 'active_directory'",
        min_length=1,
        max_length=50,
    )
    context: str | None = Field(default=None, description="Additional context about the system", max_length=500)
    response_format: ResponseFormat = Field(default=ResponseFormat.MARKDOWN)


class CVEInput(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True, extra="forbid")
    query: str = Field(
        ...,
        description="CVE ID (e.g. 'CVE-2021-44228') or keyword search (e.g. 'apache log4j')",
        min_length=1,
        max_length=200,
    )
    max_results: int | None = Field(default=5, ge=1, le=20)
    response_format: ResponseFormat = Field(default=ResponseFormat.MARKDOWN)


class ReconHandleInput(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True, extra="forbid")
    handle: str = Field(
        ...,
        description="Hacker handle / username to profile across public sources (e.g. 'j1v37u2k3y')",
        min_length=1,
        max_length=100,
    )
    ctftime_id: int | None = Field(
        default=None,
        description="Optional CTFTime numeric user ID — enables direct API enrichment instead of search-only",
        ge=1,
    )
    github_token: str | None = Field(
        default=None,
        description="Optional GitHub PAT to raise rate limit from 60/hr to 5000/hr",
        max_length=200,
    )
    response_format: ResponseFormat = Field(default=ResponseFormat.JSON)


class ModeInput(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True, extra="forbid")
    mode: str = Field(
        ...,
        description="Mode: 'be_rick', 'dick_mode', 'jarvis', 'pentest_mode', 'mentor_mode', 'evaluate_fit', 'engagement_ops'",
        min_length=1,
        max_length=50,
    )
    context: str | None = Field(
        default=None,
        description="Optional context: target for pentest, student level for mentor, job posting for evaluate, client name for engagement",
        max_length=5000,
    )


class HealthInput(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True, extra="forbid")
    fix: bool = Field(
        default=False,
        description="If True, attempt to repair failed components. Default is diagnose only.",
    )
    response_format: ResponseFormat = Field(default=ResponseFormat.MARKDOWN)


class TrackerInput(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True, extra="forbid")
    action: str = Field(
        ...,
        description="Action: 'create', 'add_finding', 'update_finding', 'status', 'export', 'export_csv', 'export_markdown'",
        min_length=1,
        max_length=20,
    )
    engagement_id: str | None = Field(default=None, max_length=100)
    data: str | None = Field(
        default=None,
        description="JSON string with action-specific data",
        max_length=5000,
    )
    response_format: ResponseFormat = Field(default=ResponseFormat.MARKDOWN)


# --- Phase 2 offensive tools ---


class C2CompareInput(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True, extra="forbid")
    scenario: str = Field(
        ...,
        description="Scenario: 'stealth', 'team_ops', 'budget', 'evasion', 'versatility', 'quick_deploy'",
        min_length=1,
        max_length=100,
    )
    response_format: ResponseFormat = Field(default=ResponseFormat.MARKDOWN)


class PayloadGuideInput(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True, extra="forbid")
    payload_type: str = Field(
        ...,
        description="Type: 'initial_access', 'persistence', 'lateral_movement', 'exfil'",
        min_length=1,
        max_length=50,
    )
    response_format: ResponseFormat = Field(default=ResponseFormat.MARKDOWN)


class CloudAttackInput(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True, extra="forbid")
    cloud_provider: str = Field(
        ...,
        description="Provider: 'azure', 'aws', 'gcp'",
        min_length=1,
        max_length=20,
    )
    response_format: ResponseFormat = Field(default=ResponseFormat.MARKDOWN)


class WirelessInput(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True, extra="forbid")
    wireless_type: str = Field(
        ...,
        description="Type: 'wifi', 'bluetooth', 'rfid'",
        min_length=1,
        max_length=20,
    )
    response_format: ResponseFormat = Field(default=ResponseFormat.MARKDOWN)


# --- Defensive tools ---


class IncidentResponseInput(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True, extra="forbid")
    incident_type: str = Field(
        ...,
        description="Type: 'ransomware', 'data_breach', 'insider_threat', 'bec', 'supply_chain'",
        min_length=1,
        max_length=50,
    )
    response_format: ResponseFormat = Field(default=ResponseFormat.MARKDOWN)


class DetectionRulesInput(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True, extra="forbid")
    attack_pattern: str = Field(
        ...,
        description="Pattern: 'credential_dumping', 'lateral_movement', 'c2_beaconing', 'data_exfil', 'persistence', 'privilege_escalation'",
        min_length=1,
        max_length=50,
    )
    response_format: ResponseFormat = Field(default=ResponseFormat.MARKDOWN)


class LogAnalysisInput(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True, extra="forbid")
    log_source: str = Field(
        ...,
        description="Source: 'windows_event', 'syslog', 'cloud_trail', 'web_server', 'firewall', 'dns'",
        min_length=1,
        max_length=50,
    )
    response_format: ResponseFormat = Field(default=ResponseFormat.MARKDOWN)


# --- Engagement tools ---


class ScopingInput(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True, extra="forbid")
    engagement_type: str = Field(
        ...,
        description="Type: 'web_app_pentest', 'network_pentest', 'ad_review', 'cloud_audit', 'red_team', 'api_security', 'full_scope'",
        min_length=1,
        max_length=50,
    )
    target_count: int = Field(default=1, ge=1, le=100)
    complexity: str = Field(
        default="medium",
        description="'low', 'medium', 'high'",
    )
    response_format: ResponseFormat = Field(default=ResponseFormat.MARKDOWN)


# --- JARVIS tools ---


class FullAutoInput(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True, extra="forbid")
    target: str = Field(
        ...,
        description="Target description — domain, IP, app name, org, or environment",
        min_length=1,
        max_length=500,
    )
    target_type: str = Field(
        default="web_app",
        description="Target type: 'web_app', 'network', 'cloud_azure', 'cloud_aws', 'active_directory', 'api', 'container', 'mobile'",
        max_length=50,
    )
    engagement_id: str | None = Field(
        default=None,
        description="Optional engagement ID to track state. Creates new if not found.",
        max_length=100,
    )
    response_format: ResponseFormat = Field(default=ResponseFormat.MARKDOWN)


class KillChainInput(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True, extra="forbid")
    action: str = Field(
        ...,
        description="Action: 'status', 'advance', 'add_finding', 'reset', 'list'",
        min_length=1,
        max_length=20,
    )
    engagement_id: str = Field(
        ...,
        description="Engagement ID to track",
        min_length=1,
        max_length=100,
    )
    phase: int | None = Field(
        default=None,
        description="Phase number (1-7) for advance/add_finding",
        ge=1,
        le=7,
    )
    finding: str | None = Field(
        default=None,
        description="Finding description to add to a phase",
        max_length=1000,
    )
    image_path: str | None = Field(
        default=None,
        description="Optional file path to attach an image/screenshot as evidence",
        max_length=500,
    )
    response_format: ResponseFormat = Field(default=ResponseFormat.MARKDOWN)


class NextMoveInput(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True, extra="forbid")
    engagement_id: str = Field(
        ...,
        description="Engagement ID to analyze",
        min_length=1,
        max_length=100,
    )
    current_position: str | None = Field(
        default=None,
        description="Where you are right now: 'linux_webserver', 'windows_workstation', 'windows_server', 'container', 'cloud_instance', 'database_server', 'network_device', or free text",
        max_length=500,
    )
    findings_so_far: str | None = Field(
        default=None,
        description="What you've found so far — comma separated or free text",
        max_length=2000,
    )
    response_format: ResponseFormat = Field(default=ResponseFormat.MARKDOWN)


class SitrepInput(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True, extra="forbid")
    engagement_id: str = Field(
        ...,
        description="Engagement ID to get sitrep for",
        min_length=1,
        max_length=100,
    )
    response_format: ResponseFormat = Field(default=ResponseFormat.MARKDOWN)


# --- JARVIS extended tools ---


class NotesInput(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True, extra="forbid")
    engagement_id: str = Field(..., min_length=1, max_length=100)
    action: str = Field(
        ...,
        description="Action: 'add', 'list', 'search', 'delete'",
        min_length=1,
        max_length=10,
    )
    content: str | None = Field(default=None, max_length=2000)
    search_term: str | None = Field(default=None, max_length=200)
    note_index: int | None = Field(default=None, ge=0, description="Index for delete action")
    image_path: str | None = Field(
        default=None,
        max_length=500,
        description="Optional file path to attach as evidence",
    )
    response_format: ResponseFormat = Field(default=ResponseFormat.MARKDOWN)


class TimelineInput(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True, extra="forbid")
    engagement_id: str = Field(..., min_length=1, max_length=100)
    filter_phase: int | None = Field(default=None, ge=1, le=7)
    filter_type: str | None = Field(
        default=None,
        description="Event type: 'finding', 'log', 'tool'",
        max_length=20,
    )
    since: str | None = Field(
        default=None,
        description="ISO timestamp — show events after this time",
        max_length=30,
    )
    until: str | None = Field(
        default=None,
        description="ISO timestamp — show events before this time",
        max_length=30,
    )
    response_format: ResponseFormat = Field(default=ResponseFormat.MARKDOWN)


class CompareInput(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True, extra="forbid")
    engagement_id_a: str = Field(..., min_length=1, max_length=100)
    engagement_id_b: str = Field(..., min_length=1, max_length=100)
    response_format: ResponseFormat = Field(default=ResponseFormat.MARKDOWN)


class ScopeCheckInput(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True, extra="forbid")
    engagement_id: str = Field(..., min_length=1, max_length=100)
    target: str | None = Field(
        default=None,
        max_length=500,
        description="Target/IP/hostname to check against scope",
    )
    action: str | None = Field(
        default=None,
        max_length=200,
        description="Action to check against ROE",
    )
    add_scope: str | None = Field(
        default=None,
        max_length=1000,
        description="Comma-separated scope items to add",
    )
    set_roe: str | None = Field(
        default=None,
        max_length=2000,
        description="Free-text ROE notes to store",
    )
    response_format: ResponseFormat = Field(default=ResponseFormat.MARKDOWN)


class ExportInput(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True, extra="forbid")
    engagement_id: str = Field(..., min_length=1, max_length=100)
    export_format: str = Field(
        default="markdown",
        description="Export format: 'markdown', 'json', 'csv'",
        max_length=10,
    )
    response_format: ResponseFormat = Field(default=ResponseFormat.MARKDOWN)


class ChecklistInput(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True, extra="forbid")
    engagement_id: str = Field(..., min_length=1, max_length=100)
    action: str = Field(
        ...,
        description="Action: 'generate', 'check', 'uncheck', 'status'",
        min_length=1,
        max_length=10,
    )
    item_index: int | None = Field(default=None, ge=0, description="Checklist item index for check/uncheck")
    phase: int | None = Field(default=None, ge=1, le=7, description="Phase to generate checklist for")
    response_format: ResponseFormat = Field(default=ResponseFormat.MARKDOWN)


class TagInput(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True, extra="forbid")
    engagement_id: str = Field(..., min_length=1, max_length=100)
    phase: int = Field(..., ge=1, le=7)
    finding_index: int = Field(..., ge=0, description="Index of finding within the phase")
    severity: str | None = Field(
        default=None,
        description="'critical', 'high', 'medium', 'low', 'info'",
        max_length=10,
    )
    category: str | None = Field(default=None, max_length=100)
    mitre_id: str | None = Field(
        default=None,
        description="MITRE ATT&CK technique ID, e.g. 'T1059.001'",
        max_length=20,
    )
    response_format: ResponseFormat = Field(default=ResponseFormat.MARKDOWN)


class RollbackInput(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True, extra="forbid")
    engagement_id: str = Field(..., min_length=1, max_length=100)
    confirm: bool = Field(default=False, description="Must be True to execute rollback")
    response_format: ResponseFormat = Field(default=ResponseFormat.MARKDOWN)


class WriteupInput(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True, extra="forbid")
    action: str = Field(
        ...,
        description="'list' (enumerate), 'read' (fetch one), 'search' (keyword search), 'index' (corpus intelligence)",
        min_length=1,
        max_length=20,
    )
    query: str | None = Field(
        default=None,
        description="Keyword/substring for search action",
        max_length=200,
    )
    path: str | None = Field(
        default=None,
        description="Relative path for read action, e.g. 'htb/lame.md'",
        max_length=500,
    )
    category: str | None = Field(
        default=None,
        description="Filter list/search by top-level directory, e.g. 'htb'",
        max_length=100,
    )
    limit: int = Field(default=20, ge=1, le=200)
    response_format: ResponseFormat = Field(default=ResponseFormat.MARKDOWN)
