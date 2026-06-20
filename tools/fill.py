#!/usr/bin/env python3
"""Concrete fill: generate a matter and pour it into a real downstream form mapping.

Shows exactly which PDF fields a mock matter populates, with a coverage report. This is
the input the downstream repo's fill engine consumes to render the actual PDF.

Examples:
  python tools/fill.py --list
  python tools/fill.py FM-004 --scenario family-divorce-cumberland --seed 1
  python tools/fill.py IRS-SS-4 --scenario business-formation-scorp --seed 1 --show-empty
  python tools/fill.py FM-004 --scenario family-divorce-cumberland --seed 1 --out out/
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from generator import fill_form, generate_matter, list_forms, load_form  # noqa: E402


def _print_plan(plan: dict, show_empty: bool) -> None:
    cov = plan["coverage"]
    req = plan["required"]
    print(f"\n{plan['form_id']} — {plan.get('title','')}  [{plan.get('repo','')}, profile={plan.get('profile')}]")
    print(f"coverage: {cov['filled_fields']}/{cov['total_fields']} fields filled ({cov['percent']}%)")
    if req["keys"]:
        status = "OK" if req["ok"] else f"MISSING {req['missing']}"
        print(f"required keys: {status}")
    print("-" * 78)
    print(f"{'field id':<46} {'value'}")
    print("-" * 78)
    for e in plan["entries"]:
        if not e["filled"] and not show_empty:
            continue
        val = "" if e["value"] is None else str(e["value"])
        if len(val) > 30:
            val = val[:27] + "..."
        fid = e["field_id"]
        if len(fid) > 44:
            fid = "..." + fid[-41:]
        marker = "  " if e["filled"] else "· "
        print(f"{marker}{fid:<44} {val}")


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("form", nargs="?", help="Form id (omit with --list).")
    ap.add_argument("--list", action="store_true", help="List wired forms and exit.")
    ap.add_argument("--scenario", help="Scenario to generate from (default: the form's best_scenario).")
    ap.add_argument("--seed", type=int, default=1)
    ap.add_argument("--show-empty", action="store_true", help="Also print unfilled fields.")
    ap.add_argument("--out", help="Directory to write the fill plan + form-namespace case JSON.")
    ap.add_argument("--json", action="store_true", help="Print the full fill plan as JSON.")
    args = ap.parse_args()

    if args.list or not args.form:
        print("Wired forms:")
        for fid in list_forms():
            meta = load_form(fid)["meta"]
            print(f"  {fid:<10} {meta['title']}  (best: {meta.get('best_scenario')})")
        return 0

    scenario = args.scenario or load_form(args.form)["meta"].get("best_scenario")
    if not scenario:
        print(f"No scenario given and no best_scenario for {args.form}.", file=sys.stderr)
        return 2

    matter = generate_matter(scenario, args.seed)
    plan = fill_form(matter, args.form)

    if args.json:
        print(json.dumps(plan, indent=2, ensure_ascii=False))
    else:
        _print_plan(plan, args.show_empty)

    if args.out:
        out = Path(args.out)
        out.mkdir(parents=True, exist_ok=True)
        stem = f"{args.form}.{scenario}.{args.seed}"
        (out / f"{stem}.fillplan.json").write_text(
            json.dumps(plan, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
        )
        (out / f"{stem}.case.json").write_text(
            json.dumps(plan["case"], indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
        )
        print(f"\nwrote {out}/{stem}.fillplan.json and .case.json")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
