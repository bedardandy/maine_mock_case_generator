# Scenario: construction-loan-closing

An owner/borrower closing a **construction loan and a construction contract to build**: the
GMP/AIA contract, draw schedule and **retainage**, lender requirements (title date-downs,
lien waivers, inspections), bonding, and the lender/GC/architect correspondence. Part of the
real-estate & asset-sale closing suite.

## Models

- Practice area: real_estate · transactional (`assign_docket: false`)
- Parties: `borrower`/owner (the client) and `general_contractor`
- Rich `facts`: project type, `contract_form` (AIA A102/A101/design-build), GMP
  `contract_price`, `contingency_line`, `construction_loan_amount`, `ltc`, `interest_rate`,
  `loan_term_months`, `draw_schedule`, `retainage`, `lien_waiver_requirement`,
  `performance_bond`, `equity_required`, and the loan-closing / groundbreaking /
  substantial-completion dates.
- `communications`: loan commitment → draw & lien-waiver mechanics → loan closing &
  disbursement → architect's first-draw certification → substantial completion & retainage
  release.

## Key issues

Mechanic's-lien priority and waivers (`10 M.R.S. §§ 3251-3269`), GMP/contingency control
(AIA A102/A201), draw and retainage terms, performance/payment security, and the building
permit (`25 M.R.S. § 2357-A`).
