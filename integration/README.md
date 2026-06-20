# Integration: concrete fills

This directory wires generated mock matters into **real downstream form mappings** so you
can see, end to end, exactly which PDF fields a matter would populate. It is the proof
that the generator's output actually drives the form-filling repos.

## What's here

Each `<repo>/<FORM_ID>/` folder vendors the **real** `mapping.json` (and `form.yaml`)
copied from the downstream repository. `mapping.json` maps each PDF field id to a
fact-key. `registry.json` declares, per form, which namespace profile bridges a projected
canonical case into that form's expected fact-keys.

```
integration/
  registry.json
  maine-court-forms/        FM-004, FM-006, FM-050, PA-001, CV-007   (profile: canonical)
  maine-probate-forms/      DE-301   (canonical; mapping AUTHORED here from the schema)
  transactional-tax-forms/  IRS-SS-4, IRS-2553   (tax)  ·  MRS-706ME (canonical)  ·  ME-RETTD (real_estate)
```

### Authored mappings

The court and tax repos ship a `mapping.json` (field-id -> fact-key), so those are vendored
as-is. The **probate** repo ships per-form field *schemas* but no fact-key mapping, so
`maine-probate-forms/DE-301/mapping.json` was **authored in this repo** from the vendored
`schema.json` (field ids + labels + data types). It is marked `"status": "authored-here"`
and `mapping_authored_here: true` in the registry. This shows how to bring a downstream repo
that lacks a canonical mapping into the same fill pipeline.

## Three namespaces

The downstream repos do **not** all speak the same fact-key namespace — surfacing this is
the real integration work:

| Profile | Namespace | Adapter | Example form |
|---------|-----------|---------|--------------|
| `canonical` | `matter.*`, `parties.<role>.*`, `party.*`, `facts.*` | none — our canonical case *is* this namespace | FM-004, CV-007, MRS-706ME |
| `tax` | `entity.*`, `responsible_party.*`, `executor.*`, `decedent.*`, `facts.*` | `adapters.to_tax_case` | IRS-SS-4, IRS-2553 |
| `real_estate` | `property.*`, `transferor.*`, `transferee.*`, `facts.*` | `adapters.to_real_estate_case` | ME-RETTD |

A `canonical` form fills natively from a projected canonical case; a `tax` or
`real_estate` form goes through the matching adapter first.

## Wired forms

| Form | Repo | Profile | Best scenario |
|------|------|---------|---------------|
| FM-004 | maine-court-forms | canonical | family-divorce-cumberland |
| FM-006 | maine-court-forms | canonical | pro-se-interstate-custody |
| FM-050 | maine-court-forms | canonical | family-divorce-cumberland |
| PA-001 | maine-court-forms | canonical | protection-from-abuse |
| CV-007 | maine-court-forms | canonical | residential-eviction |
| DE-301 | maine-probate-forms | canonical (authored) | decedent-estate-informal |
| IRS-SS-4 | transactional-tax-forms | tax | business-formation-scorp |
| IRS-2553 | transactional-tax-forms | tax | business-formation-scorp |
| MRS-706ME | transactional-tax-forms | canonical | estate-tax-706 |
| ME-RETTD | transactional-tax-forms | real_estate | real-estate-transfer |

## Run a fill

```bash
python tools/fill.py --list
python tools/fill.py FM-004 --scenario family-divorce-cumberland --seed 1
python tools/fill.py IRS-SS-4 --seed 1 --show-empty          # see unfilled fields too
python tools/fill.py FM-004 --seed 1 --out out/              # write fillplan + case JSON
```

Output is a coverage report (filled vs. mapped fields), whether the mapping's required
keys are satisfied, and the resolved `field_id -> value` plan. The smoke harness
(`python tools/smoke.py`) also prints a one-line coverage summary per wired form.

## Coverage is intentionally partial

A form has many *situational* fields (SS-4 alone has fields for LLCs, trusts, estates,
pension plans, foreign entities, third-party designees). A single matter only triggers the
fields its facts imply, so a realistic coverage is well under 100%. The report shows
honestly which fields are populated and which are blank — and the **required** keys must
always be satisfied.

## Improving coverage

To populate more fields for a form:

1. Read the form's `mapping.json` to see which fact-keys it wants.
2. For a `canonical` form, add those keys to the relevant scenario's `facts:` block
   (e.g. FM-004 wants `facts.marriage_city` / `marriage_county` / `marriage_state`).
3. For a `tax` form, extend `to_tax_case` in `generator/adapters.py`.
4. Re-run `python tools/fill.py <FORM> --seed 1` and the smoke suite.

## Rendering the actual PDF

These vendored files are the *input contract*. To render a filled PDF, hand the
form-namespace case JSON (`tools/fill.py ... --out out/`) to the downstream repo's own
fill engine, which fetches the blank PDF on demand and writes the AcroForm values. That
step lives in the downstream repos by design (they own the PDF toolchain and the
field-geometry recipes).

## Keeping vendored mappings fresh

`mapping.json` files carry a `built_against_sha256`. If a downstream form's mapping
changes, re-copy it here and re-run the fill tests to catch drift.
