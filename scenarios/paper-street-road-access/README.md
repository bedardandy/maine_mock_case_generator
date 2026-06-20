# Scenario: paper-street-road-access

A **Maine real-property dispute over a "paper street"** -- a way drawn on an old
subdivision plat but never built -- and the **cost-sharing fight in the private road
association** that maintains the actual access road. A developer claims the long-vacated
paper street as access to a landlocked **back lot** it wants to subdivide; a neighbor
**refuses to pay** his proportionate share of the road-maintenance assessments. The case
pairs the **Maine Paper Streets Law** with the **private way maintenance / cost-sharing
statute**, plus quiet title and declaratory relief over the status of the way and the
developer's claimed easement.

## Models

- **Practice area:** real_estate · **case_type:** `real_property` · **status:** `active`
- **Court:** Superior Court, random county · **docket prefix:** `RE`
- **Parties (4 + counsel):** `plaintiff` (lot owner and road-association officer, the
  client and signing filer via `client_role: plaintiff`), `defendant` (the neighbor who
  refuses to pay road maintenance), `defendant_2` (the **developer**, an
  `entity: organization`, who claims the paper street for back-lot access), and
  `other_party` (the **Town of Mooselook**, a named `organization` interested in the way's
  status). Demonstrates a mixed person/organization roster -- two organization parties,
  one with an explicit `name:` -- projecting through to the canonical case.

## Governing law

The issues are tied to the Maine paper-street and private-way statutes (`§` citations
throughout):

- **Paper Streets Law** -- a pre-1987 platted way is deemed vacated by the later of
  September 29, 1997 or 15 years after recording unless accepted -- 23 M.R.S. § 3032,
  and the related **rights of action / reservations** on vacation -- 23 M.R.S. § 3033.
- Whether lot owners retain **private access rights** (incipient dedication) over the
  paper street despite vacation of the public way -- 23 M.R.S. § 3032.
- **Private road association maintenance** and each owner's **fair and equitable
  proportionate share**, with a civil action and **attorney fees** for non-payment --
  23 M.R.S. § 3101.
- **Quiet title** -- 14 M.R.S. § 6651 -- and **declaratory judgment** -- 14 M.R.S.
  § 5951 et seq. -- as to the status of the way and the developer's claimed easement.

## Facts that vary by seed

The subdivision name, the year the plan was recorded (`plan_recorded_year`), the paper
street's name, the road association's name, the description of the actual access road,
the developer's back lot, and the developer's access theory all vary by seed, along with
integer figures for the annual maintenance cost and the neighbor's unpaid share. The
`deemed_vacated` fact is fixed (`{pick: [true]}`) because the whole theory of the case is
that the way was vacated.

`event_date` is the recording date of the plan, built as `"{plan_recorded_year}-06-15"`
-- a string that references a **fact** (`plan_recorded_year`). This is the one allowed
fact-in-a-date case: the engine resolves all facts before `event_date`, so the year is
already in context when the date string is formatted.

## Litigation depth (`litigation` block)

- **4 causes of action** (ordered, sequential counts): declaratory judgment that the
  paper street is vacated and the developer has no easement (against the developer and the
  Town); quiet title against the developer; collection of the unpaid road-maintenance
  assessment with attorney fees (against the neighbor); and an injunction barring the
  developer from opening the paper street.
- **2-4 affirmative defenses** sampled by seed (the plan reserved private access rights,
  an easement by implication/necessity, the assessment formula is not fair and equitable,
  laches/acquiescence).
- **One counterclaim** by the developer asserting an easement over the paper street to
  reach the back lot.
- **2-4 motions** sampled by seed (summary judgment on vacation of the way, a preliminary
  injunction, joinder of all lot owners as necessary parties, appointment of a referee on
  the assessment) with dispositions.
- A chronologically-ordered **docket** (6 entries; non-overlapping date windows guarantee
  order): complaint, the developer's answer and counterclaim, the neighbor's answer, the
  preliminary-injunction order, the scheduling order with the Town appearing, and the
  summary-judgment hearing.
- **trial** info (`jury: false`, estimated days, scheduled date) and `posture: pleadings`.
- **1-3 experts** (a title examiner/abstractor and a licensed surveyor retained by the
  plaintiff, and a civil engineer on road standards and feasibility retained by the
  developer, `defendant_2`).

## Third parties, evidence, financials

- **3-5 third parties** drawn from the town road commissioner (`Town Road Commissioner`),
  a title abstractor/examiner, another lot owner, the `County Registry of Deeds`, the
  original subdivider's heir, and a licensed surveyor.
- **4-7 evidence items**: the recorded subdivision plan/plat, the chain of deeds, the road
  association's bylaws and assessments, records of the unpaid share and demand letters, the
  developer's deed and access claim, a survey of the paper street and access road,
  photographs of the real road and the unbuilt paper street, and the town's records on
  acceptance of the way.
- **3-5 financials**: the annual maintenance cost, the neighbor's unpaid share plus
  attorney fees, the cost to bring the paper street to a buildable standard, the value
  impact of the access dispute, and survey/title-examination costs.

## Downstream target

[`maine-court-forms`](https://github.com/bedardandy/maine-court-forms) -- example forms
`CV-001` (civil complaint) and `RE-QT` (quiet title).

## Reproduce

```sh
python3 tools/generate.py paper-street-road-access --seed 1
python3 tools/smoke.py --scenarios paper-street-road-access --count 8 -v
```

## Notes

The litigation sub-lists that should vary by seed (affirmative defenses, motions) use the
DSL `pick_n`/`n` sampler; the ordered/numbered lists (causes of action, docket) are plain
lists so count numbering and chronology stay coherent. `deemed_vacated` is a boolean fact,
so it is never used with the `{..._lower}` string helper, and no fact references another
fact except `event_date`, which is intentionally derived from `plan_recorded_year` after
all facts resolve. The integer facts (`annual_maintenance_cost`, `defendant_unpaid_share`)
are referenced in the narrative and interview as plain `${...}` amounts, never lowercased.
