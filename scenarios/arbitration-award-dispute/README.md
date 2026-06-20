# Scenario: arbitration-award-dispute

A Maine **post-arbitration court fight** under the Uniform Arbitration Act
(14 M.R.S. ch. 706). The prevailing party (the **petitioner / award creditor**)
moves to **confirm** a commercial arbitration award and reduce it to an enforceable
judgment; the losing party (the **respondent / award debtor**) cross-moves to
**vacate** it on the narrow statutory grounds. The underlying dispute arose from a
commercial or construction contract with an arbitration clause.

This is a **record-based, motion-practice** matter: there is **no jury** and
essentially **no discovery**. Judicial review is deferential and confined to the
exclusive statutory grounds — the court does **not** reweigh the merits.

## Models

- **Practice area:** civil · **case_type:** `arbitration` · **status:** `active` · **docket_prefix:** `CV`
- **Court:** Superior Court, random county
- **Parties (2 organizations + the arbitrator + counsel):** `petitioner` and
  `respondent` (both organizations — the award creditor and award debtor),
  `other_party` (the arbitrator / panel chair, a person). The client is the
  petitioner; an attorney is generated.
- **Downstream forms:** [`maine-court-forms`](https://github.com/bedardandy/maine-court-forms) — CV-001, CV-067.

## Cross-applications (`litigation` block, `posture: motion_practice`)

The dispute is framed as **dueling applications** rather than a trial:

- **3 ordered causes of action** (sequential counts): the petitioner's application
  to confirm and enter judgment (§ 5937, § 5941); in the alternative, an application
  to modify or correct (§ 5939); and the respondent's cross-application to vacate
  (§ 5938). The confirmation count is `strong`; the vacatur count is `weak`,
  reflecting the deferential standard.
- **2–4 affirmative defenses** (raised by the respondent, `pick_n` sampled):
  arbitrators exceeded their powers, evident partiality / failure to disclose,
  refusal to hear material evidence, and non-arbitrability.
- **3–5 motions** (`pick_n` sampled): motion to confirm, cross-motion to vacate,
  motion to modify/correct, motion for entry of judgment and post-award interest,
  and motion to seal the arbitration record.
- A chronologically-ordered **docket** of 5 entries with non-overlapping date
  windows (award issued → motion to confirm → cross-motion to vacate → briefing →
  hearing/oral argument).
- **No discovery** section (arbitration review is record-based) and **no
  counterclaims** — the respondent's pleading is the cross-application to vacate.
- **trial:** `jury: false`, 1–2 estimated days (the oral-argument slot), scheduled
  date in late 2026 / early 2027.

## Governing law (Maine Uniform Arbitration Act, Title 14 ch. 706)

The spotted **issues (3–5)** track the statute and reflect the deferential standard —
**confirmation is `strong`; the vacatur grounds are weaker**:

- Confirmation of the award and entry of judgment — **14 M.R.S. § 5937, § 5941**.
- The exclusive statutory grounds to **vacate** (corruption/fraud/undue means;
  evident partiality or corruption of an arbitrator; arbitrators exceeding their
  powers; refusal to hear material evidence or other misconduct) — **14 M.R.S. § 5938**.
- Modification or correction of an award — **14 M.R.S. § 5939**.
- Substantive arbitrability and the narrow scope of judicial review (errors of law
  only; no re-weighing of the merits) — **14 M.R.S. § 5928**.
- Fees, costs, and post-award interest — **14 M.R.S. § 5943**.

## Other detail

- **Facts** capture the underlying dispute type, arbitration forum, contract clause,
  award date and amount, the alleged vacatur ground, and two booleans
  (`attorney_fees_in_award`, `included_punitive_or_consequential`).
- **Third parties (2–4):** the AAA case administrator (the explicit, real
  organization name *American Arbitration Association*), the underlying
  owner/counterparty, the surety/bonding company, a fact witness from the
  arbitration, and the arbitrator's former firm.
- **Experts (0–1):** an arbitration-procedure / disclosure-standards expert retained
  by the **respondent** on the alleged partiality.
- **Evidence (4–7):** the award and reasoned decision, the contract with the
  arbitration clause, the arbitrator's disclosures and AAA appointment record, the
  hearing transcript and exhibits, conflict correspondence, the demand and answering
  statement, and proof of the amounts.
- **Financials (3–5):** the award amount, fees and costs on confirmation, post-award
  interest, the disputed punitive/consequential component, and a related bond amount.
- **Interview (6 exchanges)** and **objectives** are from the award creditor's
  perspective — confirm fast, defeat vacatur under the deferential standard, and
  recover fees and interest. `risk_tolerance: low`.

## Notes

The sub-lists that should vary by seed (affirmative defenses, motions) use the DSL
`pick_n`/`n` sampler; the ordered/numbered lists (causes of action, docket) are fixed
plain lists so the count numbering and the award→confirm→vacate→briefing→hearing
chronology stay coherent. Because the petitioner and respondent are **organizations**,
the narrative refers to them by `{petitioner_full_name}` / `{respondent_full_name}`
(organizations have no first name to project).

## Validate

```
python3 tools/generate.py arbitration-award-dispute --seed 1
python3 tools/smoke.py --scenarios arbitration-award-dispute --count 8 -v
```
