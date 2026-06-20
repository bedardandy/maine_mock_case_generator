#!/usr/bin/env python3
"""Generate Maine probate fill fixtures via the schema-driven generator.

This is the probate pipeline's NATIVE path: it reads a form's annotated schema
(field_id / data_type / fill_strategy.source) and emits the case object the
maine-probate-forms fill pipeline consumes ({case_dict, <role>_record, narrative_facts}).

Examples:
  python tools/probate_case.py --list
  python tools/probate_case.py DE-401 --seed 7
  python tools/probate_case.py DE-301 --seed 3 --stress
  python tools/probate_case.py --all --out out/probate            # one case per form
  python tools/probate_case.py --all --seeds 0,1,2 --out out/probate
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from generator import generate_for_form, list_probate_forms  # noqa: E402


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("form", nargs="?", help="Probate form id (omit with --list/--all).")
    ap.add_argument("--list", action="store_true", help="List vendored probate forms and exit.")
    ap.add_argument("--all", action="store_true", help="Generate for every vendored form.")
    ap.add_argument("--seed", type=int, default=0)
    ap.add_argument("--seeds", help="Comma-separated seeds (overrides --seed; for --all).")
    ap.add_argument("--stress", action="store_true", help="Emit overflow-stressing values.")
    ap.add_argument("--out", help="Directory to write fixtures (default: stdout for a single case).")
    args = ap.parse_args()

    forms = list_probate_forms()
    if args.list:
        print("Vendored probate forms:")
        for fid in forms:
            print(f"  {fid}")
        return 0

    seeds = [int(s) for s in args.seeds.split(",")] if args.seeds else [args.seed]

    if args.all:
        out = Path(args.out or "out/probate")
        out.mkdir(parents=True, exist_ok=True)
        count = 0
        for fid in forms:
            for seed in seeds:
                case = generate_for_form(fid, seed, args.stress)
                suffix = ".stress" if args.stress else ""
                path = out / f"{fid}.seed{seed}{suffix}.json"
                path.write_text(json.dumps(case, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
                count += 1
        print(f"wrote {count} fixtures to {out}/")
        return 0

    if not args.form:
        print("Provide a form id, or use --list / --all.", file=sys.stderr)
        return 2

    case = generate_for_form(args.form, seeds[0], args.stress)
    text = json.dumps(case, indent=2, ensure_ascii=False)
    if args.out:
        out = Path(args.out)
        out.mkdir(parents=True, exist_ok=True)
        path = out / f"{args.form}.seed{seeds[0]}.json"
        path.write_text(text + "\n", encoding="utf-8")
        print(f"wrote {path}")
    else:
        print(text)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
