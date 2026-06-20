# Scenario: condominium-construction-dispute

A **Maine Condominium Act** dispute (Title 33, Chapter 31) that exercises the schema's
deep `litigation` section in a real-estate setting. A unit owners' association sues the
**declarant/developer** and its **general contractor** over construction defects in the
common elements, and in the same action **forecloses an assessment lien** against a
delinquent unit owner. The size and type of the condominium vary by seed (an 8-unit
conversion through a phased 110-unit community).

## Models

- **Practice area:** real_estate · **case_type:** `condominium` · **status:** `active`
- **Court:** Superior Court, random county · **docket prefix:** `CV`
- **Parties (4 + counsel):** `plaintiff` (the unit owners' association, an organization),
  `defendant` (the declarant/developer, an organization), `defendant_2` (the general
  contractor, an organization), and `other_party` (the delinquent unit owner, a person,
  named on the assessment-lien count). `client_role` is the association; an attorney is
  generated. Demonstrates a multi-party real-estate roster (three organizations plus an
  individual defendant) projecting through to the canonical case.
- **Dates:** `filing_date` in 2025; `event_date` is the `declarant_turnover_date`.

## Governing law (Maine Condominium Act)

The spotted issues are tied to the Condominium Act, using `§` citations:

- Association standing to sue for the unit owners — **33 M.R.S. § 1603-102(a)(4)**.
- Declarant tort and contract liability; litigation expenses and attorney fees —
  **33 M.R.S. § 1603-111**.
- Implied and express warranties against structural defects —
  **33 M.R.S. § 1604-113 and § 1604-114** (with disclaimer under § 1604-115).
- Assessment lien — perfection by recording the declaration, the six-year enforcement
  limit, and reasonable attorney fees — **33 M.R.S. § 1603-116**.
- Declarant-control transition period and the fiduciary duties of a declarant-appointed
  board — **33 M.R.S. § 1603-103**.
- Whether an arbitration clause in the declaration compels arbitration.

## Litigation depth (`litigation` block)

- **5 ordered causes of action** (sequential counts): breach of declarant warranties
  (association v. declarant), negligence (association v. contractor), breach of fiduciary
  duty by the declarant-controlled board (association v. declarant), breach of contract
  (association v. declarant), and foreclosure of the assessment lien (association v. the
  delinquent unit owner), each with elements, relief, and a strength.
- **3–5 affirmative defenses** (normal wear/maintenance, limitations/repose, valid
  warranty disclaimer, failure to fund reserves, lien time-barred/improperly levied) and
  **1 cross-claim** (declarant v. contractor for indemnity).
- **4–6 discovery items** (interrogatories, RFPs for construction records and financials,
  depositions of the declarant's principal / the contractor / the management company,
  an independent building inspection and testing, and a subpoena to the insurer).
- **3–5 motions** (compel arbitration, summary judgment on the lien, representative
  treatment, appoint a receiver for reserves, in limine on a defect expert) with
  dispositions.
- A chronologically-ordered **docket** of 7 entries (non-overlapping date windows
  guarantee order), plus **trial** info (jury, estimated days, scheduled date) and
  `posture: discovery`.
- **2–4 experts** (building-envelope architect, structural engineer, reserve-study
  analyst, condominium-governance/turnover expert; a defense cost estimator) retained by
  different sides.

## Third parties

3–5 of: the condominium property management company, the declarant's construction lender,
the association's building-envelope consultant, the developer's liability insurer, the
Municipal Building Department, and the delinquent unit owner's mortgage lender.

## Downstream target

[`maine-court-forms`](https://github.com/bedardandy/maine-court-forms) (civil filings),
example forms `CV-001` and `CV-067`.

## Notes

The litigation sub-lists that should vary by seed (defenses, discovery, motions) use the
DSL `pick_n`/`n` sampler; the ordered/numbered lists (causes of action, docket) and the
single cross-claim are fixed plain lists so count numbering and chronology stay coherent.
The `warranty_claim` and `arbitration_clause_in_declaration` facts are booleans, so they
are never referenced via a `_lower` form (only string facts get one).

## Validate

```
python3 tools/generate.py condominium-construction-dispute --seed 1
python3 tools/smoke.py --scenarios condominium-construction-dispute --count 8 -v
```
