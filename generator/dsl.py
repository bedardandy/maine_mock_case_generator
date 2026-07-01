"""A tiny declarative DSL so scenario archetypes stay data, not code.

A *spec* is any JSON/YAML value. Resolution rules:

* ``str``                         -> template-formatted against ``ctx``
* ``{"pick": [...]}``             -> one random element (then resolved)
* ``{"pick_n": [...], "n": N}``   -> N random elements (N may be int or {min,max})
* ``{"date_between": [iso, iso]}``-> a random ISO date in [start, end]
* ``{"date_offset": {"from": spec, "days": N}}`` -> the resolved date plus N days
  (N may be negative, or itself a spec such as ``{int_between}``) — real date
  arithmetic for statutory deadlines (45/180-day 1031 periods, cure periods,
  limitations dates) instead of hand-picked windows that can drift.
* ``{"int_between": [lo, hi]}``   -> a random integer in [lo, hi]
* ``{"int_between": [lo, hi, step]}`` -> same, quantized to multiples of step
  from lo (round dollar figures: [250000, 900000, 5000]).
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
        if "date_offset" in spec and len(spec) == 1:
            cfg = spec["date_offset"]
            base = resolve(cfg.get("from", ""), ctx, rng)
            days = cfg.get("days", 0)
            if not isinstance(days, int):
                days = int(resolve(days, ctx, rng))
            return (date.fromisoformat(str(base)) + _timedelta_days(days)).isoformat()
        if "int_between" in spec and len(spec) == 1:
            lo, hi, *step = spec["int_between"]
            if step:
                return rng.randrange(int(lo), int(hi) + 1, int(step[0]))
            return rng.randint(int(lo), int(hi))
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
