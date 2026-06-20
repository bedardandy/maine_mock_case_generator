---
name: mock-case-generator
description: >
  Guide the detailed, LLM-assisted generation of a rich, internally-consistent
  FICTIONAL US legal matter (fact pattern, intake interview, third parties, issues,
  expert opinions, evidence, client objectives) that conforms to
  catalog/mock_matter.schema.json and projects to the downstream canonical case object.
  Use when smoke-testing an end-to-end legal workflow pipeline and you want richer,
  more narrative matters than the deterministic engine produces.
---

# Mock Case Generator (LLM-guided)

This skill produces **one fictional Mock Matter** for smoke-testing a legal pipeline.
The deterministic engine (`tools/generate.py`) is best for fast, reproducible CI
fixtures; use **this skill** when you want a detailed, realistic, human-readable
matter built from a short brief — or when you need a practice area the seeded
scenarios don't cover yet.

Everything you produce is **mock and fictional**. Read `DISCLAIMER.md` once before
starting and honor the fictional-data rules below.

## Inputs you accept

A short brief, e.g. *"a contested guardianship in Penobscot County where the
grandmother seeks custody because both parents are in treatment"*, or just a
practice area. If the user names a seed scenario id (`scenarios/<id>/scenario.yaml`),
read it first and use it as the backbone.

## The contract you must satisfy

1. Output a single JSON object validating against **`catalog/mock_matter.schema.json`**.
   Required top-level keys: `schema_version` ("1.0"), `provenance`, `matter`,
   `parties`, `fact_pattern`.
2. It must **project** cleanly: after writing the file, run
   `python tools/project_canonical.py <file>` and confirm it validates against the
   downstream canonical schema. Use only canonical-compatible party role keys
   (`plaintiff`, `defendant`, `petitioner`, `respondent`, `decedent`,
   `personal_representative`, `attorney`, `other_party`, `company`, and `child_1..`).
   The represented party should be duplicated under `client` so it becomes the
   signing filer.
3. Set `provenance.mock = true`, `provenance.fictional = true`,
   `provenance.generator = "agent-skill"`, and `provenance.model` to the model id.

## Fictional-data rules (non-negotiable)

- **People & orgs**: invent names. Do not use the name of any real, identifiable person.
- **Phones**: `(207) 555-01xx` (the range reserved for fiction).
- **Emails**: `name@example.com` / `.org` / `.net` only.
- **Addresses**: invented street addresses. Real county / court-location names are
  fine (they drive routing); real specific street addresses are not.
- **SSNs**: never real. Use a fictional last-4 only if a field needs it.
- **Citations**: include realistic statute/rule cites (e.g. `19-A M.R.S. § 1653`,
  `IRC § 2056`) to exercise issue-spotting, but treat them as illustrative.

## Protocol

Work in this order; each step feeds the next. Keep everything internally consistent
(dates in the timeline must match dates in `facts`; the parties named in the
narrative must be the parties in `parties`).

1. **Frame the matter** — pick `practice_area`, `case_type`, jurisdiction
   (state/county/court), and `status`. Draft a one-sentence `matter.summary`.
   See `prompts/00-intake-brief.md`.
2. **Fact pattern** — write a 2–4 paragraph `fact_pattern.narrative`, plus
   `undisputed_facts`, `disputed_facts`, and a dated `timeline`.
   See `prompts/10-fact-pattern.md`.
3. **Parties & third parties** — derive `parties` (with contact info) and
   `third_parties` (witnesses, institutions, agencies, experts-as-people).
4. **Intake interview** — simulate `intake_interview.exchanges` (topic/question/answer)
   that surface the facts a real intake would. See `prompts/20-interview.md`.
5. **Objectives** — `client_objectives`: goals (ranked), priorities, constraints,
   `risk_tolerance`, desired outcomes, non-starters.
6. **Issues & experts** — spot `issues` (each with `governing_law`), and add
   `expert_opinions` where a real matter would retain experts.
   See `prompts/30-issues-experts.md`.
7. **Evidence & financials** — list `evidence` exhibits and any `financials`.
8. **Canonical facts** — fill `facts` with the flat, form-specific keys the
   downstream forms need (e.g. `marriage_date`, `gross_estate_value`,
   `date_of_death`, `entity_name`). These pass through to `canonical_case.facts`.
9. **Assemble & validate** — emit the JSON, then run:
   ```
   python tools/validate.py <file>
   python tools/project_canonical.py <file>   # validates canonical too
   ```
   Fix anything the validators report. See `prompts/40-assemble-json.md`.

## Honesty about gaps

If the brief doesn't state a fact, you may invent a plausible fictional value —
but prefer to **omit** a detail rather than fabricate something a real intake
couldn't know (e.g. an exact account balance). Note material unknowns in
`notes` or as a `disputed_facts` entry, mirroring how the upstream form repos flag
"missing facts" rather than inventing them.

## Quick reference

- Schema: `catalog/mock_matter.schema.json`
- Downstream contract: `catalog/canonical_case.schema.json`
- A worked example per practice area: `examples/*.matter.json`
- Seed scenario backbones: `scenarios/<id>/scenario.yaml`
