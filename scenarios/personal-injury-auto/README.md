# Scenario: personal-injury-auto

A **motor-vehicle personal-injury lawsuit** that exercises the schema's deep
`litigation` section as a contested tort matter. An injured motorist sues the
at-fault driver for negligence and, where the vehicle was commercial, joins the
driver's employer under respondeat superior. The defense disputes liability and
asserts comparative fault, and the case is in active discovery.

## Models

- **Practice area:** civil · **case_type:** `personal_injury` · **status:** `active`
- **Court:** Superior Court, random county · **docket prefix:** `CV`
- **Parties (3 + counsel):** `plaintiff` (injured motorist, the client),
  `defendant` (at-fault driver), `defendant_2` (the driver's employer, an
  organization, for the commercial-vehicle theory). `client_role: plaintiff`.
- **Dates:** `filing_date` in 2025; `event_date` set to the `collision_date`.

## Facts

Collision date, location, and type (rear-end, left-turn, T-bone, highway merge);
injury type; and the monetary spine of the case — `medical_specials`,
`lost_wages`, `property_damage`, and `policy_limits` — plus boolean flags
(`liability_disputed`, `commercial_vehicle`, `comparative_fault_alleged`) that
color the dispute. Facts are flat scalars; none references another fact.

## Third parties (3–5)

Both insurers (the plaintiff's auto/UM-UIM carrier and the defendant's liability
carrier), the investigating police officer, the treating physician, an
independent eyewitness, and the tow-and-storage company.

## Governing law for issues (3–5)

Common-law negligence (duty/breach/causation/damages); Maine comparative
negligence (14 M.R.S. § 156); statute of limitations (14 M.R.S. § 752);
vicarious liability / respondeat superior; UM/UIM coverage (24-A M.R.S. § 2902);
and punitive damages (14 M.R.S. § 1604-A).

## Litigation depth (`litigation` block)

- **Causes of action** (ordered, numbered I–III): negligence v. the driver,
  vicarious liability / negligent entrustment v. the employer, and negligence per se.
- **3–5 affirmative defenses** (comparative negligence, failure to mitigate,
  sudden emergency, statute of limitations, lack of causation) and **1 counterclaim**.
- **4–6 discovery items** (interrogatories, RFPs, depositions of the driver,
  plaintiff, and treating physician, an RFA, a defense IME, and an insurer
  subpoena) with status, and **3–5 motions** (compel IME, in limine to exclude
  reconstruction, partial summary judgment on liability, bifurcation, compel
  phone records) with dispositions.
- A chronologically-ordered **docket** (non-overlapping date windows guarantee
  order), plus **trial** info (jury, estimated days, scheduled date) and
  `posture: discovery`.
- 2–4 dueling **experts** (accident reconstructionist, treating/causation
  physician, vocational economist for the plaintiff; biomechanical engineer and
  defense medical examiner for the defense).

## Downstream target

[`maine-court-forms`](https://github.com/bedardandy/maine-court-forms) (civil
filings). Example forms: `CV-001`, `CV-067`, `CV-181`.

## Notes

The litigation sub-lists that should vary by seed (affirmative defenses,
discovery, motions) use the DSL `pick_n`/`n` sampler; the ordered/numbered lists
(causes of action, docket) are fixed so count numbering and chronology stay
coherent. `commercial_vehicle` is a fact flag rather than a structural switch —
the employer (`defendant_2`) is always present, and the narrative frames the
vicarious-liability theory as conditional on the vehicle being commercial.
