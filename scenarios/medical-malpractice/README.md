# Scenario: medical-malpractice

A Maine **medical-malpractice (professional-negligence)** action with its distinctive
procedural wrinkle: the **mandatory prelitigation screening panel**. An injured patient
sues the treating physician and the hospital/health system for a negligent diagnosis or
treatment, impleads a consulting/second provider, and litigates the standard of care,
causation, and the admissibility of the panel's findings. Exercises the deep
`litigation` block in a professional-liability posture under 24 M.R.S. ch. 21.

## Models

- **Practice area:** civil · **case_type:** `medical_malpractice` · **status:** `active`
- **Court:** Superior Court, random county · **docket prefix:** `CV`
- **Parties (multi-party, 4 + counsel):** `plaintiff` (the patient, client),
  `defendant` (the physician), `defendant_2` (the hospital / health system, an
  `organization`), and `third_party_defendant` (a consulting/second provider).
  `client_role: plaintiff`, with a retained `attorney`.
- **Key dates:** `filing_date` in 2025; `event_date` mirrors the `negligence_date`
  fact (resolved after facts so it stays consistent).

## Facts

Specialty, the alleged negligence, the negligence date, the resulting injury, the
notice-of-claim and screening-panel status, whether the standard of care was breached,
an informed-consent flag, a statute-of-limitations flag, and the economic damages.
These thread through the narrative, interview, issues, and evidence. Note that
`notice_of_claim_served`, `standard_of_care_breached`, `informed_consent_issue`, and
`statute_of_limitations_concern` are **booleans**, so no `{..._lower}` form is used for
them; only the string facts (`alleged_negligence_lower`, `injury_lower`) are templated
in lower case.

## The prelitigation screening panel

Maine requires malpractice claims to pass through a mandatory prelitigation screening
panel before suit. The scenario foregrounds this throughout: a `screening_panel_stage`
fact, an issue on the panel process and the admissibility of its findings
(24 M.R.S. § 2851, § 2853), an affirmative defense for failure to satisfy the
prerequisite, an evidentiary motion on admissibility, third parties for the panel chair
and the hospital risk-management department, and docket entries for the notice of claim
and the panel milestones (dated in 2024, before the 2025 complaint).

## Litigation depth (`litigation` block)

- **4 causes of action** (ordered, numbered): professional negligence / departure from
  the standard of care (plaintiff v. physician), vicarious liability and corporate
  negligence (plaintiff v. hospital), negligence of the consulting provider (plaintiff
  v. `third_party_defendant`), and lack of informed consent (plaintiff v. physician).
- **3–5 affirmative defenses** (sampled): the care met the standard, a known
  risk/complication, comparative negligence of the patient, the time bar
  (24 M.R.S. § 2902), an intervening cause, and failure to satisfy the screening-panel
  prerequisite (24 M.R.S. § 2851).
- A **cross-claim** (hospital v. physician for indemnification/contribution) and a
  **third-party claim** (physician v. the consulting provider).
- **4–6 discovery items** (sampled): interrogatories, RFPs for the complete records,
  policies, and credentialing file, depositions of the physician, the nurse/tech, and
  the experts, a defense `independent_examination`, an `expert_disclosure`, and a
  subpoena to the subsequent providers.
- **3–5 motions** (sampled): a motion on the screening-panel findings' admissibility, a
  motion to compel the credentialing file, partial summary judgment on informed consent,
  a motion in limine to exclude an expert (Daubert / M.R.E. 702), and a motion to
  bifurcate.
- A chronologically-ordered **docket** (notice of claim, panel convened, complaint,
  answers/cross-claim/third-party complaint, scheduling order, motion to compel,
  expert disclosures) with non-overlapping date windows that guarantee order, plus
  **trial** info (always a jury, 6–15 estimated days, scheduled date) and
  `posture: discovery`.

## Issue spotting and proof

Issues (4–6) make the **standard-of-care/causation** and the **screening-panel
procedure** prominent, alongside the notice-of-claim requirement (24 M.R.S. § 2903), the
three-year statute of limitations (24 M.R.S. § 2902), the hospital's vicarious liability
and corporate/credentialing negligence, and informed consent. Each malpractice issue
notes that **expert testimony** is required to establish the standard of care, breach,
and causation.

## Third parties, experts, evidence, and financials

- **Third parties (3–5):** the plaintiff's subsequent treating physician
  (`healthcare_provider`), the hospital's risk-management department
  (`business_entity`), the physician's malpractice insurer (`insurer`), a nurse or
  technician present (`witness`), the **Maine Board of Licensure in Medicine** (a named
  `government_agency`), and the prelitigation screening panel chair (`witness`).
- **Experts (2–4):** a same-specialty standard-of-care expert and a causation expert
  (plaintiff), a life-care-planner / economist on future medical needs and lost earnings
  (plaintiff), and a defense standard-of-care expert (defendant).
- **Evidence (5–8):** the complete medical records and imaging, the hospital's policies
  and the credentialing file, the informed-consent form, the notice of claim and the
  screening-panel submissions and findings, the subsequent-care records, the expert
  reports, the economic-loss and life-care documentation, and the incident/risk-
  management reports.
- **Financials (3–5):** past medical specials, projected future medical/life-care costs,
  lost earnings and earning capacity, a pain-and-suffering / general-damages demand, and
  expert and panel costs.

## Downstream target

[`maine-court-forms`](https://github.com/bedardandy/maine-court-forms) (civil
filings); example forms `CV-001`, `CV-067`.

## Notes

The litigation sub-lists meant to vary by seed (affirmative defenses, discovery,
motions) use the DSL `pick_n`/`n` sampler; the ordered/numbered lists (causes of action
and the docket) are fixed so count numbering and chronology stay coherent. Facts never
reference one another — `event_date` reuses `negligence_date` only because it resolves
after the facts are built. Validated with `python3 tools/generate.py medical-malpractice
--seed 1` and `python3 tools/smoke.py --scenarios medical-malpractice --count 8 -v`.
