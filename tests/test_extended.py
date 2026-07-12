"""
RICK MCP — TEST SUITE
Measure twice, cut once. Test everything.

Tests every tool, every resource, every input path, every error case.
The craft demands it. Rick demands it.
"""

import json
from unittest.mock import patch

import pytest
from pydantic import ValidationError

from rick_mcp import (
    CALLSIGN,
    AttackChainInput,
    C2CompareInput,
    CheatsheetInput,
    CloudAttackInput,
    CompatInput,
    CoverInput,
    CVEInput,
    DebriefInput,
    DetectionRulesInput,
    HardenInput,
    HealthInput,
    IncidentResponseInput,
    LogAnalysisInput,
    MentorInput,
    ModeInput,
    OnboardInput,
    PayloadGuideInput,
    PivotInput,
    ProposalInput,
    ReconInput,
    ReportInput,
    ResponseFormat,
    ROEInput,
    ScopingInput,
    ToolRecInput,
    TrackerInput,
    VulnInput,
    WirelessInput,
    mcp,
    rick_c2_compare,
    rick_cheatsheet,
    rick_client_onboarding,
    rick_cloud_attack_path,
    rick_cve,
    rick_detection_rules,
    rick_engagement_proposal,
    rick_hardening,
    rick_incident_response,
    rick_log_analysis,
    rick_mentorship,
    rick_payload_guide,
    rick_recon,
    rick_report_template,
    rick_roe,
    rick_scoping,
    rick_tool_recommend,
    rick_tracker,
    rick_vuln_assess,
    rick_wireless,
)

# ═══════════════════════════════════════════════════════════════
#  TOOL 19: rick_cve — NVD CVE Lookup (mocked)
# ═══════════════════════════════════════════════════════════════


class TestRickCVE:
    @pytest.mark.asyncio
    async def test_cve_lookup_mocked(self):
        mock_response = json.dumps(
            {
                "totalResults": 1,
                "vulnerabilities": [
                    {
                        "cve": {
                            "id": "CVE-2021-44228",
                            "descriptions": [{"lang": "en", "value": "Apache Log4j2 RCE vulnerability"}],
                            "metrics": {
                                "cvssMetricV31": [{"cvssData": {"baseScore": 10.0, "baseSeverity": "CRITICAL"}}]
                            },
                            "weaknesses": [{"description": [{"value": "CWE-502"}]}],
                            "references": [{"url": "https://example.com"}],
                        }
                    }
                ],
            }
        ).encode()

        with patch("urllib.request.urlopen") as mock_urlopen:
            mock_urlopen.return_value.__enter__ = lambda s: s
            mock_urlopen.return_value.__exit__ = lambda s, *a: None
            mock_urlopen.return_value.read.return_value = mock_response

            result = await rick_cve(CVEInput(query="CVE-2021-44228"))
            assert "CVE-2021-44228" in result
            assert "10.0" in result

    @pytest.mark.asyncio
    async def test_cve_dedupes_cwes(self):
        # NVD lists a CWE per weakness node, so the same CWE can repeat across nodes
        # (real example: CVE-2020-9488 returns CWE-295 twice). Output must dedup.
        mock_response = json.dumps(
            {
                "totalResults": 1,
                "vulnerabilities": [
                    {
                        "cve": {
                            "id": "CVE-2020-9488",
                            "descriptions": [{"lang": "en", "value": "Apache Log4j SMTP appender cert mismatch"}],
                            "metrics": {"cvssMetricV31": [{"cvssData": {"baseScore": 3.7, "baseSeverity": "LOW"}}]},
                            "weaknesses": [
                                {"description": [{"value": "CWE-295"}]},
                                {"description": [{"value": "CWE-295"}]},
                            ],
                            "references": [{"url": "https://example.com"}],
                        }
                    }
                ],
            }
        ).encode()

        with patch("urllib.request.urlopen") as mock_urlopen:
            mock_urlopen.return_value.__enter__ = lambda s: s
            mock_urlopen.return_value.__exit__ = lambda s, *a: None
            mock_urlopen.return_value.read.return_value = mock_response

            result = await rick_cve(CVEInput(query="CVE-2020-9488", response_format="json"))
            data = json.loads(result)
            cwes = data["results"][0]["cwes"]
            assert cwes == ["CWE-295"], f"expected deduped CWEs, got {cwes}"

    @pytest.mark.asyncio
    async def test_cve_keyword_mocked(self):
        mock_response = json.dumps(
            {
                "totalResults": 0,
                "vulnerabilities": [],
            }
        ).encode()

        with patch("urllib.request.urlopen") as mock_urlopen:
            mock_urlopen.return_value.__enter__ = lambda s: s
            mock_urlopen.return_value.__exit__ = lambda s, *a: None
            mock_urlopen.return_value.read.return_value = mock_response

            result = await rick_cve(CVEInput(query="nonexistent-thing-xyz"))
            assert "No CVEs found" in result

    @pytest.mark.asyncio
    async def test_cve_http_error(self):
        import urllib.error

        with patch("rick_mcp.tools.cve._cache_get", return_value=None), patch("urllib.request.urlopen") as mock_urlopen:
            mock_urlopen.side_effect = urllib.error.HTTPError(url="", code=403, msg="Forbidden", hdrs=None, fp=None)
            result = await rick_cve(CVEInput(query="CVE-2021-44228"))
            assert "Error" in result
            assert "403" in result

    @pytest.mark.asyncio
    async def test_cve_url_error(self):
        import urllib.error

        with patch("rick_mcp.tools.cve._cache_get", return_value=None), patch("urllib.request.urlopen") as mock_urlopen:
            mock_urlopen.side_effect = urllib.error.URLError("Connection refused")
            result = await rick_cve(CVEInput(query="CVE-2021-44228"))
            assert "Error" in result
            assert "NVD API" in result

    @pytest.mark.asyncio
    async def test_cve_timeout(self):
        with patch("rick_mcp.tools.cve._cache_get", return_value=None), patch("urllib.request.urlopen") as mock_urlopen:
            mock_urlopen.side_effect = TimeoutError()
            result = await rick_cve(CVEInput(query="CVE-2021-44228"))
            assert "timed out" in result

    def test_cve_input_validation(self):
        with pytest.raises(ValidationError):
            CVEInput(query="")

    def test_cve_input_max_results_bounds(self):
        with pytest.raises(ValidationError):
            CVEInput(query="test", max_results=0)
        with pytest.raises(ValidationError):
            CVEInput(query="test", max_results=21)

    def test_cve_input_rejects_extra(self):
        with pytest.raises(ValidationError):
            CVEInput(query="test", extra="nope")

    @pytest.mark.asyncio
    async def test_cve_json_format(self):
        mock_response = json.dumps(
            {
                "totalResults": 1,
                "vulnerabilities": [
                    {
                        "cve": {
                            "id": "CVE-2021-44228",
                            "descriptions": [{"lang": "en", "value": "Test"}],
                            "metrics": {},
                            "weaknesses": [],
                            "references": [],
                        }
                    }
                ],
            }
        ).encode()

        with patch("urllib.request.urlopen") as mock_urlopen:
            mock_urlopen.return_value.__enter__ = lambda s: s
            mock_urlopen.return_value.__exit__ = lambda s, *a: None
            mock_urlopen.return_value.read.return_value = mock_response

            result = await rick_cve(CVEInput(query="CVE-2021-44228", response_format=ResponseFormat.JSON))
            parsed = json.loads(result)
            assert isinstance(parsed, dict)
            assert "results" in parsed


