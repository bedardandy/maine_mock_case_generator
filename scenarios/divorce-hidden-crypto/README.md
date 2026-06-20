# Scenario: divorce-hidden-crypto

A **high-asset Maine divorce with concealed digital assets**. One spouse is hiding
a meaningful share of the marital wealth in cryptocurrency; the other spouse (the
client) fights to find, value, and divide the hidden coins through forensic tracing,
exchange subpoenas, and discovery sanctions. This deepens the basic divorce template
with a modern asset-concealment battle and exercises the schema's `litigation` block.

## Models

The plaintiff spouse petitions to divorce the defendant spouse and asks the court to
find, value, and equitably divide the entire marital estate, including roughly
`suspected_crypto_value` in cryptocurrency the plaintiff alleges the defendant
concealed. The plaintiff also seeks a dissipation finding, an adverse inference, and
attorney fees for the non-disclosure, while protecting any children's stability.

- **Practice area:** family · **case_type:** `divorce` · **status:** `active`
- **Jurisdiction:** random Maine county, District Court
- **Parties:** `plaintiff` (spouse seeking full disclosure, the client), `defendant`
  (spouse concealing assets), `attorney`, and `child_1..N` (0–2 children)
- **Signing filer (`client`):** the plaintiff
- **Dates:** `filing_date` in 2025-04 .. 2026-02; `event_date` bound to the separation date

## Downstream target

[`maine-court-forms`](https://github.com/bedardandy/maine-court-forms) — representative
forms `FM-004` (divorce complaint), `FM-043` (financial statement), `FM-050`.

## Key issues (with governing law)

- Duty of full, accurate disclosure on the financial statement (FM-043) — `M.R. Civ. P. 26` (**strong**)
- Dissipation / economic misconduct in the equitable division — `19-A M.R.S. § 953` (**strong**)
- Classification and valuation of cryptocurrency as marital property — `19-A M.R.S. § 953(1)`
- Discovery sanctions, adverse inference, fees, and preclusion — `M.R. Civ. P. 37` (**strong**)
- Contempt for violating disclosure / preservation orders — `M.R. Civ. P. 66`
- The valuation date for volatile cryptocurrency — `19-A M.R.S. § 953`

Full-disclosure and dissipation are weighted as the strongest issues.

## Litigation depth (`litigation` block)

- **4 ordered causes of action** framed as the relief sought in the divorce: equitable
  division capturing the concealed crypto, a dissipation/economic-misconduct adjustment,
  an order compelling full disclosure of all digital assets, and discovery sanctions plus
  an adverse inference.
- **2–4 affirmative defenses** raised by the defendant (acquired after separation, keys
  genuinely lost, separate property, value overstated) sampled via `pick_n`.
- **4–6 discovery items** — digital-asset interrogatories, RFP for exchange/wallet records,
  a subpoena to the cryptocurrency exchange, a deposition of the defendant, an
  `independent_examination` (forensic device imaging), and an RFA on wallet existence.
- **3–5 motions** — compel disclosure, sanctions/adverse inference, appoint a neutral
  forensic examiner, contempt, and freeze/preserve the crypto.
- A chronologically-ordered **docket** (6–7 entries, non-overlapping date windows keep it
  in order) and a bench **trial** (`jury: false`, 2–5 days, scheduled 2026-07 .. 2027-02),
  with `posture: discovery`.

## Experts

2–3 plaintiff-retained experts: a blockchain forensic analyst tracing wallet activity, a
forensic accountant valuing the estate and tracing fiat into crypto, and a business
valuation expert for the startup and its tokens.

## Third parties

Sampled (3–5) from: the cryptocurrency exchange holding KYC records (Coinbase, Inc.), a
blockchain-forensics firm, the marital business that paid the defendant in tokens, the
defendant's employer, the parties' accountant, and a bank where fiat moved before the
crypto purchases.

## Canonical `facts` emitted

`marriage_date`, `separation_date`, `grounds`, `marital_estate_value`,
`suspected_crypto_value`, `crypto_assets`, `concealment_tactic`, `known_exchange`,
`marital_business`, and the booleans `forensic_expert_retained`,
`discovery_noncompliance`, and `disclosed_on_financial_statement`.

## Notes

The litigation sub-lists that should vary by seed (defenses, discovery, motions) use the
DSL `pick_n`/`n` sampler; the ordered/numbered lists (causes of action, docket) are fixed
so count numbering and chronology stay coherent. The three boolean facts are never
lowercased in prose (only string facts get a `{key_lower}` variant), and the crypto
narrative draws on the lowercased string facts (`{grounds_lower}`,
`{concealment_tactic_lower}`, `{crypto_assets_lower}`, `{marital_business_lower}`).
Validated with `python3 tools/generate.py divorce-hidden-crypto --seed 1` and an 8-seed
smoke sweep (PASS, 0 failures).
