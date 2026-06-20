# Scenario: family-divorce-cumberland

A contested **divorce with minor children** in Cumberland County, Maine. This is the
flagship/gold-template scenario and exercises every section of the Mock Matter schema.

## Models

A plaintiff spouse petitions to divorce the defendant spouse, asking the court to resolve
parental rights and responsibilities for one to three minor children, child support,
division of marital property and debt, and (sometimes) spousal support.

- **Practice area:** family · **case_type:** `family_matters` · **status:** `pre_filing`
- **Jurisdiction:** Cumberland County District Court (Portland)
- **Parties:** `plaintiff` (filing spouse, the client), `defendant`, `attorney`,
  `child_1..N`
- **Signing filer (`party`):** the plaintiff

## Downstream target

[`maine-court-forms`](https://github.com/bedardandy/maine-court-forms) — representative
forms `FM-040` (divorce complaint), `FM-050` (family financial statement), `CV-001`.

## Key issues (with governing law)

- Parental rights and responsibilities — `19-A M.R.S. § 1653`
- Child support under the Maine guidelines — `19-A M.R.S. § 2006`
- Division of marital property and debt — `19-A M.R.S. § 953`
- Spousal support — `19-A M.R.S. § 951-A`
- Attorney fees — `19-A M.R.S. § 105`

## Canonical `facts` emitted

`marriage_date`, `marriage_place`, `separation_date`, `grounds`, `residency_months`,
`spousal_support_requested`, `marital_home`, `num_minor_children`,
`primary_residence_parent`. The number of children varies by seed (1–3) and drives
`child_1..N` plus the narrative.

## Notes

`matter.event_date` is bound to the separation date. Experts (custody evaluator,
forensic accountant, vocational analyst) and third parties (guardian ad litem, employer,
bank, family member, counselor) are sampled per seed, so volume sweeps produce varied
but always-valid matters.