# ═══════════════════════════════════════════════════════════════
#  TOOL 20: rick_tracker — Engagement Tracker
# ═══════════════════════════════════════════════════════════════


@pytest.fixture
def tracker_dir(tmp_path):
    """Use a temp directory for tracker tests."""
    eng_dir = tmp_path / ".rick_mcp" / "engagements"
    eng_dir.mkdir(parents=True)
    with patch("pathlib.Path.home", return_value=tmp_path):
        yield eng_dir


class TestRickTracker:
    @pytest.mark.asyncio
    async def test_create_engagement(self, tracker_dir):
        with patch("pathlib.Path.home", return_value=tracker_dir.parent.parent):
            result = await rick_tracker(
                TrackerInput(
                    action="create",
                    data=json.dumps({"client": "Test Corp", "type": "pentest", "id": "ENG-TEST-001"}),
                )
            )
        assert "ENG-TEST-001" in result
        assert "Test Corp" in result

    @pytest.mark.asyncio
    async def test_add_finding(self, tracker_dir):
        # Create engagement first
        eng = {
            "id": "ENG-TEST-002",
            "client": "Test Corp",
            "type": "pentest",
            "status": "active",
            "findings": [],
            "created_at": "2026-01-01T00:00:00",
        }
        (tracker_dir / "ENG-TEST-002.json").write_text(json.dumps(eng))

        with patch("pathlib.Path.home", return_value=tracker_dir.parent.parent):
            result = await rick_tracker(
                TrackerInput(
                    action="add_finding",
                    engagement_id="ENG-TEST-002",
                    data=json.dumps({"title": "SQLi in Login", "severity": "critical"}),
                )
            )
        assert "F-001" in result
        assert "SQLi in Login" in result

    @pytest.mark.asyncio
    async def test_update_finding(self, tracker_dir):
        eng = {
            "id": "ENG-TEST-003",
            "client": "Test Corp",
            "type": "pentest",
            "status": "active",
            "findings": [{"id": "F-001", "title": "Test", "severity": "high", "status": "open"}],
            "created_at": "2026-01-01T00:00:00",
        }
        (tracker_dir / "ENG-TEST-003.json").write_text(json.dumps(eng))

        with patch("pathlib.Path.home", return_value=tracker_dir.parent.parent):
            result = await rick_tracker(
                TrackerInput(
                    action="update_finding",
                    engagement_id="ENG-TEST-003",
                    data=json.dumps({"finding_id": "F-001", "status": "remediated"}),
                )
            )
        assert "F-001" in result
        assert "Updated" in result

    @pytest.mark.asyncio
    async def test_status_single(self, tracker_dir):
        eng = {
            "id": "ENG-TEST-004",
            "client": "Test Corp",
            "type": "pentest",
            "status": "active",
            "findings": [
                {"id": "F-001", "title": "Test", "severity": "critical", "status": "open"},
                {"id": "F-002", "title": "Test2", "severity": "high", "status": "open"},
            ],
            "created_at": "2026-01-01T00:00:00",
        }
        (tracker_dir / "ENG-TEST-004.json").write_text(json.dumps(eng))

        with patch("pathlib.Path.home", return_value=tracker_dir.parent.parent):
            result = await rick_tracker(TrackerInput(action="status", engagement_id="ENG-TEST-004"))
        assert "ENG-TEST-004" in result
        assert "critical" in result

    @pytest.mark.asyncio
    async def test_status_all(self, tracker_dir):
        for i in range(3):
            eng = {
                "id": f"ENG-ALL-{i}",
                "client": "Test",
                "type": "pentest",
                "status": "active",
                "findings": [],
            }
            (tracker_dir / f"ENG-ALL-{i}.json").write_text(json.dumps(eng))

        with patch("pathlib.Path.home", return_value=tracker_dir.parent.parent):
            result = await rick_tracker(TrackerInput(action="status"))
        assert "3" in result

    @pytest.mark.asyncio
    async def test_export(self, tracker_dir):
        eng = {"id": "ENG-EXPORT", "client": "Test", "findings": []}
        (tracker_dir / "ENG-EXPORT.json").write_text(json.dumps(eng))

        with patch("pathlib.Path.home", return_value=tracker_dir.parent.parent):
            result = await rick_tracker(TrackerInput(action="export", engagement_id="ENG-EXPORT"))
        parsed = json.loads(result)
        assert parsed["id"] == "ENG-EXPORT"

    @pytest.mark.asyncio
    async def test_invalid_action(self, tracker_dir):
        with patch("pathlib.Path.home", return_value=tracker_dir.parent.parent):
            result = await rick_tracker(TrackerInput(action="invalid"))
        assert "Error" in result
        assert "Unknown action" in result

    @pytest.mark.asyncio
    async def test_add_finding_missing_engagement(self, tracker_dir):
        with patch("pathlib.Path.home", return_value=tracker_dir.parent.parent):
            result = await rick_tracker(TrackerInput(action="add_finding", engagement_id="NONEXISTENT"))
        assert "Error" in result
        assert "not found" in result

    @pytest.mark.asyncio
    async def test_add_finding_no_id(self, tracker_dir):
        with patch("pathlib.Path.home", return_value=tracker_dir.parent.parent):
            result = await rick_tracker(TrackerInput(action="add_finding"))
        assert "Error" in result
        assert "engagement_id required" in result

    @pytest.mark.asyncio
    async def test_update_finding_not_found(self, tracker_dir):
        eng = {
            "id": "ENG-UPD",
            "findings": [{"id": "F-001", "title": "Test", "severity": "high", "status": "open"}],
        }
        (tracker_dir / "ENG-UPD.json").write_text(json.dumps(eng))

        with patch("pathlib.Path.home", return_value=tracker_dir.parent.parent):
            result = await rick_tracker(
                TrackerInput(
                    action="update_finding",
                    engagement_id="ENG-UPD",
                    data=json.dumps({"finding_id": "F-999"}),
                )
            )
        assert "Error" in result
        assert "not found" in result

    @pytest.mark.asyncio
    async def test_export_missing(self, tracker_dir):
        with patch("pathlib.Path.home", return_value=tracker_dir.parent.parent):
            result = await rick_tracker(TrackerInput(action="export", engagement_id="NOPE"))
        assert "Error" in result

    @pytest.mark.asyncio
    async def test_export_no_id(self, tracker_dir):
        with patch("pathlib.Path.home", return_value=tracker_dir.parent.parent):
            result = await rick_tracker(TrackerInput(action="export"))
        assert "Error" in result
        assert "engagement_id required" in result

    @pytest.mark.asyncio
    async def test_create_invalid_json(self, tracker_dir):
        with patch("pathlib.Path.home", return_value=tracker_dir.parent.parent):
            result = await rick_tracker(TrackerInput(action="create", data="not json"))
        assert "Error" in result
        assert "Invalid JSON" in result

    @pytest.mark.asyncio
    async def test_status_no_engagements(self, tracker_dir):
        with patch("pathlib.Path.home", return_value=tracker_dir.parent.parent):
            result = await rick_tracker(TrackerInput(action="status"))
        assert "No engagements found" in result

    @pytest.mark.asyncio
    async def test_update_finding_missing_finding_id(self, tracker_dir):
        eng = {"id": "ENG-MIS", "findings": []}
        (tracker_dir / "ENG-MIS.json").write_text(json.dumps(eng))

        with patch("pathlib.Path.home", return_value=tracker_dir.parent.parent):
            result = await rick_tracker(
                TrackerInput(
                    action="update_finding",
                    engagement_id="ENG-MIS",
                    data=json.dumps({"status": "closed"}),
                )
            )
        assert "Error" in result
        assert "finding_id required" in result

    def test_tracker_input_rejects_extra(self):
        with pytest.raises(ValidationError):
            TrackerInput(action="status", extra="nope")

    @pytest.mark.asyncio
    async def test_tracker_export_csv(self, tmp_path):
        tracker_dir = tmp_path / ".rick_mcp" / "engagements"
        tracker_dir.mkdir(parents=True)
        eng_data = {
            "id": "ENG-CSV",
            "client": "TestCorp",
            "status": "active",
            "findings": [
                {"id": "F-1", "title": "SQLi", "severity": "critical", "status": "open", "added_at": "2026-03-21"},
            ],
        }
        (tracker_dir / "ENG-CSV.json").write_text(json.dumps(eng_data))

        with patch("pathlib.Path.home", return_value=tmp_path):
            result = await rick_tracker(TrackerInput(action="export_csv", engagement_id="ENG-CSV"))
        assert "id,title,severity,status,added_at" in result
        assert "F-1,SQLi,critical,open" in result

    @pytest.mark.asyncio
    async def test_tracker_export_csv_no_id(self):
        result = await rick_tracker(TrackerInput(action="export_csv"))
        assert "Error" in result

    @pytest.mark.asyncio
    async def test_tracker_export_markdown(self, tmp_path):
        tracker_dir = tmp_path / ".rick_mcp" / "engagements"
        tracker_dir.mkdir(parents=True)
        eng_data = {
            "id": "ENG-MD",
            "client": "TestCorp",
            "status": "active",
            "findings": [
                {"id": "F-1", "title": "XSS", "severity": "high", "status": "open"},
            ],
        }
        (tracker_dir / "ENG-MD.json").write_text(json.dumps(eng_data))

        with patch("pathlib.Path.home", return_value=tmp_path):
            result = await rick_tracker(TrackerInput(action="export_markdown", engagement_id="ENG-MD"))
        assert "# Engagement Report" in result
        assert "| F-1 | XSS | high | open |" in result

    @pytest.mark.asyncio
    async def test_tracker_export_markdown_no_id(self):
        result = await rick_tracker(TrackerInput(action="export_markdown"))
        assert "Error" in result


