> **AI/legal-use disclosure:** This repository is experimental, AI-assisted workflow software. It is not legal advice, not a primary legal source, and not lawyer-reviewed as a complete statement of law. Outputs are first drafts for human review, intended to reduce creation effort while increasing focused review effort. See [AI_DISCLOSURE.md](AI_DISCLOSURE.md).

# Maine Mock Case Generator

Generate — or guide the detailed generation of — **fictional US legal matters** for
**smoke-testing an end-to-end legal workflow pipeline**. Each generated matter is a rich,
internally-consistent package (fact pattern, intake interview, client objectives, third
parties, legal issues, expert opinions, evidence, financials) that **projects down** to
the canonical case object consumed by the downstream form-filling repos.

> ⚠️ **Everything here is fictional mock data, not legal advice.** See
> [`DISCLAIMER.md`](DISCLAIMER.md). Phones use the `555-01xx` fiction range, emails use
> `example.*`, identities are invented.

```
scenarios/*.yaml ──▶  Mock Matter (rich)  ──▶  canonical case  ──▶  downstream form fillers
   or the LLM-guided skill                     (matter/parties/party/facts)
```

## Why

The sibling repos — [`maine-court-forms`](https://github.com/bedardandy/maine-court-forms),
[`maine-probate-forms`](https://github.com/bedardandy/maine-probate-forms),
[`transactional-tax-forms`](https://github.com/bedardandy/transactional-tax-forms) — all
consume a **canonical fact object** and fill PDFs from it. To test that pipeline
end-to-end you need realistic *inputs*. This repo manufactures those inputs on demand,
deterministically and at volume, and projects them into the exact shape the fillers expect.

## Two ways to generate

| | Deterministic engine | LLM-guided skill |
|--|--|--|
| **Use for** | Fast, reproducible CI fixtures; bulk volume | Rich, detailed, novel matters |
| **Entry point** | `tools/generate.py` | [`skills/mock-case-generator/SKILL.md`](skills/mock-case-generator/SKILL.md) |
| **Needs a model?** | No | Yes (runs inside an agent) |
| **Reproducible?** | Yes — `(scenario, seed)` | No |

Both emit the same [`mock_matter.schema.json`](catalog/mock_matter.schema.json) shape.

## Quick start

```bash
pip install -r requirements.txt          # jsonschema + PyYAML

python tools/generate.py --list          # list scenarios
python tools/generate.py family-divorce-cumberland --seed 1        # a full mock matter
python tools/generate.py family-divorce-cumberland --seed 1 --canonical   # projected canonical case
python tools/smoke.py --count 5          # end-to-end smoke test across all scenarios
python -m pytest -q                      # test suite
```

Or via `make`: `make list`, `make generate SCENARIO=estate-tax-706 SEED=2`, `make smoke`, `make test`.

## Concrete fills (end-to-end proof)

The generator doesn't stop at a canonical case — it pours matters into **real downstream
form mappings** (vendored in `integration/`) so you can see exactly which PDF fields get
populated. **Ten forms across all three repos and three fact-key namespaces** are wired
(the probate repo ships no fact-key mapping, so DE-301's was authored here from its schema):

```bash
python tools/fill.py --list
python tools/fill.py CV-007 --seed 1        # eviction, native canonical (~97%)
python tools/fill.py ME-RETTD --seed 1      # real estate transfer, via real-estate adapter (100%)
python tools/fill.py IRS-SS-4 --seed 1 --show-empty   # EIN application, via tax adapter
```

| Namespace (profile) | Forms | Adapter |
|---------------------|-------|---------|
| `canonical` (`parties`/`matter`/`facts`) | FM-004, FM-006, FM-050, PA-001, CV-007, MRS-706ME | none — native |
| `tax` (`entity`/`responsible_party`/…) | IRS-SS-4, IRS-2553 | `adapters.to_tax_case` |
| `real_estate` (`property`/`transferor`/`transferee`) | ME-RETTD | `adapters.to_real_estate_case` |

Each fill prints a coverage report and required-key check; the form-namespace case JSON it
emits is the input the downstream repo's PDF engine renders. See
[`integration/README.md`](integration/README.md).

## Compound (intertwined) matters

Real problems cascade across practice areas. A **compound matter** is a universe of linked
matters that **share one cast** and cross-reference each other:

```bash
python tools/compound.py --list
python tools/compound.py death-cascade --seed 1 --summary             # probate + estate tax + guardianship
python tools/compound.py business-dispute-cascade --seed 1 --summary  # formation + complex litigation
```

| Compound | Matters | Through-line |
|----------|---------|--------------|
| `death-cascade` | probate + estate-tax + guardianship | one decedent; estate value feeds the 706; the minor heir is the ward |
| `marital-breakdown-cascade` | divorce + protection-from-abuse + business | same spouses & children; the marital business is contested |
| `business-dispute-cascade` | formation + complex civil litigation | the company formed in one matter is the defendant in the other |
| `elder-exploitation-cascade` | improvident transfer + conservatorship + will contest | one elder (transferor → ward → decedent); same exploiter & protective relative |

The same party objects appear across matters, so identities stay consistent everywhere.
Each constituent is an independently-valid Mock Matter and projects to its own canonical
case. See [`docs/compound.md`](docs/compound.md).

## Deep litigation

The `complex-civil-litigation` scenario exercises the schema's `litigation` section: a
multi-party suit with multiple counts, affirmative defenses, counterclaims, cross-claims,
a third-party complaint, discovery, motions, a chronological docket, and trial details.

## Edge cases

Two scenarios deliberately probe boundaries: `insolvent-estate` (a probate where claims
always exceed assets, stressing claim-priority and allowance logic) and
`pro-se-interstate-custody` (a self-represented parent — no attorney generated — with a
cross-border UCCJEA jurisdiction question). `tests/test_edge.py` adds wide seed sweeps and
boundary assertions (zero-children handling, no-counsel projection, multi-party rosters).

## Probate fixtures (schema-driven path)

The probate repo fills forms a different way — each `schema.json` field carries a
`fill_strategy.source`. A second generator (`generator/schema_fill.py`) produces that
pipeline's native case shape (`case_dict` / `<role>_record` / `narrative_facts`) directly
from a form's annotated schema, with type-aware synthesis, coherent per-role identities, and
a `--stress` overflow mode:

```bash
python tools/probate_case.py --list
python tools/probate_case.py DE-401 --seed 7
python tools/probate_case.py --all --seeds 0,1,2 --out out/probate
python tools/fetch_probate_schemas.py --refresh    # add/update vendored probate schemas
```

See [`docs/probate-fixtures.md`](docs/probate-fixtures.md).

## Real-estate & asset-sale closing binders

A dedicated suite models the full arc of **real-estate and asset-sale closings** — the kind
of rich, term-sheet-and-PSA data plus back-and-forth party communications you'd find in a
closing binder. Each scenario populates a deal's economics into `facts` (a term sheet's
worth of fields), spots the governing issues, and authors a **simulated correspondence
thread** (see below):

| Scenario | Deal type | Highlights |
|----------|-----------|------------|
| `residential-purchase-sale` | Single-family PSA closing | contingencies, inspection/repair, loan commitment |
| `commercial-property-sale` | Income-property (office/retail/industrial) | cap rate/NOI, Phase I ESA, estoppels/SNDA, DSCR loan |
| `subdivision-development-sale` | Raw land for a subdivision | planning-board & DEP approvals, bonding, phased takedowns |
| `condo-unit-sale` | Condominium unit resale | Maine Condo Act resale certificate, assessments, condo loan |
| `construction-loan-closing` | Construction loan + GMP contract | AIA draw schedule, retainage, lien waivers, bonding |
| `resource-extraction-sale` | Gravel pit / quarry / timberland | reserves & royalty, extraction permits, reclamation bond |
| `business-asset-sale` | Operating-business asset purchase | Form 8594 allocation, working-capital true-up, QoE diligence |
| `like-kind-exchange-1031` | IRC § 1031 deferred exchange | qualified intermediary, 45/180-day clock, boot & debt matching |

```bash
python tools/generate.py commercial-property-sale --seed 1
python tools/generate.py business-asset-sale --seed 1 | python -m json.tool
python tools/smoke.py --scenarios like-kind-exchange-1031 -v
```

The `business-asset-sale` thread includes the buyer's accountant sending **financing and
business-accounting due-diligence questions** (general ledger, AR/AP aging, revenue
recognition, add-back support, quality-of-earnings), and `like-kind-exchange-1031` is the
deliberately **smaller, tax-driven cousin** of the sale binders.

### Simulated communications

Every matter can now carry a `communications` array — a **chronological, name-consistent
back-and-forth** between the parties and their brokers, lenders, title/escrow agents,
accountants, and counsel (emails, letters, memos). It is authored in the scenario, templated
against the same context as the narrative (so senders, dates, and deal terms stay
consistent), and date-sorted by the engine. All eight closing-suite scenarios ship a thread;
any scenario can add one under a `communications:` block. See
[`docs/data-model.md`](docs/data-model.md).

## Seed scenarios

Thirty-nine archetypes spanning the three downstream repos and eight practice areas. Add more by dropping a new
`scenarios/<id>/scenario.yaml` — no code changes required.

| Scenario | Practice area | Downstream repo |
|----------|---------------|-----------------|
| `family-divorce-cumberland` | family (divorce, kids, property) | maine-court-forms |
| `protection-from-abuse` | family (PFA order) | maine-court-forms |
| `small-claims-debt` | civil (small claims ≤ $6k) | maine-court-forms |
| `decedent-estate-informal` | probate (informal probate) | maine-probate-forms |
| `minor-guardianship` | probate (guardian of a minor) | maine-probate-forms |
| `business-formation-scorp` | business (incorporate + S-elect) | transactional-tax-forms |
| `estate-tax-706` | tax (Form 706 / 706ME + 1041) | transactional-tax-forms |
| `complex-civil-litigation` | civil (deep, multi-party litigation) | maine-court-forms |
| `insolvent-estate` | probate (edge: claims exceed assets) | maine-probate-forms |
| `pro-se-interstate-custody` | family (edge: pro se + UCCJEA jurisdiction) | maine-court-forms |
| `real-estate-transfer` | real estate (deed + transfer tax) | transactional-tax-forms |
| `residential-eviction` | civil (landlord-tenant FED) | maine-court-forms |
| `personal-injury-auto` | civil (auto tort, deep litigation) | maine-court-forms |
| `employment-discrimination` | civil (MHRA / Title VII) | maine-court-forms |
| `criminal-oui` | criminal (OUI defense) | maine-court-forms |
| `adult-conservatorship` | probate (guardian/conservator of an adult) | maine-probate-forms |
| `commercial-contract-dispute` | civil (breach + personal guaranty) | maine-court-forms |
| `construction-defect` | civil (multi-party defect/excavation) | maine-court-forms |
| `condominium-construction-dispute` | real estate (Maine Condo Act) | maine-court-forms |
| `equitable-partition` | real estate (co-tenant partition) | maine-court-forms |
| `paper-street-road-access` | real estate (paper streets + road assn.) | maine-court-forms |
| `rule-80b-zoning-appeal` | administrative (Rule 80B record review) | maine-court-forms |
| `arbitration-award-dispute` | civil (confirm/vacate award) | maine-court-forms |
| `improvident-transfer` | probate (elder undue-influence deed) | maine-court-forms |
| `divorce-hidden-crypto` | family (concealed crypto assets) | maine-court-forms |
| `timber-trespass` | real estate (tree cutting, treble damages § 7552) | maine-court-forms |
| `intertidal-shoreland-access` | real estate (intertidal / colonial ordinance) | maine-court-forms |
| `will-contest` | probate (capacity / undue influence / execution) | maine-probate-forms |
| `llc-member-oppression` | business (minority freeze-out, § 1595) | maine-court-forms |
| `short-term-rental-dispute` | civil (STR covenant / nuisance / zoning) | maine-court-forms |
| `medical-malpractice` | civil (§ 2851 screening panel) | maine-court-forms |
| `residential-purchase-sale` | real estate (single-family PSA closing) | transactional-tax-forms |
| `commercial-property-sale` | real estate (income-property closing) | transactional-tax-forms |
| `subdivision-development-sale` | real estate (subdivision land + approvals) | transactional-tax-forms |
| `condo-unit-sale` | real estate (Maine Condo Act unit resale) | transactional-tax-forms |
| `construction-loan-closing` | real estate (construction loan + GMP contract) | transactional-tax-forms |
| `resource-extraction-sale` | real estate (gravel/quarry/timberland) | transactional-tax-forms |
| `business-asset-sale` | business (operating-business asset purchase) | transactional-tax-forms |
| `like-kind-exchange-1031` | tax (IRC § 1031 deferred exchange) | transactional-tax-forms |

Browse a worked sample of each under [`examples/`](examples/) (`*.matter.json` and the
projected `*.canonical.json`).

## What a Mock Matter contains

`provenance` · `matter` · `parties` (+ `third_parties`) · `fact_pattern` (narrative,
timeline, disputed/undisputed) · `intake_interview` · `client_objectives` · `issues`
(with governing law) · `expert_opinions` · `evidence` · `financials` · `litigation` ·
`communications` (simulated deal/closing correspondence) · `facts` (the flat form-specific
bridge). Full reference: [`docs/data-model.md`](docs/data-model.md).

## Repository layout

```
catalog/      schemas (mock_matter, canonical_case, compound_matter), practice_areas, faker_pools
scenarios/    one folder per archetype (scenario.yaml + README.md)
compound/     intertwined matter universes (compound.yaml + README.md)
generator/    the engine: pools, dsl, scenarios, engine, project, schema, adapters, formfill, compound
tools/        generate, validate, project_canonical, fill, compound, smoke, build_examples, mcp_server
integration/  vendored real downstream form mappings + registry (concrete fills)
skills/       mock-case-generator/ (LLM-guided generation protocol + prompts)
examples/     generated matters, canonical projections, fill plans, and compound universes
docs/         architecture, data-model, integration, compound, smoke-testing
tests/        pytest suite
```

## Adapting it

- **New practice area / state**: copy a `scenarios/<id>/scenario.yaml`, edit the
  jurisdiction, facts, issues, and templates. Run `python tools/smoke.py --scenarios <id> -v`.
- **New downstream form**: read its `mapping.json`, add the keys it needs to the
  scenario's `facts:` block. `facts` is open (`additionalProperties`) on both schemas.
- **Wire into your pipeline**: see [`docs/integration.md`](docs/integration.md).

## Documentation

- [Architecture](docs/architecture.md) — data flow, modules, design choices
- [Data model](docs/data-model.md) — the schemas + the projection mapping
- [Integration](docs/integration.md) — feeding the downstream form repos + concrete fills
- [Compound matters](docs/compound.md) — intertwined matter universes
- [Probate fixtures](docs/probate-fixtures.md) — schema-driven probate fill path
- [Smoke testing](docs/smoke-testing.md) — CI and volume/fuzz testing
- [Disclaimer](DISCLAIMER.md) — fictional-data guarantees and responsible use
