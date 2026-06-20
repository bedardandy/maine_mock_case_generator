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
| `dsl.py` | The tiny declarative DSL (`pick`, `pick_n`, `date_between`, `int_between`, templates) that lets scenarios stay data. |
| `scenarios.py` | Discover/load `scenarios/<id>/scenario.yaml`. |
| `engine.py` | `generate_matter(scenario_id, seed)` — assembles every section. |
| `project.py` | `project_to_canonical(matter)` — the downstream seam. |
| `schema.py` | Load schemas; `validate_matter` / `validate_canonical`. |

## Adding a scenario

Drop a new `scenarios/<id>/scenario.yaml` (copy an existing one as a template). No code
changes are needed — `engine.py` interprets the scenario declaratively. Run
`python tools/smoke.py --scenarios <id> -v` to verify. This "add a file, not code"
property is what makes the generator quick to adapt to new practice areas or states.

## Design choices

- **Fictional by construction.** `pools.py` only emits reserved/invented values; the
  schema pins `provenance.mock` and `provenance.fictional` to `true`.
- **Superset, then project.** The rich matter carries far more than any single form
  needs (interview, objectives, experts). Projection discards what the canonical
  contract doesn't define and normalizes party roles.
- **Declarative scenarios.** Legal content lives in YAML reviewed by a human, not in code.