# ═══════════════════════════════════════════════════════════════
#  C2 COMPARE — Framework comparison tool
# ═══════════════════════════════════════════════════════════════

C2_SCENARIOS = ["stealth", "team_ops", "budget", "evasion", "versatility", "quick_deploy"]


class TestRickC2Compare:
    @pytest.mark.asyncio
    @pytest.mark.parametrize("scenario", C2_SCENARIOS)
    async def test_valid_scenarios(self, scenario):
        result = await rick_c2_compare(C2CompareInput(scenario=scenario))
        assert CALLSIGN in result
        assert "AUTHORIZED ENGAGEMENTS ONLY" in result

    @pytest.mark.asyncio
    async def test_invalid_scenario(self):
        result = await rick_c2_compare(C2CompareInput(scenario="nonexistent"))
        assert "Error" in result

    @pytest.mark.asyncio
    async def test_json_format(self):
        result = await rick_c2_compare(C2CompareInput(scenario="stealth", response_format=ResponseFormat.JSON))
        parsed = json.loads(result)
        assert "frameworks" in parsed

    def test_input_validation(self):
        with pytest.raises(ValidationError):
            C2CompareInput(scenario="")


# ═══════════════════════════════════════════════════════════════
#  PAYLOAD GUIDE — Methodology tool
# ═══════════════════════════════════════════════════════════════

