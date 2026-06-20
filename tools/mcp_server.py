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


if __name__ == "__main__":
    mcp.run()
