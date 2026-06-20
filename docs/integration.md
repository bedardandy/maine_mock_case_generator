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

## Keeping the contract in sync

`catalog/canonical_case.schema.json` here is a **vendored copy** of the upstream
contract in `maine-court-forms`. If the upstream canonical schema changes, re-copy it
and re-run the smoke suite to catch drift.
