# Scenario: will-contest

A **Maine formal testacy proceeding** contesting a decedent's will (18-C M.R.S. art. 3).
A **late-in-life will** left most of the estate to **one caregiver-child or a new
companion**, disinheriting the others. A **disinherited adult child** now contests it for
**lack of testamentary capacity**, **undue influence**, and **improper execution**, asking
the Probate Court to **deny probate of the contested will** and admit an **earlier will**
(or distribute by **intestacy**). The decedent and the family are treated with dignity
throughout.

> **Distinct from `improvident-transfer`.** That case voids an *inter vivos* **deed** under
> the Improvident Transfers of Title Act (33 M.R.S. ch. 20) on a statutory presumption of
> undue influence. This case contests a **testamentary instrument** (a will) under the
> **Maine Probate Code, Title 18-C**, on capacity, undue influence, and defective
> execution. Different instrument, different statute, different relief.

## Models

- **Practice area:** probate · **case_type:** `will_contest` · **status:** `active`
- **Court:** Probate Court, random county · **docket prefix:** `PE`
- **Parties (4 + counsel):** `decedent` (the testator), `plaintiff` (the contestant — a
  disinherited adult child), `defendant` (the proponent — the favored beneficiary / named
  personal representative), and `other_party` (another interested heir). The client is the
  `plaintiff`; `client_role: plaintiff` makes the contestant the signing filer. The
  `decedent` carries `with_contact: false` (no email/phone/address) and `with_dob: true`,
  so `{decedent_full_name}` projects through the narrative while the decedent is modeled
  with dignity and without contact details.

## Governing law

The issues are tied to the **Maine Probate Code, Title 18-C** (`§` citations throughout),
plus the common law:

- **Burdens of proof in a contested formal testacy proceeding** — the proponent must prove
  due execution, and the contestants bear the burden on lack of testamentary capacity,
  undue influence, fraud, duress, mistake, or revocation — 18-C M.R.S. § 3-407.
- **Execution requirements** — signed by the testator and attested by at least two
  witnesses — 18-C M.R.S. § 2-502.
- **Testamentary capacity** and who may make a will — 18-C M.R.S. § 2-501.
- **Revocation** of a prior will — 18-C M.R.S. § 2-507.
- **Formal testacy** and the order of probate — 18-C M.R.S. § 3-401 et seq.
- **Effect of a self-proved will** — 18-C M.R.S. § 2-504.

## Facts that vary by seed

The date of death, the estate value (\$300k–\$4.2M), the date of the contested will, the
prior will's date, who the favored beneficiary is, the share they received, the capacity
concern at signing, and the execution irregularity. Three facts are fixed or partly fixed
booleans — `isolation_alleged: true` (always), with `prior_will_existed` and
`drafting_attorney_used` sampled from `[true, false]`. These facts feed the summary,
narrative, disputed-facts list, timeline, interview, issues, and the litigation counts.

## Litigation depth (`litigation` block)

- **5 causes of action** (ordered, sequential counts): (1) lack of testamentary capacity,
  (2) undue influence, (3) improper execution (failure to satisfy 18-C M.R.S. § 2-502),
  (4) fraud or mistake in the will's execution, and (5) admission of the prior will /
  adjudication of testacy. The burdens-of-proof issue is the strongest, and the prior-will
  count provides the alternative relief.
- **2–4 affirmative defenses** sampled by seed (the testator had capacity and acted freely,
  the will is self-proved and validly executed, the contest is barred by limitations, no
  confidential relationship / undue influence).
- **One counterclaim** by the proponent: a petition to admit the contested will to formal
  probate and to be appointed personal representative.
- **3–5 discovery events** sampled by seed (interrogatories; an RFP for the drafting file
  and medical authorizations; depositions of the proponent, the drafting attorney, the
  attesting witnesses, and the physician; an independent examination reviewing the capacity
  records; a subpoena to the bank).
- **2–4 motions** sampled by seed (formal testacy and to supervise administration, partial
  summary judgment on due execution, a motion to compel the medical records, and a motion
  to appoint a temporary special administrator) with dispositions.
- A chronologically-ordered **docket** (6 entries; non-overlapping date windows guarantee
  order): the testacy petition, the proponent's response and petition to admit the will,
  appointment of a special administrator, an order compelling the medical records, the
  capacity expert's report, and the due-execution hearing.
- **trial** info (`jury` sampled, 3–8 estimated days, scheduled date) and
  `posture: pleadings`.
- **1–3 experts** by seed: a geriatric psychiatrist / neuropsychologist on testamentary
  capacity at the time of signing (plaintiff), a forensic document examiner on the
  signature / execution (plaintiff), and an estate-planning standard-of-care expert
  (defendant).

## Third parties, evidence, financials

- **3–5 third parties** drawn from the decedent's treating physician, the attorney or
  notary who oversaw the signing, the two attesting witnesses, another sibling and heir,
  the bank or financial advisor managing the estate accounts, and a caregiver / home
  health aide.
- **4–7 evidence items**: the contested will and any self-proving affidavit, the prior
  will, the decedent's medical and cognitive records around the signing, the drafting
  attorney's file and notes, affidavits from the attesting witnesses, the decedent's
  financial records showing the beneficiary's involvement, and correspondence showing
  isolation or control.
- **3–5 financials**: the value of the estate, the value of the share diverted to the
  favored beneficiary, the contestant's intestate or prior-will share, and the estimated
  cost of the capacity / document experts.

## Downstream target

[`maine-probate-forms`](https://github.com/bedardandy/maine-probate-forms) — example forms
`DE-101` (application/petition for probate), `DE-301` (formal testacy / appointment), and
`PP-401` (personal-representative paperwork).

## Reproduce

```sh
python3 tools/generate.py will-contest --seed 1
python3 tools/smoke.py --scenarios will-contest --count 8 -v
```

## Notes

The litigation sub-lists that should vary by seed (affirmative defenses, discovery,
motions) use the DSL `pick_n`/`n` sampler; the ordered/numbered lists (causes of action,
docket) are fixed so count numbering and chronology stay coherent. `prior_will_existed`,
`isolation_alleged`, and `drafting_attorney_used` are booleans, so they are never used with
the `{..._lower}` string helper; only string facts (e.g. `favored_beneficiary`,
`share_to_favored`, `capacity_concern`, `execution_irregularity`) are templated, and no
fact references another fact. The `decedent` role uses `with_contact: false`, so the
testator carries a name and date of birth but no email or phone, and the decedent and
family are described with dignity.
