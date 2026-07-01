"""Concrete-fill tests: generated matters must populate real downstream form mappings."""
import pytest

from generator import fill_form, generate_matter, list_forms, load_form


def test_forms_are_registered():
    assert set(list_forms()) >= {"FM-004", "IRS-SS-4"}


@pytest.mark.parametrize("form_id", list_forms())
@pytest.mark.parametrize("seed", range(4))
def test_fill_runs_and_fills_something(form_id, seed):
    scenario = load_form(form_id)["meta"]["best_scenario"]
    plan = fill_form(generate_matter(scenario, seed), form_id)
    assert plan["coverage"]["total_fields"] > 0
    # Every form should populate a meaningful chunk of its mapped fields.
    assert plan["coverage"]["filled_fields"] >= 10
    assert plan["required"]["ok"], f"{form_id} missing required keys: {plan['required']['missing']}"


def test_fm004_native_fill_covers_core_fields():
    """The court-forms namespace is our canonical namespace, so FM-004 fills natively."""
    plan = fill_form(generate_matter("family-divorce-cumberland", 1), "FM-004")
    assert plan["profile"] == "canonical"
    assert plan["coverage"]["filled_fields"] >= 25
    by_key = {e["fact_key"]: e["value"] for e in plan["entries"] if e["filled"]}
    assert by_key.get("parties.plaintiff.full_name")
    assert by_key.get("parties.defendant.full_name")
    assert by_key.get("parties.attorney.bar_number")
    assert by_key.get("matter.docket_number")


def test_ss4_adapter_fill_covers_entity_and_responsible_party():
    """The tax-forms namespace differs, so SS-4 fills via the tax adapter."""
    plan = fill_form(generate_matter("business-formation-scorp", 1), "IRS-SS-4")
    assert plan["profile"] == "tax"
    assert plan["coverage"]["filled_fields"] >= 14
    by_key = {e["fact_key"]: e["value"] for e in plan["entries"] if e["filled"]}
    assert by_key.get("entity.legal_name")
    assert by_key.get("responsible_party.name")
    tin = by_key.get("responsible_party.ssn_itin_ein", "")
    assert tin.startswith("900-"), "responsible-party TIN must be the fictional 900-series"


RETTD_SOURCES = ["real-estate-transfer", *load_form("ME-RETTD")["meta"].get("alt_scenarios", [])]


@pytest.mark.parametrize("scenario", RETTD_SOURCES)
def test_rettd_fills_from_every_sale_scenario(scenario):
    """Deed-style and closing-suite scenarios both drive the RETTD via role fallbacks."""
    plan = fill_form(generate_matter(scenario, 1), "ME-RETTD")
    assert plan["profile"] == "real_estate"
    by_key = {e["fact_key"]: e["value"] for e in plan["entries"] if e["filled"]}
    assert by_key.get("transferor.name"), f"{scenario}: no grantor"
    assert by_key.get("transferee.name"), f"{scenario}: no grantee"
    assert by_key.get("property.town"), f"{scenario}: no property town"
    assert by_key.get("property.purchase_price"), f"{scenario}: no price"
    assert by_key.get("property.transfer_date"), f"{scenario}: no transfer date"
    assert plan["coverage"]["filled_fields"] >= 15, f"{scenario}: thin coverage"


def test_rettd_grantor_grantee_fallback_maps_seller_buyer():
    matter = generate_matter("residential-purchase-sale", 2)
    plan = fill_form(matter, "ME-RETTD")
    by_key = {e["fact_key"]: e["value"] for e in plan["entries"] if e["filled"]}
    assert by_key["transferor.name"] == matter["parties"]["seller"]["full_name"]
    assert by_key["transferee.name"] == matter["parties"]["buyer"]["full_name"]


def test_ss4_does_not_invent_an_ein():
    """The form IS the EIN application; entity.ein must stay blank."""
    plan = fill_form(generate_matter("business-formation-scorp", 2), "IRS-SS-4")
    eins = [e["value"] for e in plan["entries"] if e["fact_key"] == "entity.ein"]
    assert all(v in (None, "") for v in eins)