PAYLOAD_TYPES = ["initial_access", "persistence", "lateral_movement", "exfil"]


class TestRickPayloadGuide:
    @pytest.mark.asyncio
    @pytest.mark.parametrize("payload_type", PAYLOAD_TYPES)
    async def test_valid_types(self, payload_type):
        result = await rick_payload_guide(PayloadGuideInput(payload_type=payload_type))
        assert CALLSIGN in result
        assert "AUTHORIZED ENGAGEMENTS ONLY" in result

    @pytest.mark.asyncio
    async def test_invalid_type(self):
        result = await rick_payload_guide(PayloadGuideInput(payload_type="nonexistent"))
        assert "Error" in result

    @pytest.mark.asyncio
    async def test_json_format(self):
        result = await rick_payload_guide(
            PayloadGuideInput(payload_type="initial_access", response_format=ResponseFormat.JSON)
        )
        parsed = json.loads(result)
        assert "methodology" in parsed

    def test_input_validation(self):
        with pytest.raises(ValidationError):
            PayloadGuideInput(payload_type="")


# ═══════════════════════════════════════════════════════════════
#  CLOUD ATTACK PATH — Provider-specific attack chains
# ═══════════════════════════════════════════════════════════════

CLOUD_PROVIDERS = ["azure", "aws", "gcp"]


class TestRickCloudAttackPath:
    @pytest.mark.asyncio
    @pytest.mark.parametrize("provider", CLOUD_PROVIDERS)
    async def test_valid_providers(self, provider):
        result = await rick_cloud_attack_path(CloudAttackInput(cloud_provider=provider))
        assert CALLSIGN in result
        assert "AUTHORIZED ENGAGEMENTS ONLY" in result

    @pytest.mark.asyncio
    async def test_invalid_provider(self):
        result = await rick_cloud_attack_path(CloudAttackInput(cloud_provider="oracle"))
        assert "Error" in result

    @pytest.mark.asyncio
    async def test_json_format(self):
        result = await rick_cloud_attack_path(
            CloudAttackInput(cloud_provider="aws", response_format=ResponseFormat.JSON)
        )
        parsed = json.loads(result)
        assert "attack_paths" in parsed

    def test_input_validation(self):
        with pytest.raises(ValidationError):
            CloudAttackInput(cloud_provider="")


# ═══════════════════════════════════════════════════════════════
#  WIRELESS — Physical layer attack playbooks
# ═══════════════════════════════════════════════════════════════

WIRELESS_TYPES = ["wifi", "bluetooth", "rfid"]


class TestRickWireless:
    @pytest.mark.asyncio
    @pytest.mark.parametrize("wtype", WIRELESS_TYPES)
    async def test_valid_types(self, wtype):
        result = await rick_wireless(WirelessInput(wireless_type=wtype))
        assert CALLSIGN in result
        assert "AUTHORIZED ENGAGEMENTS ONLY" in result

    @pytest.mark.asyncio
    async def test_invalid_type(self):
        result = await rick_wireless(WirelessInput(wireless_type="satellite"))
        assert "Error" in result

    @pytest.mark.asyncio
    async def test_json_format(self):
        result = await rick_wireless(WirelessInput(wireless_type="wifi", response_format=ResponseFormat.JSON))
        parsed = json.loads(result)
        assert "attack_vectors" in parsed

    def test_input_validation(self):
        with pytest.raises(ValidationError):
            WirelessInput(wireless_type="")


# ═══════════════════════════════════════════════════════════════
#  INCIDENT RESPONSE — IR playbooks
# ═══════════════════════════════════════════════════════════════

IR_TYPES = ["ransomware", "data_breach", "insider_threat", "bec", "supply_chain"]


