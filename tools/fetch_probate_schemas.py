#!/usr/bin/env python3
"""Fetch (or refresh) annotated Maine probate form schemas for the schema-driven generator.

Pulls repo/forms/<ID>/schema.json from the maine-probate-forms repo and vendors the slice
the generator reads (field_id / data_type / fill_strategy.source) under
integration/maine-probate-forms/<ID>/schema.json. Only schemas that actually carry
fill_strategy annotations are written. Network is needed only when running this tool;
generation and tests run fully offline against the vendored copies.

Examples:
  python tools/fetch_probate_schemas.py DE-101 DE-301 GS-014
  python tools/fetch_probate_schemas.py --refresh        # re-fetch all already-vendored forms
"""
from __future__ import annotations

import argparse
import json
import sys
import urllib.request
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
PROBATE_DIR = REPO_ROOT / "integration" / "maine-probate-forms"
BASE = "https://raw.githubusercontent.com/bedardandy/maine-probate-forms/main/repo/forms"


def _vendored_forms() -> list[str]:
    if not PROBATE_DIR.exists():
        return []
    return sorted(p.name for p in PROBATE_DIR.iterdir() if (p / "schema.json").exists())


def fetch_one(form_id: str) -> bool:
    url = f"{BASE}/{form_id}/schema.json"
    try:
        with urllib.request.urlopen(url, timeout=20) as resp:
            data = json.loads(resp.read().decode("utf-8"))
    except Exception as exc:  # noqa: BLE001
        print(f"  {form_id}: fetch failed ({exc})")
        return False
    fields = data.get("fields", [])
    annotated = sum(1 for f in fields if isinstance(f, dict) and "fill_strategy" in f)
    if not annotated:
        print(f"  {form_id}: skipped (no fill_strategy annotations)")
        return False
    dest = PROBATE_DIR / form_id
    dest.mkdir(parents=True, exist_ok=True)
    (dest / "schema.json").write_text(
        json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )
    print(f"  {form_id}: vendored ({annotated} annotated fields)")
    return True


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("forms", nargs="*", help="Form ids to fetch (e.g. DE-101 GS-014).")
    ap.add_argument("--refresh", action="store_true", help="Re-fetch every already-vendored form.")
    args = ap.parse_args()

    forms = list(args.forms)
    if args.refresh:
        forms = sorted(set(forms) | set(_vendored_forms()))
    if not forms:
        print("Provide form ids, or use --refresh.", file=sys.stderr)
        return 2

    ok = sum(fetch_one(fid) for fid in forms)
    print(f"{ok}/{len(forms)} schema(s) vendored.")
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
