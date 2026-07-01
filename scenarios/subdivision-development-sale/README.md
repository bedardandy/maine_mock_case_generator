# Scenario: subdivision-development-sale

A developer's acquisition of **raw land for a residential subdivision**: entitlement/approval
contingencies (planning board, Maine DEP stormwater / Site Law / NRPA), phased lot
takedowns, offsite improvements and **performance bonding**, and the approvals
correspondence. Part of the real-estate & asset-sale closing suite.

## Models

- Practice area: real_estate · transactional (`assign_docket: false`)
- Parties: `seller`/landowner (grantor) and `buyer`/developer (grantee, the client)
- Rich `facts`: parcel acres, planned lots, zoning, `approval_type`, price and
  `price_basis` (fixed, per-lot, or base-plus-bonus), `takedown_structure`,
  `offsite_improvements`, `dep_permit`, `wetlands`, `performance_security`, `road_standard`,
  and the approval-contingency deadline.
- `communications`: PSA + approval-contingency hand-off → engineer's yield/constraints note
  → planning-board conditional approval → DEP permit decision → closing & plat recording.

## Key issues

Subdivision review standards (`30-A M.R.S. § 4403`), environmental permitting / NRPA
(`38 M.R.S. §§ 480-A–490`), improvement guarantees (`30-A M.R.S. § 4404`), the entitlement
contingency, and transfer tax (`36 M.R.S. § 4641-A`).
