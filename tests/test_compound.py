"""Compound (intertwined) matter tests."""
import pytest

from generator import (
    generate_compound,
    list_compounds,
    project_compound,
    validate_canonical,
    validate_compound,
)

COMPOUNDS = list_compounds()


def test_compounds_exist():
    assert set(COMPOUNDS) >= {
        "death-cascade", "marital-breakdown-cascade", "business-dispute-cascade",
        "estate-property-sale",
    }


@pytest.mark.parametrize("compound_id", COMPOUNDS)
@pytest.mark.parametrize("seed", range(4))
def test_compound_validates(compound_id, seed):
    compound = generate_compound(compound_id, seed)
    errors = validate_compound(compound)
    assert not errors, f"{compound_id} seed={seed}: {errors[:3]}"


@pytest.mark.parametrize("compound_id", COMPOUNDS)
def test_constituents_project_to_valid_canonical(compound_id):
    compound = generate_compound(compound_id, 1)
    for item in project_compound(compound):
        errs = validate_canonical(item["canonical"])
        assert not errs, f"{compound_id} {item['matter_id']}: {errs[:2]}"


@pytest.mark.parametrize("compound_id", COMPOUNDS)
def test_universe_id_is_consistent(compound_id):
    compound = generate_compound(compound_id, 1)
    uid = compound["universe_id"]
    for matter in compound["matters"]:
        assert matter["matter"]["universe_id"] == uid


@pytest.mark.parametrize("compound_id", COMPOUNDS)
def test_shared_cast_is_truly_shared(compound_id):
    """A cast member appearing in two matters must be the SAME identity in both."""
    compound = generate_compound(compound_id, 3)
    matters = {m["matter"]["matter_id"]: m for m in compound["matters"]}
    # Map compound-local matter id -> generated matter_id via order.
    local_ids = [m["provenance"]["scenario_id"] for m in compound["matters"]]
    assert len(local_ids) == len(compound["matters"])

    shared_checked = 0
    for cast_member in compound["cast"]:
        appearances = cast_member["appears_as"]
        if len(appearances) < 2:
            continue
        names = set()
        for appearance in appearances:
            # find the matter whose compound-local id matches
            idx = [a["matter_id"] for a in [appearance]][0]
            # locate the matter by order index
            order_ids = [mm["id"] for mm in _matter_specs(compound)]
            matter = compound["matters"][order_ids.index(idx)]
            party = matter["parties"][appearance["role"]]
            names.add(party.get("full_name") or party.get("organization_name"))
        assert len(names) == 1, f"{cast_member['cast_id']} differs across matters: {names}"
        shared_checked += 1
    assert shared_checked >= 1, "expected at least one cast member shared across matters"


@pytest.mark.parametrize("compound_id", COMPOUNDS)
def test_related_matters_reference_real_siblings(compound_id):
    compound = generate_compound(compound_id, 1)
    all_ids = {m["matter"]["matter_id"] for m in compound["matters"]}
    for matter in compound["matters"]:
        for rel in matter.get("related_matters", []):
            assert rel["matter_id"] in all_ids
            assert rel["universe_id"] == compound["universe_id"]


def _matter_specs(compound):
    """Reconstruct the compound-local matter order from the loaded archetype."""
    from generator import load_compound
    return load_compound(compound["provenance"]["compound_id"])["matters"]
