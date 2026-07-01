# Scenario: edge-boundary-dates

**Edge-case pack — calendar-boundary stress.** A pedestrian-collision suit built entirely
out of dates that break naive date handling.

## What it smoke-tests downstream

- **Leap-day event date** (`2024-02-29`) — catches parsers and formatters that reject or
  shift February 29.
- **Leap-day date of birth in 1926** — catches two-digit-year windowing (26 → 2026?) and
  age computation for a centenarian whose birthday exists only every four years.
- **Limitations arithmetic into a non-leap year** — six years from 2024-02-29 lands in
  2030, which has no February 29 (`sol_expiration_date: 2030-02-28`); catches date-math
  libraries that throw or silently roll to March 1.
- **Year-boundary filing date** (`2026-01-01`) — catches fiscal/calendar-year bucketing
  and off-by-one year extraction.
- **Two timeline events on the same date** — catches unstable same-day sort orders.
- **A near-midnight time string** (`23:58`) kept in a fact — catches timezone-naive
  datetime promotion that could flip the calendar day.

## Models

- Practice area: civil (Superior Court, Penobscot); plaintiff (authored, leap-day DOB) is
  the client; defendant is generated per seed.
- Damages amounts vary by seed; every date above is pinned.
