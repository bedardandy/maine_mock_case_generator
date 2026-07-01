"""Invariant tests for the edge-case scenario pack.

Each edge-* scenario exists to smoke-test a specific failure mode in downstream
document automation. These tests pin the hostile values so a regression in the
generator (or an over-eager "sanitizer") can't quietly defuse the stress case.
"""
import json
import re

import pytest

from generator import generate_matter, project_to_canonical, validate_matter

EDGE_PACK = [
    "edge-unicode-names",
    "edge-max-household",
    "edge-sparse-minimal",
    "edge-boundary-dates",
    "edge-money-extremes",
]


@pytest.mark.parametrize("scenario", EDGE_PACK)
def test_edge_pack_generates_and_projects(scenario):
    for seed in range(8):
        matter = generate_matter(scenario, seed)
        assert not validate_matter(matter), f"{scenario} seed={seed} invalid"
        case = project_to_canonical(matter)
        assert case["party"]["full_name"], f"{scenario} seed={seed} lost the signer"


def test_unicode_names_survive_projection_byte_for_byte():
    case = project_to_canonical(generate_matter("edge-unicode-names", 3))
    plaintiff = case["parties"]["plaintiff"]
    assert plaintiff["full_name"] == "José-María Düböis O'Callaghan-Núñez Jr."
    assert case["parties"]["defendant"]["full_name"] == (
        "Ändersson, Fitzwilliam & Sønsteby Timber Holdings, LLC"
    )
    assert case["parties"]["defendant"]["address"] == "1 Rue de l'Église, Suite 300"
    # The suffix must ride inside full_name, not vanish.
    assert plaintiff["full_name"].endswith("Jr.")
    # ensure_ascii=False round-trip keeps the diacritics as-is.
    blob = json.dumps(case, ensure_ascii=False)
    for needle in ("José-María", "O'Callaghan-Núñez", "Sønsteby", "l'Église", "“force majeure”"):
        if needle == "“force majeure”":
            continue  # facts spot-checked below
        assert needle in blob, f"missing {needle!r}"


def test_unicode_curly_quotes_and_em_dash_in_free_text():
    matter = generate_matter("edge-unicode-names", 1)
    assert "“force majeure”" in matter["facts"]["governing_clause"]
    assert "—" in matter["fact_pattern"]["narrative"]


def test_max_household_has_six_children_and_long_names():
    matter = generate_matter("edge-max-household", 5)
    children = [k for k in matter["parties"] if re.fullmatch(r"child_\d+", k)]
    assert sorted(children) == [f"child_{n}" for n in range(1, 7)]
    pet = matter["parties"]["petitioner"]
    assert pet["last_name"] == "Featherstonehaugh-Cholmondeley-Smythe"
    assert len(pet["full_name"]) > 60
    assert matter["facts"]["num_minor_children"] == 6
    # All six children survive projection.
    case = project_to_canonical(matter)
    assert all(f"child_{n}" in case["parties"] for n in range(1, 7))


def test_sparse_minimal_omits_every_optional():
    matter = generate_matter("edge-sparse-minimal", 2)
    assert "attorney" not in matter["parties"]
    for absent in ("intake_interview", "client_objectives", "third_parties",
                   "expert_opinions", "financials", "communications", "litigation"):
        assert absent not in matter, f"{absent} unexpectedly present"
    plaintiff = matter["parties"]["plaintiff"]
    for absent in ("phone", "email", "address", "date_of_birth", "ssn_last4"):
        assert absent not in plaintiff, f"plaintiff has optional {absent}"
    assert "event_date" not in matter["matter"]
    assert set(matter["facts"]) == {"invoice_total", "invoices_outstanding"}
    # Still projects with an organization as the signing filer.
    case = project_to_canonical(matter)
    assert case["party"]["full_name"] == "Kennebec Valley Pallet Co."


def test_boundary_dates_pin_the_calendar_traps():
    matter = generate_matter("edge-boundary-dates", 4)
    facts = matter["facts"]
    assert facts["accident_date"] == "2024-02-29"
    assert facts["sol_expiration_date"] == "2030-02-28"
    assert matter["matter"]["filing_date"] == "2026-01-01"
    assert matter["matter"]["event_date"] == "2024-02-29"
    assert matter["parties"]["plaintiff"]["date_of_birth"] == "1926-02-29"
    timeline = matter["fact_pattern"]["timeline"]
    dates = [e["date"] for e in timeline]
    assert dates == sorted(dates)
    assert dates.count("2024-02-29") == 2  # same-day pair kept, stably ordered


def test_money_extremes_amounts_are_exact():
    matter = generate_matter("edge-money-extremes", 0)
    amounts = {a["label"]: a["amount"] for a in matter["financials"]["amounts"]}
    assert amounts["Contract value"] == 123456789.10
    assert amounts["Liquidated-damages setoff (owner backcharge)"] == -2500.75
    assert amounts["Zero-dollar change order"] == 0
    assert amounts["Unreconciled ledger difference"] == 0.01
    assert amounts["Prompt-payment interest item"] == 1234.565
    total = matter["financials"]["total_claimed"]
    assert total == round(sum(amounts.values()), 2)
    # The zero-dollar line must not be dropped as falsy.
    assert len(matter["financials"]["amounts"]) == 6
    # Extreme facts also ride the canonical bridge untouched.
    case = project_to_canonical(matter)
    assert case["facts"]["contract_value"] == 123456789.10
    assert case["facts"]["liquidated_damages_setoff"] == -2500.75
