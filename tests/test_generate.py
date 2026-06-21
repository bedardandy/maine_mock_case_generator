"""Generation tests across every scenario and a range of seeds."""
import json
import re

import pytest

from generator import generate_matter, list_scenarios, validate_matter

SCENARIOS = list_scenarios()
SEEDS = range(6)
_PLACEHOLDER = re.compile(r"\{[a-z][a-z0-9_]*\}")


def test_scenarios_exist():
    assert SCENARIOS, "no scenarios were discovered"
    assert {
        "business-dissolution",
        "llc-formation",
        "nonprofit-formation",
        "full-estate-administration",
        "emergency-guardianship",
    } <= set(SCENARIOS)


@pytest.mark.parametrize("scenario", SCENARIOS)
@pytest.mark.parametrize("seed", SEEDS)
def test_generated_matter_is_valid(scenario, seed):
    matter = generate_matter(scenario, seed)
    errors = validate_matter(matter)
    assert not errors, f"{scenario} seed={seed}: {errors}"


@pytest.mark.parametrize("scenario", SCENARIOS)
@pytest.mark.parametrize("seed", SEEDS)
def test_no_unresolved_placeholders(scenario, seed):
    matter = generate_matter(scenario, seed)
    leaks = sorted(set(_PLACEHOLDER.findall(json.dumps(matter, ensure_ascii=False))))
    assert not leaks, f"{scenario} seed={seed} leaked placeholders: {leaks}"


@pytest.mark.parametrize("scenario", SCENARIOS)
def test_generation_is_deterministic(scenario):
    first = generate_matter(scenario, 3)
    second = generate_matter(scenario, 3)
    assert first == second


@pytest.mark.parametrize("scenario", SCENARIOS)
def test_provenance_is_mock_and_reproducible(scenario):
    matter = generate_matter(scenario, 1)
    prov = matter["provenance"]
    assert prov["mock"] is True and prov["fictional"] is True
    assert prov["scenario_id"] == scenario
    assert prov["seed"] == 1


@pytest.mark.parametrize("scenario", SCENARIOS)
def test_fictional_contact_ranges(scenario):
    """Any phone/email present must use the reserved fiction ranges."""
    matter = generate_matter(scenario, 2)
    blob = json.dumps(matter, ensure_ascii=False)
    for phone in re.findall(r"\(\d{3}\) 555-\d{4}", blob):
        assert "555-01" in phone, f"non-fiction phone {phone} in {scenario}"
    for email in re.findall(r"[\w.]+@[\w.]+", blob):
        assert email.endswith(("example.com", "example.org", "example.net")), (
            f"non-fiction email {email} in {scenario}"
        )
