"""Tests for legal-issue tiering: the confounder mechanism.

The scenario-wide suite (test_generate.py) already checks every scenario for schema
validity, placeholder leaks, and determinism. Those would still pass if confounders
silently never fired, so these tests assert the mechanism's *behavior*: confounders
fire, gate coherently (requires/excludes), inject their facts into the canonical fact
set, contribute issues/defenses, record themselves in provenance, and stay deterministic
and leak-free.
"""
import json
import re

import pytest

from generator import engine, generate_matter, validate_matter

_PLACEHOLDER = re.compile(r"\{[a-z][a-z0-9_]*\}")


def _base_scenario(confounders, variants=None):
    return {
        "practice_area": "civil",
        "title": "{plaintiff_full_name} v. {defendant_full_name} (test)",
        "status": "pre_filing",
        "docket_prefix": "TST",
        "jurisdiction": {"state": "ME", "county": "random", "court_type": "District Court"},
        "dates": {"filing_date": {"date_between": ["2025-01-01", "2025-12-31"]}},
        "parties": {
            "client_role": "plaintiff",
            "attorney": False,
            "roles": [
                {"key": "plaintiff", "label": "Plaintiff"},
                {"key": "defendant", "label": "Defendant"},
            ],
        },
        "facts": {"base_fact": "present"},
        "variants": variants or [{"weight": 1, "quit_ground": "nonpayment"}],
        "confounders": confounders,
        "fact_pattern": {"summary": "A test matter.", "narrative": ["A test narrative."]},
    }


_STANDING = {
    "id": "standing-holding-co",
    "weight": 3,
    "confidence": "well-settled",
    "facts": {"standing_defect": True, "landlord_entity_type": "llc_holding_company"},
    "issue": {
        "issue": "Real party in interest / standing to bring FED",
        "category": "civil_procedure",
        "governing_law": "M.R. Civ. P. 17(a)",
        "strength": "moderate",
    },
    "defense": {
        "defense": "Plaintiff is not the real party in interest",
        "by": "{defendant_full_name}",
        "basis": "The signing landlord differs from the title-holding entity.",
    },
}
_WAIVER = {
    "id": "waiver-by-noncollection",
    "weight": 2,
    "requires": {"quit_ground": "nonpayment"},
    "facts": {"waiver_signal": True},
    "issue": {
        "issue": "Waiver of the right to terminate by long non-collection of rent",
        "category": "landlord_tenant",
        "governing_law": "14 M.R.S. § 6002",
        "strength": "weak",
    },
}


def _patch(monkeypatch, scenario):
    monkeypatch.setattr(engine, "load_scenario", lambda _id: scenario)


# --- pure helpers ---------------------------------------------------------

def test_confounder_applies_requires_and_excludes():
    ctx = {"quit_ground": "nonpayment", "tenancy_type": "at_will"}
    assert engine._confounder_applies({"requires": {"quit_ground": "nonpayment"}}, ctx)
    assert not engine._confounder_applies({"requires": {"quit_ground": "at_will"}}, ctx)
    assert engine._confounder_applies({"requires": {"quit_ground": ["nonpayment", "lease_violation"]}}, ctx)
    assert not engine._confounder_applies({"excludes": {"quit_ground": "nonpayment"}}, ctx)
    assert engine._confounder_applies({}, ctx)  # ungated applies anywhere


def test_weighted_sample_is_bounded_and_deterministic():
    import random
    pool = [{"id": "a", "weight": 1}, {"id": "b", "weight": 5}, {"id": "c", "weight": 1}]
    a = engine._weighted_sample(pool, 2, random.Random(7))
    b = engine._weighted_sample(pool, 2, random.Random(7))
    assert [x["id"] for x in a] == [x["id"] for x in b]  # deterministic
    assert len(a) == 2 and len({x["id"] for x in a}) == 2  # without replacement
    assert len(engine._weighted_sample(pool, 99, random.Random(1))) == 3  # capped at pool size


# --- integration through generate_matter ----------------------------------

def test_confounder_fires_and_injects_facts(monkeypatch):
    _patch(monkeypatch, _base_scenario({"count": {"min": 1, "max": 2}, "pool": [_STANDING, _WAIVER]}))
    matter = generate_matter("test", 0)
    fired = matter["provenance"].get("confounders")
    assert fired, "count min:1 must fire at least one confounder"
    # each fired confounder must have merged its facts into the canonical fact set
    facts = matter.get("facts", {})
    if "standing-holding-co" in fired:
        assert facts.get("standing_defect") is True
        assert facts.get("landlord_entity_type") == "llc_holding_company"
    if "waiver-by-noncollection" in fired:
        assert facts.get("waiver_signal") is True
    # a fired confounder with an issue must contribute a stamped issue
    issue_notes = " ".join(i.get("notes", "") for i in matter.get("issues", []))
    for cid in fired:
        assert f"confounder:{cid}" in issue_notes


def test_confounder_requires_gate_blocks_incoherent(monkeypatch):
    # at-will only variant: there is no rent, so the waiver confounder must never fire
    scen = _base_scenario(
        {"count": {"min": 1, "max": 2}, "pool": [_STANDING, _WAIVER]},
        variants=[{"weight": 1, "quit_ground": "at_will"}],
    )
    _patch(monkeypatch, scen)
    for seed in range(40):
        fired = generate_matter("test", seed)["provenance"].get("confounders", [])
        assert "waiver-by-noncollection" not in fired, f"waiver fired on at_will at seed {seed}"


def test_confounder_path_is_deterministic_and_leak_free(monkeypatch):
    _patch(monkeypatch, _base_scenario({"count": {"min": 1, "max": 2}, "pool": [_STANDING, _WAIVER]}))
    for seed in range(8):
        first = generate_matter("test", seed)
        second = generate_matter("test", seed)
        assert first == second
        assert not validate_matter(first)
        leaks = sorted(set(_PLACEHOLDER.findall(json.dumps(first, ensure_ascii=False))))
        assert not leaks, f"seed {seed} leaked {leaks}"


def test_zero_count_keeps_matter_clean(monkeypatch):
    _patch(monkeypatch, _base_scenario({"count": {"min": 0, "max": 0}, "pool": [_STANDING, _WAIVER]}))
    matter = generate_matter("test", 0)
    assert "confounders" not in matter["provenance"]
    assert "standing_defect" not in matter.get("facts", {})
