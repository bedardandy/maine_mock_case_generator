# Scenario: rule-80b-zoning-appeal

A Maine **Rule 80B appeal** to the **Superior Court** from a municipal land-use
decision. An aggrieved abutting neighbor (the petitioner) appeals a local board's
grant of relief to a developer (the party-in-interest). This is a **record-review**
appeal: there is **no jury** and **no traditional discovery**. The court reviews the
certified administrative record for **error of law** and whether the board's findings
rest on **substantial evidence**, rather than trying the facts anew.

## Models

- **Practice area:** administrative · **case_type:** `administrative_appeal_80b` ·
  **status:** `active` · **docket prefix:** `AP`
- **Court:** Superior Court, random county
- **Parties (3 + counsel):** `petitioner` (the aggrieved abutter, the client),
  `respondent` (the municipality, an `organization` named "Town of Harborwick"), and
  `other_party` (the party-in-interest / permittee-developer). `client_role: petitioner`,
  with a retained `attorney`.
- **Key dates:** `filing_date` in late 2025 / early 2026; `event_date` mirrors the
  `board_decision_date` fact (resolved after facts so it stays consistent).

## Facts

The municipality, the deciding board, the relief granted, the project at issue, the
board's decision date, a flag that the appeal was filed within 45 days, the
petitioner's standing basis as an abutter, the governing ordinance section, and the
particular harm alleged. These thread through the narrative, interview, issues, and
evidence. Facts never reference one another; `event_date` reuses `board_decision_date`
only because it resolves after the facts are built.

## Issue spotting and proof

Issues (3–5) track the governing law of a Rule 80B land-use appeal:

- **Standing / particularized injury** — *Adelman v. Town of Baldwin*, 2000 ME 91.
- **The 45-day appeal deadline and procedure** — 30-A M.R.S. § 2691(3)(G); M.R. Civ. P. 80B.
- **Error of law** in applying the ordinance (reviewed de novo).
- **Substantial-evidence** review of the board's findings.
- **Variance criteria, including undue hardship** — 30-A M.R.S. § 4353.
- **Adequacy of the board's findings of fact.**
- **Bias / conflict of interest** of a board member — 30-A M.R.S. § 2691; due process.

## Litigation depth (`litigation` block)

This is record review, so the block is deliberately leaner than a civil-litigation
scenario (no discovery, no counterclaims):

- **4 causes of action** (ordered, numbered) framed as the **grounds of appeal** by the
  petitioner against the respondent: error of law in applying the ordinance; the
  decision is unsupported by substantial evidence; abuse of discretion / inadequate
  findings; and procedural error or bias depriving the petitioner of a fair hearing.
- **2–4 affirmative defenses** (sampled), raised by the respondent and party-in-interest:
  lack of standing, untimely appeal, the decision is supported by substantial evidence,
  and failure to preserve the issue below.
- **2–4 motions** (sampled), characteristic of an 80B appeal: motion to specify/assemble
  the record, motion for a **trial of the facts** under M.R. Civ. P. 80B(d), motion to
  stay the permit pending appeal, and motion to supplement the record.
- A chronologically-ordered **docket** (notice of appeal, record certified and filed,
  petitioner's brief, respondent's and party-in-interest's briefs, reply / under
  advisement, oral argument scheduled) with non-overlapping date windows that guarantee
  order.
- **trial** info reflects record review: `jury: false`, 1–2 estimated days, and a
  scheduled date — with `posture: pretrial`.

## Third parties, experts, evidence, and financials

- **Third parties (3–5):** the municipal Code Enforcement Officer (record-keeper /
  administrator), the board chair who signed the decision, another objecting abutting
  neighbor, the developer's project engineer, and the town's land-use attorney. Names
  come from the fictional pools (`name_kind: person`); none are hard-coded.
- **Experts (1–3):** a land-use planner, a traffic engineer, and a real-estate appraiser
  on diminution in value — all retained by the petitioner. Each opinion is framed to note
  that, in pure record review, such expert testimony is limited unless the court grants a
  **trial of the facts** under Rule 80B(d).
- **Evidence (4–7):** the certified municipal record and decision with findings, the
  meeting minutes and hearing audio, the variance/site-plan application and plans, the
  petitioner's objection letters, photographs of the site and abutting property, the
  ordinance text, and staff and engineering reports.
- **Financials (1–3, modest):** estimated diminution in the petitioner's property value,
  the cost of the appeal, and an escrow/bond if a stay of the permit is sought.

## Client objectives

Reverse or vacate the board's decision, or in the alternative obtain a remand for proper,
record-supported findings; protect the neighborhood and the petitioner's property; and do
so within the record-review constraints. `risk_tolerance: moderate`.

## Downstream target

[`maine-court-forms`](https://github.com/bedardandy/maine-court-forms) (Superior Court
civil / administrative-appeal filings); example forms `CV-001`, `AP-80B`.

## Notes

The litigation sub-lists meant to vary by seed (affirmative defenses, motions) use the
DSL `pick_n`/`n` sampler; the ordered/numbered lists (causes of action and the docket)
are fixed so count numbering and chronology stay coherent. Because Rule 80B is an appeal
on the record, the scenario intentionally omits a discovery section and counterclaims,
and the experts and any trial of the facts are framed as the narrow exception to
record-only review.
