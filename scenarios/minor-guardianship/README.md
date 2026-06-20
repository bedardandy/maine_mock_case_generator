# Scenario: minor-guardianship

A **Maine probate** matter: a **petition for appointment of a guardian of a
minor**. The client (the **petitioner**) is a relative — often a grandparent —
seeking guardianship of a minor child whose parent or parents are **temporarily
unable** to provide care. The minor ward(s) are modeled as the children
(`child_1`, `child_2`). All names, parties, and facts are **fictional** and
generated deterministically from a `(scenario_id, seed)` pair. The subject
matter is treated sensitively and non-graphically.

## At a glance

| Field | Value |
| --- | --- |
| `id` | `minor-guardianship` |
| `practice_area` | `probate` |
| `case_type` | `guardianship` |
| `status` | `pre_filing` |
| `docket_prefix` | `GC` (e.g. `AND-GC-2026-526`) |
| Jurisdiction | ME, **random county**, Probate Court |
| Downstream repo | `maine-probate-forms` |
| Example forms | `GS-008`, `GS-014`, `PP-107` |

## Parties

- **petitioner** — "Petitioner (proposed guardian)". This is the `client_role`;
  the petitioner becomes the signing filer (`party`) in the projected canonical
  case.
- **respondent** — "Respondent parent". One parent named as the
  respondent/interested party.
- **attorney** — counsel for the petitioner (always generated).
- **children** — `1` to `2` minor children (`child_1`, `child_2`). These are the
  **minor ward(s)** the guardianship concerns. Templates use
  `{num_children_words}` and `{children_names}` and are phrased "child(ren)" so
  they read correctly for one or two wards.

## Randomized facts (DSL knobs)

These resolve **after** the parties, so they may reference party names. No
`event_date` is set for this scenario.

| Fact key | Resolution |
| --- | --- |
| `petitioner_relationship` | maternal grandmother / paternal grandfather / maternal grandparent / aunt / uncle / adult sibling |
| `reason_for_guardianship` | a parent's serious illness and hospitalization / substance use treatment / incarceration / both parents unavailable / military deployment |
| `parental_consent` | `true` / `false` (structured fact only; never rendered into prose) |
| `guardianship_type` | full guardianship of a minor / temporary guardianship |
| `current_living_arrangement` | the child already lives with the petitioner / the child splits time between relatives |
| `duration` | until the minor reaches 18 or further court order / for a temporary period subject to review |
| `minor_count` | mirrors `{num_children}` |

`filing_date` is a random date in `2025-10-01 .. 2026-06-01`.

> Note: `parental_consent` is a boolean. It drives the consent-versus-objection
> issue and is surfaced in the structured `facts` object, but it is
> intentionally **not** interpolated into any narrative string, so no
> `True`/`False` ever leaks into human-readable text. The consent question is
> instead handled neutrally in prose ("whether the parents consent or object").

## Third parties

Pool of five, `2 .. 4` selected per matter:

- Biological mother (`family_member`) — parental rights, consent/notice
- Biological father (`family_member`) — parental rights, consent/notice
- DHHS caseworker (`government_agency`) — named **Maine Department of Health and
  Human Services**
- Child's school counselor (`witness`) — stability and adjustment at school
- Child's pediatrician (`healthcare_provider`) — ongoing medical needs

Person/organization names and contacts are filled by the generator; no
fictional person names are hardcoded in the YAML (the DHHS agency uses an
explicit `name`).

## Issues and governing law

Pool of five, `3 .. 5` selected per matter, each tied to a § citation in the
**Maine Probate Code, Title 18-C**:

- Statutory basis for appointment — **18-C M.R.S. § 5-204**
- Parental consent vs. clear-and-convincing showing — **18-C M.R.S. § 5-204(2)**
- Notice to parents and interested persons — **18-C M.R.S. § 5-205**
- Hearing and required findings — **18-C M.R.S. § 5-207**
- Best interests of the child — **18-C M.R.S. § 5-204**

## Experts

`0 .. 1` selected. Pool of one: a **child psychology / best interests** expert
(field "Child psychology / best interests", `Ph.D.`), retained by the **court**.

## Evidence

Pool of six, `3 .. 6` selected per matter: the minor's certified birth
certificate (`public_record`), a signed parental consent/affidavit
(`affidavit`), the child's school records (`document`), the child's medical
records (`medical_record`), the proposed guardian's background-check results
(`document`), and a statement of the proposed guardian's home and resources
(`affidavit`).

## Interview & objectives

The intake interview runs five exchanges — the petitioner's relationship to the
child, why guardianship is needed now, where the parents stand (consent or
objection), the child's current situation, and the specific authority the client
needs (school and medical decisions). Client objectives center on obtaining
legal authority over school and medical decisions, providing a stable home, and
minimizing disruption to the child, with `risk_tolerance: low` and a non-starter
of any arrangement that endangers the child.

## Financials

Pool of three, `1 .. 3` selected per matter (`total_is_sum: false`): the child's
estimated monthly expenses, any survivor/Social Security benefits received for
the child, and the proposed guardian's monthly household income.

## Generate & validate

```sh
# Emit one matter (validates against catalog/mock_matter.schema.json)
python3 tools/generate.py minor-guardianship --seed 1

# Emit the projected canonical case instead
python3 tools/generate.py minor-guardianship --seed 1 --canonical

# End-to-end smoke test (generate -> validate -> placeholder check -> project -> validate)
python3 tools/smoke.py --scenarios minor-guardianship --count 6 -v
```

Smoke must report **PASS** with **0 failures**.
