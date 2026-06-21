"""Discover and load scenario archetypes from scenarios/<id>/scenario.yaml."""
from __future__ import annotations

from functools import lru_cache

import yaml

from .errors import ScenarioFormatError, UnknownScenarioError
from .paths import SCENARIOS_DIR


def list_scenarios() -> list[str]:
    """Return sorted scenario ids (folders containing a scenario.yaml)."""
    if not SCENARIOS_DIR.exists():
        return []
    ids = [
        path.name
        for path in SCENARIOS_DIR.iterdir()
        if path.is_dir() and (path / "scenario.yaml").exists()
    ]
    return sorted(ids)


@lru_cache(maxsize=None)
def load_scenario(scenario_id: str) -> dict:
    path = SCENARIOS_DIR / scenario_id / "scenario.yaml"
    if not path.exists():
        raise UnknownScenarioError(
            f"Unknown scenario '{scenario_id}'. Available: {', '.join(list_scenarios()) or '(none)'}"
        )
    try:
        with open(path, encoding="utf-8") as fh:
            scenario = yaml.safe_load(fh)
    except yaml.YAMLError as exc:
        raise ScenarioFormatError(f"Invalid YAML in {path}: {exc}") from exc
    if not isinstance(scenario, dict):
        raise ScenarioFormatError(f"Scenario {scenario_id} must be a YAML object")
    scenario.setdefault("id", scenario_id)
    return scenario


def scenario_metadata(scenario_id: str) -> dict:
    scenario = load_scenario(scenario_id)
    facts = sorted((scenario.get("facts") or {}).keys())
    roles = sorted(role["key"] for role in scenario.get("parties", {}).get("roles", []))
    tags = sorted(set(scenario.get("tags", [])) | {scenario.get("practice_area", "other")})
    return {
        "id": scenario_id,
        "practice_area": scenario.get("practice_area", "other"),
        "case_type": scenario.get("case_type", ""),
        "tags": tags,
        "capabilities": {"roles": roles, "fact_keys": facts},
    }
