# Scenario: intertidal-shoreland-access

A **uniquely-Maine coastal dispute over the intertidal zone** -- the **flats** that lie
between the high- and low-water marks. Under Maine's **colonial ordinance**, the upland
owner owns the flats seaward to the **low-water mark** (up to a 100-rod limit), subject
only to a narrow public easement reserved for **"fishing, fowling, and navigation."** A
shorefront owner sues to **stop others using the flats** -- commercial rockweed
harvesting, a kayak-tour landing, clam digging, public recreation, or a neighbor crossing
to launch a boat -- while the defendants assert **public, prescriptive, or customary
rights**. The case turns on whether the specific disputed use falls within that reserved
easement or is a **trespass to privately owned intertidal land**, and pairs declaratory
judgment and quiet title over ownership of the flats and the scope of the public's rights.

## Models

- **Practice area:** real_estate · **case_type:** `real_property` · **status:** `active`
- **Court:** Superior Court, random county · **docket prefix:** `RE`
- **Parties (4 + counsel):** `plaintiff` (the shorefront/upland owner, the client and
  signing filer via `client_role: plaintiff`), `defendant` (a **user of the flats** -- a
  harvester or tour operator), `defendant_2` (an **abutting owner** claiming a right of
  access over the flats), and `other_party` (the **Town of Semaphore Cove**, a named
  `entity: organization` standing in for the municipality / public interest). Demonstrates
  a mixed person/organization roster -- two named defendants plus one organization party
  with an explicit `name:` -- projecting through to the canonical case.

## Governing law

The issues are tied to Maine's intertidal-ownership and public-trust doctrine, with `§`
citations where statutory:

- **Colonial ordinance / intertidal ownership to the low-water mark** -- the upland owner
  owns the flats to the low-water mark, up to 100 rods, subject to the public's reserved
  easement -- **Bell v. Town of Wells** (the **Moody Beach** case).
- Whether the **specific disputed use** (commercial rockweed harvesting -- see **Ross v.
  Acadian Seaplants** -- or recreation) falls **within or outside** the reserved easement,
  which is limited to **fishing, fowling, and navigation**.
- **Prescriptive easement or customary public rights** -- 14 M.R.S. § 812.
- **Trespass** to the privately owned flats (common law).
- **Declaratory judgment** -- 14 M.R.S. § 5951 et seq. -- and **quiet title** --
  14 M.R.S. § 6651 -- as to ownership of the flats and the scope of public rights, against
  the backdrop of the **public trust doctrine's limits**.

## Facts that vary by seed

The kind of shorefront (`shorefront_type`), the **disputed use** (`disputed_use` --
rockweed harvesting, a tour landing, clam digging, public recreation, or a neighbor's
boat access), how far the deed reaches (`rods_to_low_water`), the theory of public use
(`public_use_claimed`), and the nearby conservation interest (`conservation_interest`)
all vary by seed, plus a `first_incident_date`. The `deed_to_low_water` fact is fixed
(`{pick: [true]}`) because the whole premise of the case is that the upland title reaches
the flats.

`event_date` is `"{first_incident_date}"` -- a quoted string referencing the
`first_incident_date` **fact**. This is the one allowed fact-in-a-date case: the engine
resolves all facts before `event_date`, so the date is already in context when the string
is formatted.

## Litigation depth (`litigation` block)

- **4 causes of action** (ordered, sequential counts): declaratory judgment that the
  plaintiff owns the flats to the low-water mark and the disputed use exceeds the public
  easement (against both defendants and the Town); trespass to the intertidal land
  (against the user `defendant`); quiet title against the abutter's claimed access
  (against `defendant_2`); and an injunction barring the disputed use (against the user).
- **2-4 affirmative defenses** sampled by seed (the use is protected fishing/fowling/
  navigation, a prescriptive or customary public right, the activity is below the
  low-water mark, the plaintiff's title does not reach the flats).
- **One counterclaim** by the user asserting a public/prescriptive right to use the flats.
- **2-4 motions** sampled by seed (a preliminary injunction, summary judgment on title,
  joinder of the State/Town as necessary parties, and a view of the property) with
  dispositions.
- A chronologically-ordered **docket** (6 entries; non-overlapping date windows guarantee
  order): complaint, the user's answer and counterclaim, the abutter's answer, the
  preliminary-injunction order, the scheduling order with the Town appearing, and the
  summary-judgment hearing.
- **trial** info (`jury: false`, estimated days, scheduled date) and `posture: pleadings`.
- **1-3 experts** (a coastal/marine-resources expert on the nature of the use retained by
  the `defendant`; a title expert on the colonial-ordinance chain and a surveyor mapping
  the high- and low-water marks retained by the `plaintiff`).

## Third parties, evidence, financials

- **3-5 third parties** drawn from a marine biologist / rockweed expert, the
  **Maine Department of Marine Resources** (a named `government_agency`), a local land
  trust, a longtime townsperson who has used the flats, a title abstractor, and the
  harbormaster.
- **4-7 evidence items**: the deed and chain of title to the low-water mark, a survey of
  the high/low-water lines and the 100-rod limit, photographs of the disputed activity,
  photographs of the posted no-trespassing signage, historical records of public use,
  cease-and-desist correspondence, and DMR licensing records for harvesting.
- **1-3 financials** (kept modest): the diminution in the property's value, the cost of
  survey and title work, and any claimed harvesting revenue at stake.

## Downstream target

[`maine-court-forms`](https://github.com/bedardandy/maine-court-forms) -- example forms
`CV-001` (civil complaint) and `RE-QT` (quiet title).

## Reproduce

```sh
python3 tools/generate.py intertidal-shoreland-access --seed 1
python3 tools/smoke.py --scenarios intertidal-shoreland-access --count 8 -v
```

## Notes

The litigation sub-lists that should vary by seed (affirmative defenses, motions) use the
DSL `pick_n`/`n` sampler; the ordered/numbered lists (causes of action, docket) are plain
lists so count numbering and chronology stay coherent. `deed_to_low_water`,
`signage_posted`, and `prior_confrontation` are **boolean** facts, so they are never used
with the `{..._lower}` string helper. No fact references another fact except `event_date`,
which is intentionally derived from `first_incident_date` after all facts resolve. The
`disputed_use` and other string facts are referenced directly in the narrative, interview,
and objectives so the dispute stays internally consistent across the matter.
