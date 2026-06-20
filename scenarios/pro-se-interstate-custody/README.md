# Scenario: pro-se-interstate-custody (edge case)

A family **edge case** on two axes: the client is **self-represented** (no attorney is
generated) and the matter turns on a **cross-border UCCJEA jurisdiction** question rather
than the merits.

## Stresses

- **No-counsel path:** `attorney: false`, so no attorney party exists. Exercises projection
  and form fills with an empty counsel block while still producing a valid signer
  (`party`). A good probe for downstream forms that assume an attorney is present.
- **UCCJEA jurisdiction** before the merits:
  - Home-state determination for initial jurisdiction (`19-A M.R.S. §§ 1745, 1748`).
  - Initial vs. modification jurisdiction (`§ 1751`).
  - Temporary emergency jurisdiction (`§ 1748(4)`).
  - Inconvenient forum / simultaneous proceedings (`§§ 1752, 1753`).
  - Registration and enforcement of an out-of-state order (`§ 1761`).

## Models

- Practice area: family · District Court · the in-Maine parent is the self-represented client.
- The other parent is in a different state; the child's home state is contested. Facts
  capture the relocation date, months in Maine, any existing order, and an emergency basis.

## Downstream

[`maine-court-forms`](https://github.com/bedardandy/maine-court-forms). The no-attorney
case is a deliberate coverage edge for the FM-004 fill.
