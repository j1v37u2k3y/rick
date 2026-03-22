"""Hypothesis property-based fuzz tests on input models."""

import pytest
from hypothesis import given, settings
from hypothesis import strategies as st
from pydantic import ValidationError

from rick_mcp.models.inputs import (
    C2CompareInput,
    CloudAttackInput,
    DetectionRulesInput,
    HardenInput,
    IncidentResponseInput,
    LogAnalysisInput,
    PayloadGuideInput,
    ReconInput,
    ScopingInput,
    VulnInput,
    WirelessInput,
)

# Strategy: printable non-whitespace-only strings within bounds
_printable = st.text(
    alphabet=st.characters(whitelist_categories=("L", "N", "P", "S")),
    min_size=1,
    max_size=20,
)


class TestFuzzReconInput:
    @given(_printable)
    @settings(max_examples=30)
    def test_accepts_printable_strings(self, target):
        model = ReconInput(target_type=target)
        assert len(model.target_type) >= 1

    @given(st.text(min_size=0, max_size=0))
    def test_rejects_empty(self, target):
        with pytest.raises(ValidationError):
            ReconInput(target_type=target)

    @given(st.text(min_size=51, max_size=100))
    @settings(max_examples=10)
    def test_rejects_too_long(self, target):
        with pytest.raises(ValidationError):
            ReconInput(target_type=target)


class TestFuzzVulnInput:
    @given(_printable)
    @settings(max_examples=20)
    def test_accepts_printable_strings(self, category):
        model = VulnInput(vuln_category=category)
        assert len(model.vuln_category) >= 1


class TestFuzzC2CompareInput:
    @given(_printable)
    @settings(max_examples=20)
    def test_accepts_printable_strings(self, scenario):
        model = C2CompareInput(scenario=scenario)
        assert len(model.scenario) >= 1


class TestFuzzCloudAttackInput:
    @given(_printable)
    @settings(max_examples=20)
    def test_accepts_printable_strings(self, provider):
        model = CloudAttackInput(cloud_provider=provider)
        assert len(model.cloud_provider) >= 1


class TestFuzzWirelessInput:
    @given(_printable)
    @settings(max_examples=20)
    def test_accepts_printable_strings(self, wtype):
        model = WirelessInput(wireless_type=wtype)
        assert len(model.wireless_type) >= 1


class TestFuzzPayloadGuideInput:
    @given(_printable)
    @settings(max_examples=20)
    def test_accepts_printable_strings(self, ptype):
        model = PayloadGuideInput(payload_type=ptype)
        assert len(model.payload_type) >= 1


class TestFuzzIncidentResponseInput:
    @given(_printable)
    @settings(max_examples=20)
    def test_accepts_printable_strings(self, itype):
        model = IncidentResponseInput(incident_type=itype)
        assert len(model.incident_type) >= 1


class TestFuzzDetectionRulesInput:
    @given(_printable)
    @settings(max_examples=20)
    def test_accepts_printable_strings(self, pattern):
        model = DetectionRulesInput(attack_pattern=pattern)
        assert len(model.attack_pattern) >= 1


class TestFuzzLogAnalysisInput:
    @given(_printable)
    @settings(max_examples=20)
    def test_accepts_printable_strings(self, source):
        model = LogAnalysisInput(log_source=source)
        assert len(model.log_source) >= 1


class TestFuzzHardenInput:
    @given(_printable)
    @settings(max_examples=20)
    def test_accepts_printable_strings(self, tech):
        model = HardenInput(technology=tech)
        assert len(model.technology) >= 1


class TestFuzzScopingInput:
    @given(_printable, st.integers(min_value=1, max_value=100))
    @settings(max_examples=20)
    def test_accepts_valid_combos(self, etype, count):
        model = ScopingInput(engagement_type=etype, target_count=count)
        assert model.target_count == count

    @given(st.integers(min_value=101, max_value=1000))
    @settings(max_examples=5)
    def test_rejects_target_count_too_high(self, count):
        with pytest.raises(ValidationError):
            ScopingInput(engagement_type="red_team", target_count=count)

    @given(st.integers(min_value=-100, max_value=0))
    @settings(max_examples=5)
    def test_rejects_target_count_too_low(self, count):
        with pytest.raises(ValidationError):
            ScopingInput(engagement_type="red_team", target_count=count)


class TestFuzzNullBytes:
    """Verify models handle null bytes in input."""

    def test_null_byte_in_recon(self):
        model = ReconInput(target_type="web\x00app")
        assert "\x00" in model.target_type
