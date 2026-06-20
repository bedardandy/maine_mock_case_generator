# Scenario: `small-claims-debt`

A **Maine District Court small claims** action to collect an unpaid debt.

The client (the **plaintiff**) is a sole-proprietor small-business owner suing a
former **customer** who did not pay. Every generated matter is fictional and
reproducible from `(scenario_id, seed)`.

## At a glance

| Field | Value |
| --- | --- |
| `id` | `small-claims-debt` |
| `practice_area` | `civil` |
| `case_type` | `small_claims` |
| `status` | `pre_filing` |
| `docket_prefix` | `SC` (e.g. `AND-SC-2025-122`) |
| Jurisdiction | Maine (`ME`), **random county**, District Court |
| Client role | `plaintiff` (the creditor / business owner) |
| Opposing party | `defendant` (the customer who owes the debt) |
| Downstream repo | `maine-court-forms` |
| Example forms | `SC-001`, `SC-013`, `CV-001` |

## The story

A sole proprietor running one of several small businesses (landscaping,
home repair, auto repair, catering, or freelance web design) completed work or
delivered goods for a customer in early 2025. The customer was invoiced, paid
only a small partial amount (or nothing), and then stopped responding. After a
written demand letter went unanswered, the owner brings a small claims action
to recover the **unpaid balance** (the invoice amount less whatever was paid),
plus court costs and post-judgment interest.

The claim is intentionally kept **at or under $6,000**, the Maine small claims
jurisdictional limit under 14 M.R.S. § 7482.

## Generated facts

These keys are randomized per seed and surface as canonical `facts` for
downstream form-fillers:

- `business_name` — the plaintiff's business (landscaping, home repair, auto
  repair, catering, or web design).
- `debt_origin` — unpaid invoice for services, goods delivered, a defaulted
  personal loan, or unpaid equipment rent.
- `services_completed_date` — when the work was finished (also the matter's
  `event_date`).
- `invoice_amount` — amount billed (\$900–\$6,000).
- `amount_paid` — partial payment received (\$0–\$800).
- `demand_letter_date` — when the written demand was sent.
- `written_contract` — boolean: whether a signed contract existed.
- `interest_claimed` — boolean: whether pre-judgment interest is sought.
- `contract_status` — plain-language description of how the deal was documented
  (signed contract, signed work order, oral agreement confirmed by email/text,
  or an informal arrangement), used to keep the narrative grammatical.

The **balance due** equals `invoice_amount - amount_paid`; the narrative refers
to it as "the unpaid balance" rather than computing exact arithmetic.

## Third parties

Drawn from a pool (1–3 selected per seed):

- A **collections agency** the plaintiff consulted (`business_entity`).
- The **bank** on which a returned check was drawn (`financial_institution`).
- An **employee / witness** who performed the work (`witness`).

## Issues (with governing law)

The issue pool (3–5 selected per seed) tracks the governing Maine law:

- **Small claims jurisdiction and the \$6,000 limit** — 14 M.R.S. § 7482.
- **Breach of contract** — Maine common law.
- **Account stated** — Maine common law.
- **Statute of limitations** (six years for contracts) — 14 M.R.S. § 752.
- **Post-judgment interest and costs** — 14 M.R.S. § 1602-C.
- **Compliance with the Maine Rules of Small Claims Procedure.**

The statute-of-limitations and jurisdiction issues are typically `strong` for
the plaintiff because the debt arose recently in 2025.

## Experts, evidence, and financials

- **Experts** (0–1): a forensic accountant (CPA) retained by the plaintiff to
  authenticate the account ledger and confirm the balance due.
- **Evidence** (3–6): the written contract / work order, the unpaid invoice, the
  account / payment ledger, the demand letter, email and text exchanges
  acknowledging the debt, and a returned / bounced check.
- **Financials** (USD; 2–4 line items, not summed): the invoice amount, the
  amount already paid, claimed pre-judgment interest, and the court filing fee.

## Client objectives

Recover the unpaid balance and court costs, resolve the matter efficiently, and
avoid throwing good money after bad. Risk tolerance is **moderate**. The single
non-starter is **writing off the full debt** and walking away with nothing.

## Generate and validate

```bash
# Emit one matter
python3 tools/generate.py small-claims-debt --seed 1

# Emit the projected canonical case (downstream contract)
python3 tools/generate.py small-claims-debt --seed 1 --canonical

# End-to-end smoke test (generate -> validate -> project -> validate)
python3 tools/smoke.py --scenarios small-claims-debt --count 6 -v
```
