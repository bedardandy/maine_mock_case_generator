# Scenario: residential-foreclosure

A **defended judicial foreclosure of an owner-occupied Maine home** — one of the most
document-heavy matters a small firm handles, modeled end to end: default, the statutory
cure notice, suit, the Foreclosure Diversion Program, and a loss-mitigation resolution
taking shape.

## Models

- Practice area: real_estate (District Court, random county); the **borrower/homeowner is
  the client** (foreclosure defense posture); lender is a generated organization;
  co-borrower spouse included.
- **Computed statutory clock** (via `date_offset`, always internally consistent): missed
  payment → § 6111 notice of right to cure → exactly **35 days** to cure → complaint
  filed 20–45 days later → FDP mediation sessions.
- Rich `facts`: loan origination/terms, arrearage vs. reinstatement vs. principal
  balance, escrow shortage, a servicing-ledger dispute (suspense postings, force-placed
  insurance, or escrow re-analysis), servicing-transfer history, property value, current
  income, and the modification offer on the table.
- `litigation`: foreclosure + note counts with the **Greenleaf** elements, borrower
  affirmative defenses (§ 6111 defect, standing, misapplication, dual-tracking, FHA
  face-to-face), discovery aimed at the collateral file, motions, and a docket.
- `communications` (6 messages): § 6111 cure notice → hardship letter → defense counsel's
  RESPA error-resolution letter → FDP scheduling notice → servicer's modification offer →
  counsel's advice memo on the offer.

## Key issues

Notice of right to cure (`14 M.R.S. § 6111`), proof of ownership of note and mortgage
(*Bank of America, N.A. v. Greenleaf*, 2014 ME 89; `14 M.R.S. § 6321`), RESPA error
resolution (`12 C.F.R. § 1024.35`), good-faith mediation (`14 M.R.S. § 6321-A`; M.R. Civ.
P. 93), loss-mitigation terms, and deficiency exposure (`14 M.R.S. § 6324`).
