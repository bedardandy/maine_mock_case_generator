# Scenario: edge-max-household

**Edge-case pack — length and cardinality stress.** A contested divorce with the maximum
six-child household and deliberately oversized strings.

## What it smoke-tests downstream

- **Very long names**: a 38-character triple-barrelled surname
  (`Featherstonehaugh-Cholmondeley-Smythe`) and 22-character hyphenated first names —
  catches fixed-width PDF caption fields, truncation, and layout overflow.
- **Six minor children** (`child_1`..`child_6`) — catches child tables and support
  worksheets that stop at three or four rows, and `num_children_words` pluralization.
- **A long multi-part address** (`1247 Passamaquoddy Narrows Road, Building 3,
  Apartment 12-B`) shared by both parties — catches address-line splitting and
  same-address dedup logic.
- **Long employer strings** in `facts` — catches financial-affidavit fields sized for
  short employer names.
- **Stepped incomes** (`int_between` with a step) — round figures that should format
  cleanly on a child support worksheet.

## Models

- Practice area: family (District Court, Washington County); petitioner is the client.
- Parents are **authored** (`parties.roles[].party`); the six children are generated per
  seed, so `children_names` still varies while the stress values stay pinned.
- Feeds the same FM-004 / FM-050 paths as `family-divorce-cumberland`, so a filler can be
  compared side-by-side on a normal and an extreme household.
