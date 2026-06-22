#!/usr/bin/env python3
"""Optional MCP adapter: expose the mock case generator as Model Context Protocol tools.

Requires the optional dependency:  pip install "mcp[cli]>=1.2"
Registered in .mcp.json. Mirrors the MCP adapters in the sibling form-filling repos.

Tools exposed:
  list_scenarios()                      -> available scenario ids
  generate_matter(scenario, seed)       -> a full Mock Matter (dict)
  project_canonical(scenario, seed)     -> the projected downstream canonical case
  validate_matter(matter)               -> list of validation errors (empty == valid)
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

try:
    from mcp.server.fastmcp import FastMCP
except ImportError:  # pragma: no cover - optional dependency
    sys.stderr.write(
        "The 'mcp' package is required for the MCP server.\n"
        'Install it with:  pip install "mcp[cli]>=1.2"\n'
    )
    raise SystemExit(1)

from generator import (  # noqa: E402
    generate_matter as _generate,
    list_scenarios as _list,
    project_to_canonical as _project,
    validate_matter as _validate,
)
from generator.ecosystem import SmokeConfig, load_catalog_lock, route_and_plan, run_ecosystem_smoke
from generator.formfill import fill_form, load_form
from generator.documents import (
    COMMUNICATION_TYPES, DOCUMENT_TYPES, generate_communication_pack, generate_document_pack
)

mcp = FastMCP("mock-case-generator")


@mcp.tool()
def list_scenarios() -> list[str]:
    """Return the available scenario archetype ids."""
    return _list()


@mcp.tool()
def generate_matter(scenario: str, seed: int = 0) -> dict:
    """Generate a fictional Mock Matter from a scenario archetype and seed."""
    return _generate(scenario, seed)


@mcp.tool()
def project_canonical(scenario: str, seed: int = 0) -> dict:
    """Generate a matter and project it to the downstream canonical case object."""
    return _project(_generate(scenario, seed))


@mcp.tool()
def validate_matter(matter: dict) -> list[str]:
    """Validate a Mock Matter against the schema; returns errors (empty == valid)."""
    return _validate(matter)


@mcp.tool()
def list_workflows() -> dict:
    """Return pinned cross-repository workflow fixtures."""
    return load_catalog_lock().get("workflows", {})


@mcp.tool()
def generate_for_form(form_id: str, seed: int = 0) -> dict:
    """Generate the best fixture and deterministic fill plan for a form."""
    form = load_form(form_id)
    matter = _generate(form["meta"]["best_scenario"], seed)
    return {"matter": matter, "fill_plan": fill_form(matter, form_id)}


@mcp.tool()
def generate_for_workflow(workflow: str, seed: int = 0) -> dict:
    """Generate fixtures for every locally wired form in a workflow."""
    workflows = load_catalog_lock().get("workflows", {})
    if workflow not in workflows:
        return {"ok": False, "error": f"Unknown workflow: {workflow}"}
    results = []
    for form_id in workflows[workflow]["forms"]:
        try:
            results.append(generate_for_form(form_id, seed))
        except KeyError:
            results.append({"form_id": form_id, "status": "external-only"})
    return {"ok": True, "workflow": workflow, "results": results}


@mcp.tool()
def plan_ecosystem_fill(scenario: str, seed: int = 0) -> dict:
    """Generate a fixture and return deterministic cross-repository routing suggestions."""
    matter = _generate(scenario, seed)
    return {"matter": matter, "plan": route_and_plan(matter)}


@mcp.tool()
def run_smoke_test(scenario: str = "", seed: int = 0) -> dict:
    """Run a read-only ecosystem contract smoke test."""
    config = SmokeConfig(scenarios=[scenario] if scenario else [], seeds=[seed])
    return run_ecosystem_smoke(config).to_dict()


@mcp.tool()
def generate_client_documents(
    scenario: str, out_dir: str, seed: int = 0, document_types: list[str] | None = None
) -> dict:
    """Generate clearly fictional pristine and raster-only client-document fixtures."""
    invalid = sorted(set(document_types or []) - set(DOCUMENT_TYPES))
    if invalid:
        return {"ok": False, "error": f"Unknown document types: {', '.join(invalid)}"}
    matter = _generate(scenario, seed)
    return {"ok": True, **generate_document_pack(matter, out_dir, seed, document_types)}


@mcp.tool()
def generate_client_communications(
    scenario: str, out_dir: str, seed: int = 0, communication_types: list[str] | None = None
) -> dict:
    """Generate synthetic text screenshots and standards-compliant email fixtures."""
    invalid = sorted(set(communication_types or []) - set(COMMUNICATION_TYPES))
    if invalid:
        return {"ok": False, "error": f"Unknown communication types: {', '.join(invalid)}"}
    matter = _generate(scenario, seed)
    return {"ok": True, **generate_communication_pack(matter, out_dir, seed, communication_types)}


if __name__ == "__main__":
    mcp.run()
