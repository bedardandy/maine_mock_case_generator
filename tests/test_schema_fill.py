"""Schema-driven probate generator: determinism, smoke, and design-preservation checks."""
import re

import pytest

from generator import generate_for_form, list_probate_forms, load_form_fields

FORMS = list_probate_forms()
SEEDS = range(6)
_TYPED = {"currency", "date", "docket_number", "person_name"}


def _fields_by_id(form_id):
    return {f["field_id"]: f for f in load_form_fields(form_id)}


def test_probate_forms_vendored():
    assert FORMS, "no vendored probate schemas found"


@pytest.mark.parametrize("form_id", FORMS)
@pytest.mark.parametrize("seed", SEEDS)
def test_generates_without_error_and_has_shape(form_id, seed):
    case = generate_for_form(form_id, seed)
    assert set(case) >= {"case_dict", "narrative_facts", "_meta"}
    assert case["_meta"]["synthetic"] is True
    assert case["_meta"]["form"] == form_id
    assert case["_meta"]["seed"] == seed


@pytest.mark.parametrize("form_id", FORMS)
@pytest.mark.parametrize("stress", [False, True])
def test_deterministic_per_seed_and_stress(form_id, stress):
    a = generate_for_form(form_id, 4, stress)
    b = generate_for_form(form_id, 4, stress)
    assert a == b


@pytest.mark.parametrize("form_id", FORMS)
def test_no_sentinel_in_typed_blanks(form_id):
    """Design rule: 'Not applicable' must never land in a date/currency/numeric blank."""
    fields = _fields_by_id(form_id)
    for seed in SEEDS:
        case = generate_for_form(form_id, seed)
        for fid, value in case["narrative_facts"].items():
            dtype = fields.get(fid, {}).get("data_type")
            if dtype in _TYPED:
                assert value != "Not applicable", f"{form_id} {fid} ({dtype}) got the text sentinel"


@pytest.mark.parametrize("form_id", FORMS)
def test_jurat_components_are_short(form_id):
    """day/month/year blanks must get short, box-fitting values, not long strings."""
    for seed in SEEDS:
        case = generate_for_form(form_id, seed)
        for fid, value in case["narrative_facts"].items():
            if re.search(r"(^|_)day($|_)", fid):
                assert str(value).isdigit() and 1 <= int(value) <= 28
            if re.search(r"(^|_)year($|_)", fid):
                assert str(value).isdigit() and len(str(value)) == 4


@pytest.mark.parametrize("form_id", FORMS)
def test_fictional_contact_ranges(form_id):
    """Any phone/email must use the reserved fiction ranges (no real PII)."""
    import json
    blob = json.dumps(generate_for_form(form_id, 2), ensure_ascii=False)
    for phone in re.findall(r"\(207\) 555-\d{4}", blob):
        assert "555-01" in phone, f"non-fiction phone {phone} in {form_id}"
    for email in re.findall(r"[\w.]+@[\w.]+", blob):
        assert email.endswith("example.com"), f"non-fiction email {email} in {form_id}"


@pytest.mark.parametrize("form_id", FORMS)
def test_coherent_role_identity(form_id):
    """A role's name is identical everywhere it appears within one case."""
    case = generate_for_form(form_id, 1)
    for key, record in case.items():
        if key.endswith("_record") and isinstance(record, dict):
            names = [v for k, v in record.items() if k.lower().endswith("name") or k == key[:-7]]
            assert len(set(names)) <= 1, f"{form_id} {key} has inconsistent names: {names}"
