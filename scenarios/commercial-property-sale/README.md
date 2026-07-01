# Scenario: commercial-property-sale

An **income-property commercial closing**: LOI/term-sheet economics (price, cap rate, NOI),
institutional **due diligence** (Phase I ESA, tenant estoppels, SNDAs, ALTA survey, rent
roll), commercial **financing** (LTV/DSCR), and the deal correspondence. Part of the
real-estate & asset-sale closing suite.

## Models

- Practice area: real_estate · transactional (`assign_docket: false`)
- Parties: `seller` (grantor) and `buyer`/principal (grantee, the client); the acquisition
  entity is carried as a `buyer_entity` fact (e.g. an LLC/LP).
- Rich `facts`: building SF, occupancy, tenant count, anchor tenant, `annual_noi`,
  `cap_rate`, price, deposit, due-diligence/financing/closing dates, `financing_type`,
  `ltv`, `dscr_required`, the Phase I `environmental_finding`, and `estoppel_status`.
- `communications`: signed-LOI hand-off → diligence request list → Phase I results →
  estoppel/CAM issue → loan commitment (DSCR) → closing statement.

## Key issues

Environmental liability / BFPP defense (`42 U.S.C. § 9601`; `38 M.R.S. § 343-E`), tenant
estoppels and lease compliance, title/survey and endorsements (`33 M.R.S. § 351`),
DSCR-based financing contingency, and transfer tax (`36 M.R.S. § 4641-A`).
