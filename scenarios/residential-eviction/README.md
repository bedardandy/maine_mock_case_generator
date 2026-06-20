# Scenario: residential-eviction

A residential **Forcible Entry and Detainer** (eviction) action — landlord versus tenant —
in the Maine District Court's summary-process track. Introduces the landlord-tenant domain
and a light `litigation` block (a writ-of-possession motion and tenant defenses).

## Models

- Practice area: civil · `case_type: forcible_entry_detainer` · the landlord is the client.
- Facts are emitted by the names **CV-007** expects (`premises_address`, `premises_city`,
  `months_in_arrears`, `notice_to_quit_date`, `other_eviction_basis`, `other_attachment`),
  giving a near-complete native fill (**~97% coverage**).
- A small `litigation` block carries the writ-of-possession motion and tenant affirmative
  defenses (habitability, defective notice, retaliation).

## Downstream

[`maine-court-forms`](https://github.com/bedardandy/maine-court-forms) → **CV-007**
(Complaint for Residential FED), with CV-100 / CV-195 as related forms.

## Key issues

Sufficiency of the notice to quit (`14 M.R.S. § 6002`), FED grounds and retaliation
(`14 M.R.S. § 6001`), implied warranty of habitability (`14 M.R.S. § 6021`), and the writ of
possession (`14 M.R.S. § 6005`).
