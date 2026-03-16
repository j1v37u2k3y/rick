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


class ModeInput(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True, extra="forbid")
    mode: str = Field(
        ...,
        description="Mode: 'be_rick', 'pentest_mode', 'mentor_mode', 'evaluate_fit', 'engagement_ops'",
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
        description="Action: 'create', 'add_finding', 'update_finding', 'status', 'export'",
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
