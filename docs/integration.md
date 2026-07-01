# Integrating with the form-filling pipeline

This generator exists to feed the downstream form repos so a whole legal workflow can
be exercised end-to-end with fictional data.

## The hand-off

```
generate_matter()  →  Mock Matter  →  project_to_canonical()  →  canonical case  →  <form repo> fill engine  →  draft PDFs
```

The **canonical case object** is the contract. Any consumer that accepts the shape in
`catalog/canonical_case.schema.json` can be driven by this generator.

## Downstream targets

| Repo | Practice areas | Representative forms |
|------|----------------|----------------------|
| [`maine-court-forms`](https://github.com/bedardandy/maine-court-forms) | family, civil, criminal | FM-040, FM-050, SC-001, CV-001 |
| [`maine-probate-forms`](https://github.com/bedardandy/maine-probate-forms) | probate, guardianship | DE-101, DE-301, PP-107, GS-008 |
| [`transactional-tax-forms`](https://github.com/bedardandy/transactional-tax-forms) | tax, business, real estate | IRS-SS-4, IRS-2553, IRS-706, MRS-706ME, MRS-1120ME |

`catalog/practice_areas.json` maps each `practice_area` to its downstream repo and a
few representative form ids, so a router can decide where a matter goes.

## Wiring example

```bash
# 1. Produce a fictional matter and project it to the canonical contract.
python tools/generate.py decedent-estate-informal --seed 3 --canonical > case.json

# 2. Hand case.json to a downstream fill engine, e.g. (illustrative):
#    cd ../maine-probate-forms
#    python tools/fill_plan.py --case ../maine_mock_case_generator/case.json --form DE-301
```

In Python:

```python
from generator import generate_matter, project_to_canonical

matter = generate_matter("estate-tax-706", seed=3)
case = project_to_canonical(matter)          # validates against the canonical schema
# feed `case` (matter / parties / party / facts) into the downstream filler
```

## Concrete fills wired in this repo

Two forms are wired end-to-end under `integration/` (real vendored `mapping.json`):

- **FM-004 — Complaint for Divorce** (`maine-court-forms`, `canonical` profile): fills
  natively from a projected canonical case.
- **IRS-SS-4 — EIN application** (`transactional-tax-forms`, `tax` profile): fills via
  `generator/adapters.py::to_tax_case`, which translates the canonical case into the
  tax namespace (`entity.*`, `responsible_party.*`, `facts.*`).

```bash
python tools/fill.py --list
python tools/fill.py FM-004 --scenario family-divorce-cumberland --seed 1
python tools/fill.py IRS-SS-4 --seed 1 --out out/    # writes the fill plan + case JSON
```

See [`integration/README.md`](../integration/README.md) for the coverage model and how to
wire additional forms.

## Consuming this generator from a sibling repo

Three supported patterns, cheapest first:

### 1. Editable install (recommended for local dev and CI)

```bash
git clone https://github.com/bedardandy/maine_mock_case_generator
pip install -e maine_mock_case_generator
```

This puts the `generator` package on the path **and** the `mmcg` console script on
`$PATH`, while the data (`catalog/`, `scenarios/`, `integration/`) resolves from the
checkout. In a downstream repo's CI:

```yaml
# e.g. maine-court-forms/.github/workflows/ci.yml
- uses: actions/checkout@v4
  with:
    repository: bedardandy/maine_mock_case_generator
    path: mockgen
- run: pip install -e ./mockgen
- run: mmcg generate family-divorce-cumberland --seed 1 --canonical > fixture.json
- run: python tools/fill_plan.py --case fixture.json --form FM-004
```

If the package must live elsewhere than its data (vendored subtree, unusual layouts),
point `MOCK_CASE_GENERATOR_ROOT` at the checkout root.

### 2. The published fixture corpus (no Python dependency at all)

Every push to this repo builds `out/corpus/` (via `make corpus`) and uploads it as the
**`mock-case-corpus`** workflow artifact: one JSONL with, per scenario, N seeds of
`{matter, canonical}` records, the four schema-valid **stressed variants** of seed 0, the
compound universes, and a `manifest.json` pinning generator version and counts. A
downstream repo can download the artifact (e.g. `dawidd6/action-download-artifact`, or
`gh run download` locally) and replay every record against its fill engine — that's a
~270-record conformance suite for free, with zero coupling to this repo's code.

### 3. Seed-pinned fixtures (golden files)

Because `(scenario_id, seed)` fully determines the output, a downstream repo can commit
*just those two values* instead of a JSON blob:

```python
matter = generate_matter("estate-tax-706", seed=3)   # byte-identical forever
```

Regenerate on demand; diff noise only appears when this repo *intentionally* changes a
scenario (and bumps `GENERATOR_VERSION`).

### Stress-testing a downstream filler

`tools/stress.py` (or `mmcg stress`) emits schema-valid but hostile variants — optionals
absent, optionals present-but-empty, oversized text, unicode-decorated text — plus the
`edge-*` scenario pack (unicode names, six-child household, sparse org parties, leap-day
dates, currency extremes). A document-automation pipeline that survives:

```bash
mmcg stress --all-scenarios --seeds 2 --canonical --jsonl stress.jsonl
```

has been exercised on every "the intake was weird" case we know how to model. Ask for
more mutators in `generator/stress.py` — each is ~20 lines.

## Matching `facts` to a specific form

Downstream forms read flat keys from `facts` via their `mapping.json`. When you add a
form to your pipeline:

1. Look at the form's `mapping.json` (or `sample_case.json`) to see which `facts.*`
   keys it expects.
2. Make sure the relevant scenario's `facts:` block emits those keys (add them to
   `scenarios/<id>/scenario.yaml`).
3. Re-run `python tools/smoke.py --scenarios <id> -v` and re-validate the projection.

Because `facts` is `additionalProperties: true` on both schemas, you can add new
form-specific keys without touching any code.

A form may also declare `alt_scenarios` in `integration/registry.json` — additional
scenarios known to drive it. ME-RETTD, for example, fills from `real-estate-transfer`
(the deed-style archetype) *and* all five closing-suite sale scenarios via the
seller/buyer → transferor/transferee role fallback in `generator/adapters.py`. The
smoke suite exercises every declared source.

## Keeping the contract in sync

`catalog/canonical_case.schema.json` here is a **vendored copy** of the upstream
contract in `maine-court-forms`. If the upstream canonical schema changes, re-copy it
and re-run the smoke suite to catch drift.

## Checklist: wiring a new downstream repo

1. Vendor the form's real `mapping.json` (and `form.yaml` if it has one) under
   `integration/<repo>/<FORM-ID>/`.
2. Add the form to `integration/registry.json` with its `profile` (`canonical`, `tax`,
   `real_estate`, or a new adapter in `generator/adapters.py`) and a `best_scenario`
   (plus `alt_scenarios` if several fit).
3. Make sure a scenario emits the `facts.*` keys the mapping reads; add keys to its
   `scenario.yaml` if not (no code changes needed).
4. `python tools/fill.py <FORM-ID> --seed 1` — check coverage and required keys.
5. `python tools/smoke.py --count 5` and `make examples` — both must stay green; the
   fill is now part of CI forever.
