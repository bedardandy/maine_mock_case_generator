# Scenario: edge-unicode-names

**Edge-case pack — character-set stress.** A plain UCC firewood-contract dispute whose
cast is deliberately hostile to naive document automation.

## What it smoke-tests downstream

- **Diacritics** in person and organization names (`José-María`, `Düböis`, `Ändersson`,
  `Sønsteby`) — catches ASCII-folding, mojibake, and encoding round-trip bugs.
- **Apostrophes and hyphens** in a compound surname (`O'Callaghan-Núñez`) — catches
  quote-escaping failures and name-splitting on the wrong delimiter.
- **A generational suffix** (`Jr.`) — catches first/last-name parsers that drop or
  misplace suffixes.
- **Commas and an ampersand in an organization name** — catches CSV-ish serializers and
  XML/HTML escaping (`&`).
- **Curly quotes and em dashes in free text** (“force majeure”) — catches smart-quote
  normalization and PDF font/subsetting gaps.
- **An address with a unit designator** (`Unit 4-B`, `Suite 300`) and a street name with
  an apostrophe (`Rue de l'Église`).

## Models

- Practice area: civil (Superior Court, Aroostook), plaintiff is the client.
- Parties are **authored** via `parties.roles[].party` so the tricky values are exact and
  stable across seeds; amounts and dates still vary by seed.
- `demand_letter_date` is computed with `date_offset` (21 days after the delivery
  deadline).
