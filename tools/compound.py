#!/usr/bin/env python3
"""Generate a compound (intertwined) matter universe: linked matters sharing one cast.

Examples:
  python tools/compound.py --list
  python tools/compound.py death-cascade --seed 1
  python tools/compound.py business-dispute-cascade --seed 1 --summary
  python tools/compound.py marital-breakdown-cascade --seed 1 --canonical --out out/
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from generator import (  # noqa: E402
    generate_compound,
    list_compounds,
    project_compound,
    validate_compound,
)


def _summary(compound: dict) -> None:
    print(f"\n{compound['universe_id']} — {compound['title']}")
    print(f"theme: {compound['theme']}")
    print(f"\ncast ({len(compound['cast'])}):")
    for c in compound["cast"]:
        roles = ", ".join(f"{a['matter_id']}:{a['role']}" for a in c["appears_as"])
        print(f"  {c['cast_id']:<18} {c['name']:<26} [{roles}]")
    print(f"\nmatters ({len(compound['matters'])}):")
    for m in compound["matters"]:
        mm = m["matter"]
        print(f"  {mm['matter_id']:<16} {mm['practice_area']:<10} {m['provenance']['scenario_id']}")
    print(f"\nrelationships ({len(compound['relationships'])}):")
    for r in compound["relationships"]:
        print(f"  {r['from']} --{r['type']}--> {r['to']}")
        print(f"      {r['description']}")


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("compound", nargs="?", help="Compound archetype id (omit with --list).")
    ap.add_argument("--list", action="store_true", help="List compound archetypes and exit.")
    ap.add_argument("--seed", type=int, default=0)
    ap.add_argument("--summary", action="store_true", help="Print a readable summary instead of full JSON.")
    ap.add_argument("--canonical", action="store_true", help="Emit the list of projected canonical cases.")
    ap.add_argument("--no-validate", action="store_true")
    ap.add_argument("--out", help="Write the compound JSON (and canonical projections) here.")
    args = ap.parse_args()

    if args.list or not args.compound:
        print("Compound archetypes:")
        for cid in list_compounds():
            print(f"  {cid}")
        return 0

    compound = generate_compound(args.compound, args.seed)

    if not args.no_validate:
        errors = validate_compound(compound)
        if errors:
            print(f"VALIDATION FAILED ({args.compound} seed={args.seed}):", file=sys.stderr)
            for err in errors[:20]:
                print(f"  - {err}", file=sys.stderr)
            return 1

    if args.canonical:
        payload = project_compound(compound)
        print(json.dumps(payload, indent=2, ensure_ascii=False))
    elif args.summary:
        _summary(compound)
    else:
        print(json.dumps(compound, indent=2, ensure_ascii=False))

    if args.out:
        out = Path(args.out)
        out.mkdir(parents=True, exist_ok=True)
        stem = f"{args.compound}.{args.seed}"
        (out / f"{stem}.compound.json").write_text(
            json.dumps(compound, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
        )
        (out / f"{stem}.canonical.json").write_text(
            json.dumps(project_compound(compound), indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
        )
        print(f"\nwrote {out}/{stem}.compound.json and .canonical.json")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
