# Legal-issue tiering (confounders)

Real matters rarely present one clean issue. A nonpayment eviction may also carry a
standing defect (the LLC that owns the building never signed the lease), a waiver
argument (the landlord stopped collecting rent two years ago), or a habitability
counterclaim. To make the smoke tests adversarial, a scenario can layer **confounding
secondary issues** on top of its **primary issue**.

## Shape

A scenario adds a top-level `confounders:` block:

```yaml
confounders:
  count: {weights: [55, 28, 13, 4]}   # P(0,1,2,3 fire) — most matters stay clean
  pool:
    - id: standing-real-party
      weight: 5                         # relative likelihood within the pool
      requires: {quit_ground: nonpayment}   # optional coherence gate (all must match)
      excludes: {tenancy_type: at_will}      # optional inverse gate
      confidence: "well-settled core; the particular mismatch is fact-specific"
      source: "14 M.R.S. § 6001(1); Bureau v. Gendron, 783 A.2d 643 (Me. 2001)"
      facts: { ... }        # merged into the canonical fact set (the decision point)
      issue: { issue, category, governing_law, sub_questions, strength }   # spotted issue
      defense: { defense, by, basis }   # optional affirmative defense
```

## Semantics

- **Independently sampled.** `count` decides how many fire; a `{weights: [...]}` count
  is a distribution over 0,1,2,… so most matters draw zero and any one exotic issue is
  rare. (The `{min,max}` form is also supported.)
- **Coherence-gated.** `requires` / `excludes` are dicts of `{fact: value-or-[values]}`;
  a confounder only attaches where it is legally coherent with the chosen variant (no
  rent-waiver issue on a no-cause termination, etc.).
- **Facts → canonical.** A confounder's `facts` are merged after the variant (so they may
  reference and override variant facts) and flow through to the canonical fact object —
  the smoke test sees a real decision point, not just a label.
- **Issue + defense.** The `issue` is appended to `issues[]` (stamped with
  `[confounder:<id>; <confidence>]` in its `notes`); a `defense` is appended to
  `litigation.affirmative_defenses` (also projected to canonical).
- **Provenance.** The ids that fired are recorded in `provenance.confounders`.

## Grounding & disclaimer

Confounder `source` / `governing_law` are **AI-assembled research, NOT legal advice**
(see [`DISCLAIMER.md`](../DISCLAIMER.md)). Each entry carries a `confidence` flag
(well-settled / fact-specific / EXPERIMENTAL) and states its overbroad-application risk
inline, so the generator encodes the *correct* rule as the oracle rather than a naive
over-claim. Statute text drifts — verify against legislature.maine.gov before any
real-world reliance. Entries marked EXPERIMENTAL reflect genuinely unsettled Maine law.
