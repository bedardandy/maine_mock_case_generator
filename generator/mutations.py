"""Deterministic fixture mutation operators for boundary and failure testing."""
from __future__ import annotations

import copy
import random
from datetime import date, timedelta

MUTATIONS = (
    "missing",
    "max_length",
    "unicode",
    "multiline",
    "repeated_party",
    "contradictory",
    "invalid_date",
    "boundary_amount",
    "radio_group",
)


def _leaf_paths(value, prefix=()):
    if isinstance(value, dict):
        for key in sorted(value):
            yield from _leaf_paths(value[key], prefix + (key,))
    elif isinstance(value, list):
        for index, item in enumerate(value):
            yield from _leaf_paths(item, prefix + (index,))
    else:
        yield prefix


def _set(root, path, value):
    node = root
    for part in path[:-1]:
        node = node[part]
    node[path[-1]] = value


def mutate_fixture(matter: dict, operator: str, seed: int = 0) -> dict:
    """Return a mutated deep copy; the source matter is never modified."""
    if operator not in MUTATIONS:
        raise ValueError(f"Unknown mutation '{operator}'. Available: {', '.join(MUTATIONS)}")
    out = copy.deepcopy(matter)
    rng = random.Random(seed)
    leaves = [p for p in _leaf_paths(out) if p and p[0] not in {"provenance", "schema_version"}]
    path = rng.choice(leaves) if leaves else ("notes",)
    if operator == "missing":
        _set(out, path, None)
    elif operator == "max_length":
        _set(out, path, "X" * 4096)
    elif operator == "unicode":
        _set(out, path, "Zoë O’Connor — Wabanaki 测试")
    elif operator == "multiline":
        _set(out, path, "Line one\nLine two\nLine three")
    elif operator == "repeated_party":
        parties = out.setdefault("parties", {})
        source = next(iter(parties.values()), {})
        parties["duplicate_test_party"] = copy.deepcopy(source)
    elif operator == "contradictory":
        out.setdefault("facts", {}).update({"resident": True, "nonresident": True})
    elif operator == "invalid_date":
        out.setdefault("matter", {})["filing_date"] = "2026-02-30"
    elif operator == "boundary_amount":
        out.setdefault("facts", {})["boundary_amount"] = 999999999.99
    elif operator == "radio_group":
        out.setdefault("facts", {})["residency_status"] = "Unsupported third option"
    out.setdefault("provenance", {})["mutation"] = {"operator": operator, "seed": seed}
    return out
