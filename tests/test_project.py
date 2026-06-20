"""Projection tests: a Mock Matter must reduce to a valid canonical case."""
import pytest

from generator import (
    generate_matter,
    list_scenarios,
    project_to_canonical,
    validate_canonical,
)
from generator.project import _CANONICAL_PARTY_FIELDS

SCENARIOS = list_scenarios()


@pytest.mark.parametrize("scenario", SCENARIOS)
@pytest.mark.parametrize("seed", range(4))
def test_projection_is_valid_canonical(scenario, seed):
    case = project_to_canonical(generate_matter(scenario, seed))
    errors = validate_canonical(case)
    assert not errors, f"{scenario} seed={seed}: {errors}"


@pytest.mark.parametrize("scenario", SCENARIOS)
def test_projection_has_matter_and_signer(scenario):
    case = project_to_canonical(generate_matter(scenario, 1))
    assert case["matter"], "canonical matter should not be empty"
    assert "party" in case, "a signing filer (party) should be present"
    assert case["party"].get("full_name")


@pytest.mark.parametrize("scenario", SCENARIOS)
def test_projected_parties_only_use_canonical_fields(scenario):
    case = project_to_canonical(generate_matter(scenario, 1))
    allowed = set(_CANONICAL_PARTY_FIELDS)
    for role, party in case["parties"].items():
        extra = set(party) - allowed
        assert not extra, f"{scenario} party '{role}' has non-canonical fields: {extra}"


@pytest.mark.parametrize("scenario", SCENARIOS)
def test_facts_pass_through_unchanged(scenario):
    matter = generate_matter(scenario, 1)
    case = project_to_canonical(matter)
    assert case.get("facts", {}) == matter.get("facts", {})
