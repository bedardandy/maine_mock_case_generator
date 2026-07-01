# Scenario: business-asset-sale

Sale of an **operating business as an asset purchase (APA)**: purchase-price allocation
(Form 8594), a **working-capital adjustment**, escrow/holdback and earnout, seller
financing, a non-compete, and the buyer's **accounting and financing due-diligence
questions**. Part of the real-estate & asset-sale closing suite.

## Models

- Practice area: business · transactional (`assign_docket: false`)
- Parties: `seller`/owner and `buyer` (asset acquirer, the client); the acquisition vehicle
  is a `new_entity_name` fact.
- Rich `facts`: business type and entity form, `annual_revenue`, `ebitda`,
  `ebitda_multiple`, `addbacks`, `working_capital_target` and `wc_adjustment`,
  `escrow_holdback`, `earnout`, `seller_note`, `financing_type` / `loan_amount`,
  `allocation_basis` (IRC § 1060 / Form 8594), `key_assets`, `assumed_liabilities`,
  `lease_status`, and `noncompete`.
- `communications`: signed LOI → the CPA's **financial due-diligence request** (GL, AR/AP
  aging, revenue recognition, add-back support) → QoE findings & working-capital peg →
  lender credit questions → closing funds flow.

## Key issues

Purchase-price allocation and tax treatment (IRC § 1060 / Form 8594), the working-capital
adjustment, successor liability / tax clearance (`36 M.R.S. § 177`), non-compete
enforceability (`26 M.R.S. § 599-A`), and assignment/consent of contracts and leases.

## Downstream

Ties into [`transactional-tax-forms`](https://github.com/bedardandy/transactional-tax-forms)
(new-entity EIN via **IRS-SS-4** through the `tax` adapter).
