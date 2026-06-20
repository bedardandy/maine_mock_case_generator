#!/usr/bin/env python3
"""Project a Mock Matter JSON file down to the downstream canonical case object.

Examples:
  python tools/project_canonical.py examples/family-divorce-cumberland.matter.json
  python tools/generate.py decedent-estate-informal | python tools/project_canonical.py -
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from generator import project_to_canonical, validate_canonical  # noqa: E402


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("path", help="Mock Matter JSON file, or '-' for stdin.")
    ap.add_argument("--out", help="Write canonical case here (default stdout).")
    ap.add_argument("--no-validate", action="store_true", help="Skip canonical-schema validation.")
    args = ap.parse_args()

    text = sys.stdin.read() if args.path == "-" else Path(args.path).read_text(encoding="utf-8")
    matter = json.loads(text)
    case = project_to_canonical(matter)

    if not args.no_validate:
        errors = validate_canonical(case)
        if errors:
            print("PROJECTION FAILED canonical validation:", file=sys.stderr)
            for err in errors:
                print(f"  - {err}", file=sys.stderr)
            return 1

    out_text = json.dumps(case, indent=2, ensure_ascii=False)
    if args.out:
        Path(args.out).write_text(out_text + "\n", encoding="utf-8")
        print(f"wrote {args.out}")
    else:
        print(out_text)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
