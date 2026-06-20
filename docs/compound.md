# Compound (intertwined) matters

A real legal problem rarely stays in one lane. A death spawns a probate, an estate-tax
filing, and maybe a guardianship. A marriage failing spawns a divorce, a protection
order, and a fight over the family business. A compound matter models this: a **universe**
of constituent matters that **share one cast** of people and organizations and
**cross-reference** one another.

## How it works

A compound archetype lives in `compound/<id>/compound.yaml` and declares:

- **`cast`** — the shared people/organizations (each built once as a fictional party).
- **`matters`** — each constituent matter: a base `scenario`, a `roles` map binding
  cast members to that scenario's role keys, and `relates` links to sibling matters.

The generator (`generator/compound.py`) builds the cast once, then generates each
constituent matter with the cast injected via the engine's `overrides` mechanism — so the
**same party object** appears across matters. Because identities are fixed *before*
templating, every matter's narrative and facts stay internally consistent with the shared
cast. Each constituent is a normal, independently-valid Mock Matter that also carries
`matter.universe_id` and `related_matters` back-links.

```
compound/death-cascade/compound.yaml
        │  shared cast: decedent, surviving_spouse, minor_child, grandparent, ...
        ▼
  ┌─────────────┐   ┌──────────────┐   ┌────────────────┐
  │  probate    │──▶│  estate_tax  │   │  guardianship  │   ← 3 Mock Matters
  │ (DE/PP)     │   │ (706/706ME)  │   │ (GS)           │
  └─────────────┘   └──────────────┘   └────────────────┘
   same decedent + personal representative; the minor is heir AND ward
```

## Seed archetypes

| Compound | Matters | Through-line |
|----------|---------|--------------|
| `death-cascade` | probate + estate tax + guardianship | One death; the estate inventory feeds the 706, the minor heir becomes a ward |
| `marital-breakdown-cascade` | divorce + protection-from-abuse + business | Same spouses and children; the marital business is a contested asset |
| `business-dispute-cascade` | business formation + complex civil litigation | The company formed in one matter is the defendant in the other; the founder is applicant then defendant |
| `elder-exploitation-cascade` | improvident transfer + adult conservatorship + will contest | One elder is the transferor, then the ward, then the decedent; the exploiter is the deed transferee then the will proponent |

## Generate one

```bash
python tools/compound.py --list
python tools/compound.py death-cascade --seed 1 --summary
python tools/compound.py business-dispute-cascade --seed 1 --canonical   # one canonical case per matter
python tools/compound.py marital-breakdown-cascade --seed 1 --out out/
```

`--summary` prints the cast (with where each member appears), the matters, and the
relationship graph. `--canonical` projects every constituent to its own canonical case,
so each can drive a downstream form fill independently.

## Validation

`validate_compound` checks the compound envelope **and** every constituent matter against
`mock_matter.schema.json`. The smoke harness and pytest sweep all archetypes across seeds,
and assert the shared cast is truly identical across matters (not just same-named).

## Adding a compound

1. Create `compound/<id>/compound.yaml` with a `cast` and `matters` list.
2. Bind cast members to each scenario's role keys (use the role keys that scenario
   defines — e.g. `plaintiff`, `decedent`, `applicant`, `company`, `child_1`).
3. Add `relates` links between matters for the cross-references.
4. Run `python tools/compound.py <id> --seed 1 --summary` and the smoke suite.

No code changes are required — `compound.py` interprets the archetype declaratively.
