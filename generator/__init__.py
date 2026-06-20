"""Mock legal-matter generator for smoke-testing an end-to-end legal pipeline.

All output is FICTIONAL mock data. See DISCLAIMER.md.
"""
from __future__ import annotations

from .compound import (
    generate_compound,
    list_compounds,
    load_compound,
    project_compound,
)
from .engine import GENERATOR_VERSION, generate_matter
from .formfill import fill_form, list_forms, load_form
from .project import project_to_canonical
from .scenarios import list_scenarios, load_scenario
from .schema import validate_canonical, validate_compound, validate_matter

__all__ = [
    "generate_matter",
    "project_to_canonical",
    "list_scenarios",
    "load_scenario",
    "validate_matter",
    "validate_canonical",
    "fill_form",
    "list_forms",
    "load_form",
    "generate_compound",
    "project_compound",
    "list_compounds",
    "load_compound",
    "validate_compound",
    "GENERATOR_VERSION",
]
