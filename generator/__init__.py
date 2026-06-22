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
from .ecosystem import SmokeConfig, route_and_plan, run_ecosystem_smoke
from .mutations import MUTATIONS, mutate_fixture
from .documents import DOCUMENT_TYPES, generate_document, generate_document_pack, pdf_embedded_text
from .formfill import fill_form, list_forms, load_form
from .project import project_to_canonical
from .scenarios import list_scenarios, load_scenario, scenario_metadata
from .schema import validate_canonical, validate_compound, validate_matter
from .schema_fill import (
    generate_case,
    generate_for_form,
    list_probate_forms,
    load_form_fields,
)

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
    "generate_case",
    "generate_for_form",
    "list_probate_forms",
    "load_form_fields",
    "GENERATOR_VERSION",
    "route_and_plan",
    "run_ecosystem_smoke",
    "SmokeConfig",
    "mutate_fixture",
    "MUTATIONS",
    "scenario_metadata",
    "DOCUMENT_TYPES",
    "generate_document",
    "generate_document_pack",
    "pdf_embedded_text",
]
