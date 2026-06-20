# Scenario: complex-civil-litigation

A **sprawling, multi-party commercial dispute** that exercises the schema's deep
`litigation` section end to end. Two investors sue a closely-held company and its CEO
over an allegedly fraudulent securities offering; the company counterclaims, cross-claims
against its own officer, and impleads its outside auditor as a third-party defendant.

## Models

- **Practice area:** civil · **case_type:** `civil` · **status:** `active`
- **Court:** Superior Court (complex civil), random county
- **Parties (5 + counsel):** `plaintiff`, `plaintiff_2` (investors), `defendant`
  (the company, an organization), `defendant_2` (the CEO), `third_party_defendant`
  (the auditor). Demonstrates multi-party rosters projecting through to the canonical case.

## Litigation depth (`litigation` block)

- **6 causes of action** (breach of contract, breach of fiduciary duty, fraud, negligent
  misrepresentation, Maine UTPA, unjust enrichment), each with elements, relief, and a strength.
- **3–5 affirmative defenses**, **2 counterclaims**, **1 cross-claim**, **1 third-party claim**.
- **4–6 discovery items** (interrogatories, RFPs, depositions, RFAs, subpoena, expert
  disclosure) with status, and **3–5 motions** with dispositions.
- A chronologically-ordered **docket** (non-overlapping date windows guarantee order),
  plus **trial** info (jury, estimated days, scheduled date) and `posture: discovery`.
- 2–4 dueling **experts** (forensic accounting, valuation, damages economics, auditing
  standards, governance) retained by different sides.

## Downstream target

[`maine-court-forms`](https://github.com/bedardandy/maine-court-forms) (civil filings).
This scenario is also reused as a constituent in compound matters (e.g. a business-dispute
cascade) via the shared-cast override mechanism.

## Notes

The litigation sub-lists that should vary by seed (defenses, discovery, motions) use the
DSL `pick_n`/`n` sampler; the ordered/numbered lists (causes of action, docket) are fixed
so count numbering and chronology stay coherent.
