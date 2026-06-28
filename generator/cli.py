"""Unified ``mmcg`` command line interface."""
from __future__ import annotations

import argparse
import json
import logging
from pathlib import Path

from . import generate_matter, list_scenarios, project_to_canonical
from .ecosystem import (
    SmokeConfig,
    refresh_catalog_lock,
    report_junit,
    report_markdown,
    route_and_plan,
    run_ecosystem_smoke,
    verify_catalog_lock,
)
from .formfill import fill_form, load_form
from .mutations import MUTATIONS, mutate_fixture
from .documents import (
    COMMUNICATION_TYPES,
    DOCUMENT_TYPES,
    generate_communication_pack,
    generate_document_pack,
)


def _json(value) -> str:
    return json.dumps(value, indent=2, ensure_ascii=False)


def _matter(args):
    return generate_matter(args.scenario, args.seed, reference_date=args.reference_date)


def _write_reports(report, out: str | None):
    payload = report.to_dict()
    if not out:
        print(_json(payload))
        return
    directory = Path(out)
    directory.mkdir(parents=True, exist_ok=True)
    (directory / "ecosystem-report.json").write_text(_json(payload) + "\n", encoding="utf-8")
    (directory / "ecosystem-report.md").write_text(report_markdown(report), encoding="utf-8")
    (directory / "ecosystem-report.junit.xml").write_text(report_junit(report), encoding="utf-8")
    print(directory)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="mmcg")
    parser.add_argument("--log-level", default="WARNING")
    sub = parser.add_subparsers(dest="command", required=True)

    generate = sub.add_parser("generate")
    generate.add_argument("scenario", choices=list_scenarios())
    generate.add_argument("--seed", type=int, default=0)
    generate.add_argument("--reference-date")
    generate.add_argument("--canonical", action="store_true")

    mutate = sub.add_parser("mutate")
    mutate.add_argument("scenario", choices=list_scenarios())
    mutate.add_argument("operator", choices=MUTATIONS)
    mutate.add_argument("--seed", type=int, default=0)
    mutate.add_argument("--reference-date")

    route = sub.add_parser("route")
    route.add_argument("scenario", choices=list_scenarios())
    route.add_argument("--seed", type=int, default=0)
    route.add_argument("--reference-date")
    route.add_argument("--catalog-lock")

    test_form = sub.add_parser("test-form")
    test_form.add_argument("form_id")
    test_form.add_argument("--scenario")
    test_form.add_argument("--seed", type=int, default=0)
    test_form.add_argument("--reference-date")

    test_workflow = sub.add_parser("test-workflow")
    test_workflow.add_argument("workflow")
    test_workflow.add_argument("--seed", type=int, action="append", default=[0])
    test_workflow.add_argument("--out")

    smoke = sub.add_parser("ecosystem-smoke")
    smoke.add_argument("--scenario", action="append", default=[])
    smoke.add_argument("--seed", type=int, action="append", default=[0])
    smoke.add_argument("--repository", action="append", default=[])
    smoke.add_argument("--workflow", action="append", default=[])
    smoke.add_argument("--trust-tier", action="append", default=[])
    smoke.add_argument("--catalog-lock")
    smoke.add_argument("--out")

    documents = sub.add_parser("documents")
    documents.add_argument("scenario", choices=list_scenarios())
    documents.add_argument("--seed", type=int, default=0)
    documents.add_argument("--reference-date")
    documents.add_argument("--type", action="append", choices=DOCUMENT_TYPES)
    documents.add_argument("--out", required=True)

    communications = sub.add_parser("communications")
    communications.add_argument("scenario", choices=list_scenarios())
    communications.add_argument("--seed", type=int, default=0)
    communications.add_argument("--reference-date")
    communications.add_argument("--type", action="append", choices=COMMUNICATION_TYPES)
    communications.add_argument("--out", required=True)

    catalog = sub.add_parser("catalog")
    catalog_sub = catalog.add_subparsers(dest="catalog_command", required=True)
    for name in ("verify", "refresh"):
        command = catalog_sub.add_parser(name)
        command.add_argument("--catalog-lock")
    return parser


def main(argv=None) -> int:
    args = build_parser().parse_args(argv)
    logging.basicConfig(level=getattr(logging, args.log_level.upper(), logging.WARNING),
                        format='{"level":"%(levelname)s","message":"%(message)s"}')
    if args.command == "generate":
        matter = _matter(args)
        print(_json(project_to_canonical(matter) if args.canonical else matter))
        return 0
    if args.command == "mutate":
        print(_json(mutate_fixture(_matter(args), args.operator, args.seed)))
        return 0
    if args.command == "route":
        print(_json(route_and_plan(_matter(args), args.catalog_lock)))
        return 0
    if args.command == "test-form":
        form = load_form(args.form_id)
        scenario = args.scenario or form["meta"]["best_scenario"]
        matter = generate_matter(scenario, args.seed, reference_date=args.reference_date)
        print(_json(fill_form(matter, args.form_id)))
        return 0
    if args.command == "documents":
        manifest = generate_document_pack(
            _matter(args), args.out, args.seed, document_types=args.type
        )
        print(_json(manifest))
        return 0
    if args.command == "communications":
        manifest = generate_communication_pack(
            _matter(args), args.out, args.seed, communication_types=args.type
        )
        print(_json(manifest))
        return 0
    if args.command in {"test-workflow", "ecosystem-smoke"}:
        workflows = [args.workflow] if args.command == "test-workflow" else args.workflow
        report = run_ecosystem_smoke(SmokeConfig(
            scenarios=getattr(args, "scenario", []),
            seeds=args.seed,
            repositories=getattr(args, "repository", []),
            workflows=workflows,
            trust_tiers=getattr(args, "trust_tier", []),
            catalog_lock=getattr(args, "catalog_lock", None),
        ))
        _write_reports(report, args.out)
        return 0 if report.ok else 1
    if args.catalog_command == "verify":
        errors = verify_catalog_lock(args.catalog_lock)
        print(_json({"ok": not errors, "errors": errors}))
        return 0 if not errors else 1
    lock = refresh_catalog_lock(args.catalog_lock)
    print(_json(lock))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
