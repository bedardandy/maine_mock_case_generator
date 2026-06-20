# Scenario: `business-formation-scorp`

A **transactional** matter: a founder forms a **Maine corporation** and elects
**S-corporation** status, driving the federal and Maine tax filings that follow.

This is a non-litigation matter, so there is no plaintiff/defendant and no court
docket. The client (the **applicant**) is the founder and IRS "responsible
party"; the newly formed corporation is a separate organization party
(`company`). Every generated matter is fictional and reproducible from
`(scenario_id, seed)`.

## At a glance

| Field | Value |
| --- | --- |
| `id` | `business-formation-scorp` |
| `practice_area` | `business` |
| `case_type` | `entity_formation` |
| `status` | `intake` |
| `docket_prefix` | `BU` (no docket assigned — `assign_docket: false`) |
| Jurisdiction | Maine (`ME`), **random county**, "Maine Secretary of State / IRS (filing offices)" |
| Client role | `applicant` (the founder / responsible party) |
| Other party | `company` (the new Maine corporation, an `organization`) |
| Attorney | Counsel for the applicant |
| Downstream repo | `transactional-tax-forms` |
| Example forms | `IRS-SS-4`, `IRS-2553`, `MRS-1120ME`, `MRS-941ME`, `MRS-W4ME` |

Because the matter is transactional, **no docket number is assigned** and the
`court_type` names the filing offices (the Maine Secretary of State and the IRS)
rather than a court.

## The story

A founder organizes a Maine corporation to carry on one of several lines of
business (software development, plumbing/HVAC, a restaurant, landscaping, or
specialty retail) and wants the corporation taxed under Subchapter S so profits
pass through to the shareholders. Articles of Incorporation are filed with the
Maine Secretary of State; the remaining work is to obtain an EIN on **Form SS-4**,
make a timely S-election on **Form 2553**, register with Maine Revenue Services
for corporate income tax and employer withholding, and stand up payroll so the
owner is paid **reasonable compensation** and the first Maine wage filings are
correct. The signing party is the applicant, and the most important output is the
`facts` block, which feeds Forms SS-4, 2553, 1120ME, 941ME, and W-4ME.

## Generated facts

These keys are randomized per seed and surface as canonical `facts` for the
downstream form-fillers:

- `entity_name` — the corporation's name (mirrors the `company` party).
- `entity_type` — "C corporation electing S status" or "corporation".
- `state_of_incorporation` — "Maine".
- `incorporation_date` — date of formation (also the matter's `event_date`).
- `ein_applied` — boolean: whether the EIN has already been requested.
- `s_corp_election` — boolean (always `true`): the S-election is intended.
- `election_effective_date` — the requested effective date of the S-election,
  drawn from the same incorporation window so it coincides with formation.
- `tax_year` / `fiscal_year_end` — "calendar year" / "December 31".
- `num_shareholders` — 1–4 shareholders at formation.
- `num_employees` — 0–12 expected employees.
- `first_payroll_date` — when payroll (and Maine withholding) begins.
- `accounting_method` — "cash" or "accrual".
- `naics_code` — NAICS code matching the principal activity.
- `principal_activity` — the line of business.
- `expected_first_year_revenue` — projected first-year gross receipts.
- `responsible_party_name` — the applicant (the SS-4 responsible party).
- `reasonable_compensation` — planned annual W-2 wages for the owner-employee.

## Third parties

Drawn from a pool (2–4 selected per seed):

- The corporation's **registered agent** (`business_entity`).
- A **co-founder / shareholder** whose eligibility affects the S-election
  (`witness`).
- The company's **CPA / accountant** (`witness`).
- The **business bank** that holds the operating account (`financial_institution`).
- The **Internal Revenue Service** (`government_agency`, named).
- The **Maine Secretary of State** (`government_agency`, named).

The generator supplies fictional person and organization names and contacts; the
two government agencies use their real, explicitly named offices for routing.

## Issues (with governing law)

The issue pool (3–5 selected per seed) tracks the governing federal and Maine
law:

- **S-corporation eligibility** (eligible shareholders, single class of stock) —
  IRC § 1361.
- **Timely Form 2553 election** (within 2 months and 15 days; shareholder
  consents) — IRC § 1362.
- **Reasonable compensation** for the S-corp owner-employee — the
  reasonable-compensation doctrine (IRS guidance; Rev. Rul. 74-44).
- **EIN application on Form SS-4** — IRC § 6109 and the SS-4 instructions.
- **Maine corporate registration and employer withholding** — 13-C M.R.S.
  (formation) and 36 M.R.S. § 5102 et seq. and § 5250 (income tax and
  withholding).
- **Pass-through treatment and owner fringe-benefit rules** — IRC § 1366 and
  § 1372.

## Experts, evidence, and financials

- **Experts** (0–2): a **CPA tax advisor** (S-corporation planning, reasonable
  compensation, payroll) and a **business valuation analyst** (CVA), each
  retained by the applicant.
- **Evidence** (3–6): the Articles of Incorporation filed with the Maine
  Secretary of State, corporate bylaws, the IRS Form SS-4 application, the IRS
  Form 2553 S-election, the shareholder agreement, the IRS EIN confirmation
  letter (CP 575), and the initial capitalization / cap table.
- **Financials** (USD; 2–4 line items, not summed): expected first-year revenue,
  initial capital contributed, planned owner reasonable compensation, and
  estimated first-year payroll.

## Client objectives

Limited liability, pass-through taxation with a reasonable owner salary, a proper
EIN and compliant payroll setup, and full Maine registration. Risk tolerance is
**moderate**. The single non-starter is **blowing the S-election deadline** and
losing pass-through treatment for the first year.

## Generate and validate

```bash
# Emit one matter
python3 tools/generate.py business-formation-scorp --seed 1

# Emit the projected canonical case (downstream contract)
python3 tools/generate.py business-formation-scorp --seed 1 --canonical

# End-to-end smoke test (generate -> validate -> project -> validate)
python3 tools/smoke.py --scenarios business-formation-scorp --count 6 -v
```
