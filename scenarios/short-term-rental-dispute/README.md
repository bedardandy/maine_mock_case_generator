# Scenario: short-term-rental-dispute

A **timely Maine short-term-rental (Airbnb/VRBO) dispute** that exercises the schema's
`litigation` section in an active real-property case. A condominium / homeowners'
association sues a unit owner and the co-owner/manager who run a transient rental,
seeking to **enforce a recorded no-short-term-rental restriction**, **abate a private
nuisance**, and obtain **declaratory and injunctive relief** — all while the **town's STR
ordinance and zoning** are in play. The matter is multi-pronged: covenant enforcement +
private nuisance + municipal land use.

## Models

- **Practice area:** civil · **case_type:** `real_property` · **status:** `active`
- **Court:** Superior Court, random county
- **Parties (4 + counsel):** `plaintiff` (the association, an organization),
  `defendant` (the unit owner / STR operator), `defendant_2` (the co-owner / property
  manager), and `other_party` (the municipality, a fixed-name organization,
  `Town of Harborwick`) joined because of the STR ordinance / zoning. The client is the
  association; an attorney is generated.

## Fact spine

Seed-varied facts drive the story: the `property_setting` (oceanfront condo, HOA
neighborhood, downtown conversion, lakeside cottages), the `platform` (Airbnb, VRBO, or
both), the `str_start_date` (which also feeds `event_date`), the
`declaration_restriction` at issue, a `pick_n` set of 2–4 `nuisance_complaints`, the
`nightly_rate` and `annual_str_revenue`, the `town_str_ordinance` posture, and the
boolean flags `cease_and_desist_sent` / `permit_appeal_pending`. The two booleans are
non-string facts, so they are never referenced as templates.

## Litigation depth (`litigation` block)

- **`posture: pleadings`** — an early-stage enforcement action.
- **4 ordered causes of action** (sequential counts): covenant enforcement against both
  owners, private nuisance, declaratory + injunctive relief, and enforcement of the
  association's assessment/fine lien.
- **3–5 affirmative defenses** (covenant does not clearly bar STRs, permitted residential
  use, selective/waived enforcement, the town ordinance permits the rental, no actionable
  nuisance) and **1 operator counterclaim** for a declaratory judgment that STRs are
  allowed.
- **2–4 motions** (preliminary injunction, summary judgment on the covenant's meaning,
  consolidation with the Rule 80B permit appeal, motion to compel platform booking
  records).
- A chronologically-ordered **docket** (non-overlapping date windows guarantee order),
  plus **trial** info (jury, 2–6 estimated days, scheduled date).
- **0–2 experts** (a land-use planner retained by the town, a real-estate appraiser and
  an acoustical/noise expert retained by the association).

## Governing law

The issues cite, with `§` symbols: the recorded restrictive covenant and the Maine
Condominium Act enforcement and lien powers (**33 M.R.S. § 1603-102** and **§ 1603-116**),
private nuisance at common law, the municipal STR ordinance and zoning
(**30-A M.R.S. § 4352**), the Rule 80B permit appeal (**30-A M.R.S. § 2691**;
**M.R. Civ. P. 80B**), and injunctive relief and attorney fees
(**14 M.R.S. § 6051**; **§ 5953**).

## Third parties

Drawn from a pool of 6 (3–5 chosen): a complaining neighboring owner (person), the town
code enforcement office, the property-management/cleaning company servicing the rental,
the booking platform (`Airbnb, Inc.`), the association's property manager, and the local
police (`Harborwick Police Department`). Government agencies and the platform carry
explicit names; person/organization roles draw fictional names from the pools.

## Downstream target

[`maine-court-forms`](https://github.com/bedardandy/maine-court-forms) (civil filings;
example forms `CV-001`, `CV-067`).

## Notes

The litigation sub-lists that should vary by seed (affirmative defenses, motions) use the
DSL `pick_n`/`n` sampler; the ordered/numbered lists (causes of action, docket) are plain
lists so count numbering and chronology stay coherent. `nuisance_complaints` is sampled
with `pick_n`, so it resolves to a list and is never referenced as a `{...}` template (the
narrative describes the disturbances generically instead).

## Validate

```
python3 tools/generate.py short-term-rental-dispute --seed 1
python3 tools/smoke.py --scenarios short-term-rental-dispute --count 8 -v
```
