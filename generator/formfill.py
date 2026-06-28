"""Concrete fill: resolve a (projected) case against a downstream form's real mapping.

This is the seam that proves the pipeline end to end. A downstream form's ``mapping.json``
maps each PDF field id to a fact-key (e.g. ``parties.plaintiff.full_name`` for FM-004,
``entity.legal_name`` for IRS-SS-4). :func:`fill_form` resolves every mapped field from a
generated matter and reports coverage, so you can see exactly which form fields a mock
matter would populate -- the input the downstream fill engine consumes to render a PDF.
"""
from __future__ import annotations

import json
from functools import lru_cache

import yaml

from . import adapters
from .paths import REPO_ROOT
from .project import project_to_canonical

INTEGRATION_DIR = REPO_ROOT / "integration"
REGISTRY_PATH = INTEGRATION_DIR / "registry.json"


@lru_cache(maxsize=1)
def registry() -> dict:
    with open(REGISTRY_PATH, encoding="utf-8") as fh:
        return json.load(fh)["forms"]


def list_forms() -> list[str]:
    return sorted(registry())


@lru_cache(maxsize=None)
def load_form(form_id: str) -> dict:
    forms = registry()
    if form_id not in forms:
        raise KeyError(f"Unknown form '{form_id}'. Available: {', '.join(list_forms())}")
    meta = forms[form_id]
    form_dir = REPO_ROOT / meta["dir"]
    with open(form_dir / "mapping.json", encoding="utf-8") as fh:
        mapping = json.load(fh)
    form_meta = {}
    yaml_path = form_dir / "form.yaml"
    if yaml_path.exists():
        with open(yaml_path, encoding="utf-8") as fh:
            form_meta = yaml.safe_load(fh) or {}
    return {"meta": meta, "mapping": mapping, "form_meta": form_meta}


def resolve_dotted(case: dict, key: str, today: str):
    """Resolve a dotted fact-key (e.g. parties.plaintiff.full_name) against a case dict."""
    if key in ("today()", "today"):
        return today
    node = case
    for part in key.split("."):
        if isinstance(node, dict) and part in node:
            node = node[part]
        else:
            return None
    if isinstance(node, (str, int, float, bool)):
        return node
    return None


def build_fill_plan(case: dict, mapping: dict, today: str | None = None) -> dict:
    """Resolve every mapped field; return per-field entries and a coverage summary."""
    today = today or case.get("matter", {}).get("filing_date")
    if not today:
        raise ValueError("A deterministic today value or matter.filing_date is required")
    field_map = mapping.get("map", {})
    entries = []
    for field_id, fact_key in field_map.items():
        if not isinstance(fact_key, str):
            continue
        value = resolve_dotted(case, fact_key, today)
        filled = value not in (None, "", [])
        entries.append({
            "field_id": field_id,
            "fact_key": fact_key,
            "value": value,
            "filled": filled,
        })

    total = len(entries)
    filled = sum(1 for e in entries if e["filled"])

    # Required keys (declared in the mapping's facts.required), if any.
    facts_meta = mapping.get("facts")
    required = facts_meta.get("required", []) if isinstance(facts_meta, dict) else []
    required_missing = [k for k in required if resolve_dotted(case, k, today) in (None, "", [])]

    return {
        "form_id": mapping.get("form_id"),
        "coverage": {
            "total_fields": total,
            "filled_fields": filled,
            "empty_fields": total - filled,
            "percent": round(100 * filled / total, 1) if total else 0.0,
        },
        "required": {
            "keys": required,
            "missing": required_missing,
            "ok": not required_missing,
        },
        "entries": entries,
    }


def to_form_namespace(form_id: str, matter: dict, canonical: dict | None = None) -> dict:
    """Project the matter and adapt it into the namespace the given form expects."""
    canonical = canonical or project_to_canonical(matter)
    profile = load_form(form_id)["meta"].get("profile", "canonical")
    adapter = adapters.PROFILES.get(profile)
    if adapter is None:
        return canonical
    return adapter(canonical, matter)


def fill_form(matter: dict, form_id: str, today: str | None = None) -> dict:
    """End-to-end: matter -> canonical -> (namespace adapter) -> fill plan for a form."""
    form = load_form(form_id)
    case = to_form_namespace(form_id, matter)
    deterministic_today = today or matter.get("provenance", {}).get("reference_date")
    plan = build_fill_plan(case, form["mapping"], today=deterministic_today)
    plan["title"] = form["meta"].get("title")
    plan["repo"] = form["meta"].get("repo")
    plan["profile"] = form["meta"].get("profile")
    plan["case"] = case
    return plan
