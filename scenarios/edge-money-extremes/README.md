# Scenario: edge-money-extremes

**Edge-case pack — currency and magnitude stress.** A retainage/prompt-payment dispute
whose ledger contains every classic money-handling trap at once.

## What it smoke-tests downstream

- **Nine figures with cents** (`123456789.10`) — catches eight-digit field widths,
  thousands-separator formatting, and float→string precision loss (`123456789.09999`).
- **A negative amount** (`-2500.75`, an owner setoff) — catches unsigned currency
  formatting and parenthesized-negative conventions.
- **A zero-dollar line** (`0`) — catches "falsy means missing" bugs that blank out a real
  line item.
- **A half-cent amount** (`1234.565`) — catches banker's-rounding vs. round-half-up
  differences; `total_is_sum: true` makes the engine commit to a rounded total.
- **A one-cent value** (`0.01`) — catches minimum-amount validation and integer-cents
  conversion.
- All extreme amounts are **pinned literals**, so downstream assertions can be exact.

## Models

- Practice area: business (Business and Consumer Docket, Cumberland); the prime
  contractor (organization) is the client.
- Both parties are authored organizations; issue/evidence sampling still varies by seed.
