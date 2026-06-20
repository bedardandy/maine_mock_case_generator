# Scenario: criminal-oui

A Maine **OUI (operating under the influence) misdemeanor prosecution**. This is the
generator's only **criminal** scenario, modeled cleanly and non-graphically: a routine
roadside stop, a chemical test, and the usual suppression and license-consequence fights.
The **client is the defendant**, represented by defense counsel; the **State of Maine
prosecutes**.

## Models

The State charges the defendant with operating under the influence after a traffic stop.
Defense counsel scrutinizes the basis for the stop and the arrest, challenges the
foundation and admissibility of the chemical test, and works to protect the client's
license across both the criminal case and the parallel administrative track.

- **Practice area:** criminal · **case_type:** `criminal` · **status:** `active`
- **Jurisdiction:** random Maine county, District Court (Unified Criminal Docket)
- **Parties:** `plaintiff` — the **State of Maine** (an organization, the prosecution);
  `defendant` (the accused, **the client**); `attorney` (defense counsel)
- **Signing filer (`client`):** the defendant

## Downstream target

[`maine-court-forms`](https://github.com/bedardandy/maine-court-forms) — representative
forms `CR-001` and `CR-030` (criminal filings).

## Key issues (with governing law)

- Validity of the stop and arrest (reasonable suspicion / probable cause) —
  `U.S. Const. amend. IV; 29-A M.R.S. § 2411`
- Admissibility and foundation of the chemical test —
  `29-A M.R.S. § 2521` (implied consent and chemical testing)
- Administrative license suspension vs. the criminal license consequence —
  `29-A M.R.S. § 2453`
- Right to an independent chemical test — `29-A M.R.S. § 2521(3)`
- Proof of every OUI element beyond a reasonable doubt — `29-A M.R.S. § 2411`

## Litigation depth (`litigation` block)

- **posture:** `pretrial`.
- **Charges as ordered counts** (`causes_of_action`): Operating Under the Influence
  (`29-A M.R.S. § 2411`) and an implied-consent count (`29-A M.R.S. § 2521`), with
  elements and relief sought.
- **2–4 affirmative defenses** (unlawful stop, lack of probable cause, improper test
  administration/foundation, rising-BAC, denial of an independent test) sampled per seed.
- **2–4 motions** (suppress the stop, suppress the breath test, motion in limine on
  field sobriety tests, motion to dismiss) and **2–4 discovery items** (Rule 16 requests,
  a calibration-records subpoena, supplemental document requests) — criminal practice, so
  document requests over depositions.
- A chronologically ordered **docket** (charging, initial appearance, arraignment/plea,
  discovery, suppression motion, dispositional conference) with non-overlapping date
  windows, plus **trial** info (jury, 1–3 estimated days, scheduled date).

## Canonical `facts` emitted

`arrest_date`, `charge`, `bac_result`, `prior_ouis`, `chemical_test`, `stop_reason`,
`field_sobriety_administered`, `accident_involved`, `license_suspended`, `plea`.
`matter.event_date` is bound to the arrest date.

## Notes

The State is an explicitly-named **organization** party (`State of Maine`); the defendant
is the represented client (`client_role: defendant`). Third parties (arresting officer,
breath-test operator, the Maine Bureau of Motor Vehicles, an independent toxicologist, a
passenger witness), defense experts (forensic toxicologist, field-sobriety expert), and
the sampled litigation sub-lists vary by seed, so volume sweeps produce varied but
always-valid matters. The litigation sub-lists that should vary use the DSL `pick_n`/`n`
sampler; the numbered counts and the docket are fixed so count numbering and chronology
stay coherent.
