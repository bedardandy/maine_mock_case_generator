"""Mock legal-matter generator for smoke-testing an end-to-end legal pipeline.

All output is FICTIONAL mock data. See DISCLAIMER.md.
"""
from __future__ import annotations

from .engine import GENERATOR_VERSION, generate_matter
from .formfill import fill_form, list_forms, load_form
from .project import project_to_canonical
from .scenarios import list_scenarios, load_scenario
from .schema import validate_canonical, validate_matter

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
    "GENERATOR_VERSION",
]
