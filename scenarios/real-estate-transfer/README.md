# Scenario: real-estate-transfer

A residential real-estate **closing** that drives the Maine **Real Estate Transfer Tax
Declaration (ME-RETTD)**. Introduces the `real_estate` practice area and a **third fact-key
namespace** (`property` / `transferor` / `transferee`).

## Models

- Practice area: real_estate · transactional (`assign_docket: false`)
- Parties: `transferor` (seller/grantor) and `transferee` (buyer/grantee, the client)
- Facts carry the RETTD fields by name: `property_address`, `property_town`,
  `property_county`, `property_map_block_lot`, `purchase_price`, `transfer_date`,
  `property_type`, `adjusted_assessed_value`, `special_circumstances_explanation`.

## Downstream + adapter

[`transactional-tax-forms`](https://github.com/bedardandy/transactional-tax-forms) →
**ME-RETTD**. Because ME-RETTD uses `property`/`transferor`/`transferee` rather than the
canonical namespace, the fill goes through `generator/adapters.py::to_real_estate_case`.
The fill reaches **100% coverage** of the form's mapped fields.

## Key issues

Transfer tax calculation (`36 M.R.S. § 4641-A`), exemptions (`36 M.R.S. § 4641-C`),
marketable title (`33 M.R.S. § 351`), and recording (`33 M.R.S. § 651`).
