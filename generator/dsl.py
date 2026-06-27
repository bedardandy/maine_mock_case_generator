"""A tiny declarative DSL so scenario archetypes stay data, not code.

A *spec* is any JSON/YAML value. Resolution rules:

* ``str``                         -> template-formatted against ``ctx``
* ``{"pick": [...]}``             -> one random element (then resolved)
* ``{"pick_n": [...], "n": N}``   -> N random elements (N may be int or {min,max})
* ``{"date_between": [iso, iso]}``-> a random ISO date in [start, end]
* ``{"int_between": [lo, hi]}``   -> a random integer in [lo, hi]
* ``{"mul": [a, b, ...]}``        -> product of the operands (each resolved first),
                                     for coherent derived amounts (e.g. rent owed =
                                     monthly_rent * months_in_arrears)
* ``{"template": "..."}``         -> explicit template format (same as a bare str)
* ``dict`` / ``list``             -> resolved recursively

Unknown ``{placeholders}`` are left intact so tests can detect them.
"""
from __future__ import annotations

import random
import string
from datetime import date


class _SafeDict(dict):
    def __missing__(self, key):  # leave unknown placeholders visible
        return "{" + key + "}"


def safe_format(text: str, ctx: dict) -> str:
    return string.Formatter().vformat(text, (), _SafeDict(ctx))


def _as_number(value) -> float:
    """Coerce a resolved operand (possibly a '$1,200' style string) to a number."""
    if isinstance(value, (int, float)):
        return float(value)
    cleaned = str(value).replace(",", "").replace("$", "").strip()
    try:
        return float(cleaned)
    except ValueError:
        return 0.0


def _date_between(start: str, end: str, rng: random.Random) -> str:
    s = date.fromisoformat(start)
    e = date.fromisoformat(end)
    delta = (e - s).days
    if delta <= 0:
        return start
    return (s + _timedelta_days(rng.randint(0, delta))).isoformat()


def _timedelta_days(n: int):
    from datetime import timedelta

    return timedelta(days=n)


def resolve_count(spec, rng: random.Random) -> int:
    if spec is None:
        return 0
    if isinstance(spec, int):
        return spec
    if isinstance(spec, dict) and "min" in spec and "max" in spec:
        return rng.randint(int(spec["min"]), int(spec["max"]))
    raise ValueError(f"Bad count spec: {spec!r}")


def resolve(spec, ctx: dict, rng: random.Random):
    if isinstance(spec, str):
        return safe_format(spec, ctx)
    if isinstance(spec, list):
        return [resolve(item, ctx, rng) for item in spec]
    if isinstance(spec, dict):
        if "pick" in spec and len(spec) == 1:
            return resolve(rng.choice(spec["pick"]), ctx, rng)
        if "pick_n" in spec:
            options = list(spec["pick_n"])
            n = resolve_count(spec.get("n", 1), rng)
            n = min(n, len(options))
            chosen = rng.sample(options, n) if n else []
            return [resolve(item, ctx, rng) for item in chosen]
        if "date_between" in spec and len(spec) == 1:
            start, end = spec["date_between"]
            return _date_between(start, end, rng)
        if "int_between" in spec and len(spec) == 1:
            lo, hi = spec["int_between"]
            return rng.randint(int(lo), int(hi))
        if "mul" in spec and len(spec) == 1:
            prod = 1.0
            for operand in spec["mul"]:
                prod *= _as_number(resolve(operand, ctx, rng))
            return int(prod) if float(prod).is_integer() else round(prod, 2)
        if "template" in spec and len(spec) == 1:
            return safe_format(spec["template"], ctx)
        return {key: resolve(value, ctx, rng) for key, value in spec.items()}
    return spec


def pick_pool(pool, count_spec, ctx: dict, rng: random.Random) -> list:
    """Select and resolve a subset of a pool of item templates."""
    if not pool:
        return []
    count = resolve_count(count_spec, rng) if count_spec is not None else len(pool)
    count = max(0, min(count, len(pool)))
    chosen = rng.sample(pool, count) if count else []
    return [resolve(item, ctx, rng) for item in chosen]
