# Scenario: residential-purchase-sale

A full **single-family purchase-and-sale closing binder**: a term-sheet's worth of PSA
economics plus the broker/lender/attorney **correspondence thread** that builds the file.
Part of the real-estate & asset-sale closing suite.

## Models

- Practice area: real_estate · transactional (`assign_docket: false`)
- Parties: `seller` (grantor) and `buyer` (grantee, the client)
- Rich `facts` fill a residential PSA / term sheet: price, earnest money, effective date,
  inspection/title/financing contingency deadlines, closing date, financing terms
  (`loan_amount`, `interest_rate`, `down_payment`), fixtures included/excluded, inspection
  findings and the repair/credit request, commission, and `deed_type`.
- `communications`: a six-message thread — offer → acceptance → inspection objection →
  title review → loan commitment → closing confirmation — date-sorted and name-consistent.

## Key issues

Inspection contingency and repairs, marketable/insurable title (`33 M.R.S. § 351`),
satisfaction of the financing contingency, transfer-tax calculation (`36 M.R.S. § 4641-A`),
and earnest-money escrow on default.

## Try it

```bash
python tools/generate.py residential-purchase-sale --seed 1
python tools/smoke.py --scenarios residential-purchase-sale -v
```
