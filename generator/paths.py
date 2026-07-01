"""Shared filesystem paths for the mock case generator.

The generator is data-driven: ``catalog/``, ``scenarios/``, ``compound/``, and
``integration/`` live beside the package in the repo checkout. Install with
``pip install -e .`` (or run from a clone) so these resolve; a consuming repo can
also point ``MOCK_CASE_GENERATOR_ROOT`` at a checkout explicitly.
"""
from __future__ import annotations

import os
from pathlib import Path

_env_root = os.environ.get("MOCK_CASE_GENERATOR_ROOT")
REPO_ROOT = Path(_env_root).resolve() if _env_root else Path(__file__).resolve().parents[1]
CATALOG_DIR = REPO_ROOT / "catalog"
SCENARIOS_DIR = REPO_ROOT / "scenarios"
COMPOUND_DIR = REPO_ROOT / "compound"
EXAMPLES_DIR = REPO_ROOT / "examples"

MOCK_MATTER_SCHEMA = CATALOG_DIR / "mock_matter.schema.json"
CANONICAL_CASE_SCHEMA = CATALOG_DIR / "canonical_case.schema.json"
COMPOUND_MATTER_SCHEMA = CATALOG_DIR / "compound_matter.schema.json"
FAKER_POOLS = CATALOG_DIR / "faker_pools.json"
PRACTICE_AREAS = CATALOG_DIR / "practice_areas.json"
