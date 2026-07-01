# Scenario: condo-unit-sale

A **resale of a condominium unit** under the Maine Condominium Act: the **resale
certificate**, association budget and assessments, a pending special assessment, master
insurance, lender condo-project eligibility, and the association/lender/attorney thread.
Part of the real-estate & asset-sale closing suite.

## Models

- Practice area: real_estate · transactional (`assign_docket: false`)
- Parties: `seller`/unit owner (grantor) and `buyer` (grantee, the client)
- Rich `facts`: unit number and type, SF, `ownership_percentage` (common-interest share),
  price, `monthly_assessment`, `reserve_balance`, `special_assessment`, `rofr`,
  `pet_rental_rules`, `insurance` (all-in vs. bare-walls), `financing_type`, and
  resale-certificate/inspection/closing deadlines.
- `communications`: request for the resale package → resale certificate delivery
  (disclosing the special assessment) → assessment-allocation demand → lender condo-project
  review → closing statement.

## Key issues

Resale-certificate disclosure (`33 M.R.S. § 1604-108`), special-assessment allocation
(`§ 1603-115`), association right of first refusal (`§ 1603-112`), lender condo eligibility,
and transfer tax (`36 M.R.S. § 4641-A`).