class TestRickIncidentResponse:
    @pytest.mark.asyncio
    @pytest.mark.parametrize("incident_type", IR_TYPES)
    async def test_valid_types(self, incident_type):
        result = await rick_incident_response(IncidentResponseInput(incident_type=incident_type))
        assert CALLSIGN in result

    @pytest.mark.asyncio
    async def test_invalid_type(self):
        result = await rick_incident_response(IncidentResponseInput(incident_type="alien_invasion"))
        assert "Error" in result

    @pytest.mark.asyncio
    async def test_json_format(self):
        result = await rick_incident_response(
            IncidentResponseInput(incident_type="ransomware", response_format=ResponseFormat.JSON)
        )
        parsed = json.loads(result)
        assert "containment" in parsed

    def test_input_validation(self):
        with pytest.raises(ValidationError):
            IncidentResponseInput(incident_type="")


# ═══════════════════════════════════════════════════════════════
#  DETECTION RULES — Sigma/YARA templates
# ═══════════════════════════════════════════════════════════════

DETECTION_PATTERNS = [
    "credential_dumping",
    "lateral_movement",
    "c2_beaconing",
    "data_exfil",
    "persistence",
    "privilege_escalation",
]


class TestRickDetectionRules:
    @pytest.mark.asyncio
    @pytest.mark.parametrize("pattern", DETECTION_PATTERNS)
    async def test_valid_patterns(self, pattern):
        result = await rick_detection_rules(DetectionRulesInput(attack_pattern=pattern))
        assert CALLSIGN in result

    @pytest.mark.asyncio
    async def test_invalid_pattern(self):
        result = await rick_detection_rules(DetectionRulesInput(attack_pattern="nonexistent"))
        assert "Error" in result

    @pytest.mark.asyncio
    async def test_json_format(self):
        result = await rick_detection_rules(
            DetectionRulesInput(attack_pattern="credential_dumping", response_format=ResponseFormat.JSON)
        )
        parsed = json.loads(result)
        assert "sigma_template" in parsed
        assert "yara_template" in parsed

    def test_input_validation(self):
        with pytest.raises(ValidationError):
            DetectionRulesInput(attack_pattern="")


# ═══════════════════════════════════════════════════════════════
#  LOG ANALYSIS — Log review methodology
# ═══════════════════════════════════════════════════════════════

LOG_SOURCES = ["windows_event", "syslog", "cloud_trail", "web_server", "firewall", "dns"]


class TestRickLogAnalysis:
    @pytest.mark.asyncio
    @pytest.mark.parametrize("source", LOG_SOURCES)
    async def test_valid_sources(self, source):
        result = await rick_log_analysis(LogAnalysisInput(log_source=source))
        assert CALLSIGN in result

    @pytest.mark.asyncio
    async def test_invalid_source(self):
        result = await rick_log_analysis(LogAnalysisInput(log_source="crystal_ball"))
        assert "Error" in result

    @pytest.mark.asyncio
    async def test_json_format(self):
        result = await rick_log_analysis(
            LogAnalysisInput(log_source="windows_event", response_format=ResponseFormat.JSON)
        )
        parsed = json.loads(result)
        assert "what_to_look_for" in parsed

    def test_input_validation(self):
        with pytest.raises(ValidationError):
            LogAnalysisInput(log_source="")


# ═══════════════════════════════════════════════════════════════
#  SCOPING — Engagement scoping calculator
# ═══════════════════════════════════════════════════════════════

SCOPING_TYPES = [
    "web_app_pentest",
    "network_pentest",
    "ad_review",
    "cloud_audit",
    "red_team",
    "api_security",
    "full_scope",
]


class TestRickScoping:
    @pytest.mark.asyncio
    @pytest.mark.parametrize("eng_type", SCOPING_TYPES)
    async def test_valid_types(self, eng_type):
        result = await rick_scoping(ScopingInput(engagement_type=eng_type))
        assert CALLSIGN in result

    @pytest.mark.asyncio
    async def test_invalid_type(self):
        result = await rick_scoping(ScopingInput(engagement_type="nonexistent"))
        assert "Error" in result

    @pytest.mark.asyncio
    async def test_complexity_affects_hours(self):
        low = await rick_scoping(
            ScopingInput(engagement_type="web_app_pentest", complexity="low", response_format=ResponseFormat.JSON)
        )
        high = await rick_scoping(
            ScopingInput(engagement_type="web_app_pentest", complexity="high", response_format=ResponseFormat.JSON)
        )
        low_data = json.loads(low)
        high_data = json.loads(high)
        assert int(low_data["estimated_hours"]) < int(high_data["estimated_hours"])

    @pytest.mark.asyncio
    async def test_target_count_scales(self):
        one = await rick_scoping(
            ScopingInput(engagement_type="api_security", target_count=1, response_format=ResponseFormat.JSON)
        )
        five = await rick_scoping(
            ScopingInput(engagement_type="api_security", target_count=5, response_format=ResponseFormat.JSON)
        )
        one_data = json.loads(one)
        five_data = json.loads(five)
        assert int(one_data["estimated_hours"]) < int(five_data["estimated_hours"])

    @pytest.mark.asyncio
    async def test_json_format(self):
        result = await rick_scoping(ScopingInput(engagement_type="red_team", response_format=ResponseFormat.JSON))
        parsed = json.loads(result)
        assert "estimated_hours" in parsed
        assert "rate_card" in parsed

    def test_input_validation(self):
        with pytest.raises(ValidationError):
            ScopingInput(engagement_type="")

    def test_input_target_count_bounds(self):
        with pytest.raises(ValidationError):
            ScopingInput(engagement_type="red_team", target_count=0)
        with pytest.raises(ValidationError):
            ScopingInput(engagement_type="red_team", target_count=101)


# ═══════════════════════════════════════════════════════════════
#  CVE CACHE — File-based caching tests
# ═══════════════════════════════════════════════════════════════


