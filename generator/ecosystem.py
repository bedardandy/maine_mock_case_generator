"""Catalog locking, routing plans, and read-only ecosystem smoke orchestration."""
from __future__ import annotations

import hashlib
import json
import subprocess
import time
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from .contracts import EcosystemReport
from .engine import generate_matter
from .formfill import fill_form, list_forms, load_form
from .paths import REPO_ROOT

DEFAULT_LOCK = REPO_ROOT / "catalog" / "ecosystem.lock.json"


def load_catalog_lock(path: str | Path | None = None) -> dict[str, Any]:
    target = Path(path) if path else DEFAULT_LOCK
    return json.loads(target.read_text(encoding="utf-8"))


def verify_catalog_lock(path: str | Path | None = None) -> list[str]:
    lock = load_catalog_lock(path)
    errors: list[str] = []
    repos = lock.get("repositories", {})
    seen_forms: dict[str, str] = {}
    for name, spec in repos.items():
        for key in ("url", "ref", "integration_manifest"):
            if not spec.get(key):
                errors.append(f"{name}: missing {key}")
        for form_id in spec.get("fixture_forms", []):
            if form_id in seen_forms:
                errors.append(f"duplicate form id {form_id}: {seen_forms[form_id]} and {name}")
            seen_forms[form_id] = name
    for workflow_id, workflow in lock.get("workflows", {}).items():
        for member in workflow.get("forms", []):
            if member not in seen_forms:
                errors.append(f"{workflow_id}: unknown form {member}")
    return errors


def refresh_catalog_lock(path: str | Path | None = None) -> dict[str, Any]:
    """Refresh commit refs with git ls-remote; does not clone or modify sibling repos."""
    target = Path(path) if path else DEFAULT_LOCK
    lock = load_catalog_lock(target)
    for spec in lock.get("repositories", {}).values():
        ref = spec.get("ref", "main")
        proc = subprocess.run(
            ["git", "ls-remote", spec["url"], f"refs/heads/{ref}"],
            capture_output=True, text=True, check=False, timeout=30,
        )
        if proc.returncode == 0 and proc.stdout.strip():
            spec["commit"] = proc.stdout.split()[0]
    lock["refreshed_at"] = datetime.now(timezone.utc).isoformat()
    target.write_text(json.dumps(lock, indent=2) + "\n", encoding="utf-8")
    return lock


def route_and_plan(matter: dict, catalog_lock: str | Path | None = None) -> dict[str, Any]:
    lock = load_catalog_lock(catalog_lock)
    scenario = matter.get("provenance", {}).get("scenario_id", "")
    practice = matter.get("matter", {}).get("practice_area", "")
    candidates = []
    for form_id in list_forms():
        meta = load_form(form_id)["meta"]
        score = 0
        reasons = []
        if meta.get("best_scenario") == scenario:
            score += 100
            reasons.append("scenario match")
        if practice in meta.get("practice_areas", []):
            score += 20
            reasons.append("practice-area match")
        if score:
            candidates.append({"form_id": form_id, "repo": meta["repo"], "score": score, "why": reasons})
    candidates.sort(key=lambda item: (-item["score"], item["repo"], item["form_id"]))
    workflows = []
    candidate_ids = {item["form_id"] for item in candidates}
    for workflow_id, workflow in lock.get("workflows", {}).items():
        overlap = candidate_ids.intersection(workflow.get("forms", []))
        if overlap:
            workflows.append({"workflow_id": workflow_id, "forms": workflow["forms"], "matched": sorted(overlap)})
    return {"scenario_id": scenario, "practice_area": practice, "forms": candidates, "workflows": workflows}


@dataclass
class SmokeConfig:
    scenarios: list[str] = field(default_factory=list)
    seeds: list[int] = field(default_factory=lambda: [0])
    repositories: list[str] = field(default_factory=list)
    workflows: list[str] = field(default_factory=list)
    trust_tiers: list[str] = field(default_factory=list)
    catalog_lock: str | Path | None = None


