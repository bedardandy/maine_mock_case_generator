#!/usr/bin/env python3
"""Validate a Mock Matter (or projected canonical case) JSON file against its schema.

Examples:
  python tools/validate.py examples/family-divorce-cumberland.matter.json
  python tools/generate.py family-divorce-cumberland --canonical | python tools/validate.py --canonical -
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from generator import validate_canonical, validate_matter  # noqa: E402


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("path", help="JSON file to validate, or '-' for stdin.")
    ap.add_argument("--canonical", action="store_true", help="Validate against the downstream canonical case schema.")
    args = ap.parse_args()

    text = sys.stdin.read() if args.path == "-" else Path(args.path).read_text(encoding="utf-8")
    instance = json.loads(text)

    errors = validate_canonical(instance) if args.canonical else validate_matter(instance)
    label = "canonical case" if args.canonical else "mock matter"
    if errors:
        print(f"INVALID {label}: {len(errors)} error(s)")
        for err in errors:
            print(f"  - {err}")
        return 1
    print(f"OK: valid {label}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