class TestCVECache:
    def test_cache_key_deterministic(self):
        from rick_mcp.tools.cve import _cache_key

        k1 = _cache_key("https://example.com/api?q=test")
        k2 = _cache_key("https://example.com/api?q=test")
        assert k1 == k2

    def test_cache_key_different_urls(self):
        from rick_mcp.tools.cve import _cache_key

        k1 = _cache_key("https://example.com/a")
        k2 = _cache_key("https://example.com/b")
        assert k1 != k2

    def test_cache_roundtrip(self, tmp_path):
        from rick_mcp.tools.cve import _cache_get, _cache_set

        with patch("rick_mcp.tools.cve.CACHE_DIR", tmp_path):
            _cache_set("testkey", {"data": "hello"})
            result = _cache_get("testkey")
            assert result == {"data": "hello"}

    def test_cache_miss(self, tmp_path):
        from rick_mcp.tools.cve import _cache_get

        with patch("rick_mcp.tools.cve.CACHE_DIR", tmp_path):
            result = _cache_get("nonexistent")
            assert result is None

    def test_cache_expired(self, tmp_path):
        import time

        from rick_mcp.tools.cve import _cache_get, _cache_set

        with patch("rick_mcp.tools.cve.CACHE_DIR", tmp_path), patch("rick_mcp.tools.cve.CACHE_TTL", 0):
            _cache_set("expiredkey", {"data": "old"})
            time.sleep(0.1)
            result = _cache_get("expiredkey")
            assert result is None


# ═══════════════════════════════════════════════════════════════
#  PYDANTIC MODEL VALIDATION — Extra field rejection across all
# ═══════════════════════════════════════════════════════════════


class TestInputValidation:
    """Every input model uses ConfigDict(extra='forbid') — verify they all reject unknown fields."""

    @pytest.mark.parametrize(
        "model_cls,kwargs",
        [
            (ReconInput, {"target_type": "web_app", "extra": "nope"}),
            (VulnInput, {"vuln_category": "xss", "extra": "nope"}),
            (ROEInput, {"engagement_type": "pentest", "extra": "nope"}),
            (ReportInput, {"section": "finding", "extra": "nope"}),
            (ToolRecInput, {"scenario": "web app test", "extra": "nope"}),
            (ProposalInput, {"engagement_type": "red_team", "extra": "nope"}),
            (OnboardInput, {"extra": "nope"}),
            (CompatInput, {"description": "a valid description for testing", "extra": "nope"}),
            (CoverInput, {"company_name": "X", "role_title": "Y", "extra": "nope"}),
            (AttackChainInput, {"scenario": "external_to_da", "extra": "nope"}),
            (PivotInput, {"position": "container", "extra": "nope"}),
            (HardenInput, {"technology": "linux_server", "extra": "nope"}),
            (CheatsheetInput, {"tool": "nmap", "extra": "nope"}),
            (DebriefInput, {"engagement_type": "pentest", "key_findings": "test", "extra": "nope"}),
            (MentorInput, {"topic": "mindset", "extra": "nope"}),
            (CVEInput, {"query": "test", "extra": "nope"}),
            (HealthInput, {"fix": True, "extra": "nope"}),
            (ModeInput, {"mode": "be_rick", "extra": "nope"}),
            (TrackerInput, {"action": "status", "extra": "nope"}),
            (C2CompareInput, {"scenario": "stealth", "extra": "nope"}),
            (PayloadGuideInput, {"payload_type": "exfil", "extra": "nope"}),
            (CloudAttackInput, {"cloud_provider": "aws", "extra": "nope"}),
            (WirelessInput, {"wireless_type": "wifi", "extra": "nope"}),
            (IncidentResponseInput, {"incident_type": "ransomware", "extra": "nope"}),
            (DetectionRulesInput, {"attack_pattern": "persistence", "extra": "nope"}),
            (LogAnalysisInput, {"log_source": "dns", "extra": "nope"}),
            (ScopingInput, {"engagement_type": "red_team", "extra": "nope"}),
        ],
    )
    def test_extra_fields_rejected(self, model_cls, kwargs):
        with pytest.raises(ValidationError):
            model_cls(**kwargs)


# ═══════════════════════════════════════════════════════════════
#  RESPONSE FORMAT — Both formats work for all tools
# ═══════════════════════════════════════════════════════════════


class TestResponseFormats:
    @pytest.mark.asyncio
    async def test_enum_values(self):
        assert ResponseFormat.MARKDOWN == "markdown"
        assert ResponseFormat.JSON == "json"

    @pytest.mark.asyncio
    @pytest.mark.parametrize(
        "tool_fn,params",
        [
            (rick_recon, ReconInput(target_type="web_app", response_format=ResponseFormat.JSON)),
            (rick_vuln_assess, VulnInput(vuln_category="xss", response_format=ResponseFormat.JSON)),
            (rick_roe, ROEInput(engagement_type="pentest", response_format=ResponseFormat.JSON)),
            (rick_report_template, ReportInput(section="finding", response_format=ResponseFormat.JSON)),
            (rick_tool_recommend, ToolRecInput(scenario="web app test", response_format=ResponseFormat.JSON)),
            (rick_engagement_proposal, ProposalInput(engagement_type="red_team", response_format=ResponseFormat.JSON)),
            (rick_client_onboarding, OnboardInput(response_format=ResponseFormat.JSON)),
            (rick_hardening, HardenInput(technology="linux_server", response_format=ResponseFormat.JSON)),
            (rick_cheatsheet, CheatsheetInput(tool="nmap", response_format=ResponseFormat.JSON)),
            (rick_mentorship, MentorInput(topic="mindset", response_format=ResponseFormat.JSON)),
            (rick_c2_compare, C2CompareInput(scenario="stealth", response_format=ResponseFormat.JSON)),
            (rick_payload_guide, PayloadGuideInput(payload_type="exfil", response_format=ResponseFormat.JSON)),
            (rick_cloud_attack_path, CloudAttackInput(cloud_provider="aws", response_format=ResponseFormat.JSON)),
            (rick_wireless, WirelessInput(wireless_type="wifi", response_format=ResponseFormat.JSON)),
            (
                rick_incident_response,
                IncidentResponseInput(incident_type="ransomware", response_format=ResponseFormat.JSON),
            ),
            (
                rick_detection_rules,
                DetectionRulesInput(attack_pattern="persistence", response_format=ResponseFormat.JSON),
            ),
            (rick_log_analysis, LogAnalysisInput(log_source="dns", response_format=ResponseFormat.JSON)),
            (rick_scoping, ScopingInput(engagement_type="red_team", response_format=ResponseFormat.JSON)),
        ],
    )
    async def test_json_output_is_valid(self, tool_fn, params):
        result = await tool_fn(params)
        parsed = json.loads(result)
        assert isinstance(parsed, dict)


