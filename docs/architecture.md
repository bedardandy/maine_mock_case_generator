# Architecture

This repo is the **upstream producer** of mock legal matters. The three form-filling
repos are the **downstream consumers**. The integration seam is a single, shared shape:
the **canonical case object**.

```
                 mock_matter.schema.json (rich superset)
                              │
   ┌──────────────┐   generate (deterministic engine)   ┌──────────────┐
   │  scenarios/  │ ───────────────────────────────────▶│  Mock Matter │
   │  *.yaml      │   or  skills/mock-case-generator     │   (JSON)     │
   └──────────────┘   (LLM-guided, richer narratives)    └──────┬───────┘
                                                                │ project_to_canonical()
                                                                ▼
                                                  canonical_case.schema.json
                                                       (downstream contract)
                                                                │
                 ┌──────────────────────────┬──────────────────┴───────────────┐
                 ▼                          ▼                                    ▼
        maine-court-forms          maine-probate-forms              transactional-tax-forms
        (family / civil)           (probate / guardianship)         (tax / business / real estate)
```

## Two generation paths

| Path | Entry point | When | Reproducible? |
|------|-------------|------|---------------|
| **Deterministic** | `tools/generate.py`, `generator/engine.py` | Fast CI fixtures, bulk volume | Yes — `(scenario_id, seed)` fully determines output (no timestamps embedded) |
| **LLM-guided** | `skills/mock-case-generator/SKILL.md` | Rich, detailed, novel matters | No — narrative varies |

Both emit the **same** `mock_matter.schema.json` shape, so everything downstream is
identical regardless of how a matter was produced.

## Module map (`generator/`)

| Module | Responsibility |
|--------|----------------|
| `paths.py` | Canonical filesystem locations. |
| `pools.py` | Seeded, *fictional* value factory (names, addresses, fiction-range phones/emails, orgs, banks, credentials). |
| `dsl.py` | The tiny declarative DSL (`pick`, `pick_n`, `date_between`, `date_offset` for real date arithmetic, `int_between` with optional step, templates) that lets scenarios stay data. |
| `scenarios.py` | Discover/load `scenarios/<id>/scenario.yaml`. |
| `engine.py` | `generate_matter(scenario_id, seed)` — assembles every section. |
| `project.py` | `project_to_canonical(matter)` — the downstream seam. |
| `schema.py` | Load schemas; `validate_matter` / `validate_canonical`. |
| `stress.py` | Deterministic mutators that turn any matter into schema-valid hostile variants (see `tools/stress.py`). |
| `cli.py` | The `mmcg` console entry point installed by `pip install -e .`. |

## Adding a scenario

Drop a new `scenarios/<id>/scenario.yaml` (copy an existing one as a template). No code
changes are needed — `engine.py` interprets the scenario declaratively. Run
`python tools/smoke.py --scenarios <id> -v` to verify. This "add a file, not code"
property is what makes the generator quick to adapt to new practice areas or states.

Two authoring notes:

- **Authored parties.** A role may pin exact party fields with
  `roles: [{key: plaintiff, party: {first_name: "José-María", ...}}]` — nothing is
  auto-filled, values may themselves be DSL specs, and `full_name` is derived from the
  name parts (including `suffix`) when omitted. The `edge-*` pack uses this to keep
  hostile values byte-stable across seeds while everything else varies.
- **Computed dates.** `facts` resolve sequentially, so later facts can reference earlier
  ones, and `{date_offset: {from: "{closing_date}", days: 45}}` yields real statutory
  arithmetic (the 1031 45/180-day clock, the § 6111 35-day cure period) instead of
  hand-picked windows that can drift.

## Design choices

- **Fictional by construction.** `pools.py` only emits reserved/invented values; the
  schema pins `provenance.mock` and `provenance.fictional` to `true`.
- **Superset, then project.** The rich matter carries far more than any single form
  needs (interview, objectives, experts). Projection discards what the canonical
  contract doesn't define and normalizes party roles.
- **Declarative scenarios.** Legal content lives in YAML reviewed by a human, not in code.
