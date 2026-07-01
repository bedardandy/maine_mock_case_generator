"""The stress harness must perturb aggressively yet never break the schema contract."""
import json

import pytest

from generator import (
    generate_matter,
    list_scenarios,
    project_to_canonical,
    validate_canonical,
    validate_matter,
)
from generator.stress import MUTATORS, stress_matter, stress_variants

SCENARIOS = list_scenarios()


@pytest.mark.parametrize("scenario", SCENARIOS)
@pytest.mark.parametrize("mutator", sorted(MUTATORS))
def test_every_mutator_keeps_every_scenario_valid(scenario, mutator):
    matter = generate_matter(scenario, 1)
    variant = stress_matter(matter, mutator, 1)
    assert not validate_matter(variant), f"{mutator} broke {scenario}"
    case = project_to_canonical(variant)
    assert not validate_canonical(case), f"{mutator} broke {scenario} projection"
    assert variant["provenance"]["stress_mutator"] == mutator


def test_stress_is_deterministic():
    matter = generate_matter("family-divorce-cumberland", 3)
    a = stress_matter(matter, "maximal_lengths", 3)
    b = stress_matter(generate_matter("family-divorce-cumberland", 3), "maximal_lengths", 3)
    assert json.dumps(a, sort_keys=True) == json.dumps(b, sort_keys=True)


def test_stress_does_not_mutate_the_input():
    matter = generate_matter("family-divorce-cumberland", 3)
    before = json.dumps(matter, sort_keys=True)
    for name in MUTATORS:
        stress_matter(matter, name, 3)
    assert json.dumps(matter, sort_keys=True) == before


def test_drop_optionals_is_actually_minimal():
    variant = stress_matter(generate_matter("complex-civil-litigation", 1), "drop_optionals", 1)
    assert set(variant) == {"schema_version", "provenance", "matter", "parties", "fact_pattern"}
    assert set(variant["matter"]) == {"matter_id", "practice_area", "jurisdiction"}
    for party in variant["parties"].values():
        assert set(party) <= {"entity_type", "full_name"}
    # And an org-signer sparse matter still projects a signer.
    case = project_to_canonical(variant)
    assert case["party"]["full_name"]


def test_blank_strings_blanks_but_keeps_keys():
    variant = stress_matter(generate_matter("personal-injury-auto", 2), "blank_strings", 2)
    plaintiff = variant["parties"]["plaintiff"]
    assert plaintiff["phone"] == "" and plaintiff["email"] == "" and plaintiff["address"] == ""
    assert "phone" in plaintiff  # present-but-empty, not absent


def test_maximal_lengths_overflows_typical_fields():
    variant = stress_matter(generate_matter("small-claims-debt", 2), "maximal_lengths", 2)
    assert len(variant["matter"]["title"]) >= 220
    assert len(variant["fact_pattern"]["summary"]) >= 600
    assert len(variant["fact_pattern"]["narrative"]) >= 2500
    for party in variant["parties"].values():
        if party.get("full_name"):
            assert len(party["full_name"]) > 100


def test_unicode_stress_decorates_text_but_not_dates_or_numbers():
    matter = generate_matter("real-estate-transfer", 2)
    variant = stress_matter(matter, "unicode_stress", 2)
    assert variant["fact_pattern"]["summary"].startswith("«Üñïçødé» ")
    facts = variant["facts"]
    # ISO dates survive untouched; prose facts get decorated.
    assert facts["transfer_date"] == matter["facts"]["transfer_date"]
    assert facts["purchase_price"] == matter["facts"]["purchase_price"]
    assert facts["deed_type"].startswith("«Üñïçødé» ")


def test_stress_variants_yields_all_mutators():
    matter = generate_matter("small-claims-debt", 1)
    names = [name for name, _ in stress_variants(matter, 1)]
    assert names == list(MUTATORS)


def test_unknown_mutator_raises():
    with pytest.raises(KeyError):
        stress_matter(generate_matter("small-claims-debt", 1), "nope", 1)
