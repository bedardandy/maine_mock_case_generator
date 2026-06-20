# Scenario: llc-member-oppression

A **closely-held Maine LLC freeze-out**. A minority member is squeezed out by the
majority/managing members — cut off from distributions and company information, removed
from management, and pressured to leave while the controlling members pay themselves. The
minority member sues for oppression, breach of fiduciary duty, and judicial dissolution
or, in the alternative, a court-ordered buyout at fair value, and adds a derivative claim
for company opportunities diverted to a side entity.

## Models

- **Practice area:** business · **case_type:** `business` · **status:** `active`
- **Docket:** `BCD` prefix · **Court:** Superior Court (Business and Consumer Docket), random county
- **Parties (3 + the entity + counsel):** `plaintiff` (minority member, the client),
  `defendant` (majority/managing member), `defendant_2` (co-manager member), and `company`
  (the LLC, an `organization`, named as a nominal defendant). Exercises a multi-party
  roster with an organization role projecting through to the canonical case.

## Governing law (Maine Limited Liability Company Act, Title 31)

The spotted `issues` (4–6) are tied to the LLC Act:

- **31 M.R.S. § 1595** — judicial dissolution where the managers or controlling members
  have acted illegally, oppressively, fraudulently, or in an unfairly prejudicial manner
  (and the equitable buyout remedy as an alternative).
- **31 M.R.S. § 1559** — the fiduciary duties of loyalty and care owed by members/managers.
- **31 M.R.S. § 1545** — a member's right to inspect the LLC's books and records.
- **31 M.R.S. § 1546 and § 1547** — distributions and the prohibition on improper distributions.
- **31 M.R.S. § 1631 et seq.** — derivative claims brought on behalf of the LLC.

## Litigation depth (`litigation` block)

- **5 causes of action** (ordered, sequentially numbered): member oppression / judicial
  dissolution (§ 1595), breach of fiduciary duty (§ 1559), breach of the operating
  agreement, a derivative claim for diversion of company assets (§ 1631 et seq.), and a
  demand for inspection of books and records (§ 1545).
- **3–5 affirmative defenses** (business judgment, authorization under the operating
  agreement, unclean hands/prior breach, a fair buyout offer, claims-are-derivative) and
  **1 counterclaim** by the majority.
- **4–6 discovery items** (interrogatories, RFPs for financials and the side entity's
  records, depositions of the managing members and the accountant, expert disclosure, and
  a subpoena to the bank) and **3–5 motions** (compel inspection, appoint a receiver or
  custodian, buyout/fair-value determination, partial summary judgment on the fiduciary
  claim, compel the diversion records), each with a disposition.
- A chronologically-ordered **docket** (non-overlapping date windows guarantee order),
  plus **trial** info (jury, estimated days, scheduled date) and `posture: discovery`.
- 1–3 plaintiff-side **experts**: business valuation (fair value of the minority interest),
  forensic accounting (tracing distributions and diverted funds), and reasonable
  compensation (the majority's salaries).

## Third parties (3–5)

Drawn from the LLC's outside accountant, the company's bank, a business-valuation firm, a
former employee with knowledge of the diversion, the side entity allegedly receiving
diverted opportunities, and the Maine Secretary of State. Third-party identities use
fictional name kinds (person/bank/organization) except the named government agency.

## Downstream target

[`maine-court-forms`](https://github.com/bedardandy/maine-court-forms) · example forms
`CV-001`, `CV-067` (civil filings).

## Notes

- The litigation sub-lists that should vary by seed (defenses, discovery, motions) use the
  DSL `pick_n`/`n` sampler; the ordered/numbered lists (causes of action, docket) are fixed
  so count numbering and chronology stay coherent.
- `oppressive_conduct` is a top-level **fact** that samples 3–5 items via `pick_n`/`n`.
  `operating_agreement_exists` and `distributions_suspended` are booleans (no `_lower`
  form); `buyout_offered` and the other string facts are referenced directly (with
  `{buyout_offered_lower}` used in prose).
