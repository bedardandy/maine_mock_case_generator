# Scenario: construction-defect

A **multi-party residential construction-defect suit** in Maine Superior Court. A
homeowner sues the **general contractor** over foundation and water-intrusion problems;
the contractor in turn **cross-claims against its excavation subcontractor** and
**impleads the design professional** (architect/engineer). The defects are traced to
improper excavation and uncompacted fill, deviation from the approved foundation plan,
or inadequate drainage design. Like `complex-civil-litigation`, this scenario exercises
the schema's deep `litigation` section end to end.

## Models

- **Practice area:** civil · **case_type:** `construction` · **status:** `active`
- **Court:** Superior Court, random county
- **Parties (4 + counsel):** `plaintiff` (homeowner), `defendant` (general contractor,
  an organization), `defendant_2` (excavation subcontractor, an organization),
  `third_party_defendant` (design professional, an organization). The homeowner is the
  represented `client`. Demonstrates a contractor-vs-subcontractor-vs-designer roster
  projecting through to the canonical case.
- **Downstream:** [`maine-court-forms`](https://github.com/bedardandy/maine-court-forms),
  example forms `CV-001`, `CV-067`.

## Facts

A homeowner contracts to build one of several project types (custom home, addition,
coastal home on ledge and fill, converted barn) for a contract price between roughly
$180k and $1.4M. After substantial completion, the owner discovers a primary defect
(basement water intrusion, foundation settlement, uncompacted fill, a failed footing
drain, or structural deficiencies) traced to a root cause in the sitework or design.
Facts also carry the repair-cost estimate, the discovery date, whether a mechanic's
lien was filed, and the warranty period. (Per the DSL, no fact references another fact.)

## Third parties (3–5)

Drawn from: the construction lender (bank), the municipal building inspector / code
office (`Town Code Enforcement Office`), the contractor's liability insurer, the surety
on the contractor's bond, a subsequent inspection company, and a neighbor whose property
floods from runoff. Insurers/inspection company use generated organization names; the
neighbor is a generated person.

## Litigation depth (`litigation` block)

- **5 causes of action** (ordered, sequentially numbered): breach of the construction
  contract, breach of the implied warranty of workmanlike construction, negligence
  (v. the GC), negligent excavation and fill compaction (v. the subcontractor), and
  enforcement/discharge of the mechanic's lien.
- **3–5 affirmative defenses** sampled from comparative fault, statute of repose, owner
  failure to maintain/grade, betterment, lack of notice/opportunity to cure, and code
  compliance.
- **1–2 cross-claims** (GC v. excavator and GC v. design professional for indemnity and
  contribution) and **1 third-party claim** (GC impleads the architect/engineer for
  contribution).
- **4–6 discovery items** (interrogatories, RFPs, depositions of the GC principal,
  excavator, and architect, destructive testing/site inspection, and a subpoena to the
  building inspector) and **3–5 motions** (compel destructive testing, summary judgment
  on the lien, consolidate, motion in limine on a defect expert, bifurcate liability and
  damages).
- A chronologically-ordered **docket** (7 entries; non-overlapping date windows guarantee
  order), plus **trial** info (jury, 6–15 estimated days, scheduled date) and
  `posture: discovery`.
- 2–4 dueling **experts**: a structural engineer, a geotechnical/soils engineer, and a
  cost estimator for the plaintiff, an architect (standard of care) for the third-party
  defendant, and a home inspector for the contractor.

## Governing law for issues (4–6)

Breach of the construction contract; breach of the implied warranty of workmanlike
construction/habitability; negligence; negligent excavation and fill compaction; the
mechanic's / materialman's lien (10 M.R.S. § 3251 et seq.); the limitation and statute
of repose for design/construction claims (14 M.R.S. § 752-A); and indemnity and
contribution among the defendants (14 M.R.S. § 156).

## Client objectives

Recover the full repair cost plus consequential damages (temporary housing, mold
remediation), allocate fault among the contractors, preserve the lien fight, and settle
through the contractors' insurers where possible.

## Notes

The litigation sub-lists that should vary by seed (affirmative defenses, discovery,
motions) use the DSL `pick_n`/`n` sampler; the ordered/numbered lists (causes of action,
docket) and the multi-party `cross_claims` / `third_party_claims` are plain lists so
count numbering and chronology stay coherent. Validated with `tools/generate.py
construction-defect --seed 1` and `tools/smoke.py --scenarios construction-defect
--count 8` (0 failures).
