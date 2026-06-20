# Schema-driven probate fixtures

This repo has **two** generation paths:

1. The **scenario-driven engine** (`generator/engine.py`) — builds rich Mock Matters that
   project to the canonical fact object and fill the court/tax forms via their `mapping.json`.
2. The **schema-driven probate generator** (`generator/schema_fill.py`) — documented here.

The probate repo ([maine-probate-forms](https://github.com/bedardandy/maine-probate-forms))
fills forms a different way: each field in a form's `schema.json` carries a
`fill_strategy.source` that says where its value comes from. This generator produces the
case object that pipeline consumes directly. (Ported from a generator built in
maine-probate-forms; see the PR that added it.)

## The routing contract

The generator reads only three keys per field — `field_id`, `data_type`,
`fill_strategy.source` — and routes a synthesized value to where the fill pipeline looks:

| `fill_strategy.source` | goes to | notes |
|---|---|---|
| `case_dict.<key>` | `case["case_dict"][key]` | county / docket / decedent-name special-cased |
| `<role>_record.<attr>` | `case["<role>_record"][attr]` | one coherent identity per role (name/address/phone/email/bar) |
| `llm_over_narrative` | `case["narrative_facts"][field_id]` | composed by `data_type` |
| `recompute_*`, `wet_ink`, `human_decision`, `left_blank`, `triage` | (nothing) | intentionally unfilled — derived, hand/ink, or decision fields |

Output shape:

```json
{ "case_dict": {…}, "<role>_record": {…}, "narrative_facts": {…}, "_meta": {…} }
```

This is **not** the `mock_matter` / `canonical_case` shape used elsewhere in this repo — it
is the probate pipeline's own fixture shape.

## Generate

```bash
python tools/probate_case.py --list
python tools/probate_case.py DE-401 --seed 7
python tools/probate_case.py DE-301 --seed 3 --stress
python tools/probate_case.py --all --seeds 0,1,2 --out out/probate     # one file per form/seed
```

In Python:

```python
from generator import generate_for_form, list_probate_forms
case = generate_for_form("DE-101", seed=7)        # deterministic per (seed, stress)
```

A committed sample per form lives in [`examples/probate/`](../examples/probate/).

## Design decisions (preserved from the handoff)

- **Type-aware synthesis** — dates by sub-meaning (death 2024–26, DOB 1940–70), currency
  comma-formatted, and `day`/`month`/`year` jurat blanks get *short* box-fitting values.
- **Never route the `"Not applicable"` sentinel into a date/currency/numeric blank** — it
  overflows narrow boxes (e.g. a 25 pt jurat "day" slot). Only free-text fields get it.
- **Coherent identities per role** — the decedent's name is identical everywhere; a role's
  address/phone/email are internally consistent.
- **`--stress` mode** — long hyphenated names, apartment addresses, and 7–8-figure amounts
  to shake out horizontal overflow.
- **Maine-flavoured, fictional banks** — counties, towns+zips, street names; `555-01xx`
  phones and `example.com` emails. No real PII.

`tests/test_schema_fill.py` enforces determinism, the no-sentinel-in-typed-blanks rule,
short jurat components, fiction ranges, and per-role name coherence across every form.

## Adding / refreshing forms

Vendored schemas live under `integration/maine-probate-forms/<ID>/schema.json`. To add or
refresh (network needed only here; generation/tests are offline):

```bash
python tools/fetch_probate_schemas.py DE-501 GS-001
python tools/fetch_probate_schemas.py --refresh        # re-pull all vendored forms
```

## Recommended downstream validation

Pair generation with an **OCR-style flattened read-back** in the forms repo (which owns the
PDF toolchain): fill → flatten AcroForm widgets to real text (`fitz` `doc.bake(widgets=True)`)
→ check for (a) **overprint** (filled glyphs overlapping printed ink, excluding `_`),
(b) **offpage** (value past the margin), and (c) **adjacent-cell collision** (two filled
values whose ink touches on the same row). That trio caught every real edge case upstream.
