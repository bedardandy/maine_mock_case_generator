#!/usr/bin/env python3
"""End-to-end smoke test for the mock case pipeline.

For every scenario (or a chosen subset) and a range of seeds, this:
  1. generates a Mock Matter,
  2. validates it against catalog/mock_matter.schema.json,
  3. checks no template placeholders leaked into the output,
  4. projects it to the downstream canonical case object, and
  5. validates that against catalog/canonical_case.schema.json.

Exits non-zero if anything fails, so it can gate CI.

Examples:
  python tools/smoke.py
  python tools/smoke.py --count 10
  python tools/smoke.py --scenarios family-divorce-cumberland,decedent-estate-informal -v
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from generator import (  # noqa: E402
    fill_form,
    generate_compound,
    generate_matter,
    list_compounds,
    list_forms,
    list_scenarios,
    load_form,
    project_to_canonical,
    validate_canonical,
    validate_compound,
    validate_matter,
)

# Matches a leftover template placeholder like {plaintiff_full_name} inside a
# string, without matching structural JSON braces (which are followed by newline/quote).
_PLACEHOLDER = re.compile(r"\{[a-z][a-z0-9_]*\}")


def _placeholder_leaks(matter: dict) -> list[str]:
    text = json.dumps(matter, ensure_ascii=False)
    return sorted(set(_PLACEHOLDER.findall(text)))


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--scenarios", help="Comma-separated scenario ids (default: all).")
    ap.add_argument("--count", type=int, default=3, help="Seeds per scenario (default 3).")
    ap.add_argument("--seed-base", type=int, default=0, help="First seed (default 0).")
    ap.add_argument("-v", "--verbose", action="store_true", help="Print each failure in detail.")
    args = ap.parse_args()

    scenarios = args.scenarios.split(",") if args.scenarios else list_scenarios()
    if not scenarios:
        print("No scenarios found.", file=sys.stderr)
        return 1

    total_runs = 0
    total_fail = 0
    rows = []

    for sid in scenarios:
        runs = matter_ok = canon_ok = clean = 0
        failures: list[str] = []
        for i in range(args.count):
            seed = args.seed_base + i
            runs += 1
            total_runs += 1
            try:
                matter = generate_matter(sid, seed)
            except Exception as exc:  # generation blew up
                failures.append(f"seed {seed}: generation error: {exc}")
                continue

            m_errors = validate_matter(matter)
            if not m_errors:
                matter_ok += 1
            else:
                failures.append(f"seed {seed}: matter invalid: {m_errors[0]}")

            leaks = _placeholder_leaks(matter)
            if not leaks:
                clean += 1
            else:
                failures.append(f"seed {seed}: unresolved placeholders: {leaks}")

            case = project_to_canonical(matter)
            c_errors = validate_canonical(case)
            if not c_errors:
                canon_ok += 1
            else:
                failures.append(f"seed {seed}: canonical invalid: {c_errors[0]}")

        ok = (matter_ok == runs) and (canon_ok == runs) and (clean == runs)
        total_fail += len(failures)
        rows.append((sid, runs, matter_ok, clean, canon_ok, ok))
        if args.verbose and failures:
            print(f"\n{sid} failures:")
            for f in failures:
                print(f"  - {f}")

    # Summary table
    print()
    print(f"{'scenario':<32} {'runs':>4} {'matter':>7} {'clean':>6} {'canon':>6}  status")
    print("-" * 72)
    for sid, runs, matter_ok, clean, canon_ok, ok in rows:
        status = "PASS" if ok else "FAIL"
        print(f"{sid:<32} {runs:>4} {matter_ok:>7} {clean:>6} {canon_ok:>6}  {status}")
    print("-" * 72)
    print(f"{len(rows)} scenarios, {total_runs} runs, {total_fail} failure(s).")

    # Concrete fills: pour a matter into each wired downstream form mapping.
    fill_fail = 0
    forms = list_forms()
    if forms:
        print()
        print(f"{'form':<10} {'repo':<26} {'profile':<10} {'coverage':>10}  required")
        print("-" * 72)
        for fid in forms:
            meta = load_form(fid)["meta"]
            scenario = meta.get("best_scenario")
            try:
                plan = fill_form(generate_matter(scenario, args.seed_base), fid)
            except Exception as exc:
                fill_fail += 1
                print(f"{fid:<10} ERROR: {exc}")
                continue
            cov = plan["coverage"]
            req = "OK" if plan["required"]["ok"] else f"MISSING {plan['required']['missing']}"
            if not plan["required"]["ok"]:
                fill_fail += 1
            print(f"{fid:<10} {meta['repo']:<26} {meta['profile']:<10} "
                  f"{cov['filled_fields']:>3}/{cov['total_fields']:<3} ({cov['percent']:>4}%)  {req}")
        print("-" * 72)
        print(f"{len(forms)} wired form(s), {fill_fail} fill failure(s).")

    # Compound (intertwined) matter universes.
    compound_fail = 0
    compounds = list_compounds()
    if compounds:
        print()
        print(f"{'compound':<30} {'matters':>7} {'cast':>5} {'links':>6}  status")
        print("-" * 72)
        for cid in compounds:
            ok = True
            matters = cast = links = 0
            for i in range(min(args.count, 3)):
                try:
                    compound = generate_compound(cid, args.seed_base + i)
                except Exception as exc:
                    ok = False
                    print(f"{cid:<30} ERROR: {exc}")
                    break
                if validate_compound(compound):
                    ok = False
                matters = len(compound["matters"])
                cast = len(compound["cast"])
                links = len(compound["relationships"])
            if not ok:
                compound_fail += 1
            print(f"{cid:<30} {matters:>7} {cast:>5} {links:>6}  {'PASS' if ok else 'FAIL'}")
        print("-" * 72)
        print(f"{len(compounds)} compound universe(s), {compound_fail} failure(s).")

    return 0 if (total_fail == 0 and fill_fail == 0 and compound_fail == 0) else 1


if __name__ == "__main__":
    raise SystemExit(main())
