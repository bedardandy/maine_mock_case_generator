# Scenario: protection-from-abuse

A **Maine Protection From Abuse (PFA)** matter. The client (the **plaintiff**)
petitions the District Court for a protection order against the **defendant**.
All names, parties, and facts are **fictional** and generated deterministically
from a `(scenario_id, seed)` pair. The subject matter is treated factually and
non-graphically.

## At a glance

| Field | Value |
| --- | --- |
| `id` | `protection-from-abuse` |
| `practice_area` | `family` |
| `case_type` | `protection_from_abuse` |
| `status` | `pre_filing` |
| `docket_prefix` | `PA` (e.g. `CUM-PA-2025-570`) |
| Jurisdiction | ME, Cumberland County, District Court |
| Downstream repo | `maine-court-forms` |
| Example forms | `PA-001`, `PA-003`, `FM-040` |

## Parties

- **plaintiff** — "Plaintiff (person seeking protection)". This is the
  `client_role`; the plaintiff becomes the signing filer (`party`) in the
  projected canonical case.
- **defendant** — "Defendant (person to be restrained)".
- **attorney** — counsel for the plaintiff (always generated).
- **children** — `0` to `2` minor children (`child_1`, `child_2`) who may need
  protection or temporary parental rights. Because the minimum is `0`, many
  seeds produce no children; templates use `{num_children_words}` and the
  children-related relief is phrased to hold whether or not children exist.

## Randomized facts (DSL knobs)

These resolve **after** the parties, so they may reference party names. The
`event_date` is bound to `most_recent_incident_date`.

| Fact key | Resolution |
| --- | --- |
| `relationship` | one of: current spouse, former spouse, dating partner, former dating partner, household member |
| `most_recent_incident_date` | random date in `2026-01-01 .. 2026-06-01` (also exposed as `event_date`) |
| `incident_location` | the shared residence / the plaintiff's workplace / a public parking lot |
| `prior_incidents` | random integer `1 .. 8` |
| `firearms_present` | `true` / `false` (used as a structured fact only; never rendered into prose) |
| `requested_relief` | no-contact + stay-away (optionally + temporary parental rights, or + exclusive use of the residence) |
| `police_called` | `true` / `false` |

`filing_date` is a random date in `2025-09-01 .. 2026-06-01`.

> Note: `firearms_present` and `police_called` are booleans. They are surfaced
> in the structured `facts` object (and the firearms/safety issues and
> interview) but are intentionally **not** interpolated into narrative strings,
> so no `True`/`False` ever leaks into human-readable text.

## Third parties

Pool of four, `1 .. 3` selected per matter:

- Responding police officer (`witness`)
- Neighbor who witnessed an incident (`neighbor`)
- Domestic-violence advocate (`healthcare_provider`) — safety planning / resources
- Plaintiff's employer (`employer`)

Person/organization names and contacts are filled by the generator; no
fictional names are hardcoded in the YAML.

## Issues and governing law

Pool of five, `3 .. 5` selected per matter, each tied to a § citation:

- Relief available — **19-A M.R.S. § 4007**
- Temporary orders — **19-A M.R.S. § 4006**
- Commencement / standing — **19-A M.R.S. § 4005**
- Firearms prohibition / surrender — **19-A M.R.S. § 4007(1)(A-1)**
- Violation / enforcement — **19-A M.R.S. § 4011**

## Experts

`0 .. 1` selected. Pool of one: a **domestic violence dynamics** expert
(field "Domestic violence dynamics"), retained by the plaintiff.

## Evidence

Pool of six, `3 .. 6` selected per matter: police incident report
(`public_record`), photographs of injuries/property damage (`photo`),
threatening text messages (`correspondence`), an emergency department medical
record (`medical_record`), a witness statement affidavit (`affidavit`), and a
prior protection order if any (`public_record`).

## Interview & objectives

The intake interview runs five exchanges — immediate safety, the most recent
incident (kept general), children, firearms, and the relief sought. Client
objectives center on safety and no contact, protection for the children, and
(where applicable) staying in the home, with `risk_tolerance: low`.

Financials are intentionally **omitted** for this scenario; monetary figures
are not relevant to a protection order.

## Generate & validate

```sh
# Emit one matter (validates against catalog/mock_matter.schema.json)
python3 tools/generate.py protection-from-abuse --seed 1

# Emit the projected canonical case instead
python3 tools/generate.py protection-from-abuse --seed 1 --canonical

# End-to-end smoke test (generate -> validate -> placeholder check -> project -> validate)
python3 tools/smoke.py --scenarios protection-from-abuse --count 6 -v
```

Smoke must report **PASS** with **0 failures**.
