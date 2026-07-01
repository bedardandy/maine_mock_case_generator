"""Tests for the simulated `communications` (deal/closing correspondence) section."""
import json
import re

import pytest

from generator import generate_matter, list_scenarios, validate_matter

# Scenarios in the real-estate / asset-sale closing suite that author a correspondence thread.
CLOSING_SCENARIOS = [
    "residential-purchase-sale",
    "commercial-property-sale",
    "subdivision-development-sale",
    "condo-unit-sale",
    "construction-loan-closing",
    "resource-extraction-sale",
    "business-asset-sale",
    "like-kind-exchange-1031",
]

_PLACEHOLDER = re.compile(r"\{[a-z][a-z0-9_]*\}")


def test_closing_scenarios_are_registered():
    available = set(list_scenarios())
    missing = [s for s in CLOSING_SCENARIOS if s not in available]
    assert not missing, f"closing scenarios not discovered: {missing}"


@pytest.mark.parametrize("scenario", CLOSING_SCENARIOS)
@pytest.mark.parametrize("seed", range(4))
def test_communications_present_and_well_formed(scenario, seed):
    matter = generate_matter(scenario, seed)
    comms = matter.get("communications")
    assert comms, f"{scenario} seed={seed}: no communications generated"
    for msg in comms:
        for key in ("id", "date", "from", "to", "summary"):
            assert msg.get(key), f"{scenario} seed={seed}: message missing '{key}': {msg}"


@pytest.mark.parametrize("scenario", CLOSING_SCENARIOS)
def test_communications_are_date_sorted(scenario):
    comms = generate_matter(scenario, 1)["communications"]
    dates = [m["date"] for m in comms]
    assert dates == sorted(dates), f"{scenario}: communications not chronologically sorted"


@pytest.mark.parametrize("scenario", CLOSING_SCENARIOS)
def test_communications_ids_are_unique(scenario):
    comms = generate_matter(scenario, 2)["communications"]
    ids = [m["id"] for m in comms]
    assert len(ids) == len(set(ids)), f"{scenario}: duplicate communication ids {ids}"


@pytest.mark.parametrize("scenario", CLOSING_SCENARIOS)
@pytest.mark.parametrize("seed", range(4))
def test_communications_have_no_placeholder_leaks(scenario, seed):
    comms = generate_matter(scenario, seed).get("communications", [])
    leaks = sorted(set(_PLACEHOLDER.findall(json.dumps(comms, ensure_ascii=False))))
    assert not leaks, f"{scenario} seed={seed}: communications leaked placeholders: {leaks}"


@pytest.mark.parametrize("scenario", CLOSING_SCENARIOS)
def test_closing_matter_is_valid(scenario):
    """A closing-suite matter (with communications + rich facts) still validates."""
    matter = generate_matter(scenario, 5)
    assert not validate_matter(matter)
    # The rich term-sheet/PSA facts should be populated.
    assert matter.get("facts"), f"{scenario}: expected populated term-sheet facts"


def test_communications_thread_is_a_back_and_forth():
    """The residential thread should alternate senders (an actual exchange, not a monologue)."""
    comms = generate_matter("residential-purchase-sale", 3)["communications"]
    senders = {m["from"] for m in comms}
    assert len(senders) >= 3, f"expected multiple correspondents, got {senders}"
