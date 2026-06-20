"""Discover and load scenario archetypes from scenarios/<id>/scenario.yaml."""
from __future__ import annotations

from functools import lru_cache

import yaml

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
        raise FileNotFoundError(
            f"Unknown scenario '{scenario_id}'. Available: {', '.join(list_scenarios()) or '(none)'}"
        )
    with open(path, encoding="utf-8") as fh:
        scenario = yaml.safe_load(fh)
    scenario.setdefault("id", scenario_id)
    return scenario
