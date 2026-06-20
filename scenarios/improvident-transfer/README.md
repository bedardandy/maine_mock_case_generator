# Scenario: improvident-transfer

A **Maine action under the Improvident Transfers of Title Act** (33 M.R.S. ch. 20).
An **elderly, dependent person** deeded the family home or farm to a caretaker — one
child, a late-life companion, or a neighbor who became a caregiver — for **far less
than full value** and **without independent counsel**, inside a relationship of trust
and confidence. That combination raises a **statutory presumption of undue influence**.
**Capacity to convey** at the time of the deed is also in question. Brought through a
**conservator/next friend**, the suit seeks to **void the deed** and restore the
property to the transferor. The elderly subject is treated with dignity and
non-graphically throughout.

## Models

- **Practice area:** probate · **case_type:** `improvident_transfer` · **status:** `active`
- **Court:** Superior Court, random county · **docket prefix:** `CV`
- **Parties (4 + counsel):** `plaintiff` (the elderly transferor, suing through a
  conservator/next friend), `defendant` (the transferee — caretaker / child / companion),
  `defendant_2` (a co-transferee or spouse of the transferee), and `other_party` (an
  interested adult child of the transferor). The client is the `plaintiff`;
  `client_role: plaintiff` makes the transferor the signing filer. Demonstrates the
  `other_party` role and a co-transferee `defendant_2` projecting through to the canonical
  case.

## Governing law

The issues are tied to the Improvident Transfers of Title Act, **Title 33, Chapter 20**
(`§` citations throughout), plus the common law:

- **Statutory presumption of undue influence** when an elderly dependent person, in a
  confidential or fiduciary relationship, makes a major transfer of property for less than
  full consideration without independent counsel — 33 M.R.S. § 1022. *(This is the
  strongest issue and the first cause of action.)*
- **Available relief** — rescission/reformation of the deed, a constructive trust, and an
  order returning the property — 33 M.R.S. § 1023.
- **Definitions** of "elderly dependent person" and "major transfer" — 33 M.R.S. § 1021.
- **Common-law lack of capacity to convey** and **common-law undue influence**.
- The **transferee's burden** to rebut the statutory presumption — 33 M.R.S. § 1022.
- The **statute of limitations** for challenging the transfer — 33 M.R.S. § 1024.

## Facts that vary by seed

The transferor's age (78–93), the basis for dependency, the relationship to the
transferee, which property was transferred, its fair market value, the (nominal)
consideration paid, the transfer date, and the transferor's medical condition. Three
statutory-trigger facts are fixed booleans — `independent_counsel: false`,
`confidential_relationship: true`, and `competency_questioned: true` — so the presumption
elements are always present. These facts feed the summary, narrative, disputed-facts list,
interview, issues, and the litigation counts.

## Litigation depth (`litigation` block)

- **5 causes of action** (ordered, sequential counts): (1) improvident transfer /
  statutory presumption of undue influence seeking rescission, (2) common-law undue
  influence against both transferees, (3) lack of capacity to convey, (4) imposition of a
  constructive trust against both transferees, and (5) conversion of personal property.
  Count 1 is the strongest claim.
- **3–5 affirmative defenses** sampled by seed (a competent and freely given gift, full
  and fair consideration through years of care, that the transferor understood the
  transaction, statute of limitations, ratification).
- **One counterclaim** by the transferee in quantum meruit for the value of care provided
  if the deed is set aside.
- **3–5 discovery events** sampled by seed (interrogatories; an RFP for financials and
  medical authorizations; depositions of the transferee, notary, and physician; a
  court-ordered independent capacity examination; a subpoena to the bank).
- **2–4 motions** sampled by seed (a constructive trust / lis pendens, a motion to compel
  the medical records, partial summary judgment establishing the presumption, and a motion
  for a guardian ad litem) with dispositions.
- A chronologically-ordered **docket** (6 entries; non-overlapping date windows guarantee
  order): complaint, answer and counterclaim, appointment of a guardian ad litem, order
  compelling the medical records, the capacity-evaluation report, and the presumption
  hearing.
- **trial** info (`jury` sampled, estimated days, scheduled date) and `posture: pleadings`.
- **1–3 experts** retained by the plaintiff: a geriatric psychiatrist/neuropsychologist on
  capacity at the time of transfer, a real estate appraiser on value versus consideration,
  and a forensic accountant tracing the transferor's finances.

## Third parties, evidence, financials

- **3–5 third parties** drawn from the transferor's primary physician, the appointed
  conservator / guardian ad litem, the notary and witnesses to the deed, another adult
  child of the transferor, `Maine Adult Protective Services`, the attorney who drafted the
  deed (if any), and the bank holding the transferor's accounts.
- **4–7 evidence items**: the recorded deed and closing/transfer documents, the
  transferor's medical and cognitive records, the appraisal showing value far above the
  consideration, the transferor's financial and bank records, correspondence and notes
  from the caretaking relationship, the conservatorship/competency filings, and affidavits
  from family and neighbors.
- **3–5 financials**: the property's fair market value, the consideration actually paid,
  the claimed value of care services offered as consideration, the transferor's depleted
  accounts, and the estimated cost of the cognitive/appraisal experts.

## Downstream target

[`maine-court-forms`](https://github.com/bedardandy/maine-court-forms) — example forms
`CV-001` (civil complaint) and `RE-QT` (quiet title / deed).

## Reproduce

```sh
python3 tools/generate.py improvident-transfer --seed 1
python3 tools/smoke.py --scenarios improvident-transfer --count 8 -v
```

## Notes

The litigation sub-lists that should vary by seed (affirmative defenses, discovery,
motions) use the DSL `pick_n`/`n` sampler; the ordered/numbered lists (causes of action,
docket) are fixed so count numbering and chronology stay coherent. The three
statutory-trigger facts are booleans, so they are never used with the `{..._lower}` string
helper; only string facts (e.g. `property_transferred`, `consideration_paid`,
`relationship_to_transferee`, `medical_condition`) are templated, and no fact references
another fact. The elderly transferor is described with dignity and non-graphically.
