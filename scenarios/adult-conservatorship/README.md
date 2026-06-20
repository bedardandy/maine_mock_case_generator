# Scenario: adult-conservatorship

A **Maine probate** matter: a **petition for appointment of a guardian and/or
conservator for an incapacitated adult**. The client (the **petitioner**) is a
relative — often an adult child — who seeks authority over the personal care
and/or finances of the **respondent**, an adult alleged to be incapacitated
(for example, an elderly parent with dementia or an adult with a serious
disability). All names, parties, and facts are **fictional** and generated
deterministically from a `(scenario_id, seed)` pair. The subject matter is
treated with **dignity and non-graphically**.

## At a glance

| Field | Value |
| --- | --- |
| `id` | `adult-conservatorship` |
| `practice_area` | `probate` |
| `case_type` | `conservatorship` |
| `status` | `pre_filing` |
| `docket_prefix` | `GC` (e.g. `AND-GC-2026-744`) |
| Jurisdiction | ME, **random county**, Probate Court |
| Downstream repo | `maine-probate-forms` |
| Example forms | `GS-014`, `PP-201`, `PP-401` |

## Parties

- **petitioner** — "Petitioner (proposed guardian/conservator)". This is the
  `client_role`; the petitioner becomes the signing filer (`party`) in the
  projected canonical case.
- **respondent** — "Respondent (alleged incapacitated adult)". The adult whose
  capacity is at issue and for whom protection is sought.
- **attorney** — counsel for the petitioner (always generated).

There are **no children** in this scenario.

## Randomized facts (DSL knobs)

These resolve **after** the parties, so they may reference party names. No
`event_date` is set for this scenario.

| Fact key | Resolution |
| --- | --- |
| `respondent_relationship` | the petitioner's mother / father / adult sibling / spouse |
| `alleged_condition` | advanced dementia / a severe traumatic brain injury / a serious developmental disability / a stroke with cognitive impairment |
| `petition_type` | guardianship of the person / conservatorship of the estate / both guardianship and conservatorship |
| `respondent_consents` | `true` / `false` (structured fact only; never rendered into prose) |
| `least_restrictive_considered` | `true` (the least restrictive alternative is always considered) |
| `estate_value` | integer `25000 .. 1200000` |
| `monthly_income` | integer `1200 .. 7000` |
| `existing_poa` | `true` / `false` (structured fact only; never rendered into prose) |
| `care_setting` | lives at home with supports / resides in a long-term care facility / lives with the petitioner |
| `physician_evaluation_obtained` | `true` / `false` (structured fact only; never rendered into prose) |

`filing_date` is a random date in `2025-10-01 .. 2026-05-15`.

> Note: `respondent_consents`, `existing_poa`, and `physician_evaluation_obtained`
> are booleans. They drive the structured `facts` object and the issue analysis
> but are intentionally **not** interpolated into any narrative string, so no
> `True`/`False` ever leaks into human-readable text. The consent question, the
> existing power of attorney, and the physician's evaluation are instead handled
> neutrally in prose. (The smoke test's placeholder/leak check is the guardrail
> here.)

## Third parties

Pool of six, `3 .. 5` selected per matter:

- Respondent's primary physician (`healthcare_provider`) — nature and extent of
  the alleged incapacity and level of care required
- Court visitor / guardian ad litem (`witness`) — investigates the petition and
  reports to the court on the respondent's circumstances and wishes
- Bank holding the respondent's accounts (`financial_institution`) — accounts a
  conservatorship would protect
- Adult sibling of the petitioner (`family_member`) — another adult child of the
  respondent, entitled to notice, who may support or object
- Adult Protective Services (`government_agency`) — named **Maine Adult
  Protective Services**
- Long-term care facility (`healthcare_provider`) — day-to-day care needs and
  supervision

Person/organization names and contacts are filled by the generator; no
fictional person names are hardcoded in the YAML (the Adult Protective Services
agency uses an explicit `name`).

## Issues and governing law

Pool of six, `3 .. 5` selected per matter, each tied to a § citation in the
**Maine Probate Code, Title 18-C**:

- Statutory basis for adult guardianship — **18-C M.R.S. § 5-301 and § 5-301-A**
- Conservatorship and protective order over the estate — **18-C M.R.S. § 5-401
  and § 5-409**
- Clear-and-convincing-evidence standard and required findings — **18-C M.R.S.
  § 5-301**
- Least restrictive alternative and supported decision-making — **18-C M.R.S.
  § 5-301-A**
- Notice and the respondent's due-process rights (right to counsel, to be
  present) — **18-C M.R.S. § 5-305**
- Powers and duties of the guardian/conservator and the role of an existing
  power of attorney — **18-C M.R.S. § 5-313 and § 5-418**

The pool deliberately covers the **clear-and-convincing-evidence standard**,
**least-restrictive alternatives**, and the respondent's **due-process rights**.

## Experts

`1 .. 2` selected. Pool of two:

- A **geriatric medicine / neuropsychology** evaluator (`M.D.`), retained by the
  **court**, on the respondent's capacity and functional abilities.
- A **geriatric care manager** (`RN, CMC`), retained by the **petitioner**, on an
  appropriate, least-restrictive care plan.

## Evidence

Pool of six, `3 .. 6` selected per matter: the physician's capacity
evaluation/affidavit (`medical_record`), the petition and proposed care plan
(`document`), a financial inventory of the respondent's assets
(`financial_record`), any existing power of attorney or advance directive
(`document`, controlled by the respondent), bank statements
(`financial_record`), and letters from family members (`correspondence`).

## Interview & objectives

The intake interview runs six exchanges from the **petitioner's perspective** —
the relationship and concern, the authority needed (and the desire not to take
more than necessary), the respondent's current situation, less restrictive
options, the financial picture, and the family's views. Client objectives
center on obtaining **only the authority that is needed**, protecting the
respondent's finances and well-being, honoring the **least restrictive
alternative**, and avoiding family conflict, with `risk_tolerance: low` and a
non-starter of any arrangement that compromises the respondent's safety or
strips away more independence than necessary.

## Financials

Pool of four, `2 .. 4` selected per matter (`total_is_sum: false`): the value of
the respondent's estate to be protected, the respondent's monthly income and
benefits, estimated monthly care costs, and any existing debts.

## Generate & validate

```sh
# Emit one matter (validates against catalog/mock_matter.schema.json)
python3 tools/generate.py adult-conservatorship --seed 1

# Emit the projected canonical case instead
python3 tools/generate.py adult-conservatorship --seed 1 --canonical

# End-to-end smoke test (generate -> validate -> placeholder check -> project -> validate)
python3 tools/smoke.py --scenarios adult-conservatorship --count 8 -v
```

Smoke must report **PASS** with **0 failures**.
