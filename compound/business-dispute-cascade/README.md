# Compound: business-dispute-cascade

A company's life cycle as two intertwined matters: its **formation** (and S-election) and
the **complex civil litigation** brought by its investors.

| Local id | Scenario | Shared roles |
|----------|----------|--------------|
| `formation` | `business-formation-scorp` | founder (applicant), the company |
| `litigation` | `complex-civil-litigation` | investor (plaintiff), co-investor (plaintiff_2), the company (defendant), founder (defendant_2), auditor (third_party_defendant) |

**Through-line:** the company formed in the `formation` matter is the **defendant** in the
`litigation` matter, and the founder is the **applicant** who later becomes a
**defendant officer**. The same organization and person carry across the transactional and
litigation matters, tying the deep-litigation archetype back to where the entity began.

```bash
python tools/compound.py business-dispute-cascade --seed 1 --summary
```