def run_ecosystem_smoke(config: SmokeConfig) -> EcosystemReport:
    started = time.perf_counter()
    report = EcosystemReport(started_at=datetime.now(timezone.utc).isoformat())
    lock = load_catalog_lock(config.catalog_lock)
    report.source_shas = {
        name: spec.get("commit", "") for name, spec in lock.get("repositories", {}).items()
    }
    lock_errors = verify_catalog_lock(config.catalog_lock)
    report.errors.extend({"code": "CATALOG_LOCK", "message": item} for item in lock_errors)
    scenarios = config.scenarios or sorted(
        {load_form(fid)["meta"]["best_scenario"] for fid in list_forms()}
    )
    for scenario in scenarios:
        for seed in config.seeds:
            matter = generate_matter(scenario, seed)
            plan = route_and_plan(matter, config.catalog_lock)
            allowed_forms = {
                form for workflow in plan["workflows"]
                if not config.workflows or workflow["workflow_id"] in config.workflows
                for form in workflow["forms"]
            }
            for candidate in plan["forms"]:
                if config.repositories and candidate["repo"] not in config.repositories:
                    continue
                if config.workflows and candidate["form_id"] not in allowed_forms:
                    continue
                form = load_form(candidate["form_id"])
                trust = form["mapping"].get("status", form["meta"].get("trust_tier", "fixture"))
                if config.trust_tiers and trust not in config.trust_tiers:
                    continue
                before = time.perf_counter()
                try:
                    fill = fill_form(matter, candidate["form_id"])
                    ok = fill["required"]["ok"]
                    run = {
                        "scenario": scenario, "seed": seed, "repo": candidate["repo"],
                        "form_id": candidate["form_id"], "trust_tier": trust, "ok": ok,
                        "coverage": fill["coverage"], "missing": fill["required"]["missing"],
                        "warnings": [], "duration_ms": round((time.perf_counter() - before) * 1000),
                        "artifact_paths": [],
                    }
                except Exception as exc:
                    run = {
                        "scenario": scenario, "seed": seed, "repo": candidate["repo"],
                        "form_id": candidate["form_id"], "trust_tier": trust, "ok": False,
                        "coverage": {}, "missing": [], "warnings": [],
                        "error": str(exc), "duration_ms": round((time.perf_counter() - before) * 1000),
                        "artifact_paths": [],
                    }
                report.runs.append(run)
    report.ok = not report.errors and all(run["ok"] for run in report.runs)
    report.duration_ms = round((time.perf_counter() - started) * 1000)
    return report


def report_markdown(report: EcosystemReport) -> str:
    lines = ["# Ecosystem smoke report", "", f"Status: **{'PASS' if report.ok else 'FAIL'}**", ""]
    lines += ["| Repository | Form | Scenario | Seed | Coverage | Status |", "|---|---|---|---:|---:|---|"]
    for run in report.runs:
        cov = run.get("coverage", {})
        coverage = f"{cov.get('filled_fields', 0)}/{cov.get('total_fields', 0)}"
        lines.append(
            f"| {run['repo']} | {run['form_id']} | {run['scenario']} | {run['seed']} | "
            f"{coverage} | {'PASS' if run['ok'] else 'FAIL'} |"
        )
    return "\n".join(lines) + "\n"


def report_junit(report: EcosystemReport) -> str:
    from xml.etree.ElementTree import Element, SubElement, tostring
    suite = Element("testsuite", name="mmcg-ecosystem", tests=str(len(report.runs)),
                    failures=str(sum(not run["ok"] for run in report.runs)))
    for run in report.runs:
        case = SubElement(suite, "testcase", classname=run["repo"],
                          name=f"{run['form_id']}[{run['scenario']}:{run['seed']}]",
                          time=str(run["duration_ms"] / 1000))
        if not run["ok"]:
            failure = SubElement(case, "failure", message=run.get("error", "required facts missing"))
            failure.text = json.dumps(run.get("missing", []))
    return tostring(suite, encoding="unicode") + "\n"
