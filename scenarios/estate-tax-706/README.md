# Scenario: `estate-tax-706`

A **tax** matter: preparation of a decedent's **federal estate tax return
(Form 706)** and **Maine estate tax return (Form 706ME)** for a taxable estate,
together with **Form 56** fiduciary notice and the estate's **fiduciary income
tax returns (Form 1041 / 1041ME)** during administration.

This is a non-litigation, transactional-tax matter, so there is no
plaintiff/defendant and no court docket. The client is the **executor /
personal representative** (the fiduciary), who is the represented client and the
signing filer. Every generated matter is fictional and reproducible from
`(scenario_id, seed)`.

## At a glance

| Field | Value |
| --- | --- |
| `id` | `estate-tax-706` |
| `practice_area` | `tax` |
| `case_type` | `estate_tax` |
| `status` | `intake` |
| `docket_prefix` | `ET` (no docket assigned — `assign_docket: false`) |
| Jurisdiction | Maine (`ME`), **random county**, "Probate Court / IRS / Maine Revenue Services" |
| Client role | `personal_representative` (the executor / fiduciary) |
| Downstream repo | `transactional-tax-forms` |
| Example forms | `IRS-706`, `MRS-706ME`, `IRS-1041`, `MRS-1041ME`, `IRS-56` |

Because the matter is transactional, **no docket number is assigned** and the
`court_type` names the taxing authorities (the Probate Court, the IRS, and Maine
Revenue Services) rather than a single court.

## The story

A Maine resident has died leaving a **multi-million-dollar gross estate** that
exceeds the federal basic exclusion amount, so a Form 706 is actually required.
The executor must value the estate as of the date of death (or elect the
alternate valuation date six months later), claim every available deduction,
decide whether to elect **portability** of the decedent's unused exclusion (the
DSUE amount), and file the federal and Maine estate tax returns within nine
months of death. Along the way the executor files **Form 56** to notify the IRS
of the fiduciary relationship and, because the estate earns income during
administration, files fiduciary income tax returns on **Form 1041** and **Form
1041ME**. The signing party is the personal representative, and the most
important output is the `facts` block, which feeds the 706, 706ME, 1041, 1041ME,
and Form 56.

## Parties

| Role key | Label | Notes |
| --- | --- | --- |
| `decedent` | Decedent | No contact info (`with_contact: false`); carries a date of birth only, so the output never implies contact with a deceased person. |
| `personal_representative` | Executor / personal representative (fiduciary) | The `client_role`; aliased to `client` and projected as the signing `party`. |
| `attorney` | Attorney for the client | Counsel for the executor. |

Both `decedent` and `personal_representative` project into the downstream
canonical `parties`. There is no `children` key.

## Generated facts (resolved per seed)

These keys are randomized per seed and surface as canonical `facts` for the
downstream form-fillers. They are the heart of the scenario:

- `date_of_death` — the decedent's date of death (also the matter's `event_date`).
- `decedent_domicile_county` — mirrors the drawn Maine county.
- `decedent_state` — "Maine".
- `gross_estate_value` — total gross estate, **$7M–$28M** (large enough that a 706 is required).
- `real_property_value` — value of the decedent's real property.
- `closely_held_business_value` — value of any closely-held business interest.
- `marketable_securities_value` — value of brokerage / investment accounts.
- `life_insurance_value` — life insurance proceeds includible under IRC § 2042.
- `debts_and_expenses` — deductible debts, funeral, and administration expenses (IRC § 2053).
- `marital_deduction` — boolean: whether property passes to a surviving spouse.
- `charitable_deduction` — boolean: whether there is a deductible charitable bequest.
- `alternate_valuation_elected` — boolean: whether the IRC § 2032 alternate valuation date is elected.
- `portability_election` — boolean: whether portability of the DSUE is elected.
- `num_beneficiaries` — 1–6 beneficiaries of the estate.
- `prior_taxable_gifts` — boolean: whether the decedent made prior taxable gifts (Form 709).
- `executor_name` — the personal representative (mirrors the `personal_representative` party).
- `return_due_date` — the Form 706 / 706ME due date (≈ nine months after death, extendable six months).

`event_date` is set to `date_of_death`.

## Third parties

Drawn from a pool (2–4 selected per seed):

- A **surviving spouse and beneficiary** (`beneficiary`) — drives the marital deduction (IRC § 2056).
- An **adult child / residuary beneficiary** (`beneficiary`).
- A **charitable beneficiary** (`beneficiary`, an organization) — supports the charitable deduction (IRC § 2055).
- The **trustee of the decedent's revocable trust** (`fiduciary`) — trust assets are includible under IRC § 2038.
- A **life insurance company** (`insurer`) — pays proceeds includible under IRC § 2042 and furnishes Form 712.
- The **Internal Revenue Service** (`government_agency`, named).
- **Maine Revenue Services** (`government_agency`, named).

The generator supplies fictional person and organization names and contacts; the
two government agencies use their real, explicitly named offices for routing.

## Issues (with governing law)

The issue pool (3–6 selected per seed) tracks the governing federal and Maine
estate-tax law:

- **Composition and valuation of the gross estate** — IRC § 2031; §§ 2033–2044.
- **Alternate valuation date election** — IRC § 2032.
- **Marital deduction** for property passing to the surviving spouse — IRC § 2056.
- **Charitable deduction** for bequests to qualified charities — IRC § 2055.
- **Applicable exclusion and portability of the DSUE amount** — IRC § 2010(c).
- **Deductibility of debts, funeral, and administration expenses** — IRC § 2053.
- **Maine estate tax and the Maine exclusion amount** — 36 M.R.S. § 4062 et seq.
- **Fiduciary income tax during administration** (Form 1041 / 1041ME) — IRC § 641.
- **Form 706 filing requirement and the nine-month due date** — IRC § 6018; § 6075.

## Experts, evidence, and financials

- **Experts** (1–3): a **business appraiser** (ASA) for the closely-held business
  interest, a **real estate appraiser** (MAI) for the real property, and an
  **estate and fiduciary tax CPA**, each retained by the personal representative.
- **Evidence** (3–6): the certified death certificate, the will and any revocable
  trust, date-of-death appraisals of the real estate and business interests,
  brokerage and bank statements, life insurance Form 712 statements, prior gift
  tax returns (Form 709), and the estate inventory.
- **Financials** (USD; 3–5 line items, not summed): the gross estate value, real
  property value, closely-held business interest, marketable securities, life
  insurance proceeds, and debts and administration expenses.

## Client objectives

File an accurate, timely Form 706 and Form 706ME; maximize the marital and
charitable deductions; preserve portability of the unused exclusion (DSUE);
obtain defensible appraisals; and file Form 56 and the fiduciary income tax
returns during administration. Risk tolerance is **low**. The non-starters are
**missing the filing deadline** (incurring penalties) and **reporting an asset at
an unsupported value** that cannot be defended on audit.

## Generate and validate

```bash
# Emit one matter
python3 tools/generate.py estate-tax-706 --seed 1

# Emit the projected canonical case (downstream contract)
python3 tools/generate.py estate-tax-706 --seed 1 --canonical

# End-to-end smoke test (generate -> validate -> project -> validate)
python3 tools/smoke.py --scenarios estate-tax-706 --count 6 -v
```
