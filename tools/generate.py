#!/usr/bin/env python3
"""Generate one or more Mock Matters from a scenario archetype.

Examples:
  python tools/generate.py --list
  python tools/generate.py family-divorce-cumberland --seed 1
  python tools/generate.py family-divorce-cumberland --seed 1 --canonical
  python tools/generate.py decedent-estate-informal --count 5 --out out/
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
    validate_matter,
)


def _dump(obj: dict) -> str:
    return json.dumps(obj, indent=2, ensure_ascii=False)


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("scenario", nargs="?", help="Scenario id (omit with --list).")
    ap.add_argument("--seed", type=int, default=0, help="Starting seed (default 0).")
    ap.add_argument("--count", type=int, default=1, help="Number of matters, seeds seed..seed+count-1.")
    ap.add_argument("--out", help="Output file (count==1) or directory (count>1). Default: stdout.")
    ap.add_argument("--canonical", action="store_true", help="Emit the projected canonical case instead of the full matter.")
    ap.add_argument("--reference-date", help="Deterministic ISO reference date (default: 2026-01-01).")
    ap.add_argument("--no-validate", action="store_true", help="Skip schema validation.")
    ap.add_argument("--list", action="store_true", help="List available scenarios and exit.")
    args = ap.parse_args()

    if args.list or not args.scenario:
        print("Available scenarios:")
        for sid in list_scenarios():
            print(f"  {sid}")
        return 0

    out_dir = None
    if args.out and args.count > 1:
        out_dir = Path(args.out)
        out_dir.mkdir(parents=True, exist_ok=True)

    for i in range(args.count):
        seed = args.seed + i
        matter = generate_matter(args.scenario, seed, reference_date=args.reference_date)
        if not args.no_validate:
            errors = validate_matter(matter)
            if errors:
                print(f"VALIDATION FAILED ({args.scenario} seed={seed}):", file=sys.stderr)
                for err in errors:
                    print(f"  - {err}", file=sys.stderr)
                return 1
        payload = project_to_canonical(matter) if args.canonical else matter
        text = _dump(payload)

        if out_dir is not None:
            suffix = "canonical" if args.canonical else "matter"
            path = out_dir / f"{args.scenario}.{seed}.{suffix}.json"
            path.write_text(text + "\n", encoding="utf-8")
            print(f"wrote {path}")
        elif args.out:
            Path(args.out).write_text(text + "\n", encoding="utf-8")
            print(f"wrote {args.out}")
        else:
            print(text)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
