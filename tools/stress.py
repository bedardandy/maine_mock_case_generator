#!/usr/bin/env python3
"""Emit stressed-but-valid variants of generated matters for smoke testing.

Every variant stays schema-valid; what changes is how hostile the *content* is to a
downstream consumer (missing optionals, empty strings, oversized text, unicode).

Examples:
  python tools/stress.py --list-mutators
  python tools/stress.py family-divorce-cumberland --seed 1                  # all mutators, stdout
  python tools/stress.py family-divorce-cumberland --mutators unicode_stress --canonical
  python tools/stress.py --all-scenarios --seeds 3 --jsonl out/stress.jsonl  # bulk corpus
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from generator import (  # noqa: E402
    generate_matter,
    list_scenarios,
    project_to_canonical,
    validate_canonical,
    validate_matter,
)
from generator.stress import MUTATORS, stress_variants  # noqa: E402


def _records(scenario: str, seed: int, mutators: list[str], canonical: bool):
    matter = generate_matter(scenario, seed)
    for name, variant in stress_variants(matter, seed, mutators):
        errors = validate_matter(variant)
        if errors:
            raise SystemExit(f"BUG: mutator {name} broke schema validity: {errors}")
        record = {"scenario": scenario, "seed": seed, "mutator": name, "matter": variant}
        if canonical:
            case = project_to_canonical(variant)
            cerrs = validate_canonical(case)
            if cerrs:
                raise SystemExit(f"BUG: mutator {name} broke canonical projection: {cerrs}")
            record["canonical"] = case
        yield record


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("scenario", nargs="?", help="Scenario id (or use --all-scenarios).")
    ap.add_argument("--all-scenarios", action="store_true", help="Sweep every scenario.")
    ap.add_argument("--seed", type=int, default=0, help="Base seed (default 0).")
    ap.add_argument("--seeds", type=int, default=1, help="Number of seeds per scenario (seed..seed+n-1).")
    ap.add_argument("--mutators", help="Comma-separated mutators (default: all).")
    ap.add_argument("--canonical", action="store_true", help="Include the projected canonical case in each record.")
    ap.add_argument("--jsonl", help="Write records as JSON Lines to this file (default: pretty-print to stdout).")
    ap.add_argument("--list-mutators", action="store_true", help="List mutators and exit.")
    args = ap.parse_args()

    if args.list_mutators:
        for name, fn in MUTATORS.items():
            print(f"  {name:18s} {fn.__doc__.strip().splitlines()[0]}")
        return 0

    scenarios = list_scenarios() if args.all_scenarios else ([args.scenario] if args.scenario else [])
    if not scenarios:
        ap.error("provide a scenario id, --all-scenarios, or --list-mutators")
    mutators = args.mutators.split(",") if args.mutators else list(MUTATORS)

    out_fh = None
    if args.jsonl:
        path = Path(args.jsonl)
        path.parent.mkdir(parents=True, exist_ok=True)
        out_fh = path.open("w", encoding="utf-8")

    n = 0
    for scenario in scenarios:
        for seed in range(args.seed, args.seed + args.seeds):
            for record in _records(scenario, seed, mutators, args.canonical):
                n += 1
                if out_fh:
                    out_fh.write(json.dumps(record, ensure_ascii=False) + "\n")
                else:
                    print(json.dumps(record, indent=2, ensure_ascii=False))
    if out_fh:
        out_fh.close()
        print(f"wrote {n} stressed variant(s) to {args.jsonl}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
