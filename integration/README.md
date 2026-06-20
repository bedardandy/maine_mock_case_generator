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
  maine-court-forms/FM-004/         Complaint for Divorce        (profile: canonical)
  transactional-tax-forms/IRS-SS-4/ EIN application (Form SS-4)  (profile: tax)
```

## The two namespaces

The downstream repos do **not** all speak the same fact-key namespace:

| Profile | Namespace | Adapter | Example form |
|---------|-----------|---------|--------------|
| `canonical` | `matter.*`, `parties.<role>.*`, `party.*`, `facts.*` | none — our canonical case *is* this namespace | FM-004 (`parties.plaintiff.full_name`, `matter.court_location`) |
| `tax` | `entity.*`, `responsible_party.*`, `executor.*`, `decedent.*`, `facts.*` | `generator/adapters.py::to_tax_case` | IRS-SS-4 (`entity.legal_name`, `responsible_party.name`) |

So a **court** form fills natively from a projected canonical case, while a **tax** form
goes through the tax adapter first. This is the real integration work, made explicit.

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
