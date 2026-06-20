"""Edge-case and fuzz tests: wide seed sweeps plus boundary-condition assertions."""
import json
import re

import pytest

from generator import (
    generate_compound,
    generate_matter,
    list_compounds,
    list_scenarios,
    project_to_canonical,
    validate_canonical,
    validate_compound,
    validate_matter,
)

SCENARIOS = list_scenarios()
COMPOUNDS = list_compounds()
_PLACEHOLDER = re.compile(r"\{[a-z][a-z0-9_]*\}")
SWEEP = range(30)


def _leaks(obj) -> list:
    return sorted(set(_PLACEHOLDER.findall(json.dumps(obj, ensure_ascii=False))))


@pytest.mark.parametrize("scenario", SCENARIOS)
def test_wide_seed_sweep_is_valid_and_clean(scenario):
    """Every scenario stays valid and placeholder-clean across a wide seed range."""
    for seed in SWEEP:
        matter = generate_matter(scenario, seed)
        assert not validate_matter(matter), f"{scenario} seed={seed} invalid"
        assert not _leaks(matter), f"{scenario} seed={seed} leaked placeholders"
        assert not validate_canonical(project_to_canonical(matter)), f"{scenario} seed={seed} canonical invalid"


@pytest.mark.parametrize("compound_id", COMPOUNDS)
def test_compound_wide_seed_sweep(compound_id):
    for seed in range(16):
        compound = generate_compound(compound_id, seed)
        assert not validate_compound(compound), f"{compound_id} seed={seed} invalid"
        assert not _leaks(compound), f"{compound_id} seed={seed} leaked placeholders"


def test_pro_se_never_has_attorney_but_signer_present():
    """The pro-se edge case must never generate counsel, yet always projects a signer."""
    for seed in SWEEP:
        matter = generate_matter("pro-se-interstate-custody", seed)
        assert "attorney" not in matter["parties"], f"seed={seed} unexpectedly has counsel"
        case = project_to_canonical(matter)
        assert "attorney" not in case["parties"]
        assert case["party"]["full_name"], f"seed={seed} missing signer"


def test_insolvent_estate_is_always_insolvent():
    """The estate's claims must always exceed its assets (the whole point of the edge case)."""
    for seed in SWEEP:
        facts = generate_matter("insolvent-estate", seed)["facts"]
        assert facts["total_allowed_claims"] > facts["total_probate_assets"], f"seed={seed} not insolvent"


def test_zero_children_boundary_is_handled():
    """A scenario that can produce zero children must do so cleanly somewhere in the sweep."""
    found_zero = False
    for seed in range(40):
        matter = generate_matter("protection-from-abuse", seed)
        n = sum(1 for k in matter["parties"] if k.startswith("child_"))
        if n == 0:
            found_zero = True
            assert not validate_matter(matter)
            assert not _leaks(matter)
    assert found_zero, "expected at least one zero-children protection-from-abuse matter"


def test_multi_party_roster_projects_extras():
    """The deep-litigation roster (plaintiff_2/defendant_2/third_party_defendant) survives projection."""
    case = project_to_canonical(generate_matter("complex-civil-litigation", 1))
    for role in ("plaintiff", "plaintiff_2", "defendant", "defendant_2", "third_party_defendant"):
        assert role in case["parties"], f"{role} dropped in projection"
