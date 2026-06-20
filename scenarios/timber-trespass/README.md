# Scenario: timber-trespass

A distinctively **Maine real-property** dispute: a landowner discovers that trees on
**a mature woodlot** were cut and hauled off across the boundary. The **neighbor** who
ordered the clearing and the **logging contractor** who did the cutting are both
defendants; the contractor claims the trees stood on the neighbor's side, weaving a
**boundary dispute / quiet-title** fight into a timber-trespass case. Maine's
timber-trespass statute, **14 M.R.S. § 7552**, allows enhanced (double, and up to
treble) damages, which drives the strongest claim and the valuation fight.

## Models

- **Practice area:** real_estate · **case_type:** `real_property` · **status:** `active`
- **Court:** Superior Court, random county · **docket prefix:** `RE`
- **Parties (3 + counsel):** `plaintiff` (the landowner whose trees were cut),
  `defendant` (the neighbor who ordered the clearing), `defendant_2`
  (the logging/forestry contractor, an **organization**). `client_role: plaintiff`.
- **Dates:** `filing_date` sampled in 2025–2026; `event_date` is the `cutting_date`
  fact (the harvest predates filing).

## Facts and third parties

- Facts cover the woodlot type, number of trees cut, stumpage value, restoration cost,
  and four booleans — `cutting_authorized` (always false), `intentional_or_knowing`
  (drives treble damages), `boundary_disputed`, and `survey_exists`. A
  `buffer_or_shoreland` string fact flags whether a shoreland buffer or conservation
  easement was crossed.
- **3–5 third parties** drawn from a pool: a licensed forester (expert) who appraised
  stumpage and damage, the timber buyer / sawmill (business entity) that took the logs,
  a licensed surveyor (expert), the **Town Code Enforcement Office** (government agency,
  explicit name) for any shoreland violation, an adjoining neighbor witness, and the
  **Maine Forest Service** (government agency, explicit name).

## Governing law (issues, citations use §)

- **14 M.R.S. § 7552** — timber trespass and **enhanced damages** (value of the trees
  plus double damages, up to treble for intentional/knowing cutting). This is the
  **strongest** issue.
- Common-law trespass to real property and conversion of the cut timber.
- **14 M.R.S. § 6651** — quiet title / boundary determination where the cutter claims
  the trees were on his land.
- Restoration-cost versus diminution-in-value measure of damages.
- **38 M.R.S. § 438-A** — shoreland-zoning buffer violation, where applicable.

## Litigation depth (`litigation` block)

- **Posture:** `pleadings`.
- **4 ordered causes of action** (sequential counts): § 7552 timber trespass with
  enhanced damages (vs. both defendants), common-law trespass (vs. the contractor),
  conversion (vs. the contractor and the sawmill), and quiet title / boundary
  determination (vs. the neighbor).
- **2–4 affirmative defenses** (sampled): trees were on the defendant's side,
  good-faith reliance on a flagged line, acquiescence in the line, comparative
  responsibility. Plus **1 counterclaim** by the neighbor for a declaratory judgment
  that the line favors him.
- **3–5 discovery items** and **2–4 motions** (sampled): partial summary judgment on
  liability, the enhanced-damages multiplier, determination of the boundary, and a
  motion in limine on valuation.
- A chronologically **ordered docket** (non-overlapping date windows) plus **trial**
  info (jury, estimated days, scheduled date).
- **1–3 experts**: a consulting forester (stumpage and restoration), a licensed
  surveyor (true boundary), and an arborist (ornamental/shade-tree value), all retained
  by the plaintiff.

## Downstream target

[`maine-court-forms`](https://github.com/bedardandy/maine-court-forms); example forms
`CV-001` (civil complaint) and `RE-QT` (quiet title).

## Notes

The litigation sub-lists that should vary by seed (affirmative defenses, discovery,
motions) use the DSL `pick_n`/`n` sampler; the ordered, numbered lists (causes of
action and docket) are fixed so count numbering and chronology stay coherent. The four
boolean facts are never templated with `_lower`; only the string fact
`buffer_or_shoreland` is, since `{factkey_lower}` exists only for string facts.

## Validation

```
python3 tools/generate.py timber-trespass --seed 1
python3 tools/smoke.py --scenarios timber-trespass --count 8 -v
```

The smoke run passes 8/8 (matter, clean, canonical) with 0 failures.
