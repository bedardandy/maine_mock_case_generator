"""Unit tests for DSL resolution ops, including date arithmetic and stepped ints."""
import random
from datetime import date

import pytest

from generator import dsl, generate_matter


@pytest.fixture()
def rng():
    return random.Random(42)


def test_date_offset_fixed_days(rng):
    out = dsl.resolve({"date_offset": {"from": "2026-02-10", "days": 45}}, {}, rng)
    assert out == "2026-03-27"


def test_date_offset_negative_days(rng):
    out = dsl.resolve({"date_offset": {"from": "2026-03-01", "days": -30}}, {}, rng)
    assert out == "2026-01-30"


def test_date_offset_from_ctx_template(rng):
    ctx = {"closing_date": "2026-06-30"}
    out = dsl.resolve({"date_offset": {"from": "{closing_date}", "days": 180}}, ctx, rng)
    assert out == "2026-12-27"


def test_date_offset_days_may_be_a_spec(rng):
    out = dsl.resolve(
        {"date_offset": {"from": "2026-01-01", "days": {"int_between": [10, 20]}}}, {}, rng
    )
    d = (date.fromisoformat(out) - date(2026, 1, 1)).days
    assert 10 <= d <= 20


def test_date_offset_crosses_leap_day(rng):
    out = dsl.resolve({"date_offset": {"from": "2024-02-28", "days": 1}}, {}, rng)
    assert out == "2024-02-29"


def test_int_between_step_quantizes(rng):
    vals = {dsl.resolve({"int_between": [100000, 900000, 5000]}, {}, rng) for _ in range(60)}
    assert all(v % 5000 == 0 for v in vals)
    assert all(100000 <= v <= 900000 for v in vals)
    assert len(vals) > 5  # actually varies


def test_int_between_two_arg_unchanged(rng):
    vals = {dsl.resolve({"int_between": [1, 3]}, {}, rng) for _ in range(50)}
    assert vals == {1, 2, 3}


def test_1031_statutory_clock_is_exact():
    """The 45/180-day identification and exchange deadlines are computed, not sampled."""
    for seed in range(12):
        facts = generate_matter("like-kind-exchange-1031", seed)["facts"]
        rc = date.fromisoformat(facts["relinquished_closing_date"])
        ident = date.fromisoformat(facts["identification_deadline"])
        exch = date.fromisoformat(facts["exchange_deadline"])
        close = date.fromisoformat(facts["replacement_closing_date"])
        assert (ident - rc).days == 45, f"seed={seed} 45-day clock wrong"
        assert (exch - rc).days == 180, f"seed={seed} 180-day clock wrong"
        assert rc < close <= exch, f"seed={seed} replacement closing outside window"
