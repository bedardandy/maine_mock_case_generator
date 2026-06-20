# Maine Mock Case Generator

Generate — or guide the detailed generation of — **fictional US legal matters** for
**smoke-testing an end-to-end legal workflow pipeline**. Each generated matter is a rich,
internally-consistent package (fact pattern, intake interview, client objectives, third
parties, legal issues, expert opinions, evidence, financials) that **projects down** to
the canonical case object consumed by the downstream form-filling repos.

> ⚠️ **Everything here is fictional mock data, not legal advice.** See
> [`DISCLAIMER.md`](DISCLAIMER.md). Phones use the `555-01xx` fiction range, emails use
> `example.*`, identities are invented.

```
scenarios/*.yaml ──▶  Mock Matter (rich)  ──▶  canonical case  ──▶  downstream form fillers
   or the LLM-guided skill                     (matter/parties/party/facts)
```

## Why

The sibling repos — [`maine-court-forms`](https://github.com/bedardandy/maine-court-forms),
[`maine-probate-forms`](https://github.com/bedardandy/maine-probate-forms),
[`transactional-tax-forms`](https://github.com/bedardandy/transactional-tax-forms) — all
consume a **canonical fact object** and fill PDFs from it. To test that pipeline
end-to-end you need realistic *inputs*. This repo manufactures those inputs on demand,
deterministically and at volume, and projects them into the exact shape the fillers expect.

## Two ways to generate

| | Deterministic engine | LLM-guided skill |
|--|--|--|
| **Use for** | Fast, reproducible CI fixtures; bulk volume | Rich, detailed, novel matters |
| **Entry point** | `tools/generate.py` | [`skills/mock-case-generator/SKILL.md`](skills/mock-case-generator/SKILL.md) |
| **Needs a model?** | No | Yes (runs inside an agent) |
| **Reproducible?** | Yes — `(scenario, seed)` | No |

Both emit the same [`mock_matter.schema.json`](catalog/mock_matter.schema.json) shape.

## Quick start

```bash
pip install -r requirements.txt          # jsonschema + PyYAML

python tools/generate.py --list          # list scenarios
python tools/generate.py family-divorce-cumberland --seed 1        # a full mock matter
python tools/generate.py family-divorce-cumberland --seed 1 --canonical   # projected canonical case
python tools/smoke.py --count 5          # end-to-end smoke test across all scenarios
python -m pytest -q                      # test suite
```

Or via `make`: `make list`, `make generate SCENARIO=estate-tax-706 SEED=2`, `make smoke`, `make test`.

## Concrete fills (end-to-end proof)

The generator doesn't stop at a canonical case — it pours matters into **real downstream
form mappings** so you can see exactly which PDF fields get populated:

```bash
python tools/fill.py --list
python tools/fill.py FM-004 --scenario family-divorce-cumberland --seed 1   # court form, native
python tools/fill.py IRS-SS-4 --seed 1 --show-empty                          # tax form, via adapter
```

`integration/` vendors the real `mapping.json` from your form repos. Court forms consume
our canonical namespace directly; tax forms (different namespace) go through
`generator/adapters.py`. Each fill prints a coverage report and required-key check; the
form-namespace case JSON it emits is the input the downstream repo's PDF engine renders.
See [`integration/README.md`](integration/README.md).

## Compound (intertwined) matters

Real problems cascade across practice areas. A **compound matter** is a universe of linked
matters that **share one cast** and cross-reference each other:

```bash
python tools/compound.py --list
python tools/compound.py death-cascade --seed 1 --summary             # probate + estate tax + guardianship
python tools/compound.py business-dispute-cascade --seed 1 --summary  # formation + complex litigation
```

| Compound | Matters | Through-line |
|----------|---------|--------------|
| `death-cascade` | probate + estate-tax + guardianship | one decedent; estate value feeds the 706; the minor heir is the ward |
| `marital-breakdown-cascade` | divorce + protection-from-abuse + business | same spouses & children; the marital business is contested |
| `business-dispute-cascade` | formation + complex civil litigation | the company formed in one matter is the defendant in the other |

The same party objects appear across matters, so identities stay consistent everywhere.
Each constituent is an independently-valid Mock Matter and projects to its own canonical
case. See [`docs/compound.md`](docs/compound.md).

## Deep litigation

The `complex-civil-litigation` scenario exercises the schema's `litigation` section: a
multi-party suit with multiple counts, affirmative defenses, counterclaims, cross-claims,
a third-party complaint, discovery, motions, a chronological docket, and trial details.

## Seed scenarios

Seven archetypes spanning the three downstream repos. Add more by dropping a new
`scenarios/<id>/scenario.yaml` — no code changes required.

| Scenario | Practice area | Downstream repo |
|----------|---------------|-----------------|
| `family-divorce-cumberland` | family (divorce, kids, property) | maine-court-forms |
| `protection-from-abuse` | family (PFA order) | maine-court-forms |
| `small-claims-debt` | civil (small claims ≤ $6k) | maine-court-forms |
| `decedent-estate-informal` | probate (informal probate) | maine-probate-forms |
| `minor-guardianship` | probate (guardian of a minor) | maine-probate-forms |
| `business-formation-scorp` | business (incorporate + S-elect) | transactional-tax-forms |
| `estate-tax-706` | tax (Form 706 / 706ME + 1041) | transactional-tax-forms |
| `complex-civil-litigation` | civil (deep, multi-party litigation) | maine-court-forms |

Browse a worked sample of each under [`examples/`](examples/) (`*.matter.json` and the
projected `*.canonical.json`).

## What a Mock Matter contains

`provenance` · `matter` · `parties` (+ `third_parties`) · `fact_pattern` (narrative,
timeline, disputed/undisputed) · `intake_interview` · `client_objectives` · `issues`
(with governing law) · `expert_opinions` · `evidence` · `financials` · `facts` (the flat
form-specific bridge). Full reference: [`docs/data-model.md`](docs/data-model.md).

## Repository layout

```
catalog/      schemas (mock_matter, canonical_case, compound_matter), practice_areas, faker_pools
scenarios/    one folder per archetype (scenario.yaml + README.md)
compound/     intertwined matter universes (compound.yaml + README.md)
generator/    the engine: pools, dsl, scenarios, engine, project, schema, adapters, formfill, compound
tools/        generate, validate, project_canonical, fill, compound, smoke, build_examples, mcp_server
integration/  vendored real downstream form mappings + registry (concrete fills)
skills/       mock-case-generator/ (LLM-guided generation protocol + prompts)
examples/     generated matters, canonical projections, fill plans, and compound universes
docs/         architecture, data-model, integration, compound, smoke-testing
tests/        pytest suite
```

## Adapting it

- **New practice area / state**: copy a `scenarios/<id>/scenario.yaml`, edit the
  jurisdiction, facts, issues, and templates. Run `python tools/smoke.py --scenarios <id> -v`.
- **New downstream form**: read its `mapping.json`, add the keys it needs to the
  scenario's `facts:` block. `facts` is open (`additionalProperties`) on both schemas.
- **Wire into your pipeline**: see [`docs/integration.md`](docs/integration.md).

## Documentation

- [Architecture](docs/architecture.md) — data flow, modules, design choices
- [Data model](docs/data-model.md) — the schemas + the projection mapping
- [Integration](docs/integration.md) — feeding the downstream form repos + concrete fills
- [Compound matters](docs/compound.md) — intertwined matter universes
- [Smoke testing](docs/smoke-testing.md) — CI and volume/fuzz testing
- [Disclaimer](DISCLAIMER.md) — fictional-data guarantees and responsible use
