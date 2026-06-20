# Scenario: commercial-contract-dispute

A **breach-of-commercial-contract** action in Maine Superior Court. A distributor/buyer
sues its supplier over a failed supply/distribution agreement and, in a separate count,
goes after the supplier's owner personally on a signed guaranty. The supplier denies the
breach and counterclaims. The matter is in active, contested discovery.

## Models

- **Practice area:** civil · **case_type:** `contract` · **status:** `active` · **docket prefix:** `CV`
- **Court:** Superior Court, random county
- **Parties (3 + counsel):** `plaintiff` (the distributor/buyer, an organization),
  `defendant` (the supplier/manufacturer, an organization), and `defendant_2` (the
  supplier's owner who signed a **personal guaranty**, a person). `client_role: plaintiff`.
  The guaranty count runs against `defendant_2` while the contract, warranty, and
  account-stated counts run against the corporate `defendant`.

## Facts

The executed agreement (`contract_type`, `goods`, `contract_date`, `contract_value`), the
breakdown (`breach_type`, `breach_date`, `amount_owed`), the `notice_of_default_date`,
`guaranty_signed`, and `cure_period_expired`. `event_date` is the `breach_date`.

## Litigation depth (`litigation` block)

- **4 causes of action** (ordered, sequential counts): breach of contract, breach of the
  implied warranties of merchantability and fitness, account stated, and enforcement of
  the personal guaranty — each with elements, relief, and a strength.
- **3–5 affirmative defenses** (failure of conditions precedent, accord and satisfaction,
  setoff/recoupment, statute of limitations, failure to mitigate, the goods conformed) and
  **2 counterclaims** (breach by the plaintiff / wrongful rejection).
- **4–6 discovery items** (interrogatories, RFPs, depositions of the owner, the account
  manager, and the plaintiff's principal, RFAs, a subpoena to the bank) with status, and
  **3–5 motions** with dispositions (incl. partial summary judgment on the guaranty and a
  motion in limine on the damages model).
- A chronologically-ordered **docket** (non-overlapping date windows guarantee order) plus
  **trial** info (jury, estimated days, scheduled date) and `posture: discovery`.

## Governing law (issues)

Common-law breach; implied warranties of merchantability and fitness (11 M.R.S. § 2-314,
§ 2-315); the UCC four-year statute of limitations (11 M.R.S. § 2-725); account stated;
enforcement of the personal guaranty (suretyship); cover/mitigation damages
(11 M.R.S. § 2-712); and prejudgment interest (14 M.R.S. § 1602-B). 3–5 issues are sampled.

## Supporting sections

- **1–3 experts:** a forensic accountant on damages/lost profits and an industry/trade-usage
  expert (both plaintiff), plus a goods-quality/engineering expert (defendant).
- **5–8 evidence items:** the executed contract and guaranty, the unpaid invoices and
  ledger, the notice of default, email negotiations and order confirmations, proof of cover
  purchases, inspection/rejection records, and the defendant's financials.
- **3–5 financials:** contract value, amount owed/claimed, cover/lost-profit damages,
  prejudgment interest, and attorney fees.
- **3–5 third parties:** the plaintiff's commercial bank, the defendant's account manager,
  a substitute supplier used in mitigation, a freight/logistics company, and a former
  employee of the defendant with knowledge of the contract.

## Downstream target

[`maine-court-forms`](https://github.com/bedardandy/maine-court-forms) (civil filings),
example forms **CV-001** and **CV-067**.

## Notes

The litigation sub-lists that should vary by seed (defenses, discovery, motions) use the
DSL `pick_n`/`n` sampler; the ordered/numbered lists (causes of action, docket) are fixed
so count numbering and chronology stay coherent.
