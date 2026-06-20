"""Load schemas and validate matters / projected canonical cases."""
from __future__ import annotations

import json
from functools import lru_cache

from jsonschema import Draft202012Validator

from .paths import CANONICAL_CASE_SCHEMA, COMPOUND_MATTER_SCHEMA, MOCK_MATTER_SCHEMA


@lru_cache(maxsize=None)
def _load(path) -> dict:
    with open(path, encoding="utf-8") as fh:
        return json.load(fh)


def mock_matter_schema() -> dict:
    return _load(MOCK_MATTER_SCHEMA)


def canonical_case_schema() -> dict:
    return _load(CANONICAL_CASE_SCHEMA)


def compound_matter_schema() -> dict:
    return _load(COMPOUND_MATTER_SCHEMA)


def _errors(instance, schema) -> list[str]:
    validator = Draft202012Validator(schema)
    messages = []
    for error in sorted(validator.iter_errors(instance), key=lambda e: list(e.path)):
        location = "/".join(str(p) for p in error.path) or "<root>"
        messages.append(f"{location}: {error.message}")
    return messages


def validate_matter(matter: dict) -> list[str]:
    """Return a list of human-readable validation errors (empty == valid)."""
    return _errors(matter, mock_matter_schema())


def validate_canonical(case: dict) -> list[str]:
    return _errors(case, canonical_case_schema())


def validate_compound(compound: dict) -> list[str]:
    """Validate the compound envelope, then each constituent matter."""
    errors = _errors(compound, compound_matter_schema())
    for i, matter in enumerate(compound.get("matters", [])):
        errors.extend(f"matters[{i}].{e}" for e in validate_matter(matter))
    return errors
