# decedent-estate-informal

Mock scenario archetype: **informal probate of a will and appointment of a personal
representative** for a decedent's estate in Maine. Every generated matter is fully
fictional and reproducible from `(scenario_id, seed)`.

- **Practice area:** probate
- **Case type:** `decedent_estate`
- **Status:** `pre_filing`
- **Docket prefix:** `PE` (a docket number is assigned)
- **Jurisdiction:** Maine **Probate Court**; the county is chosen at random per seed.
- **Downstream:** targets the `maine-probate-forms` repo
  (example forms: `DE-101`, `DE-201`, `DE-301`, `PP-107`).

## What it models

A surviving family member asks the Probate Court to open the decedent's estate
informally and to appoint them as personal representative. The applicant is the
represented client and the signing filer. Depending on the seed, the decedent either
left a will (offered for informal probate) or died intestate (informal appointment,
distribution by Maine intestacy), and the estate may or may not include real property.
The applicant's goals are to be appointed, marshal and protect the assets, pay funeral
costs and valid creditor claims in priority order, and distribute the remainder — while
avoiding a contested formal proceeding.

## Parties

| Role key | Label | Notes |
| --- | --- | --- |
| `decedent` | Decedent | No contact info (`with_contact: false`); carries a date of birth only. |
| `personal_representative` | Applicant / proposed personal representative | The `client_role`; aliased to `client` and projected as the signing `party`. |
| `attorney` | Attorney for the client | Counsel for the applicant. |

There is no `children` key. The decedent is intentionally given no address, phone, or
email so the output never implies contact with a deceased person.

## Facts (resolved per seed)

`date_of_death`, `will_exists`, `will_date`, `decedent_domicile_county` (mirrors the
drawn county), `relationship_to_decedent`, `approximate_estate_value`, `real_property`,
`num_heirs`, `bond_required`, and `probate_type` (`informal probate` or
`informal appointment`). `event_date` is set to `date_of_death`.

## Third parties

Drawn from a pool (2–4 per matter): the surviving spouse and an adult child as
beneficiaries/heirs, a hospital/medical creditor, a bank holding the decedent's
accounts, a funeral-home creditor, and a devisee named in the will. The generator
supplies fictional names and contacts; named institutions use reserved fictional names.

## Issues and governing law

Issues are spotted under the Maine Probate Code (Title 18-C), including:

- `18-C M.R.S. § 3-301` — application for informal probate / informal appointment
- `18-C M.R.S. § 3-203` — priority for appointment of a personal representative
- `18-C M.R.S. § 3-803` — limitations on creditor claims
- `18-C M.R.S. § 2-102` / `§ 2-103` — intestate share / determination of heirs (relevant when there is no will)
- `18-C M.R.S. § 2-402` — homestead allowance for a surviving spouse
- `18-C M.R.S. § 3-108` — limitation period to commence probate

## Experts, evidence, financials

- **Experts** (0–2): a real estate appraiser (MAI) and an estate accountant (CPA),
  each retained by the personal representative.
- **Evidence** (3–6): certified death certificate, original will, preliminary
  inventory, bank/brokerage statements, recorded deed, and funeral bill / other claims.
- **Financials** (USD, 2–4 line items, not summed): real property value, bank and
  brokerage accounts, vehicle and personal property, and outstanding debts and claims.

## Generate and validate

```sh
# Generate one matter
python3 tools/generate.py decedent-estate-informal --seed 1

# Emit the projected downstream canonical case
python3 tools/generate.py decedent-estate-informal --seed 1 --canonical

# Smoke-test across seeds (schema + placeholder-leak + canonical checks)
python3 tools/smoke.py --scenarios decedent-estate-informal --count 6 -v
```
