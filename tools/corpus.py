#!/usr/bin/env python3
"""Build a bulk JSONL fixture corpus for downstream repos.

One line per record. Base records carry the full Mock Matter and its projected
canonical case; --stress appends the schema-valid stressed variants; --compounds
appends whole compound universes. A manifest.json summarizes what was built so a
consuming repo (maine-court-forms, maine-probate-forms, transactional-tax-forms) can
pin exactly what its CI ran against.

Examples:
  python tools/corpus.py --out out/corpus                 # all scenarios x 3 seeds
  python tools/corpus.py --seeds 5 --stress --compounds --out out/corpus
  python tools/corpus.py --scenarios residential-purchase-sale,like-kind-exchange-1031 --canonical-only --out out/re
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from generator import (  # noqa: E402
    GENERATOR_VERSION,
    generate_compound,
    generate_matter,
    list_compounds,
    list_scenarios,
    project_to_canonical,
    validate_canonical,
    validate_matter,
)
from generator.stress import MUTATORS, stress_variants  # noqa: E402


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--out", default="out/corpus", help="Output directory (default out/corpus).")
    ap.add_argument("--seeds", type=int, default=3, help="Seeds per scenario, 0..n-1 (default 3).")
    ap.add_argument("--scenarios", help="Comma-separated scenario ids (default: all).")
    ap.add_argument("--stress", action="store_true", help="Also emit the stressed variants of seed 0.")
    ap.add_argument("--compounds", action="store_true", help="Also emit compound universes (seed 0).")
    ap.add_argument("--canonical-only", action="store_true", help="Omit the full matter; emit only the canonical case.")
    args = ap.parse_args()

    scenarios = args.scenarios.split(",") if args.scenarios else list_scenarios()
    out_dir = Path(args.out)
    out_dir.mkdir(parents=True, exist_ok=True)
    corpus_path = out_dir / "corpus.jsonl"

    counts = {"matters": 0, "stress_variants": 0, "compounds": 0}
    with corpus_path.open("w", encoding="utf-8") as fh:
        def emit(record: dict) -> None:
            fh.write(json.dumps(record, ensure_ascii=False) + "\n")

        for scenario in scenarios:
            for seed in range(args.seeds):
                matter = generate_matter(scenario, seed)
                errors = validate_matter(matter)
                if errors:
                    raise SystemExit(f"invalid matter {scenario} seed={seed}: {errors}")
                case = project_to_canonical(matter)
                cerrs = validate_canonical(case)
                if cerrs:
                    raise SystemExit(f"invalid canonical {scenario} seed={seed}: {cerrs}")
                record = {"kind": "matter", "scenario": scenario, "seed": seed, "canonical": case}
                if not args.canonical_only:
                    record["matter"] = matter
                emit(record)
                counts["matters"] += 1

            if args.stress:
                base = generate_matter(scenario, 0)
                for name, variant in stress_variants(base, 0):
                    record = {"kind": "stress", "scenario": scenario, "seed": 0,
                              "mutator": name, "canonical": project_to_canonical(variant)}
                    if not args.canonical_only:
                        record["matter"] = variant
                    emit(record)
                    counts["stress_variants"] += 1

        if args.compounds:
            for compound_id in list_compounds():
                universe = generate_compound(compound_id, 0)
                emit({"kind": "compound", "compound": compound_id, "seed": 0, "universe": universe})
                counts["compounds"] += 1

    manifest = {
        "generator_version": GENERATOR_VERSION,
        "record_counts": counts,
        "scenarios": scenarios,
        "seeds_per_scenario": args.seeds,
        "stress_mutators": list(MUTATORS) if args.stress else [],
        "compounds": list_compounds() if args.compounds else [],
        "notes": "All records are FICTIONAL mock data (see DISCLAIMER.md). "
                 "Reproduce any record from (scenario, seed) alone.",
    }
    (out_dir / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    total = sum(counts.values())
    print(f"wrote {total} record(s) to {corpus_path} ({counts})")
    print(f"wrote {out_dir / 'manifest.json'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
