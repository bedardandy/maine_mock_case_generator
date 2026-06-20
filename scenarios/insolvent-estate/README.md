# Scenario: insolvent-estate (edge case)

A probate **edge case**: the decedent's debts exceed the estate's assets. The asset and
claim ranges never overlap, so the estate is **always insolvent** regardless of seed —
making this a reliable fixture for testing claim-priority and allowance logic.

## Stresses

- **Order of priority** of claims against an insolvent estate (`18-C M.R.S. § 3-805`).
- **Family, homestead, and exempt-property allowances** versus general creditors
  (`18-C M.R.S. §§ 2-401–2-404`).
- **Abatement** of devises when assets are insufficient (`18-C M.R.S. § 3-902`).
- **Personal representative liability** for improper / out-of-order distribution
  (`18-C M.R.S. § 3-807`).

## Models

- Practice area: probate · Probate Court · the personal representative is the client.
- Competing creditors (hospital, mortgage lender, credit card, funeral home, taxing
  authority) and allowance-claiming family members appear as third parties.
- `facts.total_allowed_claims` always exceeds `facts.total_probate_assets`; financials
  spell out the deficit.

## Downstream

[`maine-probate-forms`](https://github.com/bedardandy/maine-probate-forms). Also a natural
companion to the `death-cascade` compound.
