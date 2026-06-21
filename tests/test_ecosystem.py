import json
from datetime import date

from generator import (
    SmokeConfig,
    generate_matter,
    mutate_fixture,
    route_and_plan,
    run_ecosystem_smoke,
)
from generator.ecosystem import report_junit, report_markdown, verify_catalog_lock


def test_reference_date_is_deterministic_and_in_provenance():
    matter = generate_matter("family-divorce-cumberland", 4, reference_date=date(2030, 5, 1))
    assert matter == generate_matter("family-divorce-cumberland", 4, "2030-05-01")
    assert matter["provenance"]["reference_date"] == "2030-05-01"
    assert len(matter["provenance"]["fixture_id"]) == 20


def test_mutations_are_deterministic_and_non_mutating():
    matter = generate_matter("family-divorce-cumberland", 1)
    original = json.dumps(matter, sort_keys=True)
    first = mutate_fixture(matter, "unicode", 7)
    second = mutate_fixture(matter, "unicode", 7)
    assert first == second
    assert json.dumps(matter, sort_keys=True) == original
    assert first["provenance"]["mutation"]["operator"] == "unicode"


def test_catalog_lock_and_route_plan():
    assert verify_catalog_lock() == []
    plan = route_and_plan(generate_matter("business-formation-scorp", 1))
    ids = {form["form_id"] for form in plan["forms"]}
    assert {"IRS-SS-4", "IRS-2553"} <= ids
    assert any(item["workflow_id"] == "entity-formation" for item in plan["workflows"])


def test_ecosystem_report_formats():
    report = run_ecosystem_smoke(SmokeConfig(
        scenarios=["business-formation-scorp"], seeds=[1],
        repositories=["transactional-tax-forms"],
    ))
    assert report.ok
    assert report.runs
    assert "Ecosystem smoke report" in report_markdown(report)
    assert "<testsuite" in report_junit(report)
