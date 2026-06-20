#!/usr/bin/env python3
"""Regenerate the committed examples/ directory.

For each scenario, writes a sample Mock Matter and its projected canonical case at a
fixed seed, so the repository ships a browsable, reproducible example per practice area.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from generator import (  # noqa: E402
    fill_form,
    generate_matter,
    list_forms,
    list_scenarios,
    load_form,
    project_to_canonical,
    validate_canonical,
    validate_matter,
)

EXAMPLE_SEED = 7


def main() -> int:
    examples_dir = Path(__file__).resolve().parents[1] / "examples"
    examples_dir.mkdir(exist_ok=True)

    failures = 0
    for sid in list_scenarios():
        matter = generate_matter(sid, EXAMPLE_SEED)
        case = project_to_canonical(matter)

        m_errors = validate_matter(matter)
        c_errors = validate_canonical(case)
        if m_errors or c_errors:
            failures += 1
            print(f"FAIL {sid}: matter={m_errors} canonical={c_errors}")
            continue

        (examples_dir / f"{sid}.matter.json").write_text(
            json.dumps(matter, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
        )
        (examples_dir / f"{sid}.canonical.json").write_text(
            json.dumps(case, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
        )
        print(f"wrote examples/{sid}.matter.json and examples/{sid}.canonical.json")

    # Concrete fill plans against the real vendored form mappings.
    fills_dir = examples_dir / "fills"
    fills_dir.mkdir(exist_ok=True)
    for fid in list_forms():
        scenario = load_form(fid)["meta"]["best_scenario"]
        plan = fill_form(generate_matter(scenario, EXAMPLE_SEED), fid, today="2026-06-20")
        (fills_dir / f"{fid}.fillplan.json").write_text(
            json.dumps(plan, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
        )
        cov = plan["coverage"]
        print(f"wrote examples/fills/{fid}.fillplan.json ({cov['filled_fields']}/{cov['total_fields']})")

    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
