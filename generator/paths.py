"""Shared filesystem paths for the mock case generator."""
from __future__ import annotations

from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
CATALOG_DIR = REPO_ROOT / "catalog"
SCENARIOS_DIR = REPO_ROOT / "scenarios"
COMPOUND_DIR = REPO_ROOT / "compound"
EXAMPLES_DIR = REPO_ROOT / "examples"

MOCK_MATTER_SCHEMA = CATALOG_DIR / "mock_matter.schema.json"
CANONICAL_CASE_SCHEMA = CATALOG_DIR / "canonical_case.schema.json"
COMPOUND_MATTER_SCHEMA = CATALOG_DIR / "compound_matter.schema.json"
FAKER_POOLS = CATALOG_DIR / "faker_pools.json"
PRACTICE_AREAS = CATALOG_DIR / "practice_areas.json"
