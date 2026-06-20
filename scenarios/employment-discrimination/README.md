# Scenario: employment-discrimination

A Maine **employment-discrimination / wrongful-termination** lawsuit under the
**Maine Human Rights Act** and **Title VII**. A longtime employee, after reporting
discrimination internally and exhausting before the Maine Human Rights Commission,
sues the employer (and the supervisor who carried out the adverse action) for
discrimination and retaliation. Exercises the deep `litigation` block in an
employment-law posture.

## Models

- **Practice area:** civil · **case_type:** `employment` · **status:** `active`
- **Court:** Superior Court, random county · **docket prefix:** `CV`
- **Parties (2 + supervisor + counsel):** `plaintiff` (the employee, client),
  `defendant` (the employer, an `organization`), `defendant_2` (the
  supervisor/manager). `client_role: plaintiff`, with retained `attorney`.
- **Key dates:** `filing_date` in 2025; `event_date` mirrors the `termination_date`
  fact (resolved after facts so it stays consistent).

## Facts

Protected class, adverse action, hire and termination dates, whether the employee
reported internally, MHRC exhaustion and right-to-sue flags, annual salary,
whether a younger/outside-class replacement was hired, and the performance-review
history. These thread through the narrative, interview, issues, and evidence.

## Litigation depth (`litigation` block)

- **3–4 causes of action** (ordered, numbered): MHRA discrimination (§ 4572),
  MHRA retaliation (§ 4633), Title VII discrimination (42 U.S.C. § 2000e-2), and
  aiding-and-abetting against the supervisor (`defendant_2`).
- **3–5 affirmative defenses** (sampled): legitimate non-discriminatory reason,
  failure to exhaust, after-acquired evidence, failure to mitigate, the
  same-decision / Mt. Healthy defense, and statute of limitations.
- **1 counterclaim** (breach of a confidentiality agreement).
- **4–6 discovery items** (sampled): interrogatories, RFPs for the personnel
  file / comparators / emails, depositions of the plaintiff, the supervisor, and
  the HR director, an RFA, and a subpoena to a subsequent employer on mitigation.
- **3–5 motions** (sampled): motion to dismiss, motion to compel comparator data,
  the classic motion for summary judgment, a motion in limine on me-too evidence,
  and a partial-summary-judgment motion on retaliation.
- A chronologically-ordered **docket** (charge/right-to-sue, complaint, answer,
  scheduling order, discovery disputes, summary judgment briefing) with
  non-overlapping date windows that guarantee order, plus **trial** info (jury,
  4–10 estimated days, scheduled date) and `posture: discovery`.

## Issue spotting and proof

Issues (3–5) track the **McDonnell Douglas burden-shifting framework**: the prima
facie case (5 M.R.S. § 4572; 42 U.S.C. § 2000e-2), pretext, retaliation
(5 M.R.S. § 4633), exhaustion and the right to sue (5 M.R.S. § 4622), and the
measure of damages and civil penalties (5 M.R.S. § 4613).

## Third parties, experts, evidence, and financials

- **Third parties (3–5):** the **Maine Human Rights Commission** and the
  **U.S. Equal Employment Opportunity Commission** (named government agencies),
  the employer's HR director, a coworker witness, and the plaintiff's treating
  provider for the emotional-distress claim.
- **Experts (1–3):** a vocational / economic-loss expert and a forensic economist
  (plaintiff) on back and front pay, and an industrial/organizational
  psychologist (defendant) on the evaluation process.
- **Evidence (5–8):** personnel file and reviews, the termination letter, internal
  complaint emails, the MHRC charge and right-to-sue letter, comparator/replacement
  records, the handbook and anti-discrimination policy, pay and benefits records,
  and the plaintiff's contemporaneous notes.
- **Financials (3–5):** back pay, front pay, lost benefits, an emotional-distress
  demand, and attorney fees plus the statutory civil penalty.

## Downstream target

[`maine-court-forms`](https://github.com/bedardandy/maine-court-forms) (civil
filings); example forms `CV-001`, `CV-067`.

## Notes

The litigation sub-lists meant to vary by seed (affirmative defenses, discovery,
motions) use the DSL `pick_n`/`n` sampler; the ordered/numbered lists (causes of
action and the docket) are fixed so count numbering and chronology stay coherent.
Facts never reference one another — `event_date` reuses `termination_date` only
because it resolves after the facts are built.