# ═══════════════════════════════════════════════════════════════
#  MCP SERVER — Registration integrity
# ═══════════════════════════════════════════════════════════════


class TestMCPServer:
    def test_server_name(self):
        assert mcp.name == "rick_mcp"


# ═══════════════════════════════════════════════════════════════
#  VAULT INTEGRATION — engagement tools writing to vault/Engagements/
# ═══════════════════════════════════════════════════════════════


@pytest.fixture
def configured_vault(tmp_path):
    """Bootstrap a minimal vault under tmp_path/.rick_mcp/vault. Returns the vault path.

    Note: the autouse conftest fixture already patches Path.home() to tmp_path, so this just
    needs to populate the vault subtree.
    """
    vault_dir = tmp_path / ".rick_mcp" / "vault"
    vault_dir.mkdir(parents=True)
    (vault_dir / "_CLAUDE.md").write_text("# stub\n", encoding="utf-8")
    (vault_dir / "log.md").write_text(
        "# Vault Activity Log\n\n## [2026-05-09] init | bootstrap\n\n---\n", encoding="utf-8"
    )
    (vault_dir / "Engagements").mkdir()
    return vault_dir


class TestEngagementVaultIntegration:
    @pytest.mark.asyncio
    async def test_proposal_writes_engagement_note(self, configured_vault):
        result = await rick_engagement_proposal(
            ProposalInput(
                engagement_type="web_app_pentest",
                client_name="Acme Corp",
                estimated_days=10,
            )
        )
        # Tool still returns markdown text
        assert "Proposal" in result
        # Vault note created
        eng_files = list((configured_vault / "Engagements").glob("*.md"))
        assert len(eng_files) == 1
        content = eng_files[0].read_text(encoding="utf-8")
        # AI-first frontmatter present
        assert "type: engagement" in content
        assert "ai-first: true" in content
        assert "client: Acme Corp" in content
        # Rick-voice body with wikilinks
        assert "[[Identity/Methodology]]" in content
        assert "[[Identity/Tools/Burp Suite]]" in content
        assert "[[Identity/Specializations/Web Application Security]]" in content
        # vault_path surfaced in tool output
        assert "vault_path" in result.lower() or "Engagements" in result

    @pytest.mark.asyncio
    async def test_proposal_skips_vault_when_unconfigured(self, tmp_path):
        # No vault bootstrap — autouse fixture has tmp_path as home, vault dir absent
        result = await rick_engagement_proposal(ProposalInput(engagement_type="network_pentest", client_name="Acme"))
        # Tool still works
        assert "Proposal" in result
        # No vault dir created
        assert not (tmp_path / ".rick_mcp" / "vault" / "Engagements").exists()

    @pytest.mark.asyncio
    async def test_proposal_does_not_overwrite_existing_note(self, configured_vault):
        # First call creates the note
        await rick_engagement_proposal(
            ProposalInput(engagement_type="web_app_pentest", client_name="Acme", estimated_days=10)
        )
        eng_file = next((configured_vault / "Engagements").glob("*.md"))
        original = eng_file.read_text(encoding="utf-8")

        # Second call with same client+type+date should preserve the original
        result = await rick_engagement_proposal(
            ProposalInput(engagement_type="web_app_pentest", client_name="Acme", estimated_days=20)
        )
        assert eng_file.read_text(encoding="utf-8") == original
        # Status surfaced as preserved
        assert "preserved" in result.lower() or "20" in result

    @pytest.mark.asyncio
    async def test_debrief_appends_to_matching_engagement(self, configured_vault):
        # Create the anchor first via proposal
        await rick_engagement_proposal(
            ProposalInput(engagement_type="web_app_pentest", client_name="Acme", estimated_days=10)
        )
        # Now run debrief
        await rick_debrief_inline_call_helper()
        # Find the engagement note
        eng_file = next((configured_vault / "Engagements").glob("Acme - Web App Pentest*.md"))
        content = eng_file.read_text(encoding="utf-8")
        assert "## Debrief" in content
        # Re-running debrief should append another Debrief section (or update the existing)
        assert "Updated" in content or "Engagement type" in content

    @pytest.mark.asyncio
    async def test_debrief_skips_when_no_matching_engagement(self, configured_vault):
        # Don't create a proposal first
        result = await rick_debrief_inline_call_helper()
        # Tool still returns text
        assert "Debrief" in result
        # No engagement file created
        eng_files = list((configured_vault / "Engagements").glob("*.md"))
        assert len(eng_files) == 0

    @pytest.mark.asyncio
    async def test_roe_appends_when_engagement_exists(self, configured_vault):
        # Create the proposal first
        await rick_engagement_proposal(ProposalInput(engagement_type="red_team", client_name="Acme", estimated_days=15))
        await rick_roe(ROEInput(engagement_type="red_team", client_name="Acme", duration_days=15))
        eng_file = next((configured_vault / "Engagements").glob("Acme - Red Team*.md"))
        content = eng_file.read_text(encoding="utf-8")
        assert "## Rules of Engagement" in content
        assert "Authorization" in content
        assert "PTES" in content

    @pytest.mark.asyncio
    async def test_onboarding_appends_when_engagement_exists(self, configured_vault):
        await rick_engagement_proposal(ProposalInput(engagement_type="ad_review", client_name="Acme", estimated_days=8))
        await rick_client_onboarding(OnboardInput(engagement_type="ad_review", client_name="Acme"))
        eng_file = next((configured_vault / "Engagements").glob("Acme - Ad Review*.md"))
        content = eng_file.read_text(encoding="utf-8")
        assert "## Client Onboarding" in content
        assert "Authorization checklist" in content

    @pytest.mark.asyncio
    async def test_roe_appends_when_vocab_differs_from_proposal(self, configured_vault):
        """Vault-projection vocab seam: proposal creates `Acme - Web App Pentest...`;
        ROE uses `app_security` vocab. The client-only fallback in
        `_find_matching_engagement` should still locate the proposal note."""
        await rick_engagement_proposal(
            ProposalInput(engagement_type="web_app_pentest", client_name="Acme", estimated_days=10)
        )
        await rick_roe(ROEInput(engagement_type="app_security", client_name="Acme", duration_days=10))
        eng_file = next((configured_vault / "Engagements").glob("Acme - Web App Pentest*.md"))
        content = eng_file.read_text(encoding="utf-8")
        assert "## Rules of Engagement" in content

    @pytest.mark.asyncio
    async def test_debrief_appends_when_vocab_differs_from_proposal(self, configured_vault):
        """Same vocab-mismatch path for `rick_debrief`."""
        from rick_mcp import rick_debrief
        from rick_mcp.models import DebriefInput

        await rick_engagement_proposal(
            ProposalInput(engagement_type="web_app_pentest", client_name="Acme", estimated_days=10)
        )
        await rick_debrief(DebriefInput(engagement_type="app_security", client_name="Acme"))
        eng_file = next((configured_vault / "Engagements").glob("Acme - Web App Pentest*.md"))
        content = eng_file.read_text(encoding="utf-8")
        assert "## Debrief" in content

    @pytest.mark.asyncio
    async def test_scoping_logs_to_vault(self, configured_vault):
        await rick_scoping(ScopingInput(engagement_type="red_team", target_count=2, complexity="high"))
        log_content = (configured_vault / "log.md").read_text(encoding="utf-8")
        assert "scoping | Calculator run" in log_content
        assert "red_team" in log_content

    @pytest.mark.asyncio
    async def test_scoping_suppressed_skips_vault(self, configured_vault):
        # Regression (#58): with suppress_vault_writes set (as rick_demo does during its tour),
        # scoping must NOT log to the vault — live output without mutating the Second Brain.
        from rick_mcp.tools.engagement import suppress_vault_writes

        token = suppress_vault_writes.set(True)
        try:
            await rick_scoping(ScopingInput(engagement_type="red_team", target_count=2, complexity="high"))
        finally:
            suppress_vault_writes.reset(token)
        log_content = (configured_vault / "log.md").read_text(encoding="utf-8")
        assert "scoping | Calculator run" not in log_content

    @pytest.mark.asyncio
    async def test_tracker_create_writes_vault_note(self, configured_vault):
        # Need to seed engagements/ dir for tracker
        (configured_vault.parent / "engagements").mkdir(exist_ok=True)
        result = await rick_tracker(
            TrackerInput(
                action="create",
                data=json.dumps({"id": "ENG-VAULT-001", "client": "Acme", "type": "web_app_pentest"}),
            )
        )
        assert "ENG-VAULT-001" in result
        # Vault note created
        eng_file = configured_vault / "Engagements" / "ENG-VAULT-001.md"
        assert eng_file.exists()
        content = eng_file.read_text(encoding="utf-8")
        assert "ENG-VAULT-001" in content
        assert "Acme" in content
        assert "type: engagement" in content
        assert "no findings yet" in content.lower()

    @pytest.mark.asyncio
    async def test_tracker_add_finding_refreshes_vault_note(self, configured_vault):
        eng_dir = configured_vault.parent / "engagements"
        eng_dir.mkdir(exist_ok=True)
        # Create initial engagement
        await rick_tracker(
            TrackerInput(
                action="create",
                data=json.dumps({"id": "ENG-VAULT-002", "client": "Acme", "type": "ad_review"}),
            )
        )
        # Add a finding
        result = await rick_tracker(
            TrackerInput(
                action="add_finding",
                engagement_id="ENG-VAULT-002",
                data=json.dumps({"title": "Kerberoastable SPN", "severity": "high"}),
            )
        )
        assert "F-001" in result
        # Vault note refreshed with finding row
        eng_file = configured_vault / "Engagements" / "ENG-VAULT-002.md"
        content = eng_file.read_text(encoding="utf-8")
        assert "F-001" in content
        assert "Kerberoastable SPN" in content
        assert "high" in content
        # Severity breakdown line
        assert "Severity breakdown" in content


# Helper used in vault integration tests (importable scope)
async def rick_debrief_inline_call_helper():
    """Run rick_debrief with consistent test inputs. Imported lazily to avoid name shadowing."""
    from rick_mcp import rick_debrief

    return await rick_debrief(
        DebriefInput(
            engagement_type="web_app_pentest",
            client_name="Acme",
            key_findings="SQLi in login, XSS in profile, auth bypass",
        )
    )
